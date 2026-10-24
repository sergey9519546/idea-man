# Compatibility note

New work uses router-schema-v2.md. This v1 format remains accepted for existing assessments; it lacks specialist/method/source bindings.

# Structured router assessment, version 1

The host model reads the conversation and artifacts and constructs this assessment.
The Python planner is a deterministic check of that assessment, not an NLP classifier.
Do not claim that its tests prove free-text understanding or installed host behavior.

Run from the creative-director skill directory:

```text
python scripts/studio.py plan --assessment assessment.json
```

Required fields:

| Field | Meaning / values |
|---|---|
| schema_version | Integer 1 |
| objective | Active objective, nonempty text |
| actions | Unique array: brief, ideate, vary, revise, review, develop, handoff, produce, research, resume, status, record |
| deliverable | What the user expects returned: text, image, video, audio, code, deck, document, mixed |
| scope | exact, bounded, open |
| selection | user, assistant_authorized, none, not_needed |
| source | available, missing, not_needed; revision cannot use not_needed |
| brief | sufficient, assumptions_ok, blocked |
| confidence | Internal routing judgment from 0 to 1, not a calibrated probability |
| evidence | Array of source/detail objects; source is user, artifact or inference; at least one user entry |

Optional fields:

- effort: quick, standard (default), deep.
- feedback: none (default), rejection, approval.
- rejection_count: nonnegative integer, default 0.
- requested_count: positive integer up to 10000, or null/default. Large counts need batches.
- capabilities: currently verified tools, default empty. Allowed: web, image_generation,
  video_generation, audio_generation, file_write, code_execution, deck_authoring,
  document_authoring, subagents.
- required_capabilities: additional required tool classes. Required for mixed production.
- material_ambiguity: boolean, default false; only for consequential uncertainty.
- changes: changed inputs: goal, audience, constraints, selection, feedback, capabilities.
- completed: inspected, still-valid receipts as step/evidence objects. Do not add receipts
  merely because prior text says something happened. Changes invalidate downstream work;
  a receipt cannot bypass unmet dependencies. Presentation always remains to be done.

Unknown fields and contradictory exact-plus-ideation assessments fail validation. Split
independent workstreams into separate assessments and merge their deliverables. The
scope of each assessment is one coherent source/concept branch, not an entire portfolio.

An image being reviewed is a SOURCE; the returned verdict is text. A requested image
edit or visual variation board has deliverable=image. Artifact outputs for ideate,
vary, revise and develop automatically add a production step. A handoff-only request
does not. Missing tools cause an unavailable production step with an honest handoff.

Example: the user asks to remove a bulb character's facial features while preserving
its pose and accessories. The source has been inspected and image editing is available.

```json
{
  "schema_version": 1,
  "objective": "Edit the approved Lightbulb Hero without changing pose or accessories",
  "actions": ["revise"],
  "deliverable": "image",
  "scope": "exact",
  "selection": "user",
  "source": "available",
  "brief": "sufficient",
  "confidence": 0.95,
  "effort": "standard",
  "capabilities": ["image_generation"],
  "evidence": [
    {"source": "user", "detail": "Blue bulb with glasses only; remove eyes, mouth and yellow filament"},
    {"source": "artifact", "detail": "Inspected the right-hand 02 character on the supplied comparison board"}
  ]
}
```

Expected: inspect → bounded revision → execution specification → production → visual
verification → delivery. No insight mining, new concepts, comparison tournament or
selection gate. Exact source means keep limbs/cape unless the user asks to remove them.

Plan output contains dependency IDs, states, reasons, expected outputs, blockers and
requested count. States mean ready, waiting, done (inspected evidence), needs_input or
unavailable. Plan execution_complete is always false: this helper runs no creative tools.

Low confidence alone does not force a user question. material_ambiguity or a missing
required input does. Continue independent ready branches while blocked work waits.
Read examples/recognition-cases.json for representative assessments and expected routes.
