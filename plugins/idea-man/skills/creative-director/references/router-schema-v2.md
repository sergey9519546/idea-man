# Innovation assessment v2

The host reads the actual conversation and inspected sources, then supplies this JSON.
Python validates it and selects registered specialists/methods. It does not classify prose.
User-facing answers normally omit this machinery. All paths below are skill-relative.

CLI contract ingestion rejects duplicate object keys at every depth, NaN/Infinity
constants and numeric overflow to infinity. It never silently chooses the last
conflicting action or decision. The same checks protect project-record inputs and
execution snapshots; valid legacy records and UTF-8 BOM input remain supported.

Run: `python scripts/studio.py plan --assessment assessment.json`.

## Required fields

| Field | Values |
|---|---|
| schema_version | Integer 2 |
| task_id, objective | Stable identifier (letters/numbers/hyphen/underscore); active desired outcome |
| domain | general, business, operations, engineering, research, product, service, learning, personal, policy, story, visual, campaign, game |
| actions | Nonempty unique list: brief, diagnose, ideate, vary, revise, review, decide, develop, experiment, handoff, produce, research, resume, status, record |
| deliverable | text, image, video, audio, code, deck, document, mixed; returned content type, independent of delivery medium and source type |
| artifact_kind | Specific output: analysis, decision_memo, experiment_plan, calculation, estimate, optimization, statistical_analysis, proof, derivation, explanation, coaching_turn, article, memo, report, research_brief, process, image, prototype, treatment, etc. |
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

A file observation can fail temporarily without proving that the file is missing.
The returned source then has inspected=false and observation_error containing the
exception class; resolve_source is unavailable. Reinspect after access recovers.
Independent workstreams remain usable. An unreadable prior receipt output is not
reused as done; it requires fresh inspection rather than aborting the whole plan.
observation_error is a returned observation, not an additional assessment input field.

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
  user's instruction. Exact work has no automatic method casting; an explicitly
  requested procedure can support its bounded revision or review without adding
  ideation/variation or changing protected properties.
- feedback: verdict none/approval/rejection, reason text or null. Null means unknown.
- brief: sufficient, assumptions_ok, blocked. material_ambiguity: boolean. A source
  lookup or reasonable assumption comes before unnecessary questions.
- acceptance: array of observable conditions. project_revision: integer or null.
- continuity: null or task_id/objective/pending_actions/evidence/source_rechecked.
  IDs/objective must match; pending actions exclude resume/status/record. Restore these
  only after source_rechecked=true. Resume adds pending actions; status does not.
- receipts: step/binding/evidence/output objects. Output has kind/locator/revision.

## Review, repair and completion order

The actions describe the requested operations; their input array order does not
define execution order. A combined review + revise task first inspects the exact
source and records read-only findings in review_source. revise_source depends on
those findings and the relevant source preparation. The later verify_output checks
the changed result against the acceptance conditions. Finding a defect and verifying
its repair are separate operations; a pre-change review is not a post-change pass.
Changed review findings or outputs invalidate their dependent repair/check receipts.

Explicit review combined with diagnosis, proposals, variation, decision, development,
experiment design or handoff likewise establishes review_source findings after the
relevant source preparation and before that subsequent work. Reviewing a source and
comparing newly generated options remain separate operations; suggestions alone do
not authorize editing the reviewed source.

Review alone remains read-only. Its existing evaluate_options artifact-quality step
checks the requested review and carries its acceptance conditions; it does not add
production, revision or a duplicate critique. If a separate review artifact is
requested, ordinary artifact production and its final verification still apply.

When record accompanies substantive work, record_decisions waits for the requested
results and their final verification. Changed selection or result evidence invalidates
the dependent saved-record receipt. Standalone record/status requests retain their
inspection-only prerequisites. Use a separate earlier workstream for an explicitly
requested pre-work checkpoint.

Without file_write, record_decisions remains unavailable. prepare_unsaved_recap can
deliver a clearly labeled unsaved recap after the same accepted result prerequisites;
its project-record guidance and checks require disclosing the missing capability and
unfulfilled durable save. This fallback does not release blocked persistence or mark
the assignment complete.

Research and brief outputs receive verify_output after their source/framing work,
including inline text. It carries the task's acceptance conditions so source support,
counts, format and protected requirements are checked before delivery. This does not
claim the conditions passed: only actual inspection and an appropriate receipt can
mark the check done. Status, record and an unresolved resume request do not gain a
production step from this rule.

## Receipt binding

### Read the next step's connected guidance

The primary specialist describes the whole assignment. Each step also exposes
skill_contract (registered id/path/status), reference_contracts (package-relative
path and selector), and any method/verification contracts. Use the step assignment:
record_decisions and restore_checkpoint load creative-project, while feedback
diagnosis loads creative-learning. Comparisons involving options load creative-review;
development loads concept-development. Final verification uses artifact-quality.
Canon synthesis is included in the research-and-writing service summary.

Each step also reports required_capabilities and missing_capabilities. One shared
resolver supplies the tool requirements and the availability gate for saving,
live research and artifact production. An old receipt cannot mark a step complete
while a required capability is missing. These are host-asserted capability classes,
not a claim that an external account or provider is connected.

