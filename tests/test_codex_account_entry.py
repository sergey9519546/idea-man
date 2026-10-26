"""Fixture checks; all temporary fixture files stay beside this candidate."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1] / "integrations/codex-account-entry"
SPEC = importlib.util.spec_from_file_location("account_resolver", HERE / "scripts/resolve_account_conductor.py")
RESOLVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESOLVER)


def package(root, version="1.2.3", name="idea-man"):
    directory = root / version
    files = {
        ".codex-plugin/plugin.json": json.dumps({"name": name, "version": version, "skills": "./skills"}),
        "skills/creative-director/SKILL.md": "---\nname: creative-director\ndescription: Fixture conductor\n---\nFixture instructions.\n",
        "references/recognition-playbook.md": "Fixture recognition.\n",
        "skills/creative-director/references/studio-protocol.md": "Fixture continuity.\n",
    }
    for relative, content in files.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return directory


class ResolverChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="resolver-fixture-", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_unique_complete_package_returns_actual_guidance(self):
        package(self.root)
        result = RESOLVER.resolve_root(self.root)
        self.assertEqual(result["version"], "1.2.3")
        self.assertFalse(result["registration_verified"])
        self.assertEqual([r["role"] for r in result["resources"]], ["conductor", "recognition", "continuity"])
        self.assertIn("Fixture instructions.", result["resources"][0]["content"])

    def test_missing_version_fails(self):
        with self.assertRaisesRegex(RESOLVER.ResolutionError, "exactly one"):
            RESOLVER.resolve_root(self.root)

    def test_multiple_versions_fail_instead_of_selecting_highest(self):
        package(self.root, "1.2.3")
        package(self.root, "99.0.0")
        with self.assertRaisesRegex(RESOLVER.ResolutionError, "found 2"):
            RESOLVER.resolve_root(self.root)

    def test_wrong_identity_fails(self):
        package(self.root, name="other-plugin")
        with self.assertRaisesRegex(RESOLVER.ResolutionError, "manifest name"):
            RESOLVER.resolve_root(self.root)

    def test_mismatched_version_fails(self):
        directory = package(self.root)
        manifest = directory / ".codex-plugin/plugin.json"
        manifest.write_text(json.dumps({"name": "idea-man", "version": "1.2.4", "skills": "./skills"}), encoding="utf-8")
        with self.assertRaisesRegex(RESOLVER.ResolutionError, "does not match"):
            RESOLVER.resolve_root(self.root)

    def test_missing_governing_reference_fails(self):
        directory = package(self.root)
        (directory / "references/recognition-playbook.md").unlink()
        with self.assertRaisesRegex(RESOLVER.ResolutionError, "cannot be read completely"):
            RESOLVER.resolve_root(self.root)


if __name__ == "__main__":
    unittest.main()
