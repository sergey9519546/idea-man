---
name: creative-project
description: "Save, resume and manage a creative project's brief, constraints, candidates, approvals, rejections and next steps in a portable local record. Use when asked to remember decisions, continue later or track a project's creative history."
---

# Project continuity

Apply ../creative-director/references/studio-router.md and
../creative-director/references/studio-protocol.md.

In ordinary chat, track the active objective, approved elements, current source and
feedback in context. Do not claim durable memory. Write a local project record only
when asked to save/remember/resume, or when a record workflow is already established.
Never modify global agent memories, installed plugin caches or other project records.

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
unknown. An approved choice remains locked until an explicit supersede event records the
user's changed instruction. A record is an audit of supplied decisions, not proof those
decisions were good or that an external action occurred.

On resume, read the record and inspect cited artifacts; verify current tool/account/repo
state where it matters. Missing sources and stale observations stay unverified. Continue
the outstanding objective instead of restarting discovery.

The record has revision conflict checks and atomic writes. On conflict re-read and
reconcile; never overwrite an intervening event. On an existing lock, report it and do
not delete a possible active writer's lock. Records are local, not synced across chats.

## Innovation integration

Apply ../creative-learning/SKILL.md when feedback creates a scoped preference. Store structured preferences as supported note events. On resume inspect the record, sources and preferences, reconstruct structured pending actions, and feed a v2 continuity checkpoint into the planner. Continue authorized unfinished work, not only a recap.
