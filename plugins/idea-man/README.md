# Idea-Man

*Every big idea needs a sidekick.*

Idea-Man is a free innovation and creative director for business, engineering, research,
film, series, music videos, ads, products, games and everyday problems. It helps diagnose
the assignment, find the insight, develop distinct approaches and choose practical next
steps. Independent thinker and blind-critic passes are optional and depend on the host's
agent capabilities. When agents are unavailable, sequential role passes can be used with
the limitation stated. Creative scores are judgments, not measured audience results.

By Sergey Avetisyan. Not endorsed by Anthropic or OpenAI.

## Install

- **Claude Code:** `claude plugin marketplace add sergey9519546/idea-man`, then
  `claude plugin install idea-man@idea-man-marketplace`. Run `/idea-man:creative-director <brief>`.
- **Claude.ai / Cowork:** Customize → Plugins → Add → Upload plugin, then choose a published plugin ZIP from the [GitHub Releases page](https://github.com/sergey9519546/idea-man/releases/latest). Version 1.2.2 is available from GitHub Releases.
- **Codex:** `codex plugin marketplace add sergey9519546/idea-man --ref main` Then restart the app, choose the Idea-Man marketplace in the Plugins Directory and install it. In Codex CLI, open /plugins. Start a new session before use. Public-directory publication follows a separate review process.


## Start with the job

Use `/idea-man:creative-director <what you want to change>` in Claude Code.
In other hosts, invoke the installed creative-director skill with your request.
Describe the outcome in ordinary language; no mode or thinking method is required.

- **Understand evidence:** "Use these interviews to explain why customers abandon setup.
  Separate what they said from your interpretation; do not invent additional research."
- **Make a choice:** "Compare a subscription and a one-time purchase for this product.
  Use our costs and constraints; show which missing fact could change the recommendation."
- **Fix a process:** "Our repair shop keeps missing dates. Use this job log to investigate
  the cause before proposing fixes, then suggest a small test with our existing staff."

The same entry supports developing a chosen concept, making an exact edit, or continuing
an authorized saved project. Supply the sources and constraints you already have.
For an uncertain idea, ask for a useful test; return with actual observations to review
what they support and decide the next step. A proposed test is not a completed one.

Optional modes: full session, quick spark, critique, unstick, and room (independent thinkers and
blind critique where host agents are available; otherwise disclosed sequential role passes). Scores are creative judgments, not predictions of audience response.

## How it chooses the work

The Innovation Conductor reads the active conversation and actual source material. It
distinguishes the requested outcome, problem shape, bottleneck, evidence, stage, hard
constraints, preferences, stakes and tool availability. It then selects a specialist and
thinking procedure with a concrete output. A causal problem can call for diagnosis;
an uncertain commitment can call for an experiment; a precise edit bypasses brainstorming.

The original 17 thinking modes remain available: reframing, inversion, subtraction,
provocation, connection, convention mapping, contradiction resolution, constrained
invention, systems leverage, causes/first principles, stakeholder perspective, perception,
experience mining, sequencing, repeatable mechanisms, divergence and testing. User-requested
methods take precedence within the assignment's scope.

## Eleven integrated skills

| Skill | Role |
|---|---|
| creative-director | Innovation Conductor: context, assignment, method and workflow selection |
| innovation-strategy | Diagnosis, invention, systems, decisions, experiments and practical development |
| research-and-writing | Supplied/live/mixed evidence, sourced writing and voice preservation |
| artifact-quality | Evidence-backed checks for analysis, decisions, experiments, processes, writing, media and code |
| creative-learning | Explicit corrections, scoped preferences, exceptions and workflow lessons |
| creative-brief | Desired outcome, constraints, assumptions and decisive unknown |
| concept-variations | Requested alternatives with protected invariants and distinct mechanisms |
| creative-review | Concept comparison, tradeoffs and useful critique |
| concept-development | Expand a selected direction into its domain-specific result |
| execution-handoff | Bind execution inputs and create requested artifacts with actual host tools |
| creative-project | Authorized local save/resume with revision-checked project history |

## Planner and continuity

An optional standard-library Python 3.9+ planner accepts a versioned assessment produced by
the host model. Version 2 resolves packaged specialists and method contracts, handles
supplied-source research without web access, restores inspected pending actions, and
supports independent or dependent workstreams. It validates implicit mixed-output
capabilities and binds completion receipts to source/output versions and task inputs.

Content type and delivery are separate: delivery_mode supports inline text/code or
an authored artifact. Research findings, recommendations, experiment plans and review
reports requested as artifacts include production and checks of the actual output.
Inline code needs no file-writing capability; text/code files do. Code output keeps
code checks. Authoring a report does not authorize editing its source, committing a
candidate, running code or changing a database.

live_research_dependency distinguishes independent queries from source-bound queries.
Mixed evidence or supplied inputs default to source-bound preparation; declare an
independent query only when its required terms and scope are already available.
Missing local inputs can block their dependent query while other work continues.
Both fields participate in receipt bindings; changed contracts require reinspection.
Actions describe operations, not phase order; use dependent workstreams when the
user's requested sequence differs from the planner's standard template.

The helper does not classify raw language, execute providers or certify the truth of an
inspection note. Version 1 assessments remain supported for compatibility. New work should
use the v2 schema under skills/creative-director/references/router-schema-v2.md.

Project records remain optional and local. Explicit corrections can be stored as scoped
note events with evidence and exceptions. No background observer, raw-prompt logging,
automatic global promotion, model training or cross-chat sync is installed. Multiple
approved options stay approved. A status question preserves unfinished work.

## Execution and evidence

Production uses the tools actually available in the host. A prompt/plan is not a produced
image, running prototype, measured experiment or published result. Missing capabilities
are reported while independent useful work continues. Ideas and causal explanations
remain hypotheses until the relevant evidence supports them.

The approved Invisible Nerd and faceless Lightbulb Hero identify Idea-Man. Their bright
identity is not imposed on customer projects. Both approved assets are included.

## Version and validation

Package version 1.2.2 is released on GitHub; public-directory review is separate.
Mechanical tests, source-conditioned conversation probes, independent grading and host
initialization checks are separate evidence. They do not establish automatic skill
activation, semantic routing accuracy or end-to-end execution. No claim of perfect or
"20x" recognition is made. Older task-wide v2 receipts must be reinspected and reminted;
see the receipt compatibility section in the v2 assessment reference.

## Brand kit and orchestration

[Open the packaged brand kit](assets/brand-kit.html) for the approved mascots, palette, typography and icon previews. Every skill carries both approved character icons.

[Orchestration and tool connections](references/orchestration.md) explains how the conductor assigns specialists, passes constraints and evidence, schedules dependencies and checks results. Available host tools supply execution capabilities; the plugin does not create external service connections.

## Selective supplementary craft references

The eleven skills and seventeen thinking modes now include selectively loaded framing, structural transformation, review-lens, sketch, narrative and calibration procedures. These are optional craft inside the existing task routes: requested scope/count, approved references, evidence requirements and actual host capabilities govern. They add no new method IDs, mandatory method combinations or performance claims. See skills/creative-director/references/supplementary-methods.md, storytelling-frameworks.md and scoring-calibration.md in that same reference directory.
## 1.2.2 repair follow-up

The latest local repairs require dependent workstreams to await all required upstream
work, ignore recognized obsolete step receipts after an action change while rejecting
unsupported IDs and malformed evidence, and support receipt continuity for authorized
in-place source edits. The last is opt-in: capture begin-step
evidence before editing. Retain accepted upstream outputs as versioned immutable
artifacts and revise a separately identified working copy. See the
[v2 schema and snapshot contract](skills/creative-director/references/router-schema-v2.md)
for the exact fields, commands and limits; helpers do not grant edit authority.

Active guidance now selects v2 for complex jobs and respects requested methods/counts,
optional scores and honest exploration. Historical agency scales do not predict awards.
Installation guidance distinguishes release ZIPs from repository registration
and documents Codex main-ref registration and a fresh session. Structural
checks and source-conditioned probes remain separate from installed-host behavior.

## Compare ideas and choose the next commitment

For consequential choices, compare mechanism, usefulness, hard requirements and evidence
separately. A promising idea may justify a small test before a larger investment; an
authorized prototype does not need proof of market demand. Exact edits and quick requests
need no scoring ceremony.

The optional [candidate decision helper](skills/creative-director/references/candidate-decisions.md)
reports hard failures, missing evidence, shared mechanisms, ties and tradeoffs for a
specific explore/test/make commitment. It checks host-supplied judgments, not their truth,
and grants no approval or tool authority. Source inspection and the actual task still govern.
