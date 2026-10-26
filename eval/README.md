# Offline paired-output evaluation

This harness compares **supplied actual output captures** from an ordinary assistant
and Idea-Man. It makes no model calls, generates no baseline answers, executes no
commands from captures, and uploads nothing. Python 3.9+ standard library only.

The 14 cases in cases.json are **synthetic tasks**, not customer interviews or
observed usage. They cover operations diagnosis, research, business decisions,
experiments, implementation handoffs, creative alternatives and multi-turn
corrections. They are a starting test set, not a representative sample of all users.
No observed captures or human judgments ship with this repository. An empty report
is `not_evaluated`, never a quality pass.

For task-understanding coverage beyond the executable case set, see the
[task-fit challenge journeys](task-fit-journeys.md): twelve contrastive multi-turn
scripts with supplied facts, required and forbidden behavior, and minimal local
verification. They are synthetic, unrun behavioral hypotheses, not captures or
semantic success evidence; they add no cases or execution to this harness.

## Run a comparison

1. Use two fresh independent sessions with the same model/version, settings, base
   instructions, task conversation, tools and maximum tool calls. The intended
   difference is the Idea-Man instructions. Keep supplied synthetic assistant turns
   identical in both arms; do not let one arm rewrite history before the final turn.
   Do not add other conversation memory or unequal private context.
2. Record actual final responses and artifact files without rewriting them. Preserve
   failures and refusals. Capture a timeout/error as the actual visible response, not
   a fabricated answer. Do not silently rerun only the weaker arm; preregister the
   same repeat policy and use separate run directories for independent repetitions.
3. Fill a local template with provenance. The hash reported by `cases` binds the
   supplied conversation. `base_context_sha256` hashes the exact shared base
   instructions/context, excluding the intended plugin intervention.
   `prompt_sha256` hashes each full submitted prompt (including the intervention).
   `intervention_revision` identifies the exact plugin source revision or archive
   hash; baseline uses `none`. Record actual model settings, not guesses.
4. Import both captures and create blinded packets. Give each order to a **different
   independent reviewer**. Reviewers see only their packet and the rubric below;
   keep captures and the private order key from them. Do not reuse the same reviewer
   for both orders of a case. Do not tell them which arm is expected to win.
5. Import evidence-backed judgments and inspect every case, including failures,
   missing results and mismatched provenance. No overall numeric quality score is
   calculated. A human preference never erases a hard constraint failure.

Example commands from the repository root (redirection creates local working files):

```text
python eval/paired_eval.py cases
python eval/paired_eval.py capture-template --case queue_diagnosis --arm baseline > baseline.json
python eval/paired_eval.py capture-template --case queue_diagnosis --arm idea_man > idea-man.json
python eval/paired_eval.py import-capture --run local-eval/run-01 --input baseline.json
python eval/paired_eval.py import-capture --run local-eval/run-01 --input idea-man.json
python eval/paired_eval.py make-packets --run local-eval/run-01
python eval/paired_eval.py judgment-template --run local-eval/run-01 --packet-id queue_diagnosis.order1 > judgment-1.json
python eval/paired_eval.py judgment-template --run local-eval/run-01 --packet-id queue_diagnosis.order2 > judgment-2.json
python eval/paired_eval.py import-judgment --run local-eval/run-01 --input judgment-1.json
python eval/paired_eval.py import-judgment --run local-eval/run-01 --input judgment-2.json
python eval/paired_eval.py report --run local-eval/run-01 > report.json
```

Templates are deliberately incomplete and cannot be imported unchanged. Fill them
with actual captures/judgments before importing. No approval to call a model or
export project material is implied by these instructions. Keep runs outside tracked
source or in an explicitly chosen local output folder; they may contain private
material. The harness does not modify global memory or plugin installations.

## Provenance and artifacts

Capture fields are strict. The command template is the authoritative shape.
Settings is an object containing the actual inference parameters, including
reasoning settings and output token limit where available. Use `unknown` or null
for genuinely unavailable settings; the pair will be flagged rather than silently
treated as comparable. Tool budget has `tools` and `max_calls`. Use a stable sorted
tool list so ordering alone does not create a mismatch. Distinct session IDs are
required for a comparable pair. Equal full prompt hashes are flagged because they do not
show the declared plugin intervention. Context/model/settings/host/tool-budget differences
remain visible per case.

Artifacts are optional except where a case requests one:

