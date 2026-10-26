"""Actual specialist/resource connections, ready-step boundaries and local CLI readback."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_router_v2 import assessment, router, source

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'


def node(plan, identity):
    return next(step for step in plan['steps'] if step['id'] == identity)


class WorkflowConnectionTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs/local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.evidence = self.folder / 'inspection.txt'
        self.evidence.write_text('Inspected the actual fixture contract.', encoding='utf-8')

    def finish(self, task, identity):
        plan = router.plan_v2(task)
        step = node(plan, identity)
        self.assertEqual(step['state'], 'ready')
        task.setdefault('receipts', []).append({'step': identity, 'binding': step['input_binding'],
            'evidence': 'Actually inspected the local fixture.', 'output': {
                'kind': 'file', 'locator': str(self.evidence),
                'revision': hashlib.sha256(self.evidence.read_bytes()).hexdigest()}})
        return router.plan_v2(task)

    def context(self, task, identity, task_id=None, ok=True):
        path = self.folder / 'assessment.json'
        path.write_text(json.dumps(task), encoding='utf-8')
        before = path.read_bytes()
        args = [sys.executable, str(SCRIPT), 'context', '--assessment', str(path), '--step', identity]
        if task_id is not None:
            args += ['--task-id', task_id]
        result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stderr)
        self.assertEqual(path.read_bytes(), before, 'Context loading must not rewrite task state')
        return json.loads(result.stdout if ok else result.stderr)

    def test_saving_and_restoring_use_project_storage_not_feedback_analysis(self):
        save = router.plan_v2(assessment(actions=['record'], capabilities=['file_write']))
        self.assertEqual(node(save, 'record_decisions')['skill'], 'creative-project')
        resume = router.plan_v2(assessment(actions=['resume']))
        self.assertEqual(node(resume, 'restore_checkpoint')['skill'], 'creative-project')
        self.assertEqual(node(resume, 'inspect_context')['skill'], 'creative-director')
        self.assertIn('creative-project', resume['services'])

    def test_composed_work_assigns_comparison_and_development_to_their_specialists(self):
        plan = router.plan_v2(assessment(actions=['ideate', 'develop']))
        self.assertEqual(plan['specialist']['id'], 'innovation-strategy')
        self.assertEqual(node(plan, 'evaluate_options')['skill'], 'creative-review')
        self.assertEqual(node(plan, 'develop_solution')['skill'], 'concept-development')
        for step in plan['steps']:
            contract = step['skill_contract']
            self.assertEqual(contract['id'], step['skill'])
            self.assertEqual(contract['path'], 'skills/' + step['skill'] + '/SKILL.md')

    def test_canon_synthesis_is_in_the_actual_shared_services(self):
        plan = router.plan_v2(assessment(actions=['research'], evidence_mode='canon', sources=[source()]))
        self.assertEqual(node(plan, 'synthesize_sources')['skill'], 'research-and-writing')
        self.assertIn('research-and-writing', plan['services'])

    def test_changed_step_assignment_invalidates_its_completion_not_accepted_preparation(self):
        task = assessment(actions=['record'], capabilities=['file_write'])
        self.finish(task, 'inspect_context')
        accepted = self.finish(task, 'record_decisions')
        self.assertEqual(node(accepted, 'record_decisions')['state'], 'done')
        original = router.step_specialist
        def changed(key, primary):
            return 'creative-learning' if key == 'record_decisions' else original(key, primary)
        with patch.object(router, 'step_specialist', side_effect=changed):
            revised = router.plan_v2(task)
        self.assertEqual(node(revised, 'inspect_context')['state'], 'done')
        self.assertEqual(node(revised, 'record_decisions')['state'], 'ready')

    def test_ready_context_reads_real_guidance_without_loading_every_specialist(self):
        task = assessment(actions=['produce'], artifact_kind='calculation')
        loaded = self.context(task, 'inspect_context')
        self.assertFalse(loaded['grants_execution_authority'])
        self.assertEqual(loaded['task']['evidence'], task['evidence'])
        self.assertEqual(loaded['task']['problem'], task['problem'])
        self.assertEqual(loaded['step']['skill_contract']['id'], 'creative-director')
        paths = {resource['path'] for resource in loaded['resources']}
        self.assertIn('skills/creative-director/SKILL.md', paths)
        self.assertIn('references/recognition-playbook.md', paths)
        self.assertNotIn('skills/execution-handoff/SKILL.md', paths)
        for resource in loaded['resources']:
            self.assertEqual(hashlib.sha256(resource['content'].encode('utf-8')).hexdigest(),
                             resource['content_sha256'])
        self.context(task, 'produce_artifact', ok=False)

    def test_context_loads_only_selected_method_and_matching_rubric(self):
        task = assessment(actions=['diagnose'], requested_methods=['Y2'])
        self.finish(task, 'inspect_context')
        loaded = self.context(task, 'diagnose_problem')
        methods = [resource for resource in loaded['resources'] if resource['selector']['kind'] == 'method']
        self.assertEqual(len(methods), 1)
        self.assertIn('## Y2 ROOT', methods[0]['content'])
        self.assertNotIn('## Y1 LEVERAGE', methods[0]['content'])
        self.finish(task, 'diagnose_problem')
        verify = self.context(task, 'verify_output')
        rubric = next(resource for resource in verify['resources'] if resource['selector']['kind'] == 'rubric')
        self.assertIn('`analysis`', rubric['content'])
        self.assertNotIn('| `story`', rubric['content'])
        self.assertIn('## Shared checks', rubric['content'])

    def test_portfolio_context_cannot_bypass_upstream_readiness(self):
        raw = {'schema_version': 2, 'workstreams': [
            {'assessment': assessment(task_id='upstream', actions=['review']), 'depends_on': []},
            {'assessment': assessment(task_id='dependent', actions=['status']), 'depends_on': ['upstream']},
            {'assessment': assessment(task_id='independent', actions=['status']), 'depends_on': []}]}
        self.context(raw, 'inspect_context', 'dependent', ok=False)
        self.context(raw, 'inspect_context', ok=False)
        ready = self.context(raw, 'inspect_context', 'independent')
        self.assertEqual(ready['task']['task_id'], 'independent')
        self.context(assessment(), 'inspect_context', 'foreign', ok=False)

    def test_all_registered_method_sections_and_rubrics_are_loadable(self):
        from workflow_context import load_resource
        for identity, method in router.registry()['methods'].items():
            with self.subTest(method=identity):
                loaded = load_resource({'path': method['reference'],
                                        'selector': {'kind': 'method', 'value': method['section_prefix']}})
                self.assertIn('## ' + identity + ' ', loaded['content'])
        for rubric in ['analysis','quantitative','formal_reasoning','explanation','coaching','decision',
                       'experiment','process','factual_writing','story','visual','product','campaign',
                       'presentation','code','game']:
            with self.subTest(rubric=rubric):
                self.assertIn('`' + rubric + '`', load_resource({'path': 'references/artifact-rubrics.md',
                    'selector': {'kind': 'rubric', 'value': rubric}})['content'])
        with self.assertRaises(ValueError):
            load_resource({'path': '../outside.md', 'selector': {'kind': 'all'}})
        with self.assertRaises(ValueError):
            load_resource({'path': 'references/innovation-playbooks.md',
                           'selector': {'kind': 'heading', 'value': 'Missing operation'}})

    def test_storage_context_does_not_invent_write_access(self):
        task = assessment(actions=['record'])
        self.finish(task, 'inspect_context')
        blocked = router.plan_v2(task)
        self.assertEqual(node(blocked, 'record_decisions')['required_capabilities'], ['file_write'])
        self.assertEqual(node(blocked, 'record_decisions')['missing_capabilities'], ['file_write'])
        task['receipts'].append({'step': 'record_decisions',
            'binding': node(blocked, 'record_decisions')['input_binding'], 'evidence': 'Unsupported completion claim',
            'output': {'kind': 'file', 'locator': str(self.evidence),
                       'revision': hashlib.sha256(self.evidence.read_bytes()).hexdigest()}})
        self.assertEqual(node(router.plan_v2(task), 'record_decisions')['state'], 'unavailable')
        self.context(task, 'record_decisions', ok=False)
        task['capabilities'] = ['file_write']
        task['receipts'] = []
        self.finish(task, 'inspect_context')
        loaded = self.context(task, 'record_decisions')
        self.assertEqual(loaded['step']['skill_contract']['id'], 'creative-project')
        self.assertIn('skills/creative-director/references/project-record.md',
                      {resource['path'] for resource in loaded['resources']})
        self.assertEqual(loaded['task']['capabilities'], ['file_write'])
        self.assertFalse(loaded['grants_execution_authority'])

    def test_existing_but_wrong_skill_path_is_not_a_valid_connection(self):
        registry = copy.deepcopy(router.registry())
        registry['specialists']['creative-director']['path'] = 'skills/creative-project/SKILL.md'
        with patch.object(router, 'registry', return_value=registry):
            with self.assertRaisesRegex(ValueError, 'identity'):
                router.plan_v2(assessment(actions=['status']))

    def test_context_resource_size_limit_is_enforced_before_delivery(self):
        import workflow_context
        oversized = self.folder / 'oversized.md'
        oversized.write_bytes(b'x' * (256*1024+1))
        with patch.object(workflow_context, 'PACKAGE', self.folder):
            with self.assertRaisesRegex(ValueError, 'read limit'):
                workflow_context.load_resource({'path': 'oversized.md', 'selector': {'kind': 'all'}})


if __name__ == '__main__':
    unittest.main()
