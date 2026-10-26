"""Changed user facts and complete accepted handoffs; synthetic local fixtures."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from test_router_v2 import assessment, router
from workflow_context import ready_context


def node(plan, identity):
    return next(step for step in plan['steps'] if step['id'] == identity)


class ContextIntegrityTests(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / 'test-runs/local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)

    def finish(self, task):
        while True:
            plan = router.plan_v2(task)
            step = next((s for s in plan['steps'] if s['state']=='ready' and s['id']!='present'), None)
            if step is None:
                return plan
            output = self.folder / (task['task_id']+'-'+step['id']+'.txt')
            output.write_text('Synthetic inspected output for '+step['id'], encoding='utf-8')
            task.setdefault('receipts', []).append({'step':step['id'],'binding':step['input_binding'],
                'evidence':'Synthetic fixture inspected by test','output':{'kind':'file',
                    'locator':str(output),'revision':hashlib.sha256(output.read_bytes()).hexdigest()}})

    def task(self, **overrides):
        data = assessment(actions=['produce'], artifact_kind='calculation', evidence_mode='none')
        data['problem'].update(kind='execution', novelty='none', bottleneck='implementation')
        data.update(overrides)
        return data

    def test_changed_inline_quantities_invalidate_calculation_and_check(self):
        task = self.task(evidence=[{'source':'user','detail':'240 parts,45seconds each,2 parallel workers'}])
        complete = self.finish(task)
        self.assertEqual(node(complete,'verify_output')['state'],'done')
        task['evidence'][0]['detail'] = '480 parts,45seconds each,2 parallel workers'
        changed = router.plan_v2(task)
        self.assertNotEqual(complete['input_binding'], changed['input_binding'])
        self.assertEqual(node(changed,'inspect_context')['state'],'ready')
        self.assertEqual(node(changed,'produce_artifact')['state'],'waiting')
        self.assertEqual(node(changed,'verify_output')['state'],'waiting')

    def test_changed_learner_attempt_cannot_reuse_previous_feedback(self):
        task = self.task(artifact_kind='coaching_turn',
                        evidence=[{'source':'user','detail':'I subtracted3 and got2x=14'}])
        before = self.finish(task)
        unchanged = router.plan_v2(copy.deepcopy(task))
        self.assertEqual(before, unchanged)
        task['evidence'][0]['detail'] = 'I corrected it to2x=8; what comes next?'
        self.assertNotEqual(before['input_binding'], router.plan_v2(task)['input_binding'])
        self.assertNotEqual(node(router.plan_v2(task),'produce_artifact')['state'], 'done')

    def portfolio(self):
        upstream = self.task(task_id='upstream')
        self.finish(upstream)
        downstream = self.task(task_id='downstream')
        independent = self.task(task_id='independent')
        return {'schema_version':2,'workstreams':[
            {'assessment':upstream,'depends_on':[]},
            {'assessment':downstream,'depends_on':['upstream']},
            {'assessment':independent,'depends_on':[]}]}

    def test_portfolio_handoff_contains_exact_accepted_outputs(self):
        raw = self.portfolio()
        plan = router.plan_v2(raw)
        context = ready_context(raw,'inspect_context','downstream')
        expected = {identity:node(plan,identity)['completion_output']
                    for identity in node(plan,'downstream/inspect_context')['depends_on']}
        self.assertEqual({item['step_id']:item['output'] for item in context['inputs']},expected)
        self.assertEqual(len(context['inputs']),3)
        for item in context['inputs']:
            self.assertTrue(Path(item['output']['locator']).is_file())
            self.assertEqual(hashlib.sha256(Path(item['output']['locator']).read_bytes()).hexdigest(),
                             item['output']['revision'])
        self.assertFalse(context['grants_execution_authority'])
        self.assertEqual(ready_context(raw,'inspect_context','independent')['inputs'],[])

    def test_stale_predecessor_blocks_handoff_without_blocking_independent_work(self):
        raw = self.portfolio()
        output = raw['workstreams'][0]['assessment']['receipts'][1]['output']
        Path(output['locator']).write_text('Changed after acceptance',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'ready'):
            ready_context(raw,'inspect_context','downstream')
        self.assertEqual(ready_context(raw,'inspect_context','independent')['step']['state'],'ready')

    def test_local_handoff_exposes_predecessor_identity_without_source_copy(self):
        task = self.task()
        plan = router.plan_v2(task)
        output = self.folder/'inspected.txt'
        output.write_text('Inspected task contract',encoding='utf-8')
        task['receipts']=[{'step':'inspect_context','binding':node(plan,'inspect_context')['input_binding'],
            'evidence':'Inspected actual fixture','output':{'kind':'file','locator':str(output),
            'revision':hashlib.sha256(output.read_bytes()).hexdigest()}}]
        context = ready_context(task,'produce_artifact')
        self.assertEqual(context['inputs'][0]['step_id'],'inspect_context')
        self.assertEqual(context['inputs'][0]['output']['locator'],str(output))
        self.assertNotIn('content',context['inputs'][0])


if __name__=='__main__':
    unittest.main()
