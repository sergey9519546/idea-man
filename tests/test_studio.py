import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'
spec = importlib.util.spec_from_file_location('studio', SCRIPT)
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)
CASES = json.loads((ROOT / 'plugins/idea-man/skills/creative-director/references/examples/recognition-cases.json').read_text(encoding='utf-8'))['cases']


class RoutingTests(unittest.TestCase):
    def base(self, **overrides):
        return {**copy.deepcopy(CASES[0]['assessment']), **overrides}

    def test_count_survives_routing(self):
        result = studio.plan(CASES[1]['assessment'])
        generation = next(s for s in result['steps'] if s['id'] == 'generate_concepts')
        self.assertEqual(generation['requested_count'], 6)

    def test_missing_source_blocks_edit(self):
        result = studio.plan(CASES[7]['assessment'])
        steps = {s['id']: s for s in result['steps']}
        self.assertEqual(steps['resolve_source']['state'], 'needs_input')
        self.assertIn('resolve_source', steps['revise_source']['depends_on'])
        self.assertEqual(steps['produce_artifact']['state'], 'waiting')

    def test_missing_tool_does_not_claim_production(self):
        result = studio.plan(CASES[8]['assessment'])
        production = next(s for s in result['steps'] if s['id'] == 'produce_artifact')
        self.assertEqual(production['state'], 'unavailable')
        self.assertEqual(production['missing_capabilities'], ['video_generation'])
        self.assertFalse(result['execution_complete'])

    def test_research_independent_of_missing_brief(self):
        steps = {s['id']: s for s in studio.plan(CASES[9]['assessment'])['steps']}
        self.assertEqual(steps['research']['depends_on'], ['inspect_context'])
        self.assertIn('clarify_brief', steps['extract_insight']['depends_on'])
        self.assertIn('research', steps['extract_insight']['depends_on'])

    def test_contradictory_exact_exploration_rejected(self):
        with self.assertRaises(studio.StudioError):
            studio.plan(self.base(scope='exact'))

    def test_invalid_count_and_false_confidence_rejected(self):
        for value in (0, -1, True, '6'):
            with self.subTest(count=value), self.assertRaises(studio.StudioError):
                studio.plan(self.base(requested_count=value))
        with self.assertRaises(studio.StudioError):
            studio.plan(self.base(confidence=True))

    def test_unknown_keys_and_capabilities_rejected(self):
        with self.assertRaises(studio.StudioError):
            studio.plan(self.base(unrequested_publish=True))
        with self.assertRaises(studio.StudioError):
            studio.plan(self.base(capabilities=['imaginary_tool']))

    def test_changed_constraints_invalidate_prior_work(self):
        assessment = self.base(changes=['constraints'], completed=[
            {'step': 'inspect_context', 'evidence': 'Inspected the old context'},
            {'step': 'extract_insight', 'evidence': 'Old insight'},
            {'step': 'generate_concepts', 'evidence': 'Old board'}])
        states = {s['id']: s['state'] for s in studio.plan(assessment)['steps']}
        self.assertNotEqual(states['generate_concepts'], 'done')

    def test_receipt_cannot_bypass_missing_dependency(self):
        assessment = self.base(completed=[{'step': 'generate_concepts', 'evidence': 'Prior draft'}])
        states = {s['id']: s['state'] for s in studio.plan(assessment)['steps']}
        self.assertNotEqual(states['generate_concepts'], 'done')

    def test_valid_receipts_make_next_step_ready(self):
        assessment = self.base(completed=[
            {'step': 'inspect_context', 'evidence': 'Inspected current source'},
            {'step': 'extract_insight', 'evidence': 'Confirmed insight still fits'}])
        states = {s['id']: s['state'] for s in studio.plan(assessment)['steps']}
        self.assertEqual(states['generate_concepts'], 'ready')

    def test_mixed_requires_capabilities(self):
        with self.assertRaises(studio.StudioError):
            studio.plan(self.base(actions=['produce'], deliverable='mixed'))


def make_case_test(case):
    def test(self):
        result = studio.plan(case['assessment'])
        ids = [s['id'] for s in result['steps']]
        for expected in case['includes']:
            self.assertIn(expected, ids)
        for forbidden in case['excludes']:
            self.assertNotIn(forbidden, ids)
        seen = set()
        for step in result['steps']:
            self.assertTrue(set(step['depends_on']) <= seen)
            self.assertNotIn(step['id'], seen)
            seen.add(step['id'])
        self.assertFalse(result['execution_complete'])
    return test


