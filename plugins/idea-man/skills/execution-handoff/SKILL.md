---
name: execution-handoff
description: "Turn selected creative work into production-ready instructions and execute with available host tools when requested. Use for visual briefs, prompt packs, writing packs, design/build specifications, prototypes and production handoffs."
---

# Concept to execution

Apply ../creative-director/references/studio-router.md and
../creative-director/references/studio-protocol.md.

Determine whether the user wants a handoff or the actual artifact. Inspect approved
sources and discover tools. This package does not supply provider access or credentials.

Prepare:
1. Objective and audience experience.
2. Authoritative concept/source/version and usable asset references.
3. Locked properties, permitted variation and exclusions from feedback.
4. Output count, format, dimensions/duration when known, naming and use.
5. Domain-specific instructions.
6. Acceptance conditions and inspection/test method.
7. Remaining decisions and dependencies.

Add domain detail:
- Images/design: subject relationships, composition, identity, light/material, palette,
  typography and reference roles. For edits specify changes and preservation precisely.
  Never claim a generator saw an asset that was not actually supplied.
- Video: shots/beats, action, transitions, continuity, audio relationship, verified timing,
  production limits. A shot list is not a rendered video.
- Writing: dramatic/thesis spine, audience/voice, outline, sourced required facts, causal
  constraints, length and review conditions.
- Product/code: flow, states/errors, data contract, integration boundaries, repository
  conventions, dependencies and meaningful acceptance tests.
- Campaign: executions, sequence, message invariants, resource assumptions and experiment.
  No invented performance projections.

If asked to make it, use the appropriate tool, inspect the result and fix material drift.
A prompt does not complete an image request when generation is available. Use targeted
code checks, document structure/render checks and visual source comparisons.

If execution is unavailable, deliver the usable packet and identify the missing input
or capability. Distinguish prepared, generated, inspected, tested and published. External
sends/deployments follow host authorization rules. Do not silently dispatch work elsewhere.

For multi-tool work, pass only needed context/assets and carry the same constraints
through each handoff. Replan when a tool cannot satisfy them.

## Innovation integration

Use ../artifact-quality/SKILL.md for the requested artifact's acceptance checks. Handoffs also cover process changes, business experiments, technical solutions and decision implementation. A plan does not prove those actions occurred.

If the optional v2 planner/receipt workflow is active and execution replaces its source
file in place, run studio.py begin-step before editing, retain the snapshot hash, and
mint revise_source with receipt --snapshot afterward. Use --task-id for a portfolio;
do not extract a dependent task to bypass its joined readiness checks. Then inspect
the revised output and receipt verification separately. See
../creative-director/references/router-schema-v2.md. This applies only within that
optional receipt workflow; it does not require Python for ordinary authorized edits.
