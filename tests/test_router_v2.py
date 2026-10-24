import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
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
        return {'step':step,'binding':plan['input_binding'],'evidence':'Actual inspection note',
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
        p=router.plan_v2(assessment(actions=['research'],evidence_mode='mixed',capabilities=['web'],sources=[source(status='missing',inspected=False)]))
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
        self.assertEqual(json.loads(receipt.stdout)['binding'],router.plan_v2(assessment())['input_binding'])

if __name__=='__main__':unittest.main()
