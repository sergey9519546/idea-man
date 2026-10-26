"""Phase-specific reasoning and proportional checks; these are not model evaluations."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_router_v2 import assessment, router

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'


def direct(kind='calculation', **overrides):
    task = assessment(actions=['produce'], domain='general', artifact_kind=kind,
                      evidence_mode='none', scope='bounded')
    task['problem'].update(kind='execution', novelty='none', bottleneck='implementation',
                           stakes='low')
    task.update(overrides)
    return task


def node(plan, key):
    return next(row for row in plan['steps'] if row['id'] == key)


class PhaseReasoningTests(unittest.TestCase):
    def test_mixed_diagnosis_and_generation_each_have_an_applicable_procedure(self):
        plan = router.plan_v2(assessment())
        diagnosis = node(plan, 'diagnose_problem')['method_contracts']
        generation = node(plan, 'generate_options')['method_contracts']
        self.assertEqual([m['id'] for m in diagnosis], ['Y2', 'Y1'])
        self.assertTrue(generation)
        self.assertTrue(all(m['application'] for m in diagnosis + generation))
        self.assertNotEqual(diagnosis[-1]['application'], generation[-1]['application'])

    def test_explicit_generating_method_is_not_consumed_by_earlier_diagnosis(self):
        plan = router.plan_v2(assessment(requested_methods=['S2']))
        self.assertEqual([m['id'] for m in node(plan, 'generate_options')['method_contracts']], ['S2'])
        self.assertNotIn('S2', [m['id'] for m in node(plan, 'diagnose_problem').get('method_contracts', [])])
        self.assertEqual([m['id'] for m in plan['methods']], ['S2'])

    def test_direct_inline_calculation_has_checks_without_invention_or_file_gate(self):
        plan = router.plan_v2(direct())
        self.assertEqual(plan['rubric'], 'quantitative')
        self.assertEqual(plan['methods'], [])
        self.assertEqual(plan['blockers'], [])
        ids = {row['id'] for row in plan['steps']}
        self.assertFalse(ids & {'frame_problem', 'generate_options', 'prepare_handoff', 'resolve_selection'})
        self.assertEqual(node(plan, 'produce_artifact')['missing_capabilities'], [])
        checks = node(plan, 'verify_output')['verification_contract']['checks']
        self.assertTrue({'quantity_model_inputs_units', 'calculation_validity', 'bounds_sanity_precision'} <= set(checks))

    def test_quick_changes_optional_breadth_not_required_checks(self):
        task = assessment(actions=['diagnose'], effort='quick')
        task['problem'].update(stakes='high', reversibility='irreversible')
        quick = router.plan_v2(task)
        task['effort'] = 'deep'
        deep = router.plan_v2(task)
        self.assertEqual(node(quick, 'verify_output')['verification_contract'],
                         node(deep, 'verify_output')['verification_contract'])
        self.assertIn('consequential_uncertainty_and_failure_limits',
                      node(quick, 'verify_output')['verification_contract']['checks'])
        self.assertEqual(quick['effort_policy']['optional_method_budget'], 1)
        self.assertFalse(quick['effort_policy']['required_checks_reduced'])

    def test_reasoning_artifact_contracts_are_content_specific(self):
        for kind, rubric, check in [
                ('proof', 'formal_reasoning', 'assumptions_inference_cases_counterexamples'),
                ('explanation', 'explanation', 'requested_question_level_and_accuracy'),
                ('coaching_turn', 'coaching', 'requested_learning_interaction_no_premature_solution'),
                ('statistical_analysis', 'quantitative', 'sample_comparison_confounds_and_inference_limits')]:
            with self.subTest(kind=kind):
                plan = router.plan_v2(direct(kind))
                self.assertEqual(plan['rubric'], rubric)
                self.assertEqual(plan['methods'], [])
                self.assertIn(check, node(plan, 'verify_output')['verification_contract']['checks'])

    def test_code_and_image_keep_their_rubric_over_reasoning_artifact_label(self):
        for deliverable, capabilities, expected in [('code', [], 'code'), ('image', ['image_generation'], 'visual')]:
            plan = router.plan_v2(direct('calculation', deliverable=deliverable,
                                        delivery_mode='inline' if deliverable == 'code' else 'artifact',
                                        capabilities=capabilities))
            self.assertEqual(plan['rubric'], expected)

    def test_changed_phase_check_contract_invalidates_its_receipt(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as folder:
            artifact = Path(folder) / 'inspected.txt'
            artifact.write_text('Task inspected; values and units checked.', encoding='utf-8')
            task = direct()
            first = router.plan_v2(task)
            task['receipts'] = [{'step': 'inspect_context', 'binding': node(first, 'inspect_context')['input_binding'],
                                 'evidence': 'Inspected actual task.', 'output': {'kind': 'file', 'locator': str(artifact),
                                 'revision': hashlib.sha256(artifact.read_bytes()).hexdigest()}}]
            accepted = router.plan_v2(task)
            self.assertEqual(node(accepted, 'inspect_context')['state'], 'done')
            old_binding = node(accepted, 'verify_output')['input_binding']
            original = router.verification_for_step
            def changed(a, key, rubric):
                contract = original(a, key, rubric)
                if key == 'verify_output':
                    contract['checks'].append('new_required_check')
                return contract
            with patch.object(router, 'verification_for_step', side_effect=changed):
                revised = router.plan_v2(task)
            self.assertEqual(node(revised, 'inspect_context')['state'], 'done')
            self.assertNotEqual(old_binding, node(revised, 'verify_output')['input_binding'])

    def test_public_cli_reports_typed_checks_and_still_has_no_execution_authority(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as folder:
            path = Path(folder) / 'task.json'
            task = direct('calculation', acceptance=['Return the numeric answer and unit only'])
            path.write_text(json.dumps(task), encoding='utf-8')
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), 'plan', '--assessment', str(path)],
                                    capture_output=True, text=True, encoding='utf-8',
                                    env=dict(os.environ, TEMP=folder, TMP=folder))
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan['rubric'], 'quantitative')
            self.assertEqual(node(plan, 'verify_output')['acceptance'], task['acceptance'])
            self.assertFalse(plan['execution_complete'])
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
