"""Ready variation packets must preserve the user's fixed mechanism and allowed axes."""
import unittest

from test_router_v2 import assessment, router, source
from test_record_workflow_order import WorkflowFixture, node
from workflow_context import ready_context


class ControlledVariationContextTests(WorkflowFixture, unittest.TestCase):
    def variation_task(self):
        return assessment(
            actions=['vary'], domain='campaign', artifact_kind='campaign',
            objective='Give three tone variants of selected A; keep its offer, facts and mechanism',
            evidence_mode='supplied', sources=[source()], requested_count=3,
            problem={'kind': 'communication', 'bottleneck': 'feedback', 'novelty': 'none',
                     'stakes': 'low', 'reversibility': 'reversible'},
            selection={'status': 'user', 'ids': ['A'], 'evidence': 'Selected A; its mechanism is locked'},
            constraints=[{'id': 'mechanism', 'kind': 'hard',
                          'text': 'Preserve the chosen mechanism; vary tone only',
                          'evidence': 'Explicit user instruction'}])

    def ready_design(self, task):
        for step in ['inspect_context', 'synthesize_sources']:
            self.finish(task, step)
        return ready_context(task, 'design_variations')

    def test_ready_design_preserves_mechanism_lock_and_loads_controlled_guidance(self):
        task = self.variation_task()
        packet = self.ready_design(task)
        self.assertEqual(packet['task']['constraints'], task['constraints'])
        self.assertEqual(packet['task']['selection'], task['selection'])
        self.assertIn('permitted', packet['step']['reason'])
        self.assertNotIn('mechanism-level', packet['step']['reason'])
        control = next(resource for resource in packet['resources']
                       if resource['selector'].get('value') == 'Controlled variations preserving explicit locks')
        self.assertIn('A shared locked mechanism is not a duplicate', control['content'])
        self.assertFalse(packet['grants_execution_authority'])

    def test_ready_generation_uses_permitted_axes_in_checks_methods_and_actual_guidance(self):
        task = self.variation_task()
        self.ready_design(task)
        self.finish(task, 'design_variations')
        packet = ready_context(task, 'generate_options')
        checks = packet['step']['verification_contract']['checks']
        self.assertIn('distinct_useful_variants_within_permitted_axes', checks)
        self.assertIn('explicit_locks_and_authorized_variation_scope', checks)
        self.assertNotIn('distinct_useful_mechanisms', checks)
        self.assertEqual(packet['step']['requested_count'], 3)
        self.assertEqual(packet['task']['constraints'], task['constraints'])
        for method in packet['step']['method_contracts']:
            self.assertIn('permitted axes', method['application'])
            self.assertIn('preserve explicit locks', method['application'])
        selectors = [resource['selector'].get('value') for resource in packet['resources']]
        self.assertIn('Controlled variations preserving explicit locks', selectors)
        self.assertNotIn('Invent alternatives under constraints', selectors)

    def test_ordinary_variation_allows_mechanisms_when_the_axis_is_authorized(self):
        task = self.variation_task()
        task['objective'] = 'Give three variants with different permitted persuasion mechanisms'
        task['selection']['evidence'] = 'Selected the offer and facts; its mechanism may vary'
        task['constraints'][0]['text'] = 'Keep the offer and facts; different persuasion mechanisms are allowed'
        plan = router.plan_v2(task)
        self.assertIn('permitted axes', node(plan, 'generate_options')['reason'])
        self.assertNotIn('distinct_useful_mechanisms', node(plan, 'generate_options')['verification_contract']['checks'])

    def test_ideation_retains_mechanism_diversity_in_checks_and_actual_guidance(self):
        task = assessment(actions=['ideate'])
        self.finish(task, 'inspect_context')
        packet = ready_context(task, 'generate_options')
        self.assertIn('distinct_useful_mechanisms', packet['step']['verification_contract']['checks'])
        selectors = [resource['selector'].get('value') for resource in packet['resources']]
        self.assertIn('Invent alternatives under constraints', selectors)
        self.assertNotIn('Controlled variations preserving explicit locks', selectors)

    def test_explicit_ideation_and_variation_retains_invention_criterion(self):
        task = self.variation_task()
        task['actions'] = ['vary', 'ideate']
        task['objective'] = 'Explore different persuasion mechanisms and refine the permitted offer'
        task['selection']['evidence'] = 'Selected the offer; explore mechanisms around it'
        task['constraints'][0]['text'] = 'Keep the offer; explore different permitted mechanisms'
        plan = router.plan_v2(task)
        self.assertIn('distinct_useful_mechanisms', node(plan, 'generate_options')['verification_contract']['checks'])


if __name__ == '__main__':
    unittest.main()