```json
{"name":"pilot-plan.md","path":"C:/chosen-project/pilot-plan.md","sha256":"<actual SHA-256>"}
```

Paths must be absolute. Artifact checks require an existing file and matching hash.
The harness reads only supplied artifact paths, copies their verified UTF-8 content
into reviewer packets, and never runs them. Current review limit: 1 MiB per artifact,
UTF-8 text only. Binary/media review requires a separate appropriate evaluator; do
not treat a failure to load media as a visual quality grade. A changed or missing
artifact remains a hard failure. A path in an answer alone does not prove delivery.

Duplicate JSON keys and nonfinite numbers (including numeric overflow) are rejected
before a capture file is created. Immutable imports refuse overwrite. Changed captures/artifacts invalidate bound
packets and judgments. Use a fresh run to correct evidence, retaining the old run as
provenance. Packets also include and freeze the Human grading section below, the
mechanical acceptance rule and the actual evaluator source hash. Changing any of
these invalidates bound judgments, even when the
conversation and qualitative rubric are unchanged. Preserve earlier runs and create
new packets and reviews under the new evaluator; legacy packets without this binding
must also be re-reviewed. Even a nonfunctional evaluator source edit changes that
identity; this conservative rule avoids silently reusing a verdict with a different ruler.
IDs, source paths and timestamps are assertions from the capture owner;
the harness cannot prove they describe a real run. Model names might also leak
through actual response text; reviewers must disclose loss of blinding, and such
judgments cannot be imported as blinded.

## Human grading

Judge each output against the actual user task and case-specific rubric. Cite a
short output excerpt or concrete omission for **every** grade, including N/A.
Do not grade apparent sophistication, length, method names, or confident tone as
quality. Do not infer market demand from creative originality.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Usefulness | Does not advance the requested task; major unsupported or impractical content | Usable with meaningful correction or missing detail | Directly useful, feasible within constraints, evidence/uncertainty and next action appropriate |
| Method fit | Solves the wrong problem or applies a counterproductive process | Mostly appropriate but some unnecessary or missing reasoning steps | Uses the lightest adequate process, matches stage and evidence, adapts to corrections |
| Originality | Reworded/common alternatives where novelty was requested | Some useful mechanism difference, mixed with familiar ideas | Distinct, relevant mechanisms with clear practical value; not novelty for its own sake |

Use 2/4 for intermediate cases. Use null with an explanation for originality when
the task is exact editing, evidence synthesis, or another job that does not call for
novelty. Do not penalize correct restraint. The exact-edit case especially should
not reward added ideas. Synthetic scores in automated tests are harness fixtures,
not calibrated human observations.

List each hard failure separately under A/B: violated explicit constraint, invented
evidence/execution, unauthorized action, wrong source, failed required artifact,
or missing requested deliverable. Explain the evidence, not just a label. A polished
answer can still have a hard failure. Then record A, B, tie, or neither preference
and the user-relevant rationale. Preference means a judgment on these outputs,
not proof of population preference.

## What the report means

- `not_evaluated`: captures or human judgments are missing. Mechanical checks can
  still expose failures, but passing them is not a quality grade.
- `incomplete_review`: only one order/reviewer has been judged.
- `provenance_mismatch`: the comparison is not controlled enough for attribution.
- `reviewed`: both orders have distinct independent reviewers and comparable
  observed captures. Read the judgments and hard failures; this is not a pass label.
- `test_fixture`: fixture captures are excluded from observed comparison even if
  their example judgments are complete.
- `invalid_evidence`: a capture/packet/artifact binding or supplied record failed
  validation. Investigate the case rather than averaging it away.

Preferences are shown only for complete eligible comparisons, with disagreement
reported as mixed. Per-case hard failures remain alongside them. No aggregate score,
automatic originality grade, keyword-based quality pass, benchmark superiority,
native installation proof or product-market-fit conclusion is produced.

## Local harness verification

```text
python -m unittest discover -s tests -p test_evaluation.py
```

Tests create temporary, explicitly `test_fixture` captures and judgments to exercise
the entire import -> blinded packet -> judgment -> report path. They never invoke a
provider, and fixtures are never reported as observed results or included in a
distributed run. Deterministic checks cover exact strings, JSON keys/types/counts,
and actual file existence/hash only. For example, three identical ideas can satisfy
a JSON count check while failing the human originality and usefulness review.
