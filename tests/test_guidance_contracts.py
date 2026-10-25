"""Structural authoring contracts only; these do not test model or host behavior."""
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = Path("plugins/idea-man/skills/creative-director/references")
ACTIVE = ("studio-router.md", "creative-constitution.md", "ideation-engine.md",
          "engine-science.md", "thinker-arsenal.md", "output-templates.md", "domain-lenses.md", "insight-engine.md")

def operational_directive_violations(text):
    """Detect known operational contradictions despite an unrelated scope disclaimer.

    This is bounded authoring lint over directive families, not natural-language
    understanding or proof that a host will follow the surviving instructions.
    """
    flat = re.sub(r"\s+", " ", text)
    patterns = {
        "quota before evaluation": r"(?:set a hard quota|judge only after (?:the )?quota)",
        "early idea exclusion": r"discard the first, second",
        "insight checklist floor": r"Keep the ones that pass at least seven",
        "fixed reframing quota": r"Write \*\*three HMWs at three altitudes",

        "forced insight mining floor": r"Dig in at least (?:three|[0-9]+) before choosing",
        "unconditional insight stage": r"(?:Phase\s*2.{0,35}never skip|(?:[Aa]lways|[Mm]ust) (?:mine|find|produce) (?:an? )?insight)",
        "raw generation floor": r"(?:[Vv]olume floors:|[Ff]loors: SPARK|(?:SPARK|FULL|ROOM)\s*(?:[>=≥]+|=.{0,25}[≥>])\s*\d+\s*raw|at least \d+ raw)",
        "score-driven regeneration": r"(?:[Ii]f nothing reaches.{0,25}7.{0,25}loop|[Ll]oop (?:back |again )?until.{0,35}(?:7|seven)|FULL produced nothing.{0,5}7)",
        "unselected winner development": r"(?:[Dd]evelop the winner.{0,35}before presenting|[Dd]evelop the recommended idea into its first|[Aa]utomatically develop (?:the )?(?:winner|recommendation))",
        "fixed finalist presentation": r"(?:never more than 3|at most three finalists|[Pp]resent exactly three finalists)",
        "forced score distribution": r"(?:[Ss]tart every score from 5|[Mm]ost ideas are 4[–-]6|[Mm]ost unexecuted ideas should land between 4 and 7)",
        "hook score presentation gate": r"presentable idea needs a hook.{0,5}7",
        "unconditional action": r"(?:[Aa]lways end on an action|[Nn]ever end on .build nothing)",
    }
    violations = []
    for label, pattern in patterns.items():
        for match in re.finditer(pattern, flat):
            prefix = flat[max(0, match.start() - 30):match.start()]
            if not re.search(r"(?:do not|never|no requirement to)\s*$", prefix, re.I):
                violations.append(label)
                break
    return violations

def guidance_violations(root):
    violations = []
    texts = {name: (root / REFS / name).read_text(encoding="utf-8") for name in ACTIVE}
    router = texts["studio-router.md"]
    if not re.search(r"For complex jobs use[^\n]*router-schema-v2\.md", router):
        violations.append("complex jobs must select v2")
    if "version-1 compatibility only" not in router:
        violations.append("legacy schema must be explicitly scoped")
    banned = {
        "mandatory method quota": r"(?:at least three (?:methods|method families|different modes)|[Nn]ever use a single method)",
        "fixed warm-up exclusion": r"(?:first three ideas.{0,50}(?:warm-up|WARM-UP)|[Ww]arm up, then throw it away)",
        "score presentation exclusion": r"(?:[Bb]elow 7.{0,20}(?:do not present|doesn.t get presented)|<7 redo)",
        "award equivalence": r"(?:9\.5\+.{0,30}Grand Prix|8\.0.{0,15}8\.9.{0,30}Bronze)",
    }
    for name, text in texts.items():
        for label, pattern in banned.items():
            if re.search(pattern, text):
                violations.append(name + ": " + label)
    for name, text in texts.items():
        violations.extend(name + ": " + v for v in operational_directive_violations(text))
    constitution = texts["creative-constitution.md"]
    for authority in ("recognition-playbook.md", "scoring-calibration.md"):
        if authority not in constitution:
            violations.append("constitution missing authority: " + authority)
    for name in ("creative-constitution.md", "ideation-engine.md"):
        text = texts[name]
        if re.search(r"Never skip the insight|no adjectives|No insight, no ideas", text):
            violations.append(name + ": unconditional insight or scoring rule")
        if "exact edits" not in text or "scoring-calibration.md" not in text:
            violations.append(name + ": missing exact-edit or score scope")
    science = texts["engine-science.md"]
    start = science.index("**G5.")
    tail = science[start:science.index("**G6.", start)]
    for required in ("Optional experimental", "requested count prevails",
                     "Do not fabricate probabilities", "empirical basis"):
        if required not in tail:
            violations.append("tail exercise missing scope: " + required)
    return violations

