# Innovation assessment v2

The host reads the actual conversation and inspected sources, then supplies this JSON.
Python validates it and selects registered specialists/methods. It does not classify prose.
User-facing answers normally omit this machinery. All paths below are skill-relative.

Run: `python scripts/studio.py plan --assessment assessment.json`.

## Required fields

| Field | Values |
|---|---|
| schema_version | Integer 2 |
| task_id, objective | Stable identifier (letters/numbers/hyphen/underscore); active desired outcome |
| domain | general, business, operations, engineering, research, product, service, learning, personal, policy, story, visual, campaign, game |
| actions | Nonempty unique list: brief, diagnose, ideate, vary, revise, review, decide, develop, experiment, handoff, produce, research, resume, status, record |
| deliverable | text, image, video, audio, code, deck, document, mixed; what is returned, not the source type |
| artifact_kind | Specific output: analysis, decision_memo, experiment_plan, article, memo, report, explainer, research_brief, process, image, prototype, treatment, etc. |
| scope | exact, bounded, open |
| stage | unclear, framed, evidence, options, selected, executing, checking |
| problem | Object with kind, bottleneck, novelty, stakes, reversibility, as below |
| evidence_mode | none, supplied, live, mixed, canon, hypothesis |
| sources | Array of id/kind/locator/revision/status/inspected objects; empty when no source needed |
| selection | Object with status, ids and evidence |
| constraints | Array of id/text/kind/evidence objects; kind hard or soft |
| evidence | Array of source/detail objects. Source user, artifact or inference; at least one user instruction |

Problem kind: unclear, causal, optimization, tradeoff, new_possibility, combination,
uncertainty, adoption, communication, execution. Bottleneck: framing, evidence,
assumptions, complexity, conflict, novelty, selection, implementation, feedback.
Novelty: none, improve, explore. Stakes: low, medium, high. Reversibility: reversible,
costly, irreversible. These are scoped judgments with evidence, not calibrated scores.

Source kind: file, provided, url. Status: available or missing. Available sources need
a nonempty locator and revision. File revision is SHA-256; the planner recomputes it and
invalidates stale bindings. Provided/URL source revisions are host assertions requiring
inspection. A missing source cannot be marked inspected. A user-supplied text passage
can use kind=provided with a clear conversation/source locator and revision label.

Selection status: user, assistant_authorized, none, not_needed. User selection needs
nonempty IDs and explicit evidence. Delegation needs evidence. Unselected states have
empty IDs. Selection IDs identify candidates; source IDs identify the actual evidence
or assets. Retain their relationship in evidence rather than guessing from a number.

## Optional fields

- capabilities and required_capabilities: arrays of verified classes: web,
  image_generation, video_generation, audio_generation, file_write, code_execution,
  deck_authoring, document_authoring, subagents. Default empty. Mixed production needs
  explicit required capabilities, including when production follows implicitly from
  a non-text development/variation request. File writing alone does not verify code.
- requested_count: null or integer 1..10000; use batches for large counts.
- effort: quick, standard, deep. thinking_style: adaptive, analytical, experimental,
  systemic, human_centered, contrarian, analogical, constraint_driven, combinatorial,
  playful. requested_methods: canonical method IDs from the registry, supported by the
  user's instruction. Avoid method casting for exact work.
- feedback: verdict none/approval/rejection, reason text or null. Null means unknown.
- brief: sufficient, assumptions_ok, blocked. material_ambiguity: boolean. A source
  lookup or reasonable assumption comes before unnecessary questions.
- acceptance: array of observable conditions. project_revision: integer or null.
- continuity: null or task_id/objective/pending_actions/evidence/source_rechecked.
  IDs/objective must match; pending actions exclude resume/status/record. Restore these
  only after source_rechecked=true. Resume adds pending actions; status does not.
- receipts: step/binding/evidence/output objects. Output has kind/locator/revision.

## Receipt binding

`python scripts/studio.py fingerprint --file <path>` returns file identity and SHA-256.
After actually completing and inspecting a ready step, use:

`python scripts/studio.py receipt --assessment assessment.json --step inspect_context --artifact inspected-contract.json --evidence-file inspection-note.txt`

For a workstream envelope also pass --task-id <id>; the helper checks the actual joined
step state and binds the receipt to upstream inputs and outputs.

This prints a receipt; add it to the assessment's receipts array and replan. The command
requires a ready step, existing artifact and evidence text. It binds to task inputs and
output bytes; it cannot prove that the supplied inspection note is true. Host evidence
and honest reporting remain mandatory. Non-file outputs are not automatically reused;
reinspect them. Presentation is never marked complete by an old receipt.

Changing sources, constraints, selections, objectives, requested outputs, methods or
verification-relevant inputs invalidates receipts. Current binding is deliberately
conservative across a coherent task branch. Split independent branches to avoid broad
invalidation. Stage and receipt bookkeeping alone do not invalidate work.

## Multiple workstreams

An envelope may contain only schema_version=2 and workstreams. Each workstream has an
assessment plus depends_on (task IDs). IDs are unique, dependencies exist, cycles fail.
Returned steps use task_id/step IDs. One branch's missing capability does not block an
independent branch; dependent tasks await the upstream verified terminal work step.
Presentation remains deliverable reporting and never becomes a reusable completion receipt.
The selected method contracts attach to substantive work steps; methods do not create a
second diagnosis/experiment ceremony. This is advisory ordering,
not an automatic background scheduler or subagent authorization.

## Example: staffing-constrained service improvement

```json
{
  "schema_version": 2,
  "task_id": "queue-redesign",
  "objective": "Reduce queue time without increasing staffing",
  "domain": "operations",
  "actions": ["diagnose", "ideate", "experiment"],
  "deliverable": "text",
  "artifact_kind": "experiment_plan",
  "scope": "bounded",
  "stage": "framed",
  "problem": {"kind":"optimization","bottleneck":"complexity","novelty":"improve","stakes":"medium","reversibility":"reversible"},
  "evidence_mode": "hypothesis",
  "sources": [],
  "selection": {"status":"not_needed","ids":[],"evidence":"Explore options and tests; no implementation commitment requested"},
  "constraints": [{"id":"staffing","text":"No additional staff","kind":"hard","evidence":"User says without increasing staffing"}],
  "evidence": [{"source":"user","detail":"Reduce queue time without increasing staffing"}],
  "thinking_style": "constraint_driven",
  "requested_count": 3,
  "acceptance": ["Preserve staffing limit", "Distinguish hypothesized causes from measured causes", "Specify a small pilot and decision rule"]
}
```

Expected: innovation-strategy; constrained/system/test methods; diagnosis before options;
an experiment plan, with no invented queue measurements. It does not execute a staffing
or service change. If measurements are supplied, use supplied evidence and source IDs.
