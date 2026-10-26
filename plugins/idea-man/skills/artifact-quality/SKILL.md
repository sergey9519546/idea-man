---
name: artifact-quality
description: "Idea-Man quality service for inspecting a produced or supplied artifact against its brief, sources, approved constraints and relevant craft standards. Use for a requested review or verification before delivery. Skip a full audit for a trivial response or when no artifact can be inspected."
---

# Artifact quality

Use this service for the conductor's verification step and creative-review's execution layer. Apply `../creative-director/references/studio-router.md`; avoid duplicate critiques. A concept comparison asks which direction is promising; an artifact check asks whether this analysis, decision, plan, experiment, implementation or creative deliverable fulfills the request and is usable.

## Establish the check

Inspect the actual source/version and output. Record their identifiers or paths and available revision/hash evidence. Never report a visual pass from a prompt alone, a functional pass from a screenshot alone, or a factual pass from plausible prose alone.

Extract the user's acceptance conditions, protected decisions, requested count and format. Choose the smallest relevant rubric from `../../references/artifact-rubrics.md`. Multiple artifact types can need multiple limited checks; do not run every rubric for every task.

For an exact edit, compare the requested delta and protected properties. For an exploratory solution, judge mechanism, constraints and fit while keeping expected effects unproven. For an analysis or decision, inspect the evidence and reasoning that support the conclusion. For a finished artifact, inspect the form the user will actually receive.

For calculations, formal arguments, explanations and coaching, use the matching
quantitative, formal_reasoning, explanation or coaching rubric. A coaching turn may
be one requested question or feedback, not the full answer. Mixed work needs relevant
checks at the phase they govern: correct arithmetic cannot certify an empirical claim,
and a creative mechanism does not establish numerical feasibility. Required checks
follow consequence and uncertainty, not method count or response length. Missing
verification narrows the conclusion; it is never silently counted as a pass.

When a result claims a numerical improvement, verify the original and proposed
quantities on the same basis and conserve the total available resources. For coaching,
inspect the user's actual attempt and the next interaction's response to its first
material error. Reject a hard-constraint violation, wrong calculation or unfinished
requested output even when it has the right headings, count or method labels.

## Record findings

Each finding uses:

`id; criterion; artifact_location; observation; evidence_reference; consequence; severity; smallest_fix; recheck`

- `critical`: contradicts an explicit hard constraint, misrepresents important evidence or makes the requested artifact unusable.
- `major`: materially weakens the goal, clarity, continuity or function.
- `minor`: limited polish with no material effect on the requested outcome.

These labels describe the observed issue, not a universal rating of the creator. An unsupported load-bearing claim cannot be compensated for by attractive formatting. Treat subjective taste as a recommendation tied to the brief, not an objective failure.

Each applicable check is `pass`, `fail` or `not_checked`; use `not_applicable` only with a reason. Missing tools/evidence are `not_checked`, never a pass or an irrelevant check. Show inspection coverage separately from quality. Do not average unknowns into a reassuring score. No default 80-point SEO checklist or claimed percentile.

## Repair and recheck

Review-only: deliver findings and preserve the source. If the user also requested improvement, fix the highest-impact issues within scope, then inspect the affected criteria and adjacent invariants. Use a bounded review loop proportional to the task; stop when acceptance conditions are met or a real input/tool limit remains. Do not rewrite accepted strengths just to create activity.

Record readiness as one of:

- `ready_for_requested_use`: all required inspected checks pass; disclose any optional checks omitted.
- `revision_needed`: one or more consequential observed issues remain.
- `verification_incomplete`: a required check cannot be performed or lacks evidence. List any known issues as well.

Readiness is scoped to this request. It does not authorize publication, payment, deployment or distribution. It does not prove future performance.

## Output contract

For a requested audit/review report, lead with the verdict and the strongest thing to
preserve. Show consequential findings with specific evidence, the repair when
authorized, and what remains unverified. During embedded verification, return the
needed checks to the conductor without adding a user-facing review section to a
calculation, explanation or coaching turn. The user's requested format and interaction
still control delivery. Include numerical scores only if requested; define the rubric
and keep critical failures and coverage visible outside the score.

## Activation examples

- An operations diagnosis → distinguish observations from root-cause hypotheses, check alternative explanations and whether the proposed intervention addresses the measured bottleneck.
- An investment or strategy choice → inspect constraints, assumptions and sensitivity; do not turn speculative inputs into a measured ROI.
- An experiment → inspect hypothesis, measurement, confounds and decision rules; distinguish a protocol from completed results.
- A revised mascot → compare identity, glasses, palette, facial-feature removal and pose against the approved image; inspect the delivered pixels.
- A film treatment → test causal progression, character choices, knowledge and world continuity; no demand for factual citations for invented events.
- A market article → check source support, dates, argument and voice; no fabricated expertise claims.
- A prototype → exercise the requested interaction and relevant accessibility behavior; a static image cannot prove the click works.
