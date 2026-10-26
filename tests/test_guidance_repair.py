"""Generated graph regressions and bounded instruction lint, not model-quality tests."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_reference_integrity import PLUGIN, edges


class GuidanceRepairTests(unittest.TestCase):
    def test_rebuilt_fallback_has_resolving_references_and_is_repeatable(self):
        with tempfile.TemporaryDirectory(prefix='idea-man-generated-guidance-') as directory:
            root = Path(directory) / 'plugin'
            shutil.copytree(PLUGIN, root)
            target = root / 'skills/creative-director/references/room-protocol.md'
            # Remove the curated fallback: only the builder can provide the tested file.
            target.unlink()
            subprocess.run([sys.executable, '-B', str(root / 'build_room_protocol.py')],
                           cwd=root, check=True, capture_output=True)
            first = target.read_bytes()
            _, failures = edges(root)
            self.assertEqual(failures, [])
            self.assertIn(b'candidate-decisions.md', first)
            self.assertTrue((target.parent / 'candidate-decisions.md').is_file())
            subprocess.run([sys.executable, '-B', str(root / 'build_room_protocol.py')],
                           cwd=root, check=True, capture_output=True)
            self.assertEqual(first, target.read_bytes())

    def test_variation_guidance_distinguishes_refinement_from_exploration(self):
        text = (PLUGIN / 'skills/concept-variations/SKILL.md').read_text(encoding='utf-8')
        self.assertNotIn('Each alternative\n   needs a meaningful mechanism difference', text)
        self.assertIn('For refine, preserve the chosen mechanism', text)
        self.assertIn('deduplicate on the permitted variation axes', text)

    def test_method_guidance_has_no_known_unconditional_quality_shortcuts(self):
        refs = PLUGIN / 'skills/creative-director/references'
        science = (refs / 'engine-science.md').read_text(encoding='utf-8')
        arsenal = (refs / 'thinker-arsenal.md').read_text(encoding='utf-8')
        for shortcut in ['Swap order on every comparison', 'List ≥5 domains',
                         'one far probe\n  per round', 'List 20 true facts',
                         'Promote ideas solving three or more', 'keep ideas ≥3 on both',
                         'questions back to the Dreamer 2–3 times']:
            self.assertNotIn(shortcut, science + arsenal)
        self.assertIn('hypothetical customer quote', arsenal)
        self.assertIn('hypothesis generator, not causal proof', arsenal)

    def test_continuity_discovery_is_general(self):
        text = (PLUGIN / 'skills/creative-project/SKILL.md').read_text(encoding='utf-8')
        description = text.split('description:', 1)[1].split('---', 1)[0]
        self.assertNotIn("a creative project's", description)
        self.assertIn('engineering', description)


if __name__ == '__main__':
    unittest.main()
