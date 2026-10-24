# Specialist and tool orchestration

The conductor owns the active objective and acceptance criteria. The
[recognition playbook](recognition-playbook.md) decides the assignment;
[innovation-registry.json](innovation-registry.json) resolves packaged specialists
and thinking procedures. Specialists do not independently redefine the task.

## Connect the work

1. Select a primary specialist and only the shared services needed now. Load its
   actual SKILL.md. Research, quality review and scoped learning are conditional
   services, not mandatory steps for every task.
2. For complex work, follow
   [router-schema-v2.md](../skills/creative-director/references/router-schema-v2.md)
   and run `skills/creative-director/scripts/studio.py plan --assessment <file.json>`
   from the plugin root. The host supplies semantic interpretation; the planner
   validates contracts, dependencies and completion receipts. It does not call providers.
3. Execute ready work with available host tools. Dispatch another agent only when
   host rules and user scope permit delegation and a separate context is useful.
   Independent branches may run together; dependent branches wait for inspected,
   accepted upstream results. One blocker does not stop unrelated ready work.
4. Give each worker bounded scope and one owner per mutable artifact. Do not assign
   concurrent overwrites. Preserve other contributors' edits. Exact edits bypass
   brainstorming; review-only work cannot produce changes.

## Compact dispatch contract

This is a handoff envelope, not a new input format for studio.py. Send only relevant
material and retain exact values from the assessed task:

| Field | Required meaning |
|---|---|
| Identity | Task and workstream/step IDs, active objective and requested outcome |
| Assignment | Operation, bounded scope, specialist and method card when needed |
| Inputs | Inspected source IDs/locators, versions, selected candidates and evidence mode |
| Invariants | Hard constraints, approved properties, exclusions and exact feedback scope |
| Output | Exact count/format and target artifact ownership if edits are assigned |
| Acceptance | Relevant rubric, checks, decisive unknowns and completion conditions |
| Authority | Allowed actions and available tools; host and user restrictions still govern |
| Dependencies | Accepted upstream outputs/versions and unresolved blocking inputs |

Copy the selected method's procedure and expected output, not just a thinker name.
Use [room-thinker.md](../agents/room-thinker.md) for method work and
[idea-critic.md](../agents/idea-critic.md) for read-only review. Their assignments
override legacy ROOM volume and scoring defaults. Supply relevant rubric sections
instead of applying a creative advertising rubric to every domain.

## Tool and connection boundaries

Discover actual tools through the host's supported discovery mechanism and inspect
their schemas. Prefer suitable purpose-built connectors where available. Resolve
real source and destination identifiers before action. Discovery is not authorization;
carry the same scope and allowed actions through every handoff.

This package supplies skills, references and a local planner. It does not supply
an external MCP server, credentials, subscriptions or a background dispatcher.
Do not invent connection declarations or claim a service is connected because a
workflow mentions it. Use verified connections. If a capability is absent, identify
the blocked operation and finish independent work or a useful handoff. A prompt
pack is prepared work, not a rendered image or executed deployment.

Without a subagent tool, use sequential role passes where useful and label them
non-independent. The generated
[room protocol](../skills/creative-director/references/room-protocol.md)
supplies matching prompts. Do not launch another CLI/provider solely to simulate
independent review. Independent review requires separate context and host support.

## Accept results and continue

Require the worker's task/step ID, actual output or analysis, source/output versions,
checks performed and unresolved limits. Inspect results with
[artifact-quality](../skills/artifact-quality/SKILL.md); a worker's success claim is not
proof. Return focused corrections to the responsible step when acceptance fails.
Do not restart already accepted unrelated work.

Use the existing source/output-bound receipt workflow for completed executable steps.
Changed inputs, constraints or upstream outputs invalidate affected receipts; replan
before releasing dependent work. Context or remote material needs reinspection.
Persist only through an authorized
[creative-project](../skills/creative-project/SKILL.md) workflow.
Distinguish proposed, produced, inspected, tested and published results.
