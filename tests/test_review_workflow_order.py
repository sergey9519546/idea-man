"""An explicit source review precedes proposals, development and bounded repairs."""
import copy
import unittest

from test_router_v2 import assessment, router, source
from test_record_workflow_order import WorkflowFixture, node


class ReviewWorkflowOrderTests(WorkflowFixture, unittest.TestCase):
    def review_task(self, action):
        return assessment(actions=['review', action], sources=[source()], evidence_mode='supplied')

    def test_review_and_suggestions_inspect_source_before_generating(self):
        task = self.review_task('ideate')
        task['requested_count'] = 3
        plan = router.plan_v2(task)
        self.assertEqual(node(plan, 'review_source')['skill'], 'artifact-quality')
        self.assertEqual(node(plan, 'review_source')['depends_on'], ['inspect_context', 'synthesize_sources'])
        self.assertEqual(node(plan, 'generate_options')['depends_on'], ['review_source'])
        self.assertEqual(node(plan, 'generate_options')['requested_count'], 3)
        self.assertNotIn('revise_source', [item['id'] for item in plan['steps']])
        self.assertEqual(node(plan, 'evaluate_options')['depends_on'], ['generate_options'])

    def test_review_precedes_each_requested_follow_on_operation(self):
        for action, step in [('diagnose', 'diagnose_problem'), ('vary', 'design_variations'),
                             ('revise', 'revise_source'), ('decide', 'evaluate_options'),
                             ('develop', 'develop_solution'), ('experiment', 'design_experiment'),
                             ('handoff', 'prepare_handoff')]:
            with self.subTest(action=action):
                plan = router.plan_v2(self.review_task(action))
                self.assertEqual(node(plan, step)['depends_on'], ['review_source'])

    def test_source_findings_change_invalidates_suggestions(self):
        task = self.review_task('ideate')
        for step in ['inspect_context', 'synthesize_sources', 'review_source', 'generate_options']:
            old = self.finish(task, step)
        binding = node(old, 'generate_options')['input_binding']
        task['receipts'] = [item for item in task['receipts'] if item['step'] != 'review_source']
        changed = self.finish(task, 'review_source')
        self.assertEqual(node(changed, 'generate_options')['state'], 'ready')
        self.assertNotEqual(node(changed, 'generate_options')['input_binding'], binding)

    def test_standalone_inline_review_keeps_one_read_only_quality_pass(self):
        plan = router.plan_v2(assessment(actions=['review'], sources=[source()]))
        self.assertEqual([item['id'] for item in plan['steps']],
                         ['inspect_context', 'evaluate_options', 'present'])

    def test_saved_review_report_keeps_review_before_authoring(self):
        plan = router.plan_v2(assessment(actions=['review'], sources=[source()],
                                        deliverable='document', capabilities=['document_authoring']))
        self.assertNotIn('review_source', [item['id'] for item in plan['steps']])
        self.assertEqual(node(plan, 'prepare_handoff')['depends_on'], ['evaluate_options'])
        self.assertEqual(node(plan, 'verify_output')['depends_on'], ['produce_artifact'])

    def test_action_set_order_does_not_reverse_source_review(self):
        task = self.review_task('ideate')
        inverse = copy.deepcopy(task)
        inverse['actions'].reverse()
        self.assertEqual(router.plan_v2(task), router.plan_v2(inverse))


if __name__ == '__main__':
    unittest.main()
