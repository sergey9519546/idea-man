"""Real local record conflicts/retries and injected pre-commit I/O failures.

These checks establish local state preservation, not model behavior or external
transaction guarantees. All writes are confined to test-owned temporary files.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'
SPEC = importlib.util.spec_from_file_location('studio_recovery', SCRIPT)
studio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(studio)


class RecordRecoveryBoundaryTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.record = self.folder / 'project.json'
        self.environment = dict(os.environ, TEMP=str(self.folder), TMP=str(self.folder))
        studio.init_project(self.record, 'Recovery boundary checks')

    def call(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                              capture_output=True, text=True, encoding='utf-8',
                              env=self.environment, timeout=20)

    def event_file(self, name, text):
        path = self.folder / (name + '.json')
        path.write_text(json.dumps({'type': 'note', 'text': text}), encoding='utf-8')
        return path

    def test_two_process_writers_conflict_then_reconcile_without_lost_work(self):
        inputs = [self.event_file('a', 'First authorized note'),
                  self.event_file('b', 'Second authorized note')]
        processes = []
        try:
            for path in inputs:
                processes.append(subprocess.Popen(
                    [sys.executable, str(SCRIPT), 'record', '--file', str(self.record),
                     '--expected-revision', '0', '--event', str(path)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    encoding='utf-8', env=self.environment))
            outputs = [process.communicate(timeout=20) for process in processes]
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
        self.assertEqual(sorted(process.returncode for process in processes), [0, 2])
        loser = next(i for i, process in enumerate(processes) if process.returncode == 2)
        error = json.loads(outputs[loser][1])['error']
        self.assertTrue('locked' in error.lower() or 'Revision conflict' in error, error)
        current = studio.project_view(studio.read_json(self.record))
        self.assertEqual(current['revision'], 1)
        self.assertEqual(len(current['notes']), 1)
        retry = self.call('record', '--file', self.record, '--expected-revision', '1',
                          '--event', inputs[loser])
        self.assertEqual(retry.returncode, 0, retry.stderr)
        current = json.loads(retry.stdout)
        self.assertEqual(current['revision'], 2)
        self.assertCountEqual(current['notes'], ['First authorized note', 'Second authorized note'])
        self.assertFalse(self.record.with_name(self.record.name + '.lock').exists())

    def test_failed_replace_preserves_bytes_releases_lock_and_can_retry(self):
        before = self.record.read_bytes()
        event = {'type': 'note', 'text': 'Preserve the approved branch'}
        with patch.object(studio.os, 'replace', side_effect=PermissionError('injected pre-commit failure')):
            with self.assertRaises(PermissionError):
                studio.record_event(self.record, 0, event)
        self.assertEqual(self.record.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in self.folder.iterdir()), ['project.json'])
        current = studio.record_event(self.record, 0, event)
        self.assertEqual(current['revision'], 1)
        self.assertEqual(current['notes'], [event['text']])

    def test_retry_with_old_revision_cannot_duplicate_a_committed_note(self):
        event = self.event_file('retry', 'Already committed note')
        first = self.call('record', '--file', self.record, '--expected-revision', '0', '--event', event)
        self.assertEqual(first.returncode, 0, first.stderr)
        committed = self.record.read_bytes()
        retry = self.call('record', '--file', self.record, '--expected-revision', '0', '--event', event)
        self.assertEqual(retry.returncode, 2)
        self.assertIn('Revision conflict', json.loads(retry.stderr)['error'])
        self.assertEqual(self.record.read_bytes(), committed)
        current = studio.project_view(studio.read_json(self.record))
        self.assertEqual(current['revision'], 1)
        self.assertEqual(current['notes'], ['Already committed note'])

    def test_corrupt_record_is_not_reset_or_rewritten_by_a_failed_append(self):
        self.record.write_text('{"schema_version":1,"revision":', encoding='utf-8')
        corrupt = self.record.read_bytes()
        event = self.event_file('valid-event', 'Do not erase existing history')
        result = self.call('record', '--file', self.record, '--expected-revision', '0', '--event', event)
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stderr))
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.record.read_bytes(), corrupt)
        self.assertFalse(self.record.with_name(self.record.name + '.lock').exists())

    def test_interrupted_writer_preserves_record_and_known_abandoned_lock_can_recover(self):
        before = self.record.read_bytes()
        ready = self.folder / 'writer-ready'
        child = (
            "import importlib.util,pathlib,sys,time\n"
            "spec=importlib.util.spec_from_file_location('writer',sys.argv[1])\n"
            "module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)\n"
            "with module.locked(pathlib.Path(sys.argv[2])):\n"
            " pathlib.Path(sys.argv[3]).write_text('locked',encoding='utf-8')\n"
            " time.sleep(30)\n"
        )
        process = subprocess.Popen([sys.executable, '-c', child, str(SCRIPT),
                                    str(self.record), str(ready)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env=self.environment)
        try:
            deadline = time.monotonic() + 10
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), 'Test writer did not reach its lock boundary')
            self.assertIsNone(process.poll())
            process.kill()
            process.communicate(timeout=10)
            self.assertIsNotNone(process.returncode)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=10)
        lock = self.record.with_name(self.record.name + '.lock')
        self.assertEqual(self.record.read_bytes(), before)
        self.assertTrue(lock.exists(), 'Abrupt termination must not be mistaken for ordinary cleanup')
        event = self.event_file('recovered-event', 'Recovered after interrupted writer')
        blocked = self.call('record', '--file', self.record, '--expected-revision', '0', '--event', event)
        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(self.record.read_bytes(), before)
        self.assertTrue(lock.exists(), 'A retry must preserve a lock of unknown ownership')
        # Only this test owns the record and the terminated process. It can prove
        # there is no live writer; production must not infer that from lock age/PID.
        self.assertEqual(studio.project_view(studio.read_json(self.record))['revision'], 0)
        lock.unlink()
        retry = self.call('record', '--file', self.record, '--expected-revision', '0', '--event', event)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        current = json.loads(retry.stdout)
        self.assertEqual(current['revision'], 1)
        self.assertEqual(current['notes'], ['Recovered after interrupted writer'])
        self.assertFalse(lock.exists())


if __name__ == '__main__':
    unittest.main()
