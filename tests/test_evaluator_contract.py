"""Synthetic evidence only: changing the ruler must invalidate prior judgments."""
import copy
import json
import unittest
from unittest.mock import patch

import test_evaluation as fixtures

EVAL = fixtures.EVAL

class EvaluatorContractTests(unittest.TestCase):
    setUp = fixtures.EvaluationTests.setUp
    cli = fixtures.EvaluationTests.cli
    capture = fixtures.EvaluationTests.capture
    input_file = fixtures.EvaluationTests.input_file
    import_capture = fixtures.EvaluationTests.import_capture
    prepare = fixtures.EvaluationTests.prepare
    judgment = fixtures.EvaluationTests.judgment
    import_judgment = fixtures.EvaluationTests.import_judgment
    def test_changed_mechanical_rule_invalidates_prior_judgment(self):
        self.prepare()
        self.import_judgment(self.judgment())
        catalog = copy.deepcopy(EVAL.cases())
        catalog['exact_edit']['check']['value'] = 'A different required answer.'
        with patch.object(EVAL, 'cases', return_value=catalog):
            row = EVAL.report(self.run)['cases'][0]
        self.assertEqual(row['status'], 'invalid_evidence')
        self.assertFalse(row['eligible_for_comparison'])

    def test_unchanged_rule_preserves_valid_fixture_judgment(self):
        self.prepare()
        self.import_judgment(self.judgment())
        row = EVAL.report(self.run)['cases'][0]
        self.assertEqual(row['status'], 'test_fixture')
        self.assertEqual(len(row['judgments']), 1)

    def test_changed_evaluator_invalidates_prior_judgment(self):
        self.prepare()
        self.import_judgment(self.judgment())
        with patch.object(EVAL, 'evaluator_revision', return_value='f'*64):
            row = EVAL.report(self.run)['cases'][0]
        self.assertEqual(row['status'], 'invalid_evidence')
        self.assertFalse(row['eligible_for_comparison'])

    def test_changed_human_scoring_anchors_invalidate_prior_judgment(self):
        self.prepare()
        self.import_judgment(self.judgment())
        with patch.object(EVAL, 'grading_contract', return_value='Different grading standard'):
            row = EVAL.report(self.run)['cases'][0]
        self.assertEqual(row['status'], 'invalid_evidence')
        self.assertFalse(row['eligible_for_comparison'])

    def test_packet_delivers_actual_human_grading_contract(self):
        self.prepare()
        packet, _ = EVAL.validated_packet(self.run, 'exact_edit.order1')
        self.assertEqual(packet['evaluation_contract']['human_grading'], EVAL.grading_contract())
        self.assertIn('| Usefulness |', packet['evaluation_contract']['human_grading'])

    def test_malformed_companion_identifier_is_reported_without_crash(self):
        self.prepare()
        self.import_judgment(self.judgment())
        corrupt = {'packet_id':123, 'reviewer_id':'reviewer-1'}
        (self.run/'judgments/corrupt.json').write_text(json.dumps(corrupt), encoding='utf-8')
        row = EVAL.report(self.run)['cases'][0]
        self.assertEqual(row['status'], 'invalid_evidence')
        self.assertFalse(row['eligible_for_comparison'])

    def test_legacy_packet_without_frozen_rules_requires_new_review(self):
        self.prepare()
        path = self.run/'packets/exact_edit.order1.json'
        packet = EVAL.read(path)
        packet.pop('evaluation_contract')
        path.write_text(json.dumps(packet), encoding='utf-8')
        keys_path = self.run/'private/order-key.json'
        keys = EVAL.read(keys_path)
        keys['exact_edit.order1']['packet_sha256'] = EVAL.digest(packet)
        keys_path.write_text(json.dumps(keys), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'evaluation contract'):
            EVAL.validated_packet(self.run, 'exact_edit.order1')


