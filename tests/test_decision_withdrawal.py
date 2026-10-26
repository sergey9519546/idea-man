"""Public CLI journeys for explicit approval withdrawal; no model calls."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_router_v2 import assessment


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'


class DecisionWithdrawalTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.record = self.folder / 'project.json'
        self.environment = dict(os.environ, TEMP=str(self.folder), TMP=str(self.folder))
        self.call('init', '--file', self.record, '--title', 'Current approval decisions')

    def call(self, *arguments, ok=True, markdown=False):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                                capture_output=True, text=True, encoding='utf-8',
                                env=self.environment, timeout=20)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stderr)
        if markdown:
            return result.stdout
        return json.loads(result.stdout if ok else result.stderr)

    def raw(self):
        return json.loads(self.record.read_text(encoding='utf-8'))

    def append(self, event, expected=None, ok=True):
        path = self.folder / 'event.json'
        path.write_text(json.dumps(event), encoding='utf-8')
        if expected is None:
            expected = self.raw()['revision']
        return self.call('record', '--file', self.record, '--expected-revision', expected,
                         '--event', path, ok=ok)

    def candidate(self, identity):
        return self.append({'type': 'candidate', 'id': identity, 'text': 'Solution ' + identity})

    def approve(self, identity, evidence='User: this solution is approved'):
        return self.append({'type': 'approve', 'target_id': identity, 'evidence': evidence})

    def test_withdrawal_export_stale_checkpoint_and_later_reapproval(self):
        self.candidate('A')
        self.candidate('B')
        self.approve('A')
        self.approve('B')
        task = assessment(actions=['develop'], selection={
            'status': 'user', 'ids': ['A'], 'evidence': 'User: develop approved A'})
        self.append({'type': 'checkpoint', 'assessment': task,
                     'pending_actions': ['develop'], 'evidence': 'User: save unfinished development'})
        saved = self.raw()
        before = self.call('show', '--file', self.record)
        untouched = copy.deepcopy(before['items']['B'])
        event = {'type': 'withdraw', 'target_id': 'A',
                 'evidence': 'User: do not use A anymore; no replacement selected',
                 'reason': 'Requirements changed'}
        self.append(event)
        view = self.call('show', '--file', self.record)
        self.assertEqual(view['items']['A']['status'], 'withdrawn')
        self.assertEqual(view['items']['A']['decision_evidence'], event['evidence'])
        self.assertEqual(view['items']['B'], untouched)
        self.assertEqual(set(view['items']), {'A', 'B'}, 'No fabricated replacement')
        history = self.raw()['events']
        self.assertEqual(history[:-1], saved['events'])
        self.assertEqual(history[-1]['event'], event)
        exported = self.call('export', '--file', self.record, markdown=True)
        self.assertIn('A [withdrawn]: Solution A', exported)
        self.assertIn('Reason: Requirements changed', exported)
        self.assertIn('B [approved]: Solution B', exported)
        packet = self.call('resume', '--file', self.record)
        self.assertIsNone(packet['resume_assessment'])
        self.assertFalse(packet['execution_authorized'])
        self.assertTrue(any('Record changed after checkpoint' in item for item in packet['blockers']))
        self.assertEqual(packet['project']['items']['A']['status'], 'withdrawn')
        self.assertTrue(self.call('validate', '--file', self.record)['valid'])
        fresh_evidence = 'User: after reconsidering the new requirements, approve A again'
        restored = self.approve('A', fresh_evidence)
        self.assertEqual(restored['items']['A']['status'], 'approved')
        self.assertEqual(restored['items']['A']['decision_evidence'], fresh_evidence)
        self.assertNotIn('reason', restored['items']['A'])
        self.assertEqual(restored['items']['B'], untouched)
        self.assertEqual(self.raw()['events'][-2]['event'], event)

    def test_explicit_constraint_withdrawal_preserves_other_approvals(self):
        self.candidate('A')
        self.approve('A')
        before = self.call('show', '--file', self.record)['items']['A']
        self.append({'type': 'constraint', 'id': 'budget', 'text': 'Keep the old budget cap',
                     'evidence': 'User: keep this budget cap'})
        view = self.append({'type': 'withdraw', 'target_id': 'budget',
                            'evidence': 'User: the budget cap no longer applies'})
        self.assertEqual(view['items']['budget']['type'], 'constraint')
        self.assertEqual(view['items']['budget']['status'], 'withdrawn')
        self.assertIsNone(view['items']['budget']['reason'])
        self.assertEqual(view['items']['A'], before)
        exported = self.call('export', '--file', self.record, markdown=True)
        self.assertIn('budget [withdrawn]: Keep the old budget cap', exported)
        self.assertIn('Reason: not supplied', exported)

    def test_invalid_withdrawals_preserve_record_and_existing_rejection_guard(self):
        self.candidate('A')
        self.candidate('B')
        self.candidate('C')
        self.approve('A')
        self.append({'type': 'supersede', 'target_id': 'A', 'replacement_id': 'B',
                     'evidence': 'User: replace A with B'})
        before = self.record.read_bytes()
        invalid = [
            {'type': 'withdraw', 'target_id': 'B'},
            {'type': 'withdraw', 'target_id': 'B', 'evidence': ''},
            {'type': 'withdraw', 'target_id': 'C', 'evidence': 'User: withdraw C'},
            {'type': 'withdraw', 'target_id': 'A', 'evidence': 'User: withdraw A'},
            {'type': 'withdraw', 'target_id': 'unknown', 'evidence': 'User: withdraw unknown'},
            {'type': 'reject', 'target_id': 'B', 'evidence': 'Do not silently unlock an approval'}]
        for event in invalid:
            with self.subTest(event=event):
                self.append(event, ok=False)
                self.assertEqual(self.record.read_bytes(), before)
                self.assertFalse(self.record.with_name(self.record.name + '.lock').exists())

    def test_stale_withdrawal_cannot_overwrite_then_current_retry_succeeds(self):
        self.candidate('A')
        self.approve('A')
        event = {'type': 'withdraw', 'target_id': 'A',
                 'evidence': 'User: remove approval with no replacement'}
        before = self.record.read_bytes()
        error = self.append(event, expected=1, ok=False)
        self.assertIn('Revision conflict', error['error'])
        self.assertEqual(self.record.read_bytes(), before)
        view = self.append(event)
        self.assertEqual(view['items']['A']['status'], 'withdrawn')
        withdrawn = self.record.read_bytes()
        self.append(event, ok=False)
        self.assertEqual(self.record.read_bytes(), withdrawn)


if __name__ == '__main__':
    unittest.main()
