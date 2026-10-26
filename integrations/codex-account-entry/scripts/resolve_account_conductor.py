"""Read the unique cached account Idea-Man conductor; never select by version order."""

import hashlib
import json
from pathlib import Path
import sys


class ResolutionError(ValueError):
    """The account cache cannot identify one complete package safely."""


def _contained(root, path):
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ResolutionError("A package path resolves outside the account cache.") from exc
    return resolved


def resolve_root(cache_root):
    """Read only cache_root; a root argument exists for isolated fixture tests."""
    try:
        root = cache_root.resolve(strict=True)
        candidates = [p for p in root.iterdir() if p.is_dir()]
        if len(candidates) != 1:
            raise ResolutionError(
                "Expected exactly one account-cache version directory; found "
                + str(len(candidates))
                + ". Resolve the current source/version through supported host registration."
            )
        package = _contained(root, candidates[0])
        manifest_path = _contained(root, package / ".codex-plugin" / "plugin.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest.get("name") != "idea-man":
            raise ResolutionError("Account package manifest name is not idea-man.")
        version = manifest.get("version")
        if not isinstance(version, str) or version != candidates[0].name:
            raise ResolutionError("Manifest version does not match the version directory.")
        if manifest.get("skills") != "./skills":
            raise ResolutionError("Manifest does not declare the expected ./skills entry.")
        resources = []
        for role, relative in (
            ("conductor", "skills/creative-director/SKILL.md"),
            ("recognition", "references/recognition-playbook.md"),
            ("continuity", "skills/creative-director/references/studio-protocol.md"),
        ):
            path = _contained(root, package / relative)
            raw = path.read_bytes()
            content = raw.decode("utf-8-sig")
            if not content.strip():
                raise ResolutionError("Required package guidance is empty: " + relative)
            if role == "conductor":
                lines = content.replace("\r\n", "\n").splitlines()
                if not lines or lines[0] != "---":
                    raise ResolutionError("Conductor has no skill frontmatter.")
                try:
                    frontmatter = lines[1:lines.index("---", 1)]
                except ValueError as exc:
                    raise ResolutionError("Conductor skill frontmatter is incomplete.") from exc
                if "name: creative-director" not in frontmatter:
                    raise ResolutionError("Conductor skill identity does not match creative-director.")
            resources.append({
                "role": role,
                "path": str(path),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "content": content,
            })
        return {
            "status": "resolved_cached_package",
            "plugin_identity": "idea-man@created-by-me-remote",
            "version": version,
            "package_root": str(package),
            "manifest_path": str(manifest_path),
            "registration_verified": False,
            "resources": resources,
        }
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ResolutionError("Account package cannot be read completely: " + str(exc)) from exc


def main():
    if len(sys.argv) != 1:
        print(json.dumps({"status": "activation_gap", "error": "This resolver accepts no paths or version overrides."}))
        return 2
    cache_root = Path.home() / ".codex/plugins/cache/created-by-me-remote/idea-man"
    try:
        packet = resolve_root(cache_root)
    except ResolutionError as exc:
        print(json.dumps({"status": "activation_gap", "error": str(exc)}))
        return 1
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
