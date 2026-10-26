"""Safe local fault injection for planning evidence and dependency recovery."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_router_v2 import assessment, router

ROOT = Path(__file__).resolve().parents[1]


def step(plan, key):
    return next(row for row in plan['steps'] if row['id'] == key)


class RoutingRecoveryTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.file = self.folder / 'source.txt'
        self.file.write_text('Authoritative input and inspection evidence.', encoding='utf-8')

    def file_source(self):
        return {'id': 'source', 'kind': 'file', 'locator': str(self.file),
                'revision': router.file_hash(self.file), 'status': 'available', 'inspected': True}

    @staticmethod
    def portfolio(a):
        return {'schema_version': 2, 'workstreams': [
            {'assessment': a, 'depends_on': []},
            {'assessment': assessment(task_id='independent', actions=['status']), 'depends_on': []}]}

    def test_unreadable_source_blocks_only_its_branch_and_recovers(self):
        a = assessment(task_id='dependent-source', actions=['review'], sources=[self.file_source()])
        original = router.file_hash
        def unavailable(path):
            if Path(path) == self.file:
                raise PermissionError('simulated temporary file lock')
            return original(path)
        with patch.object(router, 'file_hash', side_effect=unavailable):
            failed = router.plan_v2(self.portfolio(a))
        affected = failed['workstreams']['dependent-source']
        source = affected['sources'][0]
        self.assertEqual(source['status'], 'available', 'Unreadable is not proof of absence')
        self.assertFalse(source['inspected'])
        self.assertEqual(source['observation_error'], 'PermissionError')
        self.assertEqual(step(affected, 'resolve_source')['state'], 'unavailable')
        self.assertEqual(step(failed['workstreams']['independent'], 'inspect_context')['state'], 'ready')
        recovered = router.plan_v2(self.portfolio(a))
        self.assertNotIn('resolve_source', {row['id'] for row in recovered['workstreams']['dependent-source']['steps']})
        self.assertEqual(recovered['workstreams']['dependent-source']['sources'][0]['revision'], original(self.file))
        self.assertEqual(step(recovered['workstreams']['independent'], 'inspect_context')['state'], 'ready')

    def test_unreadable_receipt_is_not_done_and_independent_branch_survives(self):
        a = assessment(task_id='evidence', actions=['status'])
        first = router.plan_v2(a)
        a['receipts'] = [{'step': 'inspect_context', 'binding': step(first, 'inspect_context')['input_binding'],
                          'evidence': 'Read the current task.', 'output': {'kind': 'file',
                          'locator': str(self.file), 'revision': router.file_hash(self.file)}}]
        self.assertEqual(step(router.plan_v2(a), 'inspect_context')['state'], 'done')
        with patch.object(router, 'file_hash', side_effect=PermissionError('simulated temporary evidence lock')):
            failed = router.plan_v2(self.portfolio(a))
        self.assertEqual(step(failed['workstreams']['evidence'], 'inspect_context')['state'], 'ready')
        self.assertEqual(step(failed['workstreams']['independent'], 'inspect_context')['state'], 'ready')
        self.assertEqual(step(router.plan_v2(a), 'inspect_context')['state'], 'done')

    def test_snapshot_digest_and_parse_use_one_identical_buffer(self):
        snapshot = {'version': 1, 'assessment': assessment(actions=['revise'], sources=[self.file_source()]),
                    'source_id': 'source', 'binding': 'inspected-binding', 'task_id': None}
        original = json.dumps(snapshot).encode('utf-8')
        changed = copy.deepcopy(snapshot)
        changed['assessment']['objective'] = 'A different task from different bytes'
        changed_bytes = json.dumps(changed).encode('utf-8')
        target = self.folder / 'simulated-snapshot.json'
        target.write_bytes(original)
        with patch.object(Path, 'read_bytes', return_value=changed_bytes):
            with self.assertRaisesRegex(ValueError, 'snapshot changed'):
                router.load_snapshot(target, hashlib.sha256(original).hexdigest())
        # A simulated replacement at a hypothetical second text read must not
        # substitute a different task after the digest was checked.
        original_read_text = Path.read_text
        second_reads = []
        def swapped_snapshot(path, *args, **kwargs):
            if path == target:
                second_reads.append(path)
                return changed_bytes.decode('utf-8')
            return original_read_text(path, *args, **kwargs)
        with patch.object(Path, 'read_bytes', return_value=original) as read, \
                patch.object(Path, 'read_text', new=swapped_snapshot):
            loaded = router.load_snapshot(target, hashlib.sha256(original).hexdigest())
        self.assertEqual(loaded, snapshot)
        self.assertEqual(read.call_count, 1)
        self.assertEqual(second_reads, [])

    def test_long_dependency_chain_and_deep_cycle_do_not_depend_on_python_recursion(self):
        count = 1100
        streams = [{'assessment': assessment(task_id='task-'+str(index), actions=['status']),
                    'depends_on': ['task-'+str(index-1)] if index else []}
                   for index in reversed(range(count))]
        envelope = {'schema_version': 2, 'workstreams': streams}
        plan = router.plan_v2(envelope)
        self.assertEqual(list(plan['workstreams'])[0], 'task-0')
        self.assertEqual(list(plan['workstreams'])[-1], 'task-1099')
        self.assertEqual(step(plan['workstreams']['task-0'], 'inspect_context')['state'], 'ready')
        self.assertEqual(step(plan['workstreams']['task-1099'], 'inspect_context')['state'], 'waiting')
        streams[-1]['depends_on'] = ['task-1099']
        with self.assertRaisesRegex(ValueError, 'Cyclic workstream dependencies'):
            router.plan_v2(envelope)


if __name__ == '__main__':
    unittest.main()
