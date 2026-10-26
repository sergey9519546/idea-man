"""Real CLI export must retain protected checkpoint data as inert literal text."""
import copy
from html import unescape
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_router_v2 import assessment
from test_state_provenance_export import RenderedTags

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'


class CheckpointExportTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs/local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.record = self.folder / 'record.json'
        self.call('init', '--file', self.record, '--title', 'Portable checkpoint')

    def call(self, *args):
        run = subprocess.run([sys.executable, '-B', str(SCRIPT), *map(str, args)],
                             capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def append(self, event, revision=0):
        path = self.folder / 'event.json'
        path.write_text(json.dumps(event), encoding='utf-8')
        self.call('record', '--file', self.record, '--expected-revision', revision, '--event', path)

    def task(self):
        source = self.folder / 'source.txt'
        source.write_text('PRIVATE SOURCE CONTENT MUST NOT BE EXPANDED', encoding='utf-8')
        return assessment(actions=['develop'], requested_count=2,
            selection={'status': 'user', 'ids': ['pilot-A'], 'evidence': 'Develop A only; B stays parked'},
            constraints=[{'id': 'no-spend', 'kind': 'hard', 'text': 'Do not activate paid services',
                          'evidence': 'User turn 1'},
                         {'id': 'no-web', 'kind': 'hard', 'text': 'Use supplied notes only; no web',
                          'evidence': 'User turn 1'}],
            sources=[{'id': 'source-A', 'kind': 'file', 'locator': str(source), 'revision': 'saved-revision',
                      'status': 'available', 'inspected': True}],
            acceptance=['Exactly two table rows; no prose outside the table'],
            capabilities=['web'], receipts=[])

    def export(self, task):
        self.append({'type': 'checkpoint', 'assessment': task, 'pending_actions': ['develop'],
                     'evidence': 'User: save this task for continuation'})
        before = self.record.read_bytes()
        result = self.call('export', '--file', self.record)
        self.assertEqual(self.record.read_bytes(), before)
        return result

    def test_checkpoint_only_export_preserves_protected_contract_without_expanding_sources(self):
        task = self.task()
        exported = self.export(task)
        visible = unescape(exported)
        for key in ('constraints', 'selection', 'sources', 'requested_count', 'acceptance', 'evidence'):
            self.assertIn('- ' + key + ': ' + json.dumps(task[key], ensure_ascii=False, sort_keys=True), visible)
        self.assertIn('Historical checkpoint values', exported)
        self.assertIn('no saved execution authority', exported)
        self.assertNotIn('PRIVATE SOURCE CONTENT MUST NOT BE EXPANDED', exported)
        self.assertNotIn('- capabilities:', visible)
        self.assertNotIn('- receipts:', visible)
        packet = json.loads(self.call('resume', '--file', self.record))
        self.assertEqual(packet['resume_assessment']['constraints'], task['constraints'])

    def injected_export(self):
        payload = '![remote](https://example.invalid/pixel) <img src=x> &lt;tag&gt; `code` **bold**\n# injected'
        task = self.task()
        task['constraints'][0]['text'] = payload
        task['constraints'][0]['evidence'] = payload
        task['selection']['evidence'] = payload
        task['sources'][0].update(kind='provided', locator=payload, revision=payload)
        task['acceptance'] = [payload]
        task['evidence'][0]['detail'] = payload
        original = copy.deepcopy(task)
        exported = self.export(task)
        self.assertEqual(task, original)
        self.assertNotIn('![remote]', exported)
        self.assertNotIn('<img', exported)
        self.assertNotIn('\n# injected', exported)
        return exported

    def test_nested_checkpoint_values_remain_literal(self):
        self.injected_export()

    @unittest.skipUnless(importlib.util.find_spec('markdown'), 'Optional local Markdown renderer unavailable')
    def test_rendered_checkpoint_cannot_inject_images_links_or_formatting(self):
        import markdown
        parsed = RenderedTags()
        parsed.feed(markdown.markdown(self.injected_export(), extensions=['extra']))
        self.assertFalse({'a', 'img', 'script', 'code', 'strong', 'em'} & set(parsed.tags))
        self.assertEqual(parsed.tags.count('h1'), 1)

    def test_later_events_mark_exported_checkpoint_as_historical_and_stale(self):
        self.export(self.task())
        self.append({'type': 'brief', 'text': 'A newer objective requires reconciliation'}, revision=1)
        exported = self.call('export', '--file', self.record)
        self.assertIn('Record changed after this checkpoint', exported)
        self.assertIn('A newer objective requires reconciliation', unescape(exported))
        self.assertIsNone(json.loads(self.call('resume', '--file', self.record))['resume_assessment'])


if __name__ == '__main__':
    unittest.main()
