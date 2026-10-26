"""Supplied assessments test method placement, not natural-language recognition."""
import unittest

from test_router_v2 import assessment, source, router


class ResearchMethodRoutingTests(unittest.TestCase):
    def task(self, mode, artifact=False):
        return assessment(actions=['research'], evidence_mode=mode,
                          sources=[] if mode=='live' else [source()],
                          capabilities=['web','file_write'],
                          requested_methods=['D2'], artifact_kind='research_brief',
                          delivery_mode='artifact' if artifact else 'inline')

    def test_requested_research_method_attaches_to_evidence_not_file_packaging(self):
        for mode, expected in [('supplied','synthesize_sources'), ('canon','synthesize_sources'),
                               ('live','research_live'), ('mixed','research_live')]:
            for artifact in (False, True):
                with self.subTest(mode=mode, artifact=artifact):
                    plan=router.plan_v2(self.task(mode,artifact))
                    nodes={node['id']:node for node in plan['steps']}
                    self.assertEqual([m['id'] for m in nodes[expected]['method_contracts']], ['D2'])
                    self.assertNotIn('generate_options', nodes)
                    if artifact:
                        self.assertNotIn('method_contracts', nodes['produce_artifact'])

    def test_default_research_still_has_no_forced_method(self):
        task=self.task('supplied')
        task['requested_methods']=[]
        self.assertEqual(router.plan_v2(task)['methods'], [])

    def test_missing_web_remains_blocked_even_with_requested_method(self):
        task=self.task('live')
        task['capabilities']=[]
        nodes={node['id']:node for node in router.plan_v2(task)['steps']}
        self.assertEqual(nodes['research_live']['state'], 'unavailable')
        self.assertEqual(nodes['research_live']['missing_capabilities'], ['web'])

    def test_phase_scoped_method_can_be_represented_without_leaking_into_review(self):
        research=self.task('supplied')
        research['task_id']='evidence'
        review=assessment(task_id='review', actions=['review'], evidence_mode='supplied',
                          sources=[source()], requested_methods=[])
        plan=router.plan_v2({'schema_version':2, 'workstreams':[
            {'assessment':research, 'depends_on':[]},
            {'assessment':review, 'depends_on':['evidence']}]})
        nodes={node['id']:node for node in plan['steps']}
        self.assertEqual([method['id'] for method in
                          nodes['evidence/synthesize_sources']['method_contracts']], ['D2'])
        self.assertNotIn('method_contracts', nodes['review/evaluate_options'])
        self.assertEqual(nodes['review/inspect_context']['state'], 'waiting')
        self.assertTrue(all(key.startswith('evidence/') for key in
                            nodes['review/inspect_context']['depends_on']))


if __name__=='__main__':
    unittest.main()
