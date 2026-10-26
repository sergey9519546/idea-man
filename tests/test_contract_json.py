"""Reject ambiguous raw contracts before state changes; no provider calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_router_v2 import assessment, router, source


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'


class ContractJsonTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.environment = dict(os.environ, TEMP=str(self.folder), TMP=str(self.folder))
        self.record = self.folder / 'project.json'
        self.call('init', '--file', self.record, '--title', 'Contract input checks')

    def call(self, *arguments, ok=True):
        run = subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                             capture_output=True, text=True, encoding='utf-8',
                             env=self.environment)
        self.assertEqual(run.returncode, 0 if ok else 2, run.stderr)
        return json.loads(run.stdout if ok else run.stderr)

    def reject_event(self, payload, message):
        before = self.record.read_bytes()
        event = self.folder / 'event.json'
        event.write_text(payload, encoding='utf-8')
        rejection = self.call('record', '--file', self.record, '--expected-revision', 0,
                              '--event', event, ok=False)
        self.assertIn(message, rejection['error'])
        self.assertEqual(self.record.read_bytes(), before)
        current = self.call('show', '--file', self.record)
        self.assertEqual(current['revision'], 0)
        self.assertEqual(current['notes'], [])

    def test_duplicate_event_fields_rejected_without_changing_record(self):
        self.reject_event('{"type":"note","text":"Preserve approved direction",'
                          '"text":"Replace approved direction"}', 'Duplicate JSON key: text')
        self.assertFalse(self.record.with_suffix(self.record.suffix + '.lock').exists())

    def test_duplicate_plan_actions_and_nested_authority_rejected(self):
        raw = json.dumps(assessment(actions=['review'], sources=[source()]))
        payloads = [
            raw.replace('"actions": ["review"]',
                        '"actions": ["review"], "actions": ["produce"]'),
            raw.replace('"status": "not_needed"',
                        '"status": "user", "status": "not_needed"')]
        for payload in payloads:
            with self.subTest(payload=payload[:60]):
                path = self.folder / 'assessment.json'
                path.write_text(payload, encoding='utf-8')
                before = path.read_bytes()
                error = self.call('plan', '--assessment', path, ok=False)
                self.assertIn('Duplicate JSON key:', error['error'])
                self.assertEqual(path.read_bytes(), before)

    def test_nonfinite_constants_and_numeric_overflow_rejected_before_mutation(self):
        for token in ['NaN', 'Infinity', '-Infinity', '1e9999', '-1e9999']:
            with self.subTest(token=token):
                self.reject_event('{"type":"note","text":' + token + '}',
                                  'Non-finite JSON')

    def test_valid_legacy_record_bom_unicode_and_finite_plan_are_preserved(self):
        self.record.write_bytes(b'\xef\xbb\xbf' + self.record.read_bytes())
        before = self.record.read_bytes()
        current = self.call('show', '--file', self.record)
        self.assertEqual(current['revision'], 0)
        self.assertEqual(before, self.record.read_bytes())
        event = self.folder / 'valid-event.json'
        event.write_text('{"type":"note","text":"Preserve caf\u00e9; Infinity is text here."}', encoding='utf-8-sig')
        current = self.call('record', '--file', self.record, '--expected-revision', 0,
                            '--event', event)
        self.assertEqual(current['revision'], 1)
        self.assertEqual(current['notes'], ['Preserve caf\u00e9; Infinity is text here.'])
        legacy = {'schema_version': 1, 'objective': 'Review a supplied source',
                  'actions': ['review'], 'deliverable': 'text', 'scope': 'bounded',
                  'selection': 'not_needed', 'source': 'available', 'brief': 'sufficient',
                  'confidence': 0.5, 'evidence': [{'source': 'user', 'detail': 'Review only'}]}
        path = self.folder / 'legacy-plan.json'
        path.write_text(json.dumps(legacy).replace('0.5', '5e-1'), encoding='utf-8-sig')
        plan = self.call('plan', '--assessment', path)
        self.assertEqual(plan['schema_version'], 1)

    def test_snapshots_reject_duplicate_keys_and_nonfinite_nested_values(self):
        snapshot = {'version': 1, 'assessment': assessment(actions=['revise'], sources=[source()]),
                    'source_id': 'source-a', 'binding': 'inspected-binding', 'task_id': None}
        raw = json.dumps(snapshot)
        path = self.folder / 'snapshot.json'
        path.write_text(raw, encoding='utf-8')
        self.assertEqual(router.load_snapshot(path, router.file_hash(path)), snapshot)
        bad = [raw.replace('"version": 1', '"version": 9, "version": 1')]
        bad += [raw.replace('"stage": "framed"', '"stage": ' + token)
                for token in ['NaN', 'Infinity', '-Infinity', '1e9999', '-1e9999']]
        for payload in bad:
            with self.subTest(payload=payload[:80]):
                path.write_text(payload, encoding='utf-8')
                before = path.read_bytes()
                revision = hashlib.sha256(before).hexdigest()
                with self.assertRaisesRegex(ValueError, 'Duplicate JSON key:|Non-finite JSON'):
                    router.load_snapshot(path, revision)
                self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
