"""Structural package graph checks. These do not measure model compliance."""
import ast
import json
import re
from pathlib import Path
import unittest
import shutil
import tempfile
from urllib.parse import unquote, urlsplit

PLUGIN=Path(__file__).resolve().parents[1]/'plugins/idea-man'
PATH=re.compile(r'(?<![A-Za-z0-9_:/])((?:\.\.?/|references/|scripts/|skills/|agents/|examples/)[A-Za-z0-9_./-]+\.(?:md|json|py))')
LINK=re.compile(r'\[[^]\n]*\]\(([^)\s]+)(?:\s+[^)]*)?\)')

def edges(root):
    graph, failures={},[]
    for doc in root.rglob('*.md'):
        text=doc.read_text(encoding='utf-8-sig')
        targets=set(PATH.findall(text))
        targets.update(t for t in LINK.findall(text) if not urlsplit(t).scheme and not t.startswith('#'))
        graph[doc.resolve()]=set()
        for target in sorted(targets):
            local=unquote(target.split('#',1)[0])
            base=doc.parent
            # Bare references/scripts paths follow the documented skill-root convention.
            if local.startswith(('references/','scripts/')):
                skill=next((a for a in doc.parents if a.parent.name=='skills'),None)
                base=skill or root
            elif local.startswith(('skills/','agents/')):
                base=root
            resolved=(base/local).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                failures.append((doc.relative_to(root).as_posix(),target))
            else: graph[doc.resolve()].add(resolved)
    registry=root/'references/innovation-registry.json'
    data=json.loads(registry.read_text(encoding='utf-8'))
    graph[registry.resolve()]=set()
    for entry in [*data['specialists'].values(),*data['methods'].values()]:
        target=entry.get('path',entry.get('reference'))
        resolved=(root/target).resolve()
        if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
            failures.append((registry.relative_to(root).as_posix(),target))
        else: graph[registry.resolve()].add(resolved)
    return graph,failures

def reachable(graph,starts):
    seen,pending=set(),list(starts)
    while pending:
        node=pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(graph.get(node,()))
    return seen

class ReferenceIntegrityTests(unittest.TestCase):
    def test_authored_relative_links_resolve_inside_package(self):
        _,failures=edges(PLUGIN)
        self.assertEqual(failures,[],'Unresolvable packaged links: '+repr(failures))

    def test_every_reference_reachable_from_registered_skills(self):
        graph,_=edges(PLUGIN)
        registry=json.loads((PLUGIN/'references/innovation-registry.json').read_text(encoding='utf-8'))
        reached=reachable(graph,[(PLUGIN/e['path']).resolve() for e in registry['specialists'].values()])
        refs={p.resolve() for p in PLUGIN.rglob('*') if p.is_file()
              and 'references' in p.relative_to(PLUGIN).parts and p.suffix in {'.md','.json'}}
        self.assertEqual(sorted(str(p.relative_to(PLUGIN)) for p in refs-reached),[],
                         'References need reachable authored links, not package presence alone')

    def test_validator_detects_removed_reference_and_unlinked_import(self):
        # Perturb a copy: prove graph checks catch broken wiring without editing owner files.
        with tempfile.TemporaryDirectory(prefix='idea-man-reference-check-') as directory:
            package=Path(directory)/'plugin'
            shutil.copytree(PLUGIN,package)
            target=package/'skills/creative-director/references/supplementary-methods.md'
            target.unlink()
            _,failures=edges(package)
            self.assertTrue(any('supplementary-methods.md' in path for _,path in failures))
            orphan=package/'references/unlinked-procedure.md'
            orphan.write_text('# Unlinked procedure',encoding='utf-8')
            graph,_=edges(package)
            registry=json.loads((package/'references/innovation-registry.json').read_text(encoding='utf-8'))
            reached=reachable(graph,[(package/e['path']).resolve() for e in registry['specialists'].values()])
            self.assertNotIn(orphan.resolve(),reached)

    def test_packaged_router_is_imported_by_cli(self):
        script=PLUGIN/'skills/creative-director/scripts/studio.py'
        imports=set()
        for node in ast.walk(ast.parse(script.read_text(encoding='utf-8-sig'))):
            if isinstance(node,ast.Import): imports.update(n.name for n in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module: imports.add(node.module)
        self.assertIn('router_v2',imports)
        self.assertTrue((script.parent/'router_v2.py').is_file())

if __name__=='__main__': unittest.main()