for case in CASES:
    setattr(RoutingTests, 'test_route_' + case['id'], make_case_test(case))


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.test_root = ROOT / 'test-runs'
        self.temp = self.test_root / uuid.uuid4().hex
        self.temp.mkdir(parents=True)
        self.path = self.temp / 'project.json'
        studio.init_project(self.path, 'Creative project')

    def tearDown(self):
        target = self.temp.resolve()
        self.assertTrue(target.is_relative_to(self.test_root.resolve()))
        self.assertNotEqual(target, self.test_root.resolve())
        shutil.rmtree(target)

    def append(self, event):
        revision = studio.read_json(self.path)['revision']
        return studio.record_event(self.path, revision, event)

    def candidate(self, name='A'):
        return self.append({'type': 'candidate', 'id': name, 'text': 'Concept ' + name})

    def test_init_refuses_to_overwrite(self):
        before = self.path.read_bytes()
        with self.assertRaises(studio.StudioError):
            studio.init_project(self.path, 'Replacement')
        self.assertEqual(before, self.path.read_bytes())

    def test_multiple_approvals_are_preserved(self):
        self.candidate('A')
        self.candidate('B')
        self.append({'type': 'approve', 'target_id': 'A', 'evidence': 'User approved both'})
        view = self.append({'type': 'approve', 'target_id': 'B', 'evidence': 'User approved both'})
        self.assertEqual([i['status'] for i in view['items'].values()], ['approved', 'approved'])

    def test_stale_revision_cannot_overwrite(self):
        self.candidate()
        before = self.path.read_bytes()
        with self.assertRaises(studio.StudioError):
            studio.record_event(self.path, 0, {'type': 'note', 'text': 'Stale write'})
        self.assertEqual(before, self.path.read_bytes())

    def test_approved_item_requires_explicit_supersede(self):
        self.candidate()
        self.append({'type': 'approve', 'target_id': 'A', 'evidence': 'User: approved'})
        before = self.path.read_bytes()
        with self.assertRaises(studio.StudioError):
            self.append({'type': 'reject', 'target_id': 'A', 'evidence': 'Assistant dislikes it'})
        self.assertEqual(before, self.path.read_bytes())
        self.candidate('B')
        view = self.append({'type': 'supersede', 'target_id': 'A', 'replacement_id': 'B', 'evidence': 'User: replace A with B'})
        self.assertEqual(view['items']['A']['status'], 'superseded')
        self.assertEqual(view['items']['B']['status'], 'approved')
        self.assertEqual(len(studio.read_json(self.path)['events']), 4)

    def test_rejection_reason_stays_unknown(self):
        self.candidate()
        view = self.append({'type': 'reject', 'target_id': 'A', 'evidence': 'User: no'})
        self.assertIsNone(view['items']['A']['reason'])
        self.assertIn('not supplied', studio.markdown(view))

    def test_existing_lock_is_not_removed(self):
        lock = self.path.with_name(self.path.name + '.lock')
        lock.write_text('other writer', encoding='utf-8')
        with self.assertRaises(studio.StudioError):
            self.candidate()
        self.assertEqual(lock.read_text(encoding='utf-8'), 'other writer')

    def test_invalid_history_rejected(self):
        data = studio.read_json(self.path)
        data['revision'] = 99
        with self.assertRaises(studio.StudioError):
            studio.project_view(data)

    def test_unknown_target_rejected_without_write(self):
        before = self.path.read_bytes()
        with self.assertRaises(studio.StudioError):
            self.append({'type': 'approve', 'target_id': 'missing', 'evidence': 'User approval'})
        self.assertEqual(before, self.path.read_bytes())

    def test_duplicate_candidate_id_rejected(self):
        self.candidate()
        with self.assertRaises(studio.StudioError):
            self.candidate()

    def test_unicode_and_literal_shell_text_roundtrip(self):
        text = 'Caf\u00e9: $(not-a-command) `literal` <tag>'
        view = self.append({'type': 'note', 'text': text})
        self.assertEqual(view['notes'], [text])
        self.assertEqual(studio.project_view(studio.read_json(self.path))['notes'], [text])

    def test_cli_roundtrip_and_invalid_exit(self):
        event = self.path.parent / 'event.json'
        event.write_text(json.dumps({'type': 'brief', 'text': 'Build a distinct creative studio'}), encoding='utf-8')
        result = subprocess.run([sys.executable, str(SCRIPT), 'record', '--file', str(self.path),
                                 '--expected-revision', '0', '--event', str(event)], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['revision'], 1)
        result = subprocess.run([sys.executable, str(SCRIPT), 'validate', '--file', str(self.path)], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(json.loads(result.stdout), {'valid': True, 'revision': 1})
        result = subprocess.run([sys.executable, str(SCRIPT), 'record', '--file', str(self.path),
                                 '--expected-revision', '0', '--event', str(event)], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Revision conflict', json.loads(result.stderr)['error'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
