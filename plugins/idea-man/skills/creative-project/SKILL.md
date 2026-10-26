---
name: creative-project
description: "Save, resume and manage a project's brief, constraints, candidates, approvals, rejections and next steps in a portable local record. Use when asked to remember decisions, continue later or track project history across engineering, research, business, learning and creative work."
---

# Project continuity

Apply ../creative-director/references/studio-router.md and
../creative-director/references/studio-protocol.md.

In ordinary chat, track the active objective, approved elements, current source and
feedback in context. Do not claim durable memory. Write a local project record only
when asked to save/remember/resume, or when a record workflow is already established.
Never modify global agent memories, installed plugin caches or other project records.

## Task anchor and working checkpoint

Continuity comes from the context the host actually supplies, or an explicitly
loaded record. This plugin does not read a hidden chat cache, guarantee that all
earlier turns survive compaction, or automatically remember a future session.

Separate the user-grounded task anchor from the changing work state:
- Anchor: project identity, desired outcome, assigned role and limits, explicit
  constraints, selection and action authority, with their user/source evidence.
- Working checkpoint: current inputs and versions, facts versus assumptions,
  accepted results, scoped corrections/rejections, pending work and the next action.

An anchor resists accidental drift, not authorized change. A new user instruction
can change the goal, selection or limits; update only the affected fields and retain
the relevant decision history. A specialist's persona, evolving self-description
or generated recap cannot grant permission, select an option or overwrite explicit
user evidence. Never use a personality file as a substitute for that evidence.

Keep this state in context for ordinary short work. At a handoff, interruption or
loss of relevant history, use a compact recap that preserves the actual selected
mechanism and any details needed to continue. Reconcile it against available user
instructions and current artifacts; generated summaries can omit or distort facts.
If the required history is absent, identify the specific missing decision instead
of inventing continuity. Avoid a mandatory state dump or file write on each turn.

Before delivering a handoff or replacing a checkpoint, compare it with the current
task anchor and subsequent user amendments. Check that every still-active hard
limit, tool/data restriction and authorization boundary survives with its original
scope. Omission from a newer summary is not withdrawal. Carry explicit changes
forward; keep superseded values labeled with their historical task or run. Preserve
which work is active, parked, completed or canceled, rather than inventing pending
work to fill a next-action field.

Keep user/project constraints distinct from session/host restrictions and observed
capabilities; label the latter with their source and session scope when relevant to
the handoff. On resume, recheck current capabilities and applicable host restrictions.
Do not turn temporary limits into enduring user decisions. Rechecking does not revoke
still-applicable user authorization or grant permission from tool availability; all
currently applicable restrictions continue to govern.

Compress repeated narrative and completed-work detail before these invariants.
Keep enough of each retained option's mechanism to distinguish it from the others;
an ID or persona label alone may not support continuation. Under a tight length
limit, check the compressed result again against the protected constraints. If a
necessary detail cannot fit, identify the incomplete part and an accessible source
instead of presenting a lossy recap as sufficient. On receipt, reconcile the anchor
and checkpoint: a missing restriction cannot grant permission, and a missing anchor
cannot be reconstructed by guessing. This check is for continuity boundaries, not
an extra visible checklist or mandatory memory write during ordinary answers.

Use the existing authorized project-record workflow below when persistence is
requested. A session-only file is not inherently private or temporary: if one is
requested, agree its project-owned location and lifetime, minimize sensitive data,
and do not claim automatic expiration or delete it without authority. Without a
save request, provide a reusable unsaved recap rather than creating a memory file.

Use ../creative-director/scripts/studio.py (standard-library Python) and the event
contract in ../creative-director/references/project-record.md:
- init creates a NEW record without overwriting.
- show reconstructs current decisions from the event history.
- record appends one validated event with a required expected revision.
- validate checks a record without modifying it.
- export prints a portable Markdown recap.

Use an explicit project-owned destination. Save event JSON to a temporary project file
and pass --event; do not interpolate user text into shell commands. No code environment:
give the user a structured recap they can save, clearly labeled not persisted.

Only approve from explicit user evidence. Record a rejection with an unknown reason as
unknown. An approved choice or constraint remains active until an explicit supersede
event selects a replacement or withdraw records the user's removal of approval without
a replacement. Withdraw only the named approved item; retain other approvals and history.
Do not interpret a narrow correction as withdrawal or fabricate a replacement. Later
reapproval needs fresh user evidence. A record is an audit of supplied decisions, not
proof those decisions were good or that an external action occurred. Records containing
withdraw events require the updated helper; never remove history for an older reader.

On resume, read the record and inspect cited artifacts; verify current tool/account/repo
state where it matters. Missing sources and stale observations stay unverified. Continue
the outstanding objective instead of restarting discovery.

The record has revision conflict checks and atomic writes. On conflict re-read and
reconcile; never overwrite an intervening event. On an existing lock, report it and do
not delete a possible active writer's lock. Records are local, not synced across chats.

## Innovation integration

Apply ../creative-learning/SKILL.md when feedback creates a scoped preference. Store structured preferences as supported note events. On resume inspect the record, sources and preferences, reconstruct structured pending actions, and feed a v2 continuity checkpoint into the planner. Continue authorized unfinished work, not only a recap.

## Structured checkpoint and resume

For an authorized save of unfinished work, record a checkpoint event containing one
validated v2 assessment, nonempty pending_actions and concise evidence; use the exact
contract in ../creative-director/references/project-record.md. File locators must be
absolute. Store the minimum task contract and evidence pointers, not raw transcripts.
Portfolio checkpoints are unsupported; preserve separate records rather than flattening
dependencies.

Use studio.py resume --file <record.json> to get a read-only packet. Its
resume_assessment is an unverified draft, with current capabilities/receipts cleared,
source inspection false and selection authority withheld. Pass it to the planner only
as a restore checkpoint request. Read the historical checkpoint and current decisions;
reinspect sources, objective, scoped preferences and actual tools before supplying a
fresh substantive assessment. Never flip source_rechecked merely because a hash matches.
After any intervening record event, reconcile decisions and save a new checkpoint;
resume deliberately withholds an obsolete draft. Old records remain supported and
report the missing checkpoint rather than inventing pending actions.

Reconcile still-current explicit user decisions from the historical record; this does
not require asking for approval again. Preserve existing authorization when inspection
confirms its scope still applies. Saved choice authority is withheld in the draft to
require this reconciliation, not to revoke the user's instruction.