Run `python scripts/studio.py context --assessment assessment.json --step <ready-step>`.
For a workstream envelope pass --task-id ID. The reader checks the joined current
plan before returning instructions: waiting, unavailable, done or missing steps cannot
be requested as ready work. A single-task assessment cannot accept --task-id. The
command is read-only and preserves the assessment. It does not execute work or grant
authority; capabilities in its task payload remain host assertions.

The response contains the current task, source identities, ready node and resources.
Each resource has a locator/selector, the full-file SHA-256, returned-content SHA-256
and actual UTF-8 content. Skills load as a whole; playbooks load the selected heading;
methods load only section_prefix with the scope guard; rubrics load the matching row
and shared checks. Reads are bounded to 256 KiB per packaged resource and cannot
resolve outside the package. Missing or ambiguous sections fail clearly. Other links
are conditional follow-up references, not automatically recursive loads. Source
content, external tools and model inference are not supplied by this reader.

Assigned skill paths, selected reference/section contracts and the exact selected
content participate in the step binding through `guidance_content`. Skills bind their
whole content; methods bind the selected section plus its scope guard; rubrics bind
the selected row and applicable shared checks. An unrelated method edit does not
retire valid work. Changing selected guidance invalidates that step and dependent
work, while unchanged preparation can remain accepted. This conservatively retires
receipts minted before selected-content binding; actually reinspect affected ready
steps instead of copying a prior pass. Unreadable, missing or malformed selected
guidance marks the affected step unavailable with a resource error; independent
branches can still proceed. The context reader also rejects guidance changed between
planning and delivery. Hashes do not certify that the host read, followed or correctly
applied those instructions; honest execution evidence is still mandatory.

### Record inspected execution

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
unrelated method edits do not. Selected packaged guidance is read through the same
bounded selector as the context reader. This does not fetch external references or
recursively load conditional links, and does not certify instruction compliance.

Each step's phase-specific method application and verification contract are bound
before deciding whether its receipt can be reused. A changed check invalidates that
step and its dependents; unchanged independent preparation can remain accepted.

The binding envelope remains `step-output-v1`, with selected-content identities in
its contract. Receipts lacking this contract or from the older task-wide v2 format
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

The normalized evidence array is also bound. Inline quantities, user corrections and
learner attempts can be material inputs even when the objective and source list stay
the same; changing them retires old answers and checks. Do not conceal changed facts
as routing-only annotations.

The context response's inputs array supplies each accepted direct dependency's joined
step ID, input binding, output locator/version and completion evidence. For a portfolio,
these are the actual upstream outputs from the joined graph, not only local receipt IDs.
The reader supplies identities rather than user-file contents; inspect the referenced
result before using it. Stale or missing outputs prevent dependent readiness, while
independent tasks remain available.

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

Snapshot hashing and strict JSON parsing use the same byte buffer, so a second read
cannot substitute different instructions after the digest check.

Well-formed receipts for recognized steps removed by an action change are reported in
ignored_receipts as obsolete. Unsupported step IDs and malformed receipt schemas still
fail validation, including malformed transition objects.

## Multiple workstreams

Use dependent workstreams for explicit phase-specific method requirements as well
as output dependencies. A task-wide requested_methods list follows the planner's
phase priorities; the objective string does not select a phase. For "research with
D2, then independently review", put research and requested_methods ["D2"] in the
first stream and review with no requested methods in its dependent stream. Inspect
and identify the accepted research output as the review source before proceeding.
Do not claim that applying D2 only in the final review fulfills the earlier research
instruction. Simple research-only requests can use the ordinary single stream;
their requested methods attach to evidence work even when the answer stays inline.

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

## Verification follows the task

The primary rubric follows the named artifact kind before domain defaults. Analysis, decisions, experiments and processes retain substantive checks when saved as documents. Code and image outputs retain code/visual checks. Decks with no more specific kind use presentation. Medium-specific rendering/readability checks remain additional requirements when applicable.

Calculation, estimate, optimization and statistical_analysis use quantitative;
proof, formal_proof and derivation use formal_reasoning; explanation and explainer
use explanation; coaching and coaching_turn use coaching. These labels describe
the requested content, not a claim that the result is correct. For a direct inline
text produce operation with one of these rubrics, no prepare_handoff is added.
Relevant verification still applies, including statistical inference limits when
statistical_analysis is requested. There are no new required assessment fields.

Returned substantive steps can include:

- method_contracts: selected id/reason/procedure/output/reference plus application
  for this phase. A system or causal procedure may support both diagnosis and
  intervention generation; its phase applications differ. A user-requested
  generating method is not consumed by an earlier diagnosis step.
- verification_contract: rubric and checks for the step's requested result.
  Checks are requirements for host inspection, not passed verdicts or automated
  validators of truth. Applicable scope, authority, output, evidence, numerical,
  formal or learning-interaction checks cannot be replaced by a method name.
- effort_policy at plan level: optional_method_budget, required_checks_reduced=false
  and its basis. Quick/standard/deep limits optional method breadth, not required
  checking or response length. Explicit methods and a necessary evidence lens may
  exceed that optional budget. Time/tool limits still control actual execution;
  qualify a result that cannot be checked within them.

These contracts remain advisory until the host performs the work and inspects the
output. execution_complete stays false; the helper never authorizes an external
action, runs an experiment or certifies mathematical validity by planning it.
