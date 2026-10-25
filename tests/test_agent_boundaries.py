"""Native specialist declarations must not inherit mutation-capable tools."""
from pathlib import Path
import re
import unittest

PLUGIN=Path(__file__).resolve().parents[1]/'plugins/idea-man'
INSPECTION_TOOLS={'Read','Grep','Glob','WebFetch','WebSearch'}
AGENTS=('idea-critic','room-thinker')

class NativeAgentBoundaryTests(unittest.TestCase):
    def test_native_specialists_have_explicit_inspection_allowlists(self):
        for name in AGENTS:
            with self.subTest(agent=name):
                source=(PLUGIN/'agents'/(name+'.md')).read_text(encoding='utf-8')
                self.assertTrue(source.startswith('---\n'))
                header=source.split('---',2)[1]
                matches=re.findall(r'^tools:\s*([^\n]+)$',header,re.MULTILINE)
                self.assertEqual(len(matches),1,'Omitted tools inherits every parent-available tool')
                tools=[item.strip() for item in matches[0].split(',')]
                self.assertEqual(len(tools),len(set(tools)),'Duplicate tool declarations')
                self.assertEqual(set(tools),INSPECTION_TOOLS,
                    'Specialist inspection must not inherit shell, edits, agents or action-capable MCP tools')

    def test_read_only_roles_do_not_enable_native_memory_or_action_hooks(self):
        for name in AGENTS:
            with self.subTest(agent=name):
                header=(PLUGIN/'agents'/(name+'.md')).read_text(encoding='utf-8').split('---',2)[1]
                self.assertIsNone(re.search(r'^(memory|hooks|mcpServers|permissionMode):',header,re.MULTILINE),
                    'Any native persistence, hook, server or permission-mode change needs explicit authority review')

if __name__=='__main__':
    unittest.main()
