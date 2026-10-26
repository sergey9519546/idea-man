"""Persist requested results only after those results have accepted evidence."""
import copy
from pathlib import Path
import tempfile
import unittest

from test_router_v2 import assessment, router


def node(plan, step):
    return next(item for item in plan['steps'] if item['id'] == step)


class WorkflowFixture:
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / 'test-runs/local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.serial = 0

    def finish(self, task, step):
        current = node(router.plan_v2(task), step)
        self.assertEqual(current['state'], 'ready')
        self.serial += 1
        output = self.folder / (str(self.serial) + '.txt')
        output.write_text('Synthetic inspected fixture output for ' + step, encoding='utf-8')
        task.setdefault('receipts', []).append({
            'step': step, 'binding': current['input_binding'],
            'evidence': 'Inspected the synthetic fixture output',
            'output': {'kind': 'file', 'locator': str(output), 'revision': router.file_hash(output)}})
        return router.plan_v2(task)

    def decision_task(self):
        return assessment(actions=['decide', 'record'], capabilities=['file_write'],
                          artifact_kind='decision_memo',
                          selection={'status': 'assistant_authorized', 'ids': [],
                                     'evidence': 'Choose the best option and save the decision'})


class RecordWorkflowOrderTests(WorkflowFixture, unittest.TestCase):
    def test_record_awaits_selection_and_result_verification(self):
        task = self.decision_task()
        plan = self.finish(task, 'inspect_context')
        self.assertEqual(node(plan, 'evaluate_options')['state'], 'ready')
        self.assertEqual(node(plan, 'record_decisions')['state'], 'waiting')
        for step in ['evaluate_options', 'select_option']:
            plan = self.finish(task, step)
            self.assertEqual(node(plan, 'record_decisions')['state'], 'waiting')
        plan = self.finish(task, 'verify_output')
        self.assertEqual(node(plan, 'record_decisions')['state'], 'ready')
        from workflow_context import ready_context
        context = ready_context(task, 'record_decisions')
        self.assertEqual([item['step_id'] for item in context['inputs']], ['verify_output'])

    def test_changed_selected_output_invalidates_completed_record(self):
        task = self.decision_task()
        for step in ['inspect_context', 'evaluate_options', 'select_option', 'verify_output', 'record_decisions']:
            before = self.finish(task, step)
        old = node(before, 'record_decisions')['input_binding']
        task['receipts'] = [item for item in task['receipts'] if item['step'] != 'select_option']
        after = self.finish(task, 'select_option')
        self.assertEqual(node(after, 'verify_output')['state'], 'ready')
        self.assertEqual(node(after, 'record_decisions')['state'], 'waiting')
        self.assertNotEqual(node(after, 'record_decisions')['input_binding'], old)
        self.assertIn('record_decisions', [item['step'] for item in after['ignored_receipts']])

    def test_record_without_write_tool_does_not_block_decision(self):
        task = self.decision_task()
        task['capabilities'] = []
        plan = self.finish(task, 'inspect_context')
        self.assertEqual(node(plan, 'evaluate_options')['state'], 'ready')
        self.assertEqual(node(plan, 'record_decisions')['state'], 'unavailable')

    def test_standalone_record_and_status_keep_independent_readiness(self):
        for actions in [['record'], ['status', 'record']]:
            with self.subTest(actions=actions):
                task = assessment(actions=actions, capabilities=['file_write'])
                plan = self.finish(task, 'inspect_context')
                self.assertEqual(node(plan, 'record_decisions')['depends_on'], ['inspect_context'])
                self.assertEqual(node(plan, 'record_decisions')['state'], 'ready')
                if 'status' in actions:
                    self.assertEqual(node(plan, 'answer_status')['state'], 'ready')

    def test_blocked_production_holds_record_but_not_status_or_independent_stream(self):
        task = assessment(actions=['produce', 'record', 'status'], deliverable='image',
                          capabilities=['file_write'])
        plan = self.finish(task, 'inspect_context')
        self.assertEqual(node(plan, 'produce_artifact')['state'], 'unavailable')
        self.assertEqual(node(plan, 'record_decisions')['state'], 'waiting')
        self.assertEqual(node(plan, 'answer_status')['state'], 'ready')
        independent = assessment(task_id='other', actions=['status'])
        portfolio = {'schema_version': 2, 'workstreams': [
            {'assessment': task, 'depends_on': []},
            {'assessment': independent, 'depends_on': []}]}
        self.assertEqual(node(router.plan_v2(portfolio), 'other/inspect_context')['state'], 'ready')

    def test_request_array_order_does_not_move_record_before_results(self):
        task = self.decision_task()
        reversed_task = copy.deepcopy(task)
        reversed_task['actions'].reverse()
        self.assertEqual(router.plan_v2(task), router.plan_v2(reversed_task))

    def test_unsaved_fallback_is_ready_without_releasing_requested_persistence(self):
        task = assessment(actions=['record'])
        plan = self.finish(task, 'inspect_context')
        self.assertEqual(node(plan, 'record_decisions')['state'], 'unavailable')
        self.assertEqual(node(plan, 'prepare_unsaved_recap')['state'], 'ready')
        self.assertIn('file_write is unavailable', node(plan, 'prepare_unsaved_recap')['output'])
        self.assertEqual(node(plan, 'present')['state'], 'waiting')
        self.assertFalse(plan['execution_complete'])
        from workflow_context import ready_context
        context = ready_context(task, 'prepare_unsaved_recap')
        self.assertIn('skills/creative-director/references/project-record.md',
                      [resource['path'] for resource in context['resources']])
        plan = self.finish(task, 'prepare_unsaved_recap')
        self.assertEqual(node(plan, 'record_decisions')['state'], 'unavailable')
        self.assertEqual(node(plan, 'present')['state'], 'waiting')

    def test_unsaved_fallback_waits_for_the_pending_selected_decision(self):
        task = self.decision_task()
        task['capabilities'] = []
        for step in ['inspect_context', 'evaluate_options', 'select_option']:
            plan = self.finish(task, step)
            self.assertEqual(node(plan, 'prepare_unsaved_recap')['state'], 'waiting')
        plan = self.finish(task, 'verify_output')
        self.assertEqual(node(plan, 'prepare_unsaved_recap')['state'], 'ready')
        self.assertEqual(node(plan, 'prepare_unsaved_recap')['depends_on'], ['verify_output'])
        self.assertEqual(node(plan, 'record_decisions')['state'], 'unavailable')


if __name__ == '__main__':
    unittest.main()
