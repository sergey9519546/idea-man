"""Verify published worked evidence without grading authored prose as model quality."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('worked', ROOT/'eval/worked_examples.py')
worked = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worked)

class WorkedEvidenceTests(unittest.TestCase):
    def test_current_sources_and_executions_match_record(self):
        record = json.loads((ROOT/'eval/examples/results.json').read_text(encoding='utf-8'))
        self.assertEqual(record, worked.build())
        self.assertEqual(record['status'], 'worked_examples_only')
        for key in ['model_runs','baseline_comparisons','independent_quality_reviews']:
            self.assertEqual(record[key], 0)
        by_id = {x['id']:x for x in record['examples']}
        decision = by_id['choice_sensitivity']['mechanical_checks']
        self.assertEqual(decision['naive_payback_weeks'],20)
        self.assertAlmostEqual(decision['break_even_weekly_overhead'],46.15384615384616)
        self.assertGreater(decision['positive_savings_at_40_overhead'],0)
        self.assertLess(decision['negative_savings_at_50_overhead'],0)
        pilot = by_id['weak_pilot']['mechanical_checks']
        self.assertAlmostEqual(pilot['median_wait_reduction'],.3)
        self.assertAlmostEqual(pilot['baseline_error_rate'],.05)
        self.assertAlmostEqual(pilot['pilot_error_rate'],.2)
        self.assertFalse(by_id['queue_diagnosis']['mechanical_checks']['on_time_approval_denominator_available'])
        repeat, rollout = [x['output'] for x in record['helper_probes']]
        self.assertEqual(repeat['eligible_for_scoped_next_step'],['repeat'])
        self.assertEqual(rollout['eligible_for_scoped_next_step'],[])
        self.assertEqual(rollout['candidates'][0]['readiness'],'needs_evidence')
        for output in [repeat,rollout]:
            for key in ['selection_made','execution_authorized','semantic_truth_verified']:
                self.assertFalse(output[key])

    def test_changed_casebook_requires_deliberate_editorial_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'cases.json'
            path.write_text('{"cases":[]}',encoding='utf-8')
            original = worked.CASES
            try:
                worked.CASES = path
                with self.assertRaisesRegex(ValueError,'Source cases changed'):
                    worked.build()
            finally:
                worked.CASES = original

    def test_missing_test_does_not_become_ready(self):
        record = json.loads((ROOT/'eval/examples/results.json').read_text(encoding='utf-8'))
        assessment = copy.deepcopy(record['helper_probes'][0]['input'])
        assessment['candidates'][0]['next_test'] = None
        import subprocess
        with self.assertRaises(subprocess.CalledProcessError):
            worked.run_candidate(assessment)
