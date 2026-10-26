"""Local causal regressions for alias protection, direct methods and guidance drift."""
import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from test_router_v2 import assessment, router
import workflow_context


def node(plan, key):
    return next(item for item in plan['steps'] if item['id'] == key)


class RoutingAuditRepairs(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / 'test-runs/local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)

    def finish(self, task, stop=None, first_output=None):
        while True:
            plan = router.plan_v2(task)
            step = next((row for row in plan['steps'] if row['state']=='ready' and row['id']!='present'), None)
            if step is None or step['id']==stop:
                return plan
            output = first_output if step['id']=='inspect_context' and first_output else self.folder/(task['task_id']+'-'+step['id']+'.txt')
            if output != first_output:
                output.write_text('Synthetic inspected '+step['id'], encoding='utf-8')
            task.setdefault('receipts', []).append({'step':step['id'], 'binding':step['input_binding'],
                'evidence':'Local synthetic fixture', 'output':{'kind':'file','locator':str(output),'revision':router.file_hash(output)}})

    def revision(self, hardlink):
        original = self.folder/'accepted.txt'
        original.write_text('Accepted predecessor evidence', encoding='utf-8')
        working = self.folder/'working.txt'
        if hardlink:
            os.link(original, working)
        else:
            shutil.copyfile(original, working)
        source = {'id':'working','kind':'file','locator':str(working),'revision':router.file_hash(working),'status':'available','inspected':True}
        task = assessment(actions=['revise'],scope='exact',sources=[source])
        self.finish(task,stop='revise_source',first_output=original)
        return task, original, working

    def test_hardlink_alias_cannot_be_authorized_as_independent_working_copy(self):
        task, original, working = self.revision(True)
        self.assertTrue(original.samefile(working))
        before = original.read_bytes()
        with self.assertRaisesRegex(ValueError,'accepted predecessor'):
            router.begin_step(task,'working')
        self.assertEqual(original.read_bytes(),before)

    def test_identical_bytes_in_a_distinct_copy_are_allowed(self):
        task, original, working = self.revision(False)
        self.assertFalse(original.samefile(working))
        self.assertEqual(router.begin_step(task,'working')['source_id'],'working')

    def test_unobservable_file_identity_cannot_authorize_edit(self):
        task, _, _ = self.revision(False)
        with patch.object(Path,'samefile',side_effect=PermissionError('synthetic identity failure')):
            with self.assertRaisesRegex(ValueError,'identity'):
                router.begin_step(task,'working')

    def test_portfolio_alias_of_upstream_evidence_is_blocked(self):
        upstream=assessment(task_id='upstream',actions=['produce'],artifact_kind='calculation',evidence_mode='none')
        self.finish(upstream)
        original=Path(next(r for r in upstream['receipts'] if r['step']=='produce_artifact')['output']['locator'])
        working=self.folder/'portfolio-working.txt'
        os.link(original,working)
        source={'id':'working','kind':'file','locator':str(working),'revision':router.file_hash(working),'status':'available','inspected':True}
        downstream=assessment(task_id='downstream',actions=['revise'],scope='exact',sources=[source])
        portfolio={'schema_version':2,'workstreams':[{'assessment':upstream,'depends_on':[]},{'assessment':downstream,'depends_on':['upstream']}]}
        while True:
            plan=router.plan_v2(portfolio)['workstreams']['downstream']
            step=next(row for row in plan['steps'] if row['state']=='ready' and row['id']!='present')
            if step['id']=='revise_source':
                break
            artifact=self.folder/('downstream-'+step['id']+'.txt')
            artifact.write_text('Synthetic preparation',encoding='utf-8')
            downstream.setdefault('receipts',[]).append({'step':step['id'],'binding':step['input_binding'],'evidence':'Synthetic inspection',
                'output':{'kind':'file','locator':str(artifact),'revision':router.file_hash(artifact)}})
        with self.assertRaisesRegex(ValueError,'accepted predecessor'):
            router.begin_step(portfolio,'working','downstream')

    def test_direct_explicit_methods_are_applied_without_extra_ideation(self):
        for kind, method, rubric in [('calculation','Y2','quantitative'),('explanation','L5','explanation'),('coaching_turn','L5','coaching')]:
            with self.subTest(kind=kind):
                task=assessment(actions=['produce'],artifact_kind=kind,evidence_mode='none',requested_methods=[method])
                task['problem'].update(kind='execution',novelty='none',bottleneck='implementation')
                plan=router.plan_v2(task)
                self.assertEqual([row['id'] for row in plan['steps']],['inspect_context','produce_artifact','verify_output','present'])
                self.assertEqual([m['id'] for m in node(plan,'produce_artifact')['method_contracts']],[method])
                self.assertEqual(node(plan,'verify_output')['verification_contract']['rubric'],rubric)

    def copied_package(self):
        target=self.folder/'package'
        shutil.copytree(router.PACKAGE,target,ignore=shutil.ignore_patterns('__pycache__','assets'))
        self.enterContext(patch.object(router,'PACKAGE',target))
        self.enterContext(patch.object(workflow_context,'PACKAGE',target))
        return target

    def test_selected_guidance_changes_invalidate_only_affected_work(self):
        package=self.copied_package()
        task=assessment(actions=['diagnose'],requested_methods=['Y2'])
        before=self.finish(task)
        self.assertEqual(node(before,'verify_output')['state'],'done')
        method=router.registry()['methods']['Y2']
        selected=package/method['reference']
        original=selected.read_text(encoding='utf-8')
        marker='## '+method['section_prefix']
        at=original.index('\n', original.index(marker))
        selected.write_text(original[:at]+'\nChanged selected procedure requirement.'+original[at:],encoding='utf-8')
        changed=router.plan_v2(task)
        self.assertEqual(node(changed,'inspect_context')['state'],'done')
        self.assertEqual(node(changed,'diagnose_problem')['state'],'ready')
        self.assertEqual(node(changed,'verify_output')['state'],'waiting')
        selected.write_text(original,encoding='utf-8')
        self.assertEqual(router.plan_v2(task),before)

    def test_unselected_method_text_does_not_retire_receipts(self):
        package=self.copied_package()
        task=assessment(actions=['diagnose'],requested_methods=['Y2'])
        before=self.finish(task)
        method=router.registry()['methods']['L4']
        path=package/method['reference']
        original=path.read_text(encoding='utf-8')
        at=original.index('\n', original.index('## '+method['section_prefix']))
        path.write_text(original[:at]+'\nChanged unrelated procedure.'+original[at:],encoding='utf-8')
        self.assertEqual(router.plan_v2(task),before)

    def test_assigned_skill_and_selected_rubric_each_retire_affected_receipts(self):
        package=self.copied_package()
        task=assessment(actions=['diagnose'],requested_methods=['Y2'])
        before=self.finish(task)
        for relative, changed_step in [('skills/innovation-strategy/SKILL.md','diagnose_problem'),('references/artifact-rubrics.md','verify_output')]:
            with self.subTest(path=relative):
                path=package/relative
                original=path.read_text(encoding='utf-8')
                revised=original+'\nNew required instruction.\n' if 'SKILL' in relative else original.replace('## Shared checks','## Shared checks\n\nNew shared verification requirement.',1)
                path.write_text(revised,encoding='utf-8')
                changed=router.plan_v2(task)
                self.assertEqual(node(changed,'inspect_context')['state'],'done')
                self.assertNotEqual(node(changed,changed_step)['state'],'done')
                if changed_step=='verify_output':
                    self.assertEqual(node(changed,'diagnose_problem')['state'],'done')
                path.write_text(original,encoding='utf-8')
                self.assertEqual(router.plan_v2(task),before)

    def test_missing_selected_guidance_blocks_affected_step_without_aborting_plan(self):
        package=self.copied_package()
        task=assessment(actions=['diagnose'],requested_methods=['Y2'])
        self.finish(task)
        method=router.registry()['methods']['Y2']
        (package/method['reference']).unlink()
        changed=router.plan_v2(task)
        self.assertEqual(node(changed,'inspect_context')['state'],'done')
        self.assertEqual(node(changed,'diagnose_problem')['state'],'unavailable')
        self.assertEqual(node(changed,'verify_output')['state'],'waiting')

    def test_missing_specialist_does_not_disable_unrelated_workstream(self):
        package=self.copied_package()
        (package/'skills/innovation-strategy/SKILL.md').unlink()
        portfolio={'schema_version':2,'workstreams':[
            {'assessment':assessment(task_id='diagnosis',actions=['diagnose']),'depends_on':[]},
            {'assessment':assessment(task_id='status',actions=['status']),'depends_on':[]}]}
        plan=router.plan_v2(portfolio)
        self.assertEqual(node(plan['workstreams']['diagnosis'],'diagnose_problem')['state'],'unavailable')
        self.assertEqual(node(plan['workstreams']['status'],'inspect_context')['state'],'ready')

    def test_context_rejects_guidance_changed_after_planning(self):
        package=self.copied_package()
        original=router.plan_v2
        def changing(task):
            result=original(task)
            path=package/'skills/creative-director/SKILL.md'
            path.write_text(path.read_text(encoding='utf-8')+'\nChanged during read.\n',encoding='utf-8')
            return result
        with patch.object(router,'plan_v2',side_effect=changing):
            with self.assertRaisesRegex(ValueError,'changed during context'):
                workflow_context.ready_context(assessment(actions=['status']),'inspect_context')

    def test_blank_headings_do_not_crash_independent_portfolio_work(self):
        package=self.copied_package()
        method=router.registry()['methods']['Y2']
        path=package/method['reference']
        path.write_text(path.read_text(encoding='utf-8')+'\n##  \n##\n##\t\n',encoding='utf-8')
        portfolio={'schema_version':2,'workstreams':[
            {'assessment':assessment(task_id='diagnosis',actions=['diagnose'],requested_methods=['Y2']),'depends_on':[]},
            {'assessment':assessment(task_id='status',actions=['status']),'depends_on':[]}]}
        plan=router.plan_v2(portfolio)
        self.assertEqual(node(plan['workstreams']['diagnosis'],'diagnose_problem')['state'],'waiting')
        self.assertEqual(node(plan['workstreams']['status'],'inspect_context')['state'],'ready')

    def test_blank_boundaries_and_missing_or_ambiguous_sections_are_explicit(self):
        for blank in ['##  ','##','##\t','## \r']:
            with self.subTest(blank=blank):
                self.assertEqual(workflow_context.section('## Y2 Method\nKeep this\n'+blank+'\nDo not include this','Y2',prefix=True),
                                 '## Y2 Method\nKeep this')
                with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):
                    workflow_context.section(blank+'\nNo selected method','Y2',prefix=True)
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):
            workflow_context.section('## Y2 Method\nA\n##  \n## Y2 Duplicate\nB','Y2',prefix=True)

    def test_ambiguous_selected_section_blocks_only_affected_stream(self):
        package=self.copied_package()
        method=router.registry()['methods']['Y2']
        path=package/method['reference']
        path.write_text(path.read_text(encoding='utf-8')+'\n## Y2 Duplicate\nConflicting guidance\n',encoding='utf-8')
        portfolio={'schema_version':2,'workstreams':[
            {'assessment':assessment(task_id='diagnosis',actions=['diagnose'],requested_methods=['Y2']),'depends_on':[]},
            {'assessment':assessment(task_id='status',actions=['status']),'depends_on':[]}]}
        plan=router.plan_v2(portfolio)
        self.assertEqual(node(plan['workstreams']['diagnosis'],'diagnose_problem')['state'],'unavailable')
        self.assertEqual(node(plan['workstreams']['status'],'inspect_context')['state'],'ready')


if __name__=='__main__':
    unittest.main()
