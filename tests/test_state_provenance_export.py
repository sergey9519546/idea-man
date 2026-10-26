"""Record/readback and literal export regressions; no model or network calls."""
import copy
from html import unescape
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_studio import studio, ROOT, SCRIPT


class RenderedTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_data(self, data):
        self.text.append(data)


class StateProvenanceExportTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs' / 'state-provenance'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / 'project.json'
        studio.init_project(self.path, 'Operations project')

    def append(self, event):
        return studio.record_event(self.path, studio.read_json(self.path)['revision'], event)

    def check_supersede(self, already_approved):
        for identity in ('A', 'B', 'C'):
            self.append({'type': 'candidate', 'id': identity, 'text': 'Option ' + identity})
        for identity in ('A', 'C') + (('B',) if already_approved else ()):
            self.append({'type': 'approve', 'target_id': identity, 'evidence': 'Older approval of ' + identity})
        before = studio.read_json(self.path)
        untouched = copy.deepcopy(studio.project_view(before)['items']['C'])
        evidence = 'User: replace A with B for the current bounded pilot'
        event = {'type': 'supersede', 'target_id': 'A', 'replacement_id': 'B', 'evidence': evidence}
        returned = self.append(event)
        self.assertEqual(returned['items']['B'].get('decision_evidence'), evidence)
        self.assertEqual(returned['items']['A']['decision_evidence'], evidence)
        self.assertEqual(returned['items']['B']['status'], 'approved')
        self.assertEqual(returned['items']['C'], untouched)
        saved = studio.read_json(self.path)
        self.assertEqual(saved['events'][:-1], before['events'])
        self.assertEqual(saved['events'][-1]['event'], event)
        self.assertEqual(studio.project_view(saved), returned)
        run = subprocess.run([sys.executable, '-B', str(SCRIPT), 'resume', '--file', str(self.path)],
                             capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['project']['items']['B']['decision_evidence'], evidence)

    def test_supersede_new_replacement_has_current_approval_evidence(self):
        self.check_supersede(False)

    def test_supersede_preapproved_replacement_refreshes_current_evidence(self):
        self.check_supersede(True)

    def export_payload(self):
        payload = '![remote](https://example.invalid/pixel) [click](https://example.invalid) <img src=x> &lt;tag&gt; `code` **bold** \\ [ref]: /path\n# injected'
        self.path.unlink()
        studio.init_project(self.path, payload)
        for kind in ('brief', 'note', 'next_step'):
            self.append({'type': kind, 'text': payload})
        self.append({'type': 'candidate', 'id': payload, 'text': payload})
        self.append({'type': 'reject', 'target_id': payload, 'evidence': 'User rejection', 'reason': payload})
        self.append({'type': 'artifact', 'id': payload, 'path': payload, 'status': 'prepared'})
        from test_router_v2 import assessment
        task = assessment(actions=['develop'])
        task['objective'] = payload
        self.append({'type': 'checkpoint', 'assessment': task, 'pending_actions': ['develop'],
                     'evidence': 'User: save continuation'})
        before = self.path.read_bytes()
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'export', '--file', str(self.path)],
                                capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(studio.project_view(studio.read_json(self.path))['notes'], [payload])
        return payload.replace('\n', ' '), result.stdout

    def test_all_dynamic_export_fields_stay_literal_and_history_stays_original(self):
        payload, exported = self.export_payload()
        self.assertNotIn('![remote]', exported)
        self.assertNotIn('[click](https:', exported)
        self.assertNotIn('<img', exported)
        self.assertNotIn('\n# injected', exported)
        self.assertIn('## Decisions\n', exported)
        self.assertIn('## Continuation checkpoint\n', exported)
        # HTML entities are decoded once by a renderer. The original entity text
        # must survive as text rather than becoming markup through double parsing.
        self.assertEqual(unescape(exported).count(payload), 10)

    @unittest.skipUnless(importlib.util.find_spec('markdown'), 'Optional local Markdown renderer unavailable')
    def test_rendered_export_has_no_injected_images_links_or_formatting(self):
        import markdown
        payload, exported = self.export_payload()
        parsed = RenderedTags()
        parsed.feed(markdown.markdown(exported, extensions=['extra']))
        self.assertFalse({'a', 'img', 'script', 'code', 'strong', 'em'} & set(parsed.tags))
        self.assertEqual(parsed.tags.count('h1'), 1)
        self.assertIn('h2', parsed.tags)
        self.assertEqual(''.join(parsed.text).count(payload), 10)


if __name__ == '__main__':
    unittest.main()
