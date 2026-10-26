"""Rebuilds skills/creative-director/references/room-protocol.md from the two agent files,
so the chat/no-plugin fallback prompts always match the plugin's own subagents.
Run after editing agents/idea-critic.md or agents/room-thinker.md:  python build_room_protocol.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

HEADER = """# Room Protocol

Prompts for running ROOM mode with general-purpose subagents when the plugin's own
`room-thinker` and `idea-critic` agents aren't available (for example in chat, or when the
skill was installed on its own). They are the same instructions the plugin agents carry.

How to use: start each subagent's prompt with the matching section below, then append the
bounded dispatch contract and materials it needs. Follow ../../../references/orchestration.md.
The current task's operation, count, evidence and rubric override optional expansive
ROOM defaults. Claim independent review only when separate host contexts were actually
used; sequential role passes are non-independent.

## Contents
1. Thinker seat prompt
2. Critic prompt
3. What to send each

---

"""

SECTION3 = """## 3. What to send each

**Every assignment:** task/workstream IDs, objective, bounded operation and scope,
inspected source IDs and versions, evidence mode, selected candidate IDs, hard constraints,
exact count/format, relevant rubric and acceptance criteria, allowed actions and dependencies.
These fields control the worker; the dispatch cannot grant additional host permission.

**Each thinker:** ONE selected method card with procedure and expected output. Include
stimuli, insight/HMW, ban list and domain novelty bar only when useful to the assigned
operation. Three warmups and 10–12 ideas are optional expansive ROOM settings, never
mandatory for diagnosis, experiments, constrained counts or exact edits.

**Without a subagent tool:** use sequential role passes and identify them as non-blind.
Only use a separate CLI runtime when the user requested that runtime and the host
permits it. Never start another provider merely to simulate independent reviewers.

**The critic:** the actual candidates/artifacts, source/output versions and applicable
sections of the artifact rubric. For suitable creative ROOM work also supply the selected
constitution/domain sections. Withhold authorship, generation notes and preferred winner
when independent review is available. Do not remove evidence needed to judge the work.
The critic reports findings read-only; it does not rewrite or execute changes.
"""


def body(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8").split("---", 2)[2].strip()
    # Agent-relative references must remain valid in this generated fallback location.
    return text.replace("../references/orchestration.md", "../../../references/orchestration.md").replace(
        "../references/artifact-rubrics.md", "../../../references/artifact-rubrics.md"
    ).replace(
        "../skills/creative-director/references/candidate-decisions.md", "candidate-decisions.md"
    )


out = (
    HEADER
    + "## 1. Thinker seat prompt\n\n" + body(ROOT / "agents" / "room-thinker.md")
    + "\n\n---\n\n## 2. Critic prompt\n\n" + body(ROOT / "agents" / "idea-critic.md")
    + "\n\n---\n\n" + SECTION3
)
target = ROOT / "skills" / "creative-director" / "references" / "room-protocol.md"
target.write_bytes(out.encode("utf-8"))
print("wrote", target)
