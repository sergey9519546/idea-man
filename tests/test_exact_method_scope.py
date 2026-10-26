"""Explicit reasoning can support a protected edit without expanding its scope."""
import unittest

from test_router_v2 import assessment, router, source


class ExactMethodScopeTests(unittest.TestCase):
    def exact(self, **changes):
        task = assessment(actions=['revise'], scope='exact', sources=[source()],
                          artifact_kind='article')
        task.update(changes)
        return task

    def test_exact_default_does_not_cast_methods(self):
        plan = router.plan_v2(self.exact(thinking_style='contrarian'))
        self.assertEqual(plan['methods'], [])

    def test_explicit_inversion_supports_only_the_bounded_revision(self):
        task = self.exact(requested_methods=['L2'],
            objective='Use inversion to improve only the final sentence; earlier text is locked')
        default = router.plan_v2(self.exact())
        plan = router.plan_v2(task)
        self.assertEqual([m['id'] for m in plan['methods']], ['L2'])
        self.assertEqual([s['id'] for s in plan['steps']], [s['id'] for s in default['steps']])
        revision = next(s for s in plan['steps'] if s['id'] == 'revise_source')
        self.assertEqual([m['id'] for m in revision['method_contracts']], ['L2'])
        self.assertIn('authorized bounded revision', revision['method_contracts'][0]['application'])
        self.assertIn('authorized_delta_and_protected_properties', revision['verification_contract']['checks'])

    def test_explicit_causal_analysis_preserves_review_then_repair(self):
        plan = router.plan_v2(self.exact(actions=['review', 'revise'], requested_methods=['Y2']))
        ids = [s['id'] for s in plan['steps']]
        self.assertLess(ids.index('review_source'), ids.index('revise_source'))
        self.assertLess(ids.index('revise_source'), ids.index('verify_output'))
        self.assertEqual([m['id'] for m in plan['methods']], ['Y2'])
        self.assertFalse({'generate_options', 'design_variations'} & set(ids))

    def test_explicit_methods_do_not_make_exact_ideation_compatible(self):
        for action in ['ideate', 'vary']:
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, 'Exact scope conflicts'):
                router.plan_v2(self.exact(actions=['revise', action], requested_methods=['L2']))

    def test_status_is_not_a_substantive_method_target(self):
        with self.assertRaisesRegex(ValueError, 'no compatible substantive step'):
            router.plan_v2(self.exact(actions=['status'], requested_methods=['Y2']))


if __name__ == '__main__':
    unittest.main()
