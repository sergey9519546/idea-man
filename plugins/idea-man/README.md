# Idea Man

*Every big idea needs a sidekick.*

Idea Man is a free creative director for film, series, music videos, ads, products, games
and stubborn business problems. It diagnoses the problem, finds the insight first, casts
structural methods from real master thinkers, and generates far past the obvious. A separate
blind critic then scores every idea on a calibrated scale. Only ideas scoring 7+ are
presented, each with its risks and the cheapest test.

Modes: full session, quick spark, critique, unstick, and room (parallel thinkers plus a
blind critic). Scores are creative judgments, not predictions of audience response.
By Sergey Avetisyan. Not endorsed by Anthropic or OpenAI.

## Install

- **Claude Code:** `claude plugin marketplace add sergey9519546/idea-man`, then
  `claude plugin install idea-man@idea-man-marketplace`. Run `/idea-man:creative-director <brief>`.
- **Claude.ai / Cowork:** Customize → Plugins → Add → Upload plugin, then choose idea-man-1.2.1.zip from the [GitHub Releases page](https://github.com/sergey9519546/idea-man/releases/latest).
- **Codex:** `codex plugin marketplace add sergey9519546/idea-man --ref main` (Codex directory listing is pending review).


## Start with the outcome

- "Our repair shop keeps missing dates. Help us figure out why before proposing fixes."
- "Find five business models for this unused equipment, using the resources we already have."
- "Resolve this engineering contradiction: lower weight without losing impact resistance."
- "Use only these interviews to write a findings memo."
- "Choose the cheapest useful test of these two strategies."
- "Give me six different mechanisms, using analogy rather than cosmetic variations."
- "Keep the approved glasses and colors; change only the bulb silhouette."
- "Continue the selected pilot plan from our saved project record."

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

An optional standard-library Python planner accepts a versioned assessment produced by
the host model. Version 2 resolves packaged specialists and method contracts, handles
supplied-source research without web access, restores inspected pending actions, and
supports independent or dependent workstreams. It validates implicit mixed-output
capabilities and binds completion receipts to source/output versions and task inputs.

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

The approved Invisible Nerd and faceless Lightbulb Hero identify Idea Man. Their bright
identity is not imposed on customer projects. Both approved assets are included.

## Version and validation

Package version 1.2.1. Mechanical regression tests and fresh-context conversation replays
are recorded separately in the release report. Model replays are not installed ChatGPT
runtime or external-tool end-to-end tests. No claim of perfect or "20x" recognition is made.

## Brand kit and orchestration

[Open the packaged brand kit](assets/brand-kit.html) for the approved mascots, palette, typography and icon previews. Every skill carries both approved character icons.

[Orchestration and tool connections](references/orchestration.md) explains how the conductor assigns specialists, passes constraints and evidence, schedules dependencies and checks results. Available host tools supply execution capabilities; the plugin does not create external service connections.