class GuidanceContracts(unittest.TestCase):
    def test_recognition_does_not_restore_removed_engine_defaults(self):
        path = ROOT / "plugins/idea-man/references/recognition-playbook.md"
        text = path.read_text(encoding="utf-8")
        pattern = r"(?:method rule, mandatory|floors apply only|must use (?:three|3))"
        self.assertIsNone(re.search(pattern, text))
        stale = text + " The original engine method rule, mandatory floors apply only to expansive ideation."
        self.assertIsNotNone(re.search(pattern, stale))

    def test_conductor_and_strength_guidance_are_not_duplicated(self):
        main = (ROOT / "plugins/idea-man/skills/creative-director/SKILL.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## (.+)$", main, re.M)
        self.assertEqual(len(headings), len(set(headings)))
        recognition = (ROOT / "plugins/idea-man/references/recognition-playbook.md").read_text(encoding="utf-8")
        self.assertEqual(recognition.count("Before changing existing work, inspect what already succeeds"), 1)

    def test_active_reference_contracts(self):
        self.assertEqual(guidance_violations(ROOT), [])

    def test_operational_mutations_survive_scope_disclaimers(self):
        # Append bad procedures to otherwise valid copies, preserving every
        # authority header. This catches contradictions that token-presence tests miss.
        cases = (
            ("thinker-arsenal.md", "Set a hard quota (30-100); judge only after the quota.", "quota before evaluation"),
            ("thinker-arsenal.md", "discard the first, second and most obvious ideas by rule", "early idea exclusion"),
            ("insight-engine.md", "Keep the ones that pass at least seven.", "insight checklist floor"),
            ("insight-engine.md", "Write **three HMWs at three altitudes**:", "fixed reframing quota"),
            ("insight-engine.md", "Dig in at least three before choosing.", "forced insight mining floor"),
            ("ideation-engine.md", "## Phase 2 - The insight (never skip)",
             "unconditional insight stage"),
            ("engine-science.md", "Floors: SPARK >=10 raw, FULL >=20 raw.",
             "raw generation floor"),
            ("domain-lenses.md", "Generate at least 30 raw before judging.",
             "raw generation floor"),
            ("ideation-engine.md", "If nothing reaches HumanKind 7: loop back.",
             "score-driven regeneration"),
            ("ideation-engine.md", "Loop again until the strongest concept reaches seven.",
             "score-driven regeneration"),
            ("output-templates.md", "Develop the recommended idea into its first concrete version.",
             "unselected winner development"),
            ("ideation-engine.md", "Automatically develop the winner.",
             "unselected winner development"),
            ("output-templates.md", "Present exactly three finalists.",
             "fixed finalist presentation"),
            ("creative-constitution.md", "Start every score from 5.",
             "forced score distribution"),
            ("creative-constitution.md", "Most ideas are 4-6.",
             "forced score distribution"),
            ("domain-lenses.md", "A presentable idea needs a hook >=7.",
             "hook score presentation gate"),
            ("output-templates.md", "Always end on an action.",
             "unconditional action"),
        )
        for name, mutation, expected in cases:
            with self.subTest(name=name, mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                target = root / REFS
                target.mkdir(parents=True)
                for active in ACTIVE:
                    text = (ROOT / REFS / active).read_text(encoding="utf-8")
                    if active == name:
                        text += "\n" + mutation
                    (target / active).write_text(text, encoding="utf-8")
                self.assertTrue(any(expected in v for v in guidance_violations(root)),
                                guidance_violations(root))

    def test_directive_lint_distinguishes_explicit_negation(self):
        safe = ("Do not loop until a score reaches 7. "
                "Never automatically develop the winner. "
                "No requirement to present exactly three finalists.")
        self.assertEqual(operational_directive_violations(safe), [])
        # An initial disclaimer must not excuse a later contradictory instruction.
        unsafe = safe + " Loop again until a score reaches seven."
        self.assertIn("score-driven regeneration", operational_directive_violations(unsafe))

    def test_method_working_contract_keeps_operations_and_boundaries(self):
        text = (ROOT / REFS / "ideation-engine.md").read_text(encoding="utf-8")
        for operation in ("map roles", "lost function", "independent dimensions",
                          "distinguishing observation", "removal/reordering"):
            self.assertIn(operation, text)
        for boundary in ("Change-method triggers", "repeated mechanisms",
                         "outside evidence", "selected direction",
                         "Recommendation does not create approval"):
            self.assertIn(boundary, text)

    def test_mutated_copy_detects_scope_regressions(self):
        mutations = (
            ("creative-constitution.md", "Understand the goal and evidence", "Never skip the insight",
             "unconditional insight or scoring rule"),
            ("ideation-engine.md", "Describe evidence-backed strengths and weaknesses",
             "Report scores; no adjectives", "unconditional insight or scoring rule"),
            ("engine-science.md", "Do not fabricate probabilities", "Assign proposal probabilities",
             "tail exercise missing scope"),
            ("engine-science.md", "requested count prevails", "exercise count prevails",
             "tail exercise missing scope"),
        )
        for name, old, new, expected in mutations:
            with self.subTest(name=name, expected=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                target = root / REFS
                target.mkdir(parents=True)
                for active in ACTIVE:
                    text = (ROOT / REFS / active).read_text(encoding="utf-8")
                    if active == name:
                        self.assertIn(old, text)
                        text = text.replace(old, new)
                    (target / active).write_text(text, encoding="utf-8")
                self.assertTrue(any(expected in v for v in guidance_violations(root)))

    def test_mutated_copy_detects_instruction_regressions(self):
        mutations = {
            "studio-router.md": ("router-schema-v2.md and a schema_version",
                                 "router-schema.md and a schema_version", "complex jobs must select v2"),
            "creative-constitution.md": ("3. **Choose task-fit methods.**",
                                         "3. Never use a single method", "mandatory method quota"),
            "engine-science.md": ("**G1. Optional warm-up, no automatic exclusion.**",
                                  "**G1. The first three ideas are warm-up.**", "fixed warm-up exclusion"),
            "ideation-engine.md": ("**Calibration:**", "**Calibration:** 9.5+ = Grand Prix", "award equivalence"),
            "output-templates.md": ("In SPARK, compare ideas", "Below 7: do not present. In SPARK, compare ideas",
                                    "score presentation exclusion"),
        }
        for name, (old, new, expected) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                target = root / REFS
                target.mkdir(parents=True)
                for active in ACTIVE:
                    text = (ROOT / REFS / active).read_text(encoding="utf-8")
                    if active == name:
                        self.assertIn(old, text)
                        text = text.replace(old, new, 1)
                    (target / active).write_text(text, encoding="utf-8")
                self.assertTrue(any(expected in v for v in guidance_violations(root)),
                                guidance_violations(root))

if __name__ == "__main__":
    unittest.main()
