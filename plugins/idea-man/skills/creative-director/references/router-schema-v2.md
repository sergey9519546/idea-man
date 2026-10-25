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
| deliverable | text, image, video, audio, code, deck, document, mixed; returned content type, independent of delivery medium and source type |
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
Producing an analysis, brief, research result, review report or decision recommendation
does not commit a candidate and does not require a prior selection, even when produce
is explicit. Delivery cannot grant choice authority. Development, handoff and
candidate-dependent experiments retain selection gates. Use not_needed for a
candidate-free experiment; do not invent user approval.

## Optional fields

- delivery_mode: inline or artifact. Default inline for text, artifact otherwise.
  Inline supports text and code. Inline code needs no file_write; its code rubric
  still applies. Artifact text/code requires file_write. Other artifact types
  retain their authoring/generation capability requirements.
  Any substantive requested operation returning nontext content or an artifact
  includes production and verification, including research, diagnosis, decisions,
  experiments and separate review reports. A review report does not authorize
  changing its reviewed source. Inline text review stays read-only. Pure status,
  record and resume without restored substantive work do not imply production.
  File delivery does not grant code execution or database mutation authority.
- live_research_dependency: independent or source_bound. Defaults to source_bound
  for mixed evidence or any supplied source entries, independent otherwise.
  Source-bound live queries wait for required source resolution and synthesis,
  plus applicable brief/checkpoint preparation. Explicit source_bound with no
  source entries adds a source-resolution blocker. Declare independent only when
  the query can actually be formed without those inputs; web access alone does
  not establish independence. Independent queries can proceed while unrelated
  supplied-source or variation work is blocked. Split workstreams when different
  queries require different source subsets.

- capabilities and required_capabilities: arrays of verified classes: web,
  image_generation, video_generation, audio_generation, file_write, code_execution,
  deck_authoring, document_authoring, subagents. Default empty. Mixed production needs
  explicit required capabilities, including when production follows implicitly from
  any non-text or artifact request. File writing alone does not verify code.
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

Each executable step exposes its own `input_binding`. The receipt helper uses that
step binding, not the plan-level semantic binding. A step binds the task contract, its
step ID, and accepted predecessor bindings and output identities. Replacing a generated
artifact therefore invalidates its old evaluation and verification, transitively.
Portfolio dependencies are checked before task-local readiness and receipt reuse;
nested and flattened step states must agree. Independent workstreams remain independent.
Selected method IDs, procedures, expected outputs and references are also bound.
Changing a selected contract invalidates receipts even when its ID stays the same;
unrelated method edits do not. The contents of referenced documents still require host
inspection; the planner does not fetch or certify those documents from their locator.

The binding format is `step-output-v1`. Receipts from the older task-wide v2 format
are deliberately ignored. Replan, actually reinspect affected ready steps, and mint new
receipts with the helper; do not copy an old approval into a new binding.

Normalized delivery_mode and live_research_dependency are also receipt inputs.
Omitting them uses the defaults above; explicitly supplying the same default does
not change a new binding. Older receipts lack these inputs and must be replanned
and reinspected; changing either value invalidates prior receipts. The conservative
source-bound default replaces old implicit independence of mixed live research.

Changing sources, constraints, selections, objectives, requested outputs, methods or
verification-relevant inputs invalidates affected receipts. Split independent branches
to avoid broad invalidation. Stage and receipt bookkeeping alone do not invalidate work.

## Explicit in-place source revisions

Ordinary out-of-place output receipts keep the existing form. For an authorized edit
that replaces the source file itself, capture execution evidence BEFORE editing:

1. Finish and receipt the dependencies until revise_source is ready. Keep dependency
   evidence in separate stable artifacts, not in the file being replaced. begin-step
   rejects a target matching any accepted transitive predecessor output before editing.
   For an upstream generated file, retain that accepted file as the immutable upstream
   output, copy it to a separate working path, identify the working copy as the revision
   source, and inspect/receipt the revised task contract before begin-step. The accepted
   upstream artifact stays current while the working source transitions to its postimage.
