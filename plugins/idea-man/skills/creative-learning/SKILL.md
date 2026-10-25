---
name: creative-learning
description: "Idea-Man service for applying explicit corrections, approved examples and scoped problem-solving, workflow or creative preferences. Use after feedback changes a decision or when the user asks to remember, inspect or reuse project preferences. Do not infer approval from silence or enable background observation."
---

# Creative learning

Use this service with `../creative-project/SKILL.md` and apply `../creative-director/references/studio-router.md`. Preserve inspectable project preferences and workflow lessons across innovation tasks. Learning here means better use of the user's evidence and decisions. It does not train the host model or rewrite the plugin's instructions.

## Classify the feedback

Separate four kinds of information:

- Hard project constraint: "No additional staff" or "Keep the round glasses." Apply immediately within the named project/artifact scope.
- Explicit preference: "For this project, prefer reversible tests before major investment" or "For this brand, I prefer cheeky over cute." Preserve context and exceptions.
- Inferred preference: a pattern in selected or edited examples. Keep tentative; the user did not explicitly state it.
- Workflow correction: "Diagnose the bottleneck before inventing solutions" or "I asked for six images, not six written concepts." Update the current task contract and add a candidate routing regression case.

An approval of an artifact approves that artifact, not every incidental feature as a permanent taste rule. "No" is a rejection with an unknown reason. Repeated rejection warrants diagnosis from the actual differences; ask one discriminating question only if the missing reason blocks a useful next attempt.

## Apply a scoped preference

Represent each useful item as:

`id; project_id; scope_verbatim; applies_to; trigger; guidance; kind; evidence_refs; status; exceptions; supersedes; last_confirmed`

Preserve the user's exact scope phrase in scope_verbatim. Bind applies_to to the named
project, artifact, audience AND any limiting condition together. An exception for one
client-facing pitch does not cover other client-facing outputs. A rule for a staging
pilot does not cover production. Before applying or summarizing a preference, compare
the proposed applicability against the source phrase; never broaden "only this X" into
"all things with property Y." Keep the broader default active outside the exact exception.
If artifact IDs exist, record them; otherwise retain the quoted scope until identity can
be resolved. Test at least one adjacent non-matching example before saving a broad rule.

Statuses are `explicit`, `tentative`, `disputed`, `superseded`. They are evidence states, not probability scores. A repeated model inference does not become user confirmation. Counterexamples narrow a rule's scope or make it disputed; they should not disappear from history.

Newest explicit instructions control the present assignment. Preserve the older decision in history when a durable record exists. If two current explicit constraints conflict materially, surface the conflict and continue unrelated work. A soft preference cannot override a hard requirement.

## Persistence and control

Use current conversation context by default and do not claim durable recall. Save only when the user requests it or an authorized project-record workflow is established. Use the explicit project-owned destination and the existing record writer's revision/lock checks. Never fall back to global storage when project identity is missing.

Persist the structured item as JSON text inside the supported `note` event. Include `schema: "idea_man_preference_v1"` in that serialized object together with the fields above. The event itself has exactly `type: "note"` and `text: <serialized JSON string>`. Use `../creative-director/scripts/studio.py record --file <record.json> --expected-revision <observed revision> --event <event.json>`. Write the event file through file tools; do not interpolate user text into shell commands. Read back `show` or `validate` before claiming a save. Do not invent a new `preference` event type. The writer stores notes; the conductor inspects their scope and evidence on resume before applying them.

Save the minimum useful statement and evidence pointer rather than full prompts, private documents or raw tool logs. Do not turn on observer hooks, background providers, cross-project sync or automatic global promotion. Importing preferences into another project requires an explicit user request and a scope check.

On "forget this preference," stop applying it immediately. Distinguish logical retirement from physical erasure: an append-only record retains history. If the user requests deletion, explain the actual storage behavior and perform only an authorized, verified redaction supported by the host. Never claim a tombstone erased old data.

## Reuse and improve

On resume, verify project identity, source revisions and active preferences. Load only those relevant to the task. An approved example may be unavailable or superseded; say so rather than recreating it from memory.

For reusable workflow lessons, write a candidate maintainer note: failure, expected behavior, minimal counterexample and proposed test. Keep it out of the live core until a normal reviewed change and regression check establish that it helps. Do not self-modify SKILL.md during a user's creative project.

## Output contract

Usually apply the correction without a lecture. When saving is requested, report what was saved, its scope and location. When uncertain, say what is inferred. On request, provide a concise list of active, tentative and superseded preferences with evidence references.

Example: both Invisible Nerd and Lightbulb Hero are approved for Idea-Man; neither approval eliminates the other. Their bright palette is a project decision and must not silently become the default identity of every future customer's brand.
