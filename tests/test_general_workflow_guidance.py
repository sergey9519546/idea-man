"""Bounded authoring lint; it does not measure host/model output quality."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]/'plugins/idea-man/skills'

def spillovers(text):
    patterns={
      'creative-only execution trigger':r'Turn selected creative work into',
      'unconditional creative review':r'For new concepts read relevant sections',
      'forced method plurality':r'For invention use several real thinking procedures',
      'forced candidate length':r'Describe each candidate in one sentence',
      'capped audit findings':r'one to three consequential weaknesses',
    }
    return [name for name,pattern in patterns.items() if re.search(pattern,text)]

class GeneralWorkflowGuidanceTests(unittest.TestCase):
    def test_active_workflows_have_no_known_scope_spillovers(self):
        for name in ['creative-review','concept-variations','execution-handoff']:
            with self.subTest(name=name):
                text=(ROOT/name/'SKILL.md').read_text(encoding='utf-8')
                self.assertEqual(spillovers(text),[])
    def test_known_spillovers_are_caught_even_after_general_scope_disclaimer(self):
        prefix='Supports business, research, engineering, learning and creative work. '
        bad=['Turn selected creative work into production instructions.',
             'For new concepts read relevant sections of the creative constitution.',
             'For invention use several real thinking procedures.',
             'Describe each candidate in one sentence.',
             'Report one to three consequential weaknesses.']
        for mutation in bad:
            with self.subTest(mutation=mutation):
                self.assertEqual(len(spillovers(prefix+mutation)),1)

if __name__=='__main__':unittest.main()