2. Run: `python scripts/studio.py begin-step --assessment assessment.json --source-id source-a --snapshot project/execution-before.json`.
   The project directory must already exist. Retain the returned snapshot path and
   revision hash. Publication is atomic and exclusive; an existing snapshot is never
   overwritten. The snapshot records the pre-edit assessment, file revision and ready
   operation binding, without copying source contents.
3. Perform and inspect only the authorized source edit.
4. Run: `python scripts/studio.py receipt --assessment assessment.json --step revise_source --artifact source.txt --evidence-file inspection.txt --snapshot project/execution-before.json --snapshot-revision CAPTURED_HASH`.
5. Add the printed receipt and replan. Verification is now ready and must inspect the
   actual revised output before receiving its own ordinary receipt.

Only a ready revise_source targeting one identified available file supports this
opt-in transition. For a portfolio pass --task-id ID to both begin-step and receipt.
The snapshot captures the full portfolio and target task identity; readiness and minting
use the joined current graph. Upstream accepted output changes invalidate reuse while
unrelated independent workstreams may change or remain unfinished. The assessment retains its original source revision;
the transition records the post-edit output identity. The snapshot hash, same task,
operation, constraints, exact target path, prior receipts, other live source versions
and current post-edit bytes must remain valid. Changing a different source or changing
the output again invalidates dependent work. Rebase to a new inspected assessment
before starting a subsequent in-place transaction; nested transitions are unsupported.

Snapshots and receipts are editable host evidence, not signatures or cryptographic
authorization. Retain the original returned snapshot hash outside the snapshot, inspect
the source and evidence honestly, and preserve preimages separately when recovery is
required. The helper does not grant source-edit authority or prove an edit was correct.

Well-formed receipts for recognized steps removed by an action change are reported in
ignored_receipts as obsolete. Unsupported step IDs and malformed receipt schemas still
fail validation, including malformed transition objects.

## Multiple workstreams

An envelope may contain only schema_version=2 and workstreams. Each workstream has an
assessment plus depends_on (task IDs). IDs are unique, dependencies exist, cycles fail.
Returned steps use task_id/step IDs. One branch's missing capability does not block an
independent branch; dependent tasks await every required upstream work step. All accepted step outputs and bindings feed downstream identity; a completed independent query cannot release a sibling's unresolved source work.
Presentation remains deliverable reporting and never becomes a reusable completion receipt.
The selected method contracts attach to substantive work steps; methods do not create a
second diagnosis/experiment ceremony. This is advisory ordering,
not an automatic background scheduler or subagent authorization.

## Action templates and explicit phase order

An assessment's actions are a set of requested operations. Their JSON array order
does not schedule phases; the planner uses its defined dependency template.
Research plus experiment plus a document artifact synthesizes evidence, designs
the experiment, produces the document, then verifies that actual output. It does
not claim that the experiment has been executed. Inline research text can be
presented after synthesis without requesting a separate authored file.

Use a workstream envelope and depends_on for an explicitly requested order that
differs from the single-assessment template. For example, make a research workstream,
then an experiment-plan workstream depending on that research, then a separately
authorized execution workstream depending on the plan. Independent policy research
can use live_research_dependency=independent while an inventory-bound SKU lookup
uses source_bound in a different workstream. Each dependency awaits the preceding
workstream's complete accepted work frontier; an action list does not authorize external
execution.

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

## Legacy compatibility reference

See the [version-1 compatibility contract](router-schema.md). This link does not change version-2 schema or receipt behavior.

## Method fitness and optional candidate decisions

The quick effort setting limits optional breadth. When a default D2 evidence lens
would otherwise replace requested invention, variation or causal diagnosis, the
planner retains a substantive method alongside D2. A high-stakes decision-only route
may still use D2 alone; explicit requested_methods remain authoritative.

For consequential candidate comparisons, the separate candidate-decisions.md contract
and ../scripts/studio.py compare-candidates --assessment <file.json> support host-reported
hard gates, conditional readiness and optional criterion comparisons. They do not
create a completion receipt, prove source truth, replace v2 source inspection or
authorize execution. They are not required for every plan.
