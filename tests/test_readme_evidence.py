"""Documentation evidence integrity, not a model-quality or host-activation test."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReadmeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'eval/captured/captures.json').read_text(encoding='utf-8'))
        self.readme = (ROOT / 'README.md').read_text(encoding='utf-8')

    def test_published_capture_text_matches_its_bindings(self):
        for case in self.record['cases']:
            for field in ['request', 'response']:
                text = case[field].replace('\r\n', '\n')
                self.assertEqual(hashlib.sha256(text.encode('utf-8')).hexdigest(), case[field + '_sha256'])
            self.assertTrue(case['request'].startswith(self.record['invocation'] + ' '))
            self.assertTrue(case['current_conductor_read_observed'])
            self.assertFalse(case['all_references_loaded'])

    def test_highlighted_diagnosis_quote_is_an_actual_capture_excerpt(self):
        diagnosis = next(case for case in self.record['cases'] if case['id'] == 'noncreative-diagnosis')
        quotes = re.findall(r'^> (The evidence shows .+)$', self.readme, re.MULTILINE)
        self.assertEqual(len(quotes), 1)
        self.assertIn(quotes[0], diagnosis['response'])

    def test_both_demos_link_to_the_full_capture_and_keep_evidence_type(self):
        self.assertEqual(self.record['evidence_kind'], 'captured_model_responses_to_synthetic_prompts')
        self.assertIn('fictional briefs', self.readme)
        self.assertTrue(self.record['limitations'])
        transcript = (ROOT / 'eval/captured/README.md').read_text(encoding='utf-8')
        for case in self.record['cases']:
            self.assertIn('eval/captured/README.md#' + case['id'], self.readme)
            self.assertIn(case['request'], transcript)
            self.assertIn(case['response'].strip(), transcript)

    def test_public_record_excludes_private_host_locators(self):
        text = json.dumps(self.record)
        self.assertNotIn('C:\\', text)
        self.assertNotIn('/Users/', text)
        self.assertNotIn('threadId', text)


if __name__ == '__main__':
    unittest.main()
