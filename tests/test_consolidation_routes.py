"""Executable planner regressions; recognition from prose is tested separately."""
import unittest
from test_router_v2 import assessment, source, router

class NoncreativeBypassTests(unittest.TestCase):
    def test_exact_engineering_patch_does_not_invent_alternatives(self):
        p=router.plan_v2(assessment(domain='engineering',actions=['revise'],scope='exact',
            artifact_kind='code',sources=[source()],requested_count=1))
        ids={n['id'] for n in p['steps']}
        self.assertEqual(p['methods'],[])
        self.assertIn('revise_source',ids)
        self.assertTrue(ids.isdisjoint({'generate_options','design_variations','develop_solution','design_experiment'}))

    def test_diagnosis_only_preserves_causal_checks_without_ideation(self):
        p=router.plan_v2(assessment(domain='engineering',actions=['diagnose']))
        nodes={n['id']:n for n in p['steps']}
        self.assertIn('diagnose_problem',nodes)
        self.assertNotIn('generate_options',nodes)
        self.assertNotIn('design_variations',nodes)
        self.assertEqual([m['id'] for m in nodes['diagnose_problem']['method_contracts']],['Y2','Y1'])

    def test_supplied_research_does_not_attach_creative_methods(self):
        p=router.plan_v2(assessment(domain='research',actions=['research'],
            evidence_mode='supplied',sources=[source()],artifact_kind='research_brief'))
        ids={n['id'] for n in p['steps']}
        self.assertEqual(p['methods'],[])
        self.assertEqual(p['specialist']['id'],'research-and-writing')
        self.assertIn('synthesize_sources',ids)
        self.assertTrue(ids.isdisjoint({'generate_options','design_variations','revise_source','produce_artifact'}))

    def test_explicit_count_survives_divergent_method(self):
        p=router.plan_v2(assessment(actions=['ideate'],requested_count=3,requested_methods=['D1']))
        node=next(n for n in p['steps'] if n['id']=='generate_options')
        self.assertEqual(node['requested_count'],3)
        self.assertEqual([m['id'] for m in node['method_contracts']],['D1'])

if __name__=='__main__': unittest.main()
