# Candidate decisions for a scoped next commitment

Use this helper only when a consequential comparison benefits from an explicit evidence
contract. It is optional. A quick idea, exact edit or requested list does not need a
scorecard. Preserve the user's requested count, format and methods. One modest practical
idea can be sufficient; do not invent alternatives to fill this schema.

The standard-library Python 3.9+ helper is read-only and deterministic:

```text
python scripts/candidates.py --assessment candidate-assessment.json
python scripts/studio.py compare-candidates --assessment candidate-assessment.json
```

The host interprets the assignment, inspects sources and supplies judgments. The helper
validates their structure, applies hard gates and compares optional ordinal ratings.
It does not generate ideas, fetch/inspect cited material, prove semantic truth or
novelty, make a user selection, authorize tools, execute a test or produce an artifact.
Its readiness is conditional on host-reported evidence for the stated commitment.

## Define the actual commitment

The commitment has level explore, test or make plus a concrete text description:

- explore: investigate a question or direction.
- test: execute the specifically described bounded informative test.
- make: produce or implement the specifically described result.

These are not universal project phases or quality badges. A reversible prototype can
be a make commitment while demand remains unknown, if demand is not a critical
assumption for making that prototype. Conversely, a test involving a constrained
resource must satisfy the hard conditions for using that resource before it is ready.
Include only constraints and critical assumptions applicable to this next commitment;
do not transfer a narrow readiness judgment to broad deployment.

## Input schema, version 1

All listed fields are required. Unknown fields, duplicate IDs, dangling references and
invalid types fail validation. Arrays may be empty except candidates. IDs use letters,
numbers, hyphens or underscores. IDs are unique within their collection; assumption,
check and rating uniqueness is per candidate.

| Object | Exact fields |
|---|---|
| Assessment | schema_version=1, decision, commitment, sources, constraints, criteria, candidates, comparisons |
| commitment | level=explore/test/make, text; optional evidence_refs |
| source | id, locator, revision |
| hard constraint | id, text |
| optional comparison criterion | id, text |
| candidate | id, mechanism, checks, ratings, assumptions, next_test |
| check | constraint_id, status=pass/fail/unresolved, evidence_refs, detail |
| rating | criterion_id, value, evidence_refs, detail |
| assumption | id, text, status=supported/unresolved/refuted, critical, evidence_refs |
| next_test | null, or hypothesis, observation, decision_rule |
| mechanism comparison | left, right, relation=equivalent/distinct/unknown, evidence_refs, detail |

All text fields are nonempty strings. source locator and revision must identify the
host-inspected supplied source and its version. The helper checks nonempty identity,
not whether inspection occurred. Do not invent a source/version to satisfy a check.
evidence_refs are unique source IDs from this assessment. A pass/fail check, any rating,
supported/refuted assumption, and equivalent/distinct mechanism comparison need source
references. Missing checks become unresolved. For unavailable evidence use unresolved
with an empty evidence_refs list; do not label it pass. Unknown mechanism comparisons
may have no references. Source references support inspection, not automatic truth.

critical is a Boolean scoped to the stated commitment. An unresolved or refuted
critical assumption needs a next_test with hypothesis, observable result and a
prospective decision rule. The test remains a plan. Critical uncertainty gates make;
it may be the actual purpose of an explore/test commitment when its hard conditions
are satisfied. Noncritical counterevidence remains visible in the result.

Ratings are optional host judgments: integer 0..5, higher is preferred. Fractions,
Booleans, NaN and Infinity are rejected. They are ordinal judgments against explicit
criteria, never measured novelty, expected performance, ROI, customer demand or
probability. Use criteria=[] and ratings=[] when quantification adds no useful
distinction. There are no weights or averages.

Mechanism equivalence is a separate host-supplied evidence judgment. Explain the causal
difference or sameness in detail and cite its source. Similar words do not prove
equivalence; new names do not prove distinctness. Reversed/duplicate pairs, self pairs
and unknown candidate links fail validation. Omitting a pair supplies no evidence of
distinctness.

## Result interpretation

Each candidate reports readiness plus failed/unresolved hard constraints, assumptions
and next test. Any failed hard constraint blocks the current commitment. An omitted or
unresolved hard check needs evidence. Scores never compensate. For make, critical
refuted assumptions block, and critical unresolved assumptions need evidence.

Only candidates passing these gates enter eligible_for_scoped_next_step. That list
is not a recommendation to execute or a user selection. Existing approval and actual
host capabilities must be reconciled separately.

