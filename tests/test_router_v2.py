import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'plugins/idea-man/skills/creative-director/scripts'
sys.path.insert(0,str(SCRIPTS))
import router_v2 as router


def assessment(**overrides):
    data={'schema_version':2,'task_id':'task-a','objective':'Reduce service delays without increasing staffing',
          'domain':'operations','actions':['diagnose','ideate'],'deliverable':'text','artifact_kind':'analysis',
          'scope':'bounded','stage':'framed',
          'problem':{'kind':'causal','bottleneck':'complexity','novelty':'improve','stakes':'medium','reversibility':'reversible'},
          'evidence_mode':'hypothesis','sources':[],
          'selection':{'status':'not_needed','ids':[],'evidence':''},
          'constraints':[{'id':'staff','text':'Keep staffing fixed','kind':'hard','evidence':'User explicitly requires this'}],
          'evidence':[{'source':'user','detail':'Find why service is delayed and suggest options; no new staff'}]}
    data.update(overrides)
    return data


def source(**kw):
    return dict({'id':'source-a','kind':'provided','locator':'conversation:notes','revision':'r1','status':'available','inspected':True},**kw)


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.temp=ROOT/'test-runs'/str(uuid.uuid4()); self.temp.mkdir(parents=True)
        self.output=self.temp/'inspection.txt'; self.output.write_text('Inspected actual inputs.',encoding='utf-8')

    def tearDown(self):
        target=self.temp.resolve(); boundary=(ROOT/'test-runs').resolve()
        assert target.is_relative_to(boundary) and target!=boundary
        shutil.rmtree(target)

    def receipt(self,plan,step='inspect_context'):
        node=next((s for s in plan['steps'] if s['id']==step),{})
        return {'step':step,'binding':node.get('input_binding',plan['input_binding']),'evidence':'Actual inspection note',
                'output':{'kind':'file','locator':str(self.output),'revision':router.file_hash(self.output)}}

    def test_general_diagnosis_selects_causal_methods(self):
        p=router.plan_v2(assessment())
        self.assertEqual(p['specialist']['id'],'innovation-strategy')
        self.assertEqual([x['id'] for x in p['methods']],['Y2','Y1'])
        ids=[s['id'] for s in p['steps']]
        self.assertLess(ids.index('diagnose_problem'),ids.index('generate_options'))
        self.assertNotIn('apply_methods',ids)
        self.assertEqual([m['id'] for m in next(s for s in p['steps'] if s['id']=='diagnose_problem')['method_contracts']],['Y2','Y1'])

    def test_explicit_method_preserved(self):
        p=router.plan_v2(assessment(requested_methods=['S2'],requested_count=3))
        self.assertEqual([m['id'] for m in p['methods']],['S2'])
        self.assertEqual(next(s for s in p['steps'] if s['id']=='generate_options')['requested_count'],3)

    def test_resource_style_selects_constraints(self):
        p=router.plan_v2(assessment(thinking_style='constraint_driven'))
        self.assertEqual(p['methods'][0]['id'],'S3')

    def test_exact_revision_avoids_methods(self):
        p=router.plan_v2(assessment(actions=['revise'],scope='exact',sources=[source()]))
        self.assertEqual(p['methods'],[])
        self.assertNotIn('generate_options',[s['id'] for s in p['steps']])

    def test_review_is_read_only(self):
        p=router.plan_v2(assessment(actions=['review'],sources=[source()]))
        self.assertEqual(p['specialist']['id'],'artifact-quality')
        self.assertEqual([s['id'] for s in p['steps']],['inspect_context','evaluate_options','present'])

    def test_supplied_research_without_web(self):
        p=router.plan_v2(assessment(actions=['research','develop'],artifact_kind='memo',evidence_mode='supplied',sources=[source()]))
        self.assertEqual(p['blockers'],[])
        self.assertEqual(p['specialist']['id'],'research-and-writing')
        self.assertIn('synthesize_sources',[s['id'] for s in p['steps']])

    def test_live_research_reports_missing_web(self):
        p=router.plan_v2(assessment(actions=['research'],evidence_mode='live'))
        self.assertEqual(p['blockers'],['research_live'])

    def test_missing_local_does_not_disable_independent_live_research(self):
        p=router.plan_v2(assessment(actions=['research'],evidence_mode='mixed',live_research_dependency='independent',capabilities=['web'],sources=[source(status='missing',inspected=False)]))
        live=next(s for s in p['steps'] if s['id']=='research_live')
        self.assertEqual(live['depends_on'],['inspect_context'])
        self.assertIn('resolve_source',p['blockers'])

    def test_resume_recovers_pending_actions(self):
        a=assessment(actions=['resume'],continuity={'task_id':'task-a','objective':'Reduce service delays without increasing staffing',
              'pending_actions':['develop','experiment'],'evidence':'Inspected checkpoint','source_rechecked':True})
        p=router.plan_v2(a)
        self.assertIn('develop_solution',[s['id'] for s in p['steps']])
        self.assertIn('design_experiment',[s['id'] for s in p['steps']])

    def test_uninspected_resume_requires_restore(self):
        p=router.plan_v2(assessment(actions=['resume']))
        self.assertIn('restore_checkpoint',p['blockers'])

    def test_foreign_checkpoint_rejected(self):
        a=assessment(actions=['resume'],continuity={'task_id':'other','objective':'wrong','pending_actions':['develop'],'evidence':'Old note','source_rechecked':True})
        with self.assertRaises(ValueError):router.plan_v2(a)

    def test_status_does_not_execute_pending_work(self):
        a=assessment(actions=['status'],continuity={'task_id':'task-a','objective':'Reduce service delays without increasing staffing',
             'pending_actions':['produce'],'evidence':'Checkpoint','source_rechecked':True})
        p=router.plan_v2(a)
        self.assertEqual([s['id'] for s in p['steps']],['inspect_context','answer_status','present'])

    def test_mixed_implicit_production_needs_capabilities(self):
        with self.assertRaises(ValueError):router.plan_v2(assessment(actions=['develop'],deliverable='mixed'))

    def test_missing_production_tool(self):
        p=router.plan_v2(assessment(actions=['develop'],deliverable='image'))
        self.assertIn('produce_artifact',p['blockers'])
        self.assertFalse(p['execution_complete'])

    def test_counts_not_reduced(self):
        p=router.plan_v2(assessment(requested_count=6))
        self.assertEqual(next(s for s in p['steps'] if s['id']=='generate_options')['requested_count'],6)

    def test_multiple_selections_preserved_in_binding(self):
        a=assessment(selection={'status':'user','ids':['A','B'],'evidence':'Both approved'},sources=[source()])
        p=router.plan_v2(a)
        b=copy.deepcopy(a); b['selection']['ids']=['A']
        self.assertNotEqual(p['input_binding'],router.plan_v2(b)['input_binding'])

    def test_receipt_validity_and_dependency(self):
        a=assessment(); p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        q=router.plan_v2(a)
        self.assertEqual(q['steps'][0]['state'],'done')
        self.assertEqual(q['steps'][1]['state'],'ready')
        a['receipts']=[self.receipt(p,'generate_options')]
        q=router.plan_v2(a)
        self.assertNotEqual(next(s for s in q['steps'] if s['id']=='generate_options')['state'],'done')

    def test_changed_constraint_invalidates_receipt(self):
        a=assessment(); p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        a['constraints'][0]['text']='Cut staffing'
        self.assertNotEqual(router.plan_v2(a)['steps'][0]['state'],'done')

    def test_changed_source_bytes_invalidate_receipt(self):
        f=self.temp/'source.txt'; f.write_text('Original',encoding='utf-8')
        a=assessment(sources=[source(kind='file',locator=str(f),revision=router.file_hash(f))])
        p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        f.write_text('Replaced source',encoding='utf-8')
        q=router.plan_v2(a)
        self.assertNotEqual(q['steps'][0]['state'],'done')
        self.assertFalse(q['sources'][0]['inspected'])

    def test_changed_output_invalidates_receipt(self):
        a=assessment(); p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        self.output.write_text('Changed',encoding='utf-8')
        self.assertNotEqual(router.plan_v2(a)['steps'][0]['state'],'done')

    def test_remote_receipt_requires_reinspection(self):
        a=assessment(); p=router.plan_v2(a); r=self.receipt(p)
        r['output']={'kind':'url','locator':'https://example.com/source','revision':'v1'}
        a['receipts']=[r]
        self.assertNotEqual(router.plan_v2(a)['steps'][0]['state'],'done')

    def test_unknown_receipt_rejected(self):
        a=assessment(); a['receipts']=[self.receipt(router.plan_v2(a),'made-up')]
        with self.assertRaises(ValueError):router.plan_v2(a)

    def test_bad_types_return_validation_errors(self):
        for field,value in [('domain',[]),('actions',{}),('selection',None),('problem',[]),('deliverable',{}),('requested_count',True)]:
            with self.subTest(field=field),self.assertRaises(ValueError):router.plan_v2(assessment(**{field:value}))

    def test_independent_workstream_survives_blocker(self):
        a=assessment(actions=['produce'],deliverable='video')
        b=assessment(task_id='task-b',actions=['develop'])
        p=router.plan_v2({'schema_version':2,'workstreams':[{'assessment':a,'depends_on':[]},{'assessment':b,'depends_on':[]}]})
        self.assertIn('task-a/produce_artifact',p['blockers'])
        self.assertEqual(next(s for s in p['steps'] if s['id']=='task-b/inspect_context')['state'],'ready')
        self.assertEqual(len({s['id'] for s in p['steps']}),len(p['steps']))

    def test_dependency_cycle_rejected(self):
        with self.assertRaises(ValueError):router.plan_v2({'schema_version':2,'workstreams':[
           {'assessment':assessment(),'depends_on':['task-b']},
           {'assessment':assessment(task_id='task-b'),'depends_on':['task-a']}]})

    def test_dependent_task_cannot_bypass_upstream(self):
        a=assessment(); b=assessment(task_id='task-b'); pb=router.plan_v2(b)
        b['receipts']=[self.receipt(pb)]
        p=router.plan_v2({'schema_version':2,'workstreams':[{'assessment':a,'depends_on':[]},{'assessment':b,'depends_on':['task-a']}]})
        node=next(s for s in p['steps'] if s['id']=='task-b/inspect_context')
        self.assertEqual(node['state'],'waiting'); self.assertIn('task-a/verify_output',node['depends_on'])

    def test_completed_upstream_releases_dependent_branch(self):
        a=assessment(actions=['develop']); b=assessment(task_id='task-b',actions=['develop'])
        while True:
            p=router.plan_v2(a)
            ready=[s for s in p['steps'] if s['state']=='ready' and s['id']!='present']
            if not ready:break
            a.setdefault('receipts',[]).append(self.receipt(p,ready[0]['id']))
        env={'schema_version':2,'workstreams':[{'assessment':a,'depends_on':[]},{'assessment':b,'depends_on':['task-a']}]}
        p=router.plan_v2(env)
        self.assertEqual(next(s for s in p['steps'] if s['id']=='task-b/inspect_context')['state'],'ready')
        old=p['workstreams']['task-b']['input_binding']
        a['constraints'][0]['text']='Changed staffing constraint'
        q=router.plan_v2(env)
        self.assertNotEqual(old,q['workstreams']['task-b']['input_binding'])
        self.assertEqual(next(s for s in q['steps'] if s['id']=='task-b/inspect_context')['state'],'waiting')

    def test_high_stakes_decision_keeps_test_method_ahead_of_style(self):
        a=assessment(actions=['decide'],effort='quick',thinking_style='contrarian')
        a['problem'].update(stakes='high',reversibility='irreversible')
        self.assertEqual(router.plan_v2(a)['methods'][0]['id'],'D2')

    def test_mixed_research_requires_local_sources(self):
        p=router.plan_v2(assessment(actions=['research'],evidence_mode='mixed',capabilities=['web']))
        self.assertIn('resolve_source',p['blockers'])

    def test_resume_control_does_not_invalidate_same_work(self):
        a=assessment(actions=['develop']); p=router.plan_v2(a)
        a['actions']=['resume']
        a['continuity']={'task_id':a['task_id'],'objective':a['objective'],'pending_actions':['develop'],
                         'evidence':'Same inspected checkpoint','source_rechecked':True}
        self.assertEqual(p['input_binding'],router.plan_v2(a)['input_binding'])

    def test_artifact_specific_rubrics(self):
        self.assertEqual(router.plan_v2(assessment(domain='engineering'))['rubric'],'analysis')
        self.assertEqual(router.plan_v2(assessment(domain='business',deliverable='deck',actions=['produce']))['rubric'],'presentation')

    def test_record_requires_write_capability(self):
        self.assertIn('record_decisions',router.plan_v2(assessment(actions=['record']))['blockers'])
        self.assertNotIn('record_decisions',router.plan_v2(assessment(actions=['record'],capabilities=['file_write']))['blockers'])

    def test_registry_files_and_methods_exist(self):
        data=router.registry()
        self.assertEqual(len(data['specialists']),11)
        self.assertEqual(len(data['methods']),17)

    def test_cli_fingerprint_and_receipt(self):
        path=self.temp/'assessment.json'; path.write_text(json.dumps(assessment()),encoding='utf-8')
        cmd=[sys.executable,str(SCRIPTS/'studio.py')]
        fingerprint=subprocess.run(cmd+['fingerprint','--file',str(self.output)],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(fingerprint.stdout)['revision'],router.file_hash(self.output))
        receipt=subprocess.run(cmd+['receipt','--assessment',str(path),'--step','inspect_context','--artifact',str(self.output),
                  '--evidence-file',str(self.output)],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(receipt.stdout)['binding'],router.plan_v2(assessment())['steps'][0]['input_binding'])



    def finish(self, a, portfolio=None, task_id=None):
        """Accept each ready step with a separate, real output artifact."""
        for _ in range(40):
            p=router.plan_v2(portfolio if portfolio is not None else a)
            current=p['workstreams'][task_id] if portfolio is not None else p
            ready=next((s for s in current['steps'] if s['state']=='ready' and s['id']!='present'),None)
            if ready is None:
                return p
            output=self.temp/(a['task_id']+'-'+ready['id']+'.txt')
            output.write_text('Accepted '+a['task_id']+'/'+ready['id'],encoding='utf-8')
            receipt=self.receipt(current,ready['id'])
            receipt['output']={'kind':'file','locator':str(output),'revision':router.file_hash(output)}
            a.setdefault('receipts',[]).append(receipt)
        self.fail('Planner did not reach a stable terminal state')

    def test_replaced_generated_output_invalidates_old_downstream(self):
        a=assessment(actions=['ideate'])
        self.finish(a)
        replacement=self.temp/'new-options.txt'
        replacement.write_text('Different generated options',encoding='utf-8')
        generated=next(r for r in a['receipts'] if r['step']=='generate_options')
        generated['output']={'kind':'file','locator':str(replacement),'revision':router.file_hash(replacement)}
        p=router.plan_v2(a)
        nodes={s['id']:s for s in p['steps']}
        self.assertEqual(nodes['generate_options']['state'],'done')
        self.assertEqual(nodes['evaluate_options']['state'],'ready')
        self.assertEqual(nodes['verify_output']['state'],'waiting')
        # Fresh evaluation with the SAME evaluated artifact still cannot revive an old verification.
        fresh=self.receipt(p,'evaluate_options')
        a['receipts']=[r for r in a['receipts'] if r['step']!='evaluate_options']+[fresh]
        q=router.plan_v2(a)
        nodes={s['id']:s for s in q['steps']}
        self.assertEqual(nodes['evaluate_options']['state'],'done')
        self.assertEqual(nodes['verify_output']['state'],'ready')

    def test_modified_generated_bytes_require_refresh_then_recheck(self):
        a=assessment(actions=['ideate']); self.finish(a)
        generated=next(r for r in a['receipts'] if r['step']=='generate_options')
        path=Path(generated['output']['locator'])
        path.write_text('Changed bytes after acceptance',encoding='utf-8')
        p=router.plan_v2(a)
        self.assertEqual(next(s for s in p['steps'] if s['id']=='generate_options')['state'],'ready')
        generated['output']['revision']=router.file_hash(path)
        q=router.plan_v2(a)
        self.assertEqual(next(s for s in q['steps'] if s['id']=='evaluate_options')['state'],'ready')
        self.assertEqual(next(s for s in q['steps'] if s['id']=='verify_output')['state'],'waiting')

    def test_legacy_task_binding_receipt_fails_closed(self):
        a=assessment(); p=router.plan_v2(a)
        old=self.receipt(p); old['binding']=p['input_binding']
        a['receipts']=[old]
        q=router.plan_v2(a)
        self.assertEqual(q['steps'][0]['state'],'ready')
        self.assertEqual([r['step'] for r in q['ignored_receipts']],['inspect_context'])
        self.assertIn('legacy',q['receipt_compatibility'].lower())

    def test_portfolio_wait_propagates_in_both_views_and_keeps_independent_ready(self):
        a=assessment(actions=['develop'])
        b=assessment(task_id='task-b',actions=['develop'])
        c=assessment(task_id='task-c',actions=['develop'])
        b['receipts']=[self.receipt(router.plan_v2(b))]
        env={'schema_version':2,'workstreams':[
            {'assessment':a,'depends_on':[]},
            {'assessment':b,'depends_on':['task-a']},
            {'assessment':c,'depends_on':[]}]}
        b['receipts']=[self.receipt(router.plan_v2(env)['workstreams']['task-b'])]
        p=router.plan_v2(env)
        flat={s['id']:s for s in p['steps']}
        for node in flat.values():
            if node['state'] in {'ready','done'}:
                self.assertTrue(all(flat[dep]['state']=='done' for dep in node['depends_on']))
        for node in p['workstreams']['task-b']['steps']:
            self.assertNotIn(node['state'],{'ready','done'})
            self.assertEqual(node['state'],flat['task-b/'+node['id']]['state'])
            self.assertNotIn('completion_evidence',node)
        self.assertEqual(flat['task-c/inspect_context']['state'],'ready')

    def test_portfolio_upstream_output_refresh_does_not_revive_old_descendants(self):
        a=assessment(actions=['develop']); self.finish(a)
        b=assessment(task_id='task-b',actions=['develop'])
        c=assessment(task_id='task-c',actions=['develop'])
        env={'schema_version':2,'workstreams':[
            {'assessment':a,'depends_on':[]},
            {'assessment':b,'depends_on':['task-a']},
            {'assessment':c,'depends_on':[]}]}
        self.finish(b,env,'task-b')
        replacement=self.temp/'new-upstream-verification.txt'
        replacement.write_text('New accepted upstream artifact',encoding='utf-8')
        terminal=next(r for r in a['receipts'] if r['step']=='verify_output')
        terminal['output']={'kind':'file','locator':str(replacement),'revision':router.file_hash(replacement)}
        p=router.plan_v2(env)
        self.assertEqual(p['workstreams']['task-b']['steps'][0]['state'],'ready')
        b['receipts']=[r for r in b['receipts'] if r['step']!='inspect_context']+[
            self.receipt(p['workstreams']['task-b'])]
        q=router.plan_v2(env)
        nodes={s['id']:s for s in q['workstreams']['task-b']['steps']}
        self.assertEqual(nodes['inspect_context']['state'],'done')
        self.assertEqual(nodes['develop_solution']['state'],'ready')
        self.assertEqual(nodes['verify_output']['state'],'waiting')
        self.assertEqual(next(s for s in q['steps'] if s['id']=='task-c/inspect_context')['state'],'ready')

    def test_cli_refuses_blocked_portfolio_descendant(self):
        a=assessment(actions=['develop']); b=assessment(task_id='task-b',actions=['develop'])
        b['receipts']=[self.receipt(router.plan_v2(b))]
        env={'schema_version':2,'workstreams':[
            {'assessment':a,'depends_on':[]},{'assessment':b,'depends_on':['task-a']}]}
        b['receipts']=[self.receipt(router.plan_v2(env)['workstreams']['task-b'])]
        file=self.temp/'portfolio.json'; file.write_text(json.dumps(env),encoding='utf-8')
        result=subprocess.run([sys.executable,str(SCRIPTS/'studio.py'),'receipt','--assessment',str(file),
            '--task-id','task-b','--step','develop_solution','--artifact',str(self.output),
            '--evidence-file',str(self.output)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2,result.stdout)
        self.assertIn('ready executable step',result.stderr)

    def test_cli_mints_node_binding_and_binds_changed_predecessor_output(self):
        a=assessment(actions=['ideate'])
        a['receipts']=[self.receipt(router.plan_v2(a))]
        file=self.temp/'assessment.json'; file.write_text(json.dumps(a),encoding='utf-8')
        cmd=[sys.executable,str(SCRIPTS/'studio.py'),'receipt','--assessment',str(file),
            '--step','generate_options','--artifact',str(self.output),'--evidence-file',str(self.output)]
        minted=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
        p=router.plan_v2(a); node=next(s for s in p['steps'] if s['id']=='generate_options')
        self.assertEqual(minted['binding'],node['input_binding'])
        self.assertNotEqual(minted['binding'],p['input_binding'])
        a['receipts'].append(minted)
        p=router.plan_v2(a); a['receipts'].append(self.receipt(p,'evaluate_options'))
        replacement=self.temp/'replacement.txt'; replacement.write_text('Replacement options',encoding='utf-8')
        minted['output']={'kind':'file','locator':str(replacement),'revision':router.file_hash(replacement)}
        q=router.plan_v2(a)
        self.assertEqual(next(s for s in q['steps'] if s['id']=='evaluate_options')['state'],'ready')




    def test_unchanged_outputs_keep_receipts_stable_across_replans(self):
        a=assessment(actions=['ideate']); first=self.finish(a)
        second=router.plan_v2(a); third=router.plan_v2(a)
        self.assertEqual(first,second)
        self.assertEqual(second,third)
        self.assertEqual(second['ignored_receipts'],[])
        self.assertTrue(all(s['state']=='done' for s in second['steps'] if s['id']!='present'))

    def test_changed_inspection_output_identity_invalidates_all_descendants(self):
        a=assessment(actions=['ideate']); self.finish(a)
        original=next(r for r in a['receipts'] if r['step']=='inspect_context')
        replacement=self.temp/'reinspected-context.txt'
        replacement.write_bytes(Path(original['output']['locator']).read_bytes())
        original['output']={'kind':'file','locator':str(replacement),'revision':router.file_hash(replacement)}
        p=router.plan_v2(a)
        nodes={s['id']:s for s in p['steps']}
        self.assertEqual(nodes['inspect_context']['state'],'done')
        self.assertEqual(nodes['generate_options']['state'],'ready')
        self.assertEqual(nodes['evaluate_options']['state'],'waiting')
        self.assertEqual(nodes['verify_output']['state'],'waiting')

    def test_unaccepted_upstream_output_is_not_a_downstream_input(self):
        a=assessment(actions=['develop']); b=assessment(task_id='task-b',actions=['develop'])
        env={'schema_version':2,'workstreams':[
            {'assessment':a,'depends_on':[]},{'assessment':b,'depends_on':['task-a']}]}
        a['receipts']=[self.receipt(router.plan_v2(a),'verify_output')]
        first=router.plan_v2(env)
        replacement=self.temp/'not-accepted.txt'
        replacement.write_text('Unaccepted replacement',encoding='utf-8')
        a['receipts'][0]['output']={'kind':'file','locator':str(replacement),'revision':router.file_hash(replacement)}
        second=router.plan_v2(env)
        self.assertEqual(first['workstreams']['task-b']['input_binding'],second['workstreams']['task-b']['input_binding'])
        self.assertTrue(all(s['state']=='waiting' for s in second['workstreams']['task-b']['steps']))

    def test_cli_portfolio_receipt_uses_same_node_binding_as_workstream(self):
        a=assessment(actions=['develop']); self.finish(a)
        b=assessment(task_id='task-b',actions=['develop'])
        env={'schema_version':2,'workstreams':[
            {'assessment':a,'depends_on':[]},{'assessment':b,'depends_on':['task-a']}]}
        p=router.plan_v2(env); file=self.temp/'portfolio.json'
        file.write_text(json.dumps(env),encoding='utf-8')
        result=subprocess.run([sys.executable,str(SCRIPTS/'studio.py'),'receipt','--assessment',str(file),
            '--task-id','task-b','--step','inspect_context','--artifact',str(self.output),
            '--evidence-file',str(self.output)],capture_output=True,text=True,check=True)
        receipt=json.loads(result.stdout)
        self.assertEqual(receipt['binding'],p['workstreams']['task-b']['steps'][0]['input_binding'])
        self.assertEqual(receipt['binding'],next(s for s in p['steps'] if s['id']=='task-b/inspect_context')['input_binding'])
        b['receipts']=[receipt]
        self.assertEqual(router.plan_v2(env)['workstreams']['task-b']['steps'][0]['state'],'done')




    def test_explicit_review_method_is_retained_and_attached(self):
        p=router.plan_v2(assessment(actions=['review'],sources=[source()],requested_methods=['L2']))
        self.assertEqual([m['id'] for m in p['methods']],['L2'])
        review=next(s for s in p['steps'] if s['id']=='evaluate_options')
        self.assertEqual([m['id'] for m in review['method_contracts']],['L2'])
        self.assertNotIn('generate_options',[s['id'] for s in p['steps']])

    def test_explicit_bounded_revision_method_is_attached_without_ideation(self):
        p=router.plan_v2(assessment(actions=['revise'],scope='bounded',sources=[source()],requested_methods=['L3']))
        revised=next(s for s in p['steps'] if s['id']=='revise_source')
        self.assertEqual([m['id'] for m in p['methods']],['L3'])
        self.assertEqual([m['id'] for m in revised['method_contracts']],['L3'])
        self.assertNotIn('generate_options',[s['id'] for s in p['steps']])

    def test_exact_explicit_method_requires_scope_clarification(self):
        with self.assertRaisesRegex(ValueError,'exact scope.*clarification'):
            router.plan_v2(assessment(actions=['revise'],scope='exact',sources=[source()],requested_methods=['L2']))

    def test_requested_method_without_substantive_target_rejected(self):
        for action in ['status','handoff','produce','record']:
            with self.subTest(action=action),self.assertRaisesRegex(ValueError,'no compatible substantive step'):
                router.plan_v2(assessment(actions=[action],requested_methods=['L2']))

    def test_reference_based_variations_require_identified_source(self):
        p=router.plan_v2(assessment(actions=['vary']))
        self.assertIn('resolve_source',p['blockers'])
        generated=next(s for s in p['steps'] if s['id']=='generate_options')
        self.assertEqual(generated['state'],'waiting')
        provided=router.plan_v2(assessment(actions=['vary'],sources=[source()]))
        self.assertNotIn('resolve_source',provided['blockers'])
        free=router.plan_v2(assessment(actions=['ideate']))
        self.assertNotIn('resolve_source',free['blockers'])

    def test_cli_plan_returns_explicit_method_scope_error(self):
        a=assessment(actions=['revise'],scope='exact',sources=[source()],requested_methods=['L2'])
        file=self.temp/'exact.json'; file.write_text(json.dumps(a),encoding='utf-8')
        result=subprocess.run([sys.executable,str(SCRIPTS/'studio.py'),'plan','--assessment',str(file)],
            capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('clarification',json.loads(result.stderr)['error'])



    def test_changed_selected_method_contract_invalidates_completed_work(self):
        for field in ['procedure','output','reference']:
            with self.subTest(field=field):
                a=assessment(); original=self.finish(a)
                changed=copy.deepcopy(router.registry())
                changed['methods']['Y2'][field]+=' revised contract'
                with patch.object(router,'registry',return_value=changed):
                    current=router.plan_v2(a)
                self.assertNotEqual(original['input_binding'],current['input_binding'])
                self.assertTrue(all(s['state']!='done' for s in current['steps']))
                self.assertEqual(current['steps'][0]['state'],'ready')
                self.assertTrue(current['ignored_receipts'])

    def test_unassigned_method_contract_change_preserves_completed_work(self):
        a=assessment(); original=self.finish(a)
        changed=copy.deepcopy(router.registry())
        self.assertNotIn('L4',[m['id'] for m in original['methods']])
        for field in ['procedure','output','reference']:
            changed['methods']['L4'][field]+=' unrelated update'
        with patch.object(router,'registry',return_value=changed):
            current=router.plan_v2(a)
            repeated=router.plan_v2(a)
        self.assertEqual(original,current)
        self.assertEqual(current,repeated)
        self.assertEqual(current['ignored_receipts'],[])



    def test_requested_artifacts_follow_noncreative_operations(self):
        for action,kind in [('research','research_brief'),('diagnose','analysis'),
                            ('decide','decision_memo'),('experiment','experiment_plan'),
                            ('brief','memo'),('review','report')]:
            for medium,caps in [('document',['document_authoring']),('text',['file_write'])]:
                with self.subTest(action=action,medium=medium):
                    a=assessment(actions=[action],artifact_kind=kind,deliverable=medium,
                        delivery_mode='artifact',evidence_mode='supplied',
                        sources=[source()],capabilities=caps)
                    p=router.plan_v2(a); nodes={n['id']:n for n in p['steps']}
                    self.assertIn('produce',p['effective_actions'])
                    self.assertIn('produce_artifact',nodes)
                    self.assertEqual(nodes['produce_artifact']['missing_capabilities'],[])
                    self.assertEqual(nodes['verify_output']['depends_on'],['produce_artifact'])
                    self.assertEqual(p['blockers'],[])
                    self.assertNotIn('revise_source',nodes)
                    completed=self.finish(a)
                    self.assertEqual(next(n for n in completed['steps'] if n['id']=='verify_output')['state'],'done')

    def test_artifact_text_and_code_need_write_but_inline_sql_does_not(self):
        for medium in ['text','code']:
            with self.subTest(medium=medium):
                a=assessment(actions=['produce'],deliverable=medium,delivery_mode='artifact')
                p=router.plan_v2(a)
                self.assertEqual(next(n for n in p['steps'] if n['id']=='produce_artifact')['missing_capabilities'],['file_write'])
                a['capabilities']=['file_write']
                self.assertNotIn('produce_artifact',router.plan_v2(a)['blockers'])
        a=assessment(actions=['develop'],domain='engineering',deliverable='code',
            delivery_mode='inline',artifact_kind='sql',
            constraints=[{'id':'no-files','text':'Return SQL inline; do not write or execute it',
                          'kind':'hard','evidence':'User explicitly requires inline SQL only'}])
        p=router.plan_v2(a); nodes={n['id']:n for n in p['steps']}
        self.assertEqual(p['rubric'],'code')
        self.assertEqual(p['delivery_mode'],'inline')
        self.assertEqual(nodes['produce_artifact']['missing_capabilities'],[])
        self.assertEqual(p['blockers'],[])
        self.assertNotIn('revise_source',nodes)
        self.assertFalse(any('execute' in n['id'] for n in p['steps']))

    def test_legacy_code_default_still_requires_file_write(self):
        p=router.plan_v2(assessment(actions=['produce'],deliverable='code'))
        self.assertEqual(p['delivery_mode'],'artifact')
        self.assertEqual(next(n for n in p['steps'] if n['id']=='produce_artifact')['missing_capabilities'],['file_write'])

    def test_inline_delivery_rejects_non_inline_artifact_types(self):
        for medium in ['image','audio','video','document','deck','mixed']:
            with self.subTest(medium=medium),self.assertRaisesRegex(ValueError,'Inline delivery'):
                router.plan_v2(assessment(deliverable=medium,delivery_mode='inline'))



    def test_text_reasoning_and_inline_review_keep_narrow_scope(self):
        for action in ['research','diagnose','decide','experiment','brief','review']:
            with self.subTest(action=action):
                p=router.plan_v2(assessment(actions=[action],evidence_mode='supplied',sources=[source()]))
                self.assertNotIn('produce_artifact',[n['id'] for n in p['steps']])
                self.assertNotIn('revise_source',[n['id'] for n in p['steps']])
        for action in ['status','record','resume']:
            for medium in ['document','code','text']:
                with self.subTest(action=action,medium=medium):
                    p=router.plan_v2(assessment(actions=[action],deliverable=medium,delivery_mode='artifact'))
                    self.assertNotIn('produce',p['effective_actions'])
                    self.assertNotIn('produce_artifact',[n['id'] for n in p['steps']])

    def test_report_production_preserves_review_source_bytes(self):
        path=self.temp/'review-source.txt'; path.write_bytes(b'Owner source; preserve exactly.')
        original=path.read_bytes()
        for medium,delivery,caps in [('text','inline',[]),('document','artifact',['document_authoring'])]:
            a=assessment(actions=['review'],deliverable=medium,delivery_mode=delivery,
                artifact_kind='report',evidence_mode='supplied',capabilities=caps,
                sources=[source(kind='file',locator=str(path),revision=router.file_hash(path))])
            p=self.finish(a)
            self.assertEqual(path.read_bytes(),original)
            self.assertNotIn('revise_source',[n['id'] for n in p['steps']])
            self.assertEqual('produce_artifact' in [n['id'] for n in p['steps']],delivery=='artifact')
            self.assertEqual(p['specialist']['id'],'artifact-quality')

    def test_source_bound_sku_lookup_waits_for_inventory(self):
        for extra in [{},{'live_research_dependency':'source_bound'}]:
            with self.subTest(extra=extra):
                a=assessment(actions=['research'],evidence_mode='mixed',capabilities=['web'],
                    sources=[source(id='inventory',status='missing',inspected=False)],**extra)
                p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
                q=router.plan_v2(a); nodes={n['id']:n for n in q['steps']}
                self.assertEqual(q['live_research_dependency'],'source_bound')
                self.assertIn('resolve_source',nodes['research_live']['depends_on'])
                self.assertIn('synthesize_sources',nodes['research_live']['depends_on'])
                self.assertEqual(nodes['research_live']['state'],'waiting')
                self.assertEqual(nodes['synthesize_sources']['state'],'waiting')

    def test_live_mode_with_supplied_inputs_defaults_to_source_bound(self):
        a=assessment(actions=['research'],evidence_mode='live',capabilities=['web'],
            sources=[source(id='inventory')])
        p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        p=router.plan_v2(a); nodes={n['id']:n for n in p['steps']}
        self.assertEqual(nodes['synthesize_sources']['state'],'ready')
        self.assertEqual(nodes['research_live']['state'],'waiting')
        a['receipts'].append(self.receipt(p,'synthesize_sources'))
        p=router.plan_v2(a)
        self.assertEqual(next(n for n in p['steps'] if n['id']=='research_live')['state'],'ready')



    def test_explicit_source_bound_lookup_without_inputs_needs_resolution(self):
        a=assessment(actions=['research'],evidence_mode='live',capabilities=['web'],
            live_research_dependency='source_bound')
        p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        q=router.plan_v2(a)
        self.assertIn('resolve_source',q['blockers'])
        self.assertEqual(next(n for n in q['steps'] if n['id']=='research_live')['state'],'waiting')

    def test_explicit_independent_policy_lookup_survives_unrelated_blockers(self):
        a=assessment(actions=['research','vary'],evidence_mode='mixed',capabilities=['web'],
            live_research_dependency='independent',
            sources=[source(id='inventory',status='missing',inspected=False)])
        p=router.plan_v2(a); a['receipts']=[self.receipt(p)]
        q=router.plan_v2(a); nodes={n['id']:n for n in q['steps']}
        self.assertEqual(nodes['research_live']['depends_on'],['inspect_context'])
        self.assertEqual(nodes['research_live']['state'],'ready')
        self.assertEqual(nodes['design_variations']['state'],'waiting')
        self.assertIn('resolve_source',q['blockers'])

    def test_no_source_live_lookup_defaults_independent(self):
        p=router.plan_v2(assessment(actions=['research'],evidence_mode='live',capabilities=['web']))
        self.assertEqual(p['live_research_dependency'],'independent')
        self.assertEqual(next(n for n in p['steps'] if n['id']=='research_live')['depends_on'],['inspect_context'])

    def test_new_execution_fields_invalidate_prior_receipts(self):
        for field,initial,changed in [('delivery_mode','inline','artifact'),
                                     ('live_research_dependency','independent','source_bound')]:
            with self.subTest(field=field):
                a=assessment(actions=['develop'],capabilities=['file_write'],**{field:initial})
                p=self.finish(a)
                a[field]=changed
                q=router.plan_v2(a)
                self.assertNotEqual(p['input_binding'],q['input_binding'])
                self.assertTrue(q['ignored_receipts'])
                self.assertTrue(all(n['state']!='done' for n in q['steps']))

    def test_new_execution_fields_validate_types_and_values(self):
        for field in ['delivery_mode','live_research_dependency']:
            for value in [None,[],False,'unknown']:
                with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                    router.plan_v2(assessment(**{field:value}))



    def test_noncreative_artifact_capability_gaps_remain_visible(self):
        for action in ['research','decide','experiment','review']:
            for medium,cap in [('document','document_authoring'),('text','file_write')]:
                with self.subTest(action=action,medium=medium):
                    p=router.plan_v2(assessment(actions=[action],deliverable=medium,
                        delivery_mode='artifact',evidence_mode='supplied',sources=[source()]))
                    nodes={n['id']:n for n in p['steps']}
                    self.assertEqual(nodes['produce_artifact']['state'],'unavailable')
                    self.assertEqual(nodes['produce_artifact']['missing_capabilities'],[cap])
                    self.assertEqual(nodes['verify_output']['state'],'waiting')
                    self.assertNotIn('revise_source',nodes)

    def test_explicit_normalized_defaults_preserve_new_receipts(self):
        for mode,sources in [('live',[]),('mixed',[source()])]:
            with self.subTest(mode=mode):
                a=assessment(actions=['research'],evidence_mode=mode,sources=sources,capabilities=['web'])
                p=self.finish(a)
                a['delivery_mode']=p['delivery_mode']
                a['live_research_dependency']=p['live_research_dependency']
                self.assertEqual(p,router.plan_v2(a))



    def test_report_delivery_does_not_require_candidate_commitment(self):
        for action in ['brief','diagnose','research','review','decide']:
            for explicit_produce in [False,True]:
                with self.subTest(action=action,explicit_produce=explicit_produce):
                    a=assessment(actions=[action]+(['produce'] if explicit_produce else []),
                        deliverable='document',artifact_kind='decision_memo' if action=='decide' else 'report',
                        evidence_mode='supplied',sources=[source()],capabilities=['document_authoring'],
                        selection={'status':'none','ids':[],
                            'evidence':'Recommendation/report only; no candidate commitment delegated'})
                    p=self.finish(a); nodes={n['id']:n for n in p['steps']}
                    self.assertNotIn('resolve_selection',nodes)
                    self.assertNotIn('select_option',nodes)
                    self.assertNotIn('revise_source',nodes)
                    self.assertEqual(nodes['produce_artifact']['state'],'done')
                    self.assertEqual(nodes['verify_output']['state'],'done')

    def test_solution_and_experiment_selection_gates_survive_report_delivery(self):
        for actions in [['develop','decide'],['handoff','research'],['experiment'],
                        ['produce'],['ideate'],['vary'],['revise']]:
            with self.subTest(actions=actions):
                a=assessment(actions=actions,deliverable='document',capabilities=['document_authoring'],
                    evidence_mode='supplied',sources=[source()],
                    selection={'status':'none','ids':[],'evidence':'No candidate selected or delegated'})
                p=router.plan_v2(a); nodes={n['id']:n for n in p['steps']}
                self.assertEqual(nodes['resolve_selection']['state'],'needs_input')
                self.assertEqual(nodes['produce_artifact']['state'],'waiting')



    def test_code_output_rubric_survives_research_or_report_specialization(self):
        for kind in ['research_brief','decision_memo','experiment_plan']:
            with self.subTest(kind=kind):
                p=router.plan_v2(assessment(actions=['research'],deliverable='code',
                    delivery_mode='inline',artifact_kind=kind,evidence_mode='supplied',sources=[source()]))
                self.assertEqual(p['rubric'],'code')
                self.assertEqual(p['blockers'],[])


    def test_independent_research_cannot_complete_blocked_portfolio(self):
        a=assessment(actions=['research'],evidence_mode='mixed',live_research_dependency='independent',
            capabilities=['web'],sources=[source(status='missing',inspected=False)])
        self.finish(a)
        b=assessment(task_id='task-b',actions=['develop'])
        env={'schema_version':2,'workstreams':[{'assessment':a,'depends_on':[]},
            {'assessment':b,'depends_on':['task-a']}]}
        p=router.plan_v2(env); nodes={n['id']:n for n in p['steps']}
        self.assertEqual(nodes['task-a/research_live']['state'],'done')
        self.assertEqual(nodes['task-b/inspect_context']['state'],'waiting')
        self.assertIn('task-a/resolve_source',nodes['task-b/inspect_context']['depends_on'])
        self.assertIn('task-a/synthesize_sources',nodes['task-b/inspect_context']['depends_on'])

    def test_action_change_classifies_removed_valid_receipt_as_stale(self):
        a=assessment(actions=['develop']); self.finish(a)
        a['actions']=['status']
        p=router.plan_v2(a)
        self.assertTrue(any(r['step']=='develop_solution' for r in p['ignored_receipts']))
        self.assertEqual(p['steps'][0]['state'],'ready')


    def in_place_fixture(self):
        target=self.temp/'authoritative.txt'; target.write_text('Original authoritative text',encoding='utf-8')
        other=self.temp/'other.txt'; other.write_text('Unrelated source',encoding='utf-8')
        a=assessment(actions=['revise'],scope='exact',sources=[
            source(kind='file',locator=str(target),revision=router.file_hash(target)),
            source(id='other',kind='file',locator=str(other),revision=router.file_hash(other))])
        a['receipts']=[self.receipt(router.plan_v2(a))]
        snapshot=self.temp/'execution.json'
        snapshot.write_text(json.dumps(router.begin_step(a,'source-a')),encoding='utf-8')
        return a,target,other,snapshot,router.file_hash(snapshot)

    def test_in_place_transition_and_negative_drift_checks(self):
        a,target,other,snapshot,revision=self.in_place_fixture()
        target.write_text('Requested revision',encoding='utf-8')
        out={'kind':'file','locator':str(target),'revision':router.file_hash(target)}
        receipt=router.receipt_from_snapshot(a,snapshot,out,'Inspected bounded edit',revision)
        a['receipts'].append(receipt)
        p=router.plan_v2(a)
        self.assertEqual(next(n for n in p['steps'] if n['id']=='revise_source')['state'],'done')
        self.assertEqual(next(n for n in p['steps'] if n['id']=='verify_output')['state'],'ready')
        other.write_text('External drift',encoding='utf-8')
        self.assertTrue(all(n['state']!='done' for n in router.plan_v2(a)['steps']))
        other.write_text('Unrelated source',encoding='utf-8')
        target.write_text('Postimage tamper',encoding='utf-8')
        self.assertTrue(all(n['state']!='done' for n in router.plan_v2(a)['steps']))

    def test_snapshot_rejects_cross_task_constraints_tamper_and_wrong_target(self):
        a,target,other,snapshot,revision=self.in_place_fixture()
        target.write_text('Requested revision',encoding='utf-8')
        out={'kind':'file','locator':str(target),'revision':router.file_hash(target)}
        for field,value in [('task_id','other-task'),('constraints',[])]:
            changed=copy.deepcopy(a); changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                router.receipt_from_snapshot(changed,snapshot,out,'Inspected',revision)
        wrong={'kind':'file','locator':str(other),'revision':router.file_hash(other)}
        with self.assertRaises(ValueError):router.receipt_from_snapshot(a,snapshot,wrong,'Inspected',revision)
        snapshot.write_text(snapshot.read_text()+' ',encoding='utf-8')
        with self.assertRaises(ValueError):router.receipt_from_snapshot(a,snapshot,out,'Inspected',revision)

    def test_invalid_transition_cannot_bypass_ordinary_receipt_validation(self):
        a,target,other,snapshot,revision=self.in_place_fixture()
        receipt=self.receipt(router.plan_v2(a),'revise_source')
        receipt['transition']={'snapshot':str(snapshot),'revision':'invalid'}
        a['receipts'].append(receipt)
        self.assertNotEqual(next(n for n in router.plan_v2(a)['steps'] if n['id']=='revise_source')['state'],'done')
        receipt['transition']['extra']=True
        with self.assertRaises(ValueError):router.plan_v2(a)

    def test_cli_in_place_begin_edit_receipt_verify_and_no_overwrite(self):
        a,target,other,snapshot,revision=self.in_place_fixture()
        snapshot.unlink()
        assessment_file=self.temp/'assessment.json'
        assessment_file.write_text(json.dumps(a),encoding='utf-8')
        cmd=[sys.executable,str(SCRIPTS/'studio.py')]
        begin=cmd+['begin-step','--assessment',str(assessment_file),'--source-id','source-a','--snapshot',str(snapshot)]
        result=subprocess.run(begin,capture_output=True,text=True,check=True)
        frozen=json.loads(result.stdout)
        before=snapshot.read_bytes()
        self.assertEqual(subprocess.run(begin,capture_output=True,text=True).returncode,2)
        self.assertEqual(snapshot.read_bytes(),before)
        target.write_text('Requested CLI revision',encoding='utf-8')
        receipt=subprocess.run(cmd+['receipt','--assessment',str(assessment_file),'--step','revise_source',
            '--artifact',str(target),'--evidence-file',str(self.output),'--snapshot',str(snapshot),
            '--snapshot-revision',frozen['revision']],capture_output=True,text=True,check=True)
        a['receipts'].append(json.loads(receipt.stdout))
        p=router.plan_v2(a)
        self.assertEqual(next(n for n in p['steps'] if n['id']=='verify_output')['state'],'ready')
        a['receipts'].append(self.receipt(p,'verify_output'))
        self.assertEqual(next(n for n in router.plan_v2(a)['steps'] if n['id']=='verify_output')['state'],'done')


    def test_snapshot_malformed_content_is_validation_error(self):
        a,target,other,snapshot,revision=self.in_place_fixture()
        valid=json.loads(snapshot.read_text())
        for field,value in [('assessment',None),('version',True),('source_id',[])]:
            malformed=copy.deepcopy(valid); malformed[field]=value
            snapshot.write_text(json.dumps(malformed),encoding='utf-8')
            with self.subTest(field=field),self.assertRaises(ValueError):
                router.load_snapshot(snapshot,router.file_hash(snapshot))

    def test_snapshot_cannot_mint_after_unrelated_drift_or_dependency_change(self):
        a,target,other,snapshot,revision=self.in_place_fixture()
        target.write_text('Requested revision',encoding='utf-8')
        out={'kind':'file','locator':str(target),'revision':router.file_hash(target)}
        other.write_text('External change',encoding='utf-8')
        with self.assertRaises(ValueError):router.receipt_from_snapshot(a,snapshot,out,'Inspected',revision)
        other.write_text('Unrelated source',encoding='utf-8')
        a['receipts'][0]['evidence']='Replaced pre-edit evidence'
        with self.assertRaises(ValueError):router.receipt_from_snapshot(a,snapshot,out,'Inspected',revision)


    def test_cli_portfolio_in_place_gates_upstream_and_binds_its_output(self):
        target=self.temp/'portfolio-source.txt'; target.write_text('Original portfolio source',encoding='utf-8')
        a=assessment(task_id='upstream',actions=['research'],evidence_mode='live',capabilities=['web'])
        b=assessment(task_id='edit',actions=['revise'],scope='exact',
            sources=[source(kind='file',locator=str(target),revision=router.file_hash(target))])
        c=assessment(task_id='independent',actions=['develop'])
        env={'schema_version':2,'workstreams':[{'assessment':a,'depends_on':[]},
            {'assessment':b,'depends_on':['upstream']},{'assessment':c,'depends_on':[]}]}
        file=self.temp/'portfolio.json'; snapshot=self.temp/'portfolio-snapshot.json'
        cmd=[sys.executable,str(SCRIPTS/'studio.py')]
        begin=cmd+['begin-step','--assessment',str(file),'--task-id','edit',
            '--source-id','source-a','--snapshot',str(snapshot)]
        file.write_text(json.dumps(env),encoding='utf-8')
        blocked=subprocess.run(begin,capture_output=True,text=True)
        self.assertEqual(blocked.returncode,2)
        self.assertFalse(snapshot.exists())
        self.finish(a)
        p=router.plan_v2(env)
        b['receipts']=[self.receipt(p['workstreams']['edit'])]
        file.write_text(json.dumps(env),encoding='utf-8')
        frozen=json.loads(subprocess.run(begin,capture_output=True,text=True,check=True).stdout)
        self.assertEqual(json.loads(snapshot.read_text())['task_id'],'edit')
        self.assertIn('workstreams',json.loads(snapshot.read_text())['assessment'])
        target.write_text('Requested portfolio revision',encoding='utf-8')
        # An independent workstream may change without invalidating this operation.
        c['objective']='Different independent objective'
        file.write_text(json.dumps(env),encoding='utf-8')
        receipt_cmd=cmd+['receipt','--assessment',str(file),'--task-id','edit','--step','revise_source',
            '--artifact',str(target),'--evidence-file',str(self.output),'--snapshot',str(snapshot),
            '--snapshot-revision',frozen['revision']]
        receipt=json.loads(subprocess.run(receipt_cmd,capture_output=True,text=True,check=True).stdout)
        with self.assertRaises(ValueError):
            router.receipt_from_snapshot(env,snapshot,receipt['output'],'Inspected',frozen['revision'],'independent')
        b['receipts'].append(receipt)
        p=router.plan_v2(env)
        self.assertEqual(next(n for n in p['workstreams']['edit']['steps'] if n['id']=='verify_output')['state'],'ready')
        b['receipts'].append(self.receipt(p['workstreams']['edit'],'verify_output'))
        self.assertEqual(next(n for n in router.plan_v2(env)['workstreams']['edit']['steps'] if n['id']=='verify_output')['state'],'done')
        upstream_output=Path(a['receipts'][-1]['output']['locator'])
        upstream_output.write_text('Changed upstream output',encoding='utf-8')
        self.assertTrue(all(n['state']!='done' for n in router.plan_v2(env)['workstreams']['edit']['steps']))
        with self.assertRaises(ValueError):
            router.receipt_from_snapshot(env,snapshot,receipt['output'],'Inspected',frozen['revision'],'edit')

    def test_cli_snapshot_rejects_shared_predecessor_output_before_edit(self):
        target=self.temp/'shared.txt'; target.write_text('Accepted upstream source',encoding='utf-8')
        a=assessment(task_id='upstream',actions=['research'],evidence_mode='live',capabilities=['web'])
        self.finish(a)
        # The last accepted research output is the source the owner proposes to edit.
        a['receipts'][-1]['output']={'kind':'file','locator':str(target),'revision':router.file_hash(target)}
        b=assessment(task_id='edit',actions=['revise'],scope='exact',
            sources=[source(kind='file',locator=str(target),revision=router.file_hash(target))])
        env={'schema_version':2,'workstreams':[{'assessment':a,'depends_on':[]},
            {'assessment':b,'depends_on':['upstream']}]}
        p=router.plan_v2(env); b['receipts']=[self.receipt(p['workstreams']['edit'])]
        file=self.temp/'shared-portfolio.json'; file.write_text(json.dumps(env),encoding='utf-8')
        snapshot=self.temp/'shared-snapshot.json'
        cmd=[sys.executable,str(SCRIPTS/'studio.py'),'begin-step','--assessment',str(file),
            '--task-id','edit','--source-id','source-a','--snapshot',str(snapshot)]
        before=router.file_hash(target)
        result=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('separate working copy',json.loads(result.stderr)['error'])
        self.assertFalse(snapshot.exists())
        self.assertEqual(router.file_hash(target),before)
        # Preserve the immutable accepted upstream file and revise a distinct copy.
        working=self.temp/'working.txt'; working.write_bytes(target.read_bytes())
        b['sources'][0]['locator']=str(working)
        b['receipts']=[self.receipt(router.plan_v2(env)['workstreams']['edit'])]
        file.write_text(json.dumps(env),encoding='utf-8')
        frozen=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
        working.write_text('Requested working revision',encoding='utf-8')
        output={'kind':'file','locator':str(working),'revision':router.file_hash(working)}
        b['receipts'].append(router.receipt_from_snapshot(env,snapshot,output,'Inspected',frozen['revision'],'edit'))
        p=router.plan_v2(env)
        b['receipts'].append(self.receipt(p['workstreams']['edit'],'verify_output'))
        self.assertEqual(next(n for n in router.plan_v2(env)['workstreams']['edit']['steps'] if n['id']=='verify_output')['state'],'done')
        self.assertEqual(router.file_hash(target),before)

if __name__=='__main__':unittest.main()