Optional ratings use Pareto comparison: a candidate dominates another only when it is
at least as preferred on every criterion and strictly preferred on at least one.
Exact ties, incomparable tradeoffs and missing comparisons remain explicit.
The frontier contains only eligible candidates with a complete set of ratings.
Eligible candidates with missing ratings appear in unranked; they are never promoted
as winners or treated as inferior because their evidence is missing. When status is
incomplete the frontier is only the fully rated subset, not a complete ranking.
No criteria means no scoring or frontier ceremony.

The output retains source identities, criteria, hard checks, all assumptions and
comparison evidence for inspection. selection_made, execution_authorized and
semantic_truth_verified are always false. Missing provider capabilities cannot be
overridden by this result. A proposed next test is not an executed experiment.

## Minimal illustrative input

This is a schema illustration, not an observed customer result. Here the host supplies
the assessment that discussing a handoff change respects the stated staffing limit;
it claims no measured reduction in delay.

```json
{
  "schema_version": 1,
  "decision": "Investigate one practical way to reduce service delays",
  "commitment": {"level": "explore", "text": "Discuss an earlier existing handoff"},
  "sources": [{"id": "brief", "locator": "provided:current-brief", "revision": "turn-1"}],
  "constraints": [{"id": "staff", "text": "No additional staff"}],
  "criteria": [],
  "candidates": [{
    "id": "earlier-handoff",
    "mechanism": "Move an existing handoff earlier without adding a role",
    "checks": [{"constraint_id": "staff", "status": "pass",
      "evidence_refs": ["brief"], "detail": "The exploration proposes the existing team only"}],
    "ratings": [],
    "assumptions": [{
      "id": "delay-effect", "text": "Timing contributes to delays",
      "status": "unresolved", "critical": true, "evidence_refs": []
    }],
    "next_test": {
      "hypothesis": "Earlier handoff reduces delay without overtime",
      "observation": "Compare handoff timing and delays during a reversible pilot",
      "decision_rule": "Retain the change only if delay improves without shifted burden"
    }
  }],
  "comparisons": []
}
```

For the exact existing review boundaries see
[creative-review](../../creative-review/SKILL.md) and
[artifact rubrics](../../../references/artifact-rubrics.md).
The implementation is [candidates.py](../scripts/candidates.py).

## Evidence-backed mechanism groups and coverage

Explicit equivalent assertions form transitive groups: if A is equivalent to B and B
to C, the helper groups A/B/C and retains their supporting source references. A distinct
assertion inside that group is a validation error, even when no direct pair conflicts.
These groups are consequences of the host's equivalence assertions, not text similarity
or independently verified novelty.

mechanism_pair_coverage lists total pairs, supplied relation count, explicit unknown
pairs and unassessed pairs. A group does not rewrite an explicitly unknown direct pair
as checked evidence: its transitive basis and that pair's inspection gap remain visible.
Likewise, an omitted pair remains unassessed even if a group connects its members.
No all-pairs input is required; single candidates and sparse comparisons stay valid.
Use a group to identify options whose asserted mechanism is shared, then inspect
execution differences or seek a meaningfully different mechanism when useful.

## Minimum evidence for consequential next steps

For a test or make commitment, commitment.evidence_refs must link at least one supplied
versioned source identity supporting that specific commitment. Merely listing an
unrelated source in sources is insufficient. Missing/empty evidence_refs remains valid
input but yields needs_evidence with readiness_gaps containing
commitment_source_evidence. Unknown/duplicate reference IDs are validation errors.
The helper verifies links and nonempty versions, not the truth of a source or whether
it actually supports the commitment; the host must inspect that relationship.

A test commitment also requires each candidate's next_test protocol with a hypothesis,
observation and prospective decision rule. Missing protocol yields needs_evidence with
test_protocol in readiness_gaps. Nonempty prose is structurally checked, not certified
as an adequate experimental design. A make commitment is still scoped: evidence for
a bounded prototype need not prove broad rollout value. Hard failures remain blocked
even when these additional evidence gaps are also present.

Exploration may remain source-free and have no protocol when that is the useful next
step. These are optional-helper gates for consequential comparisons, not a universal
questionnaire or new ceremony for simple tasks.

JSON imports reject duplicate field names at every nesting level rather than accepting
the last conflicting value. The standalone CLI and studio integration use the same
load_assessment parser; rejected inputs remain untouched.
