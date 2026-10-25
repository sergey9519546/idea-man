<div align="center">

<img src="plugins/idea-man/assets/lightbulb-hero-1024.webp" alt="Idea-Man: a faceless cyan lightbulb in round violet glasses and a coral cape" width="280" />

# Idea-Man

### **Every big idea needs a sidekick.**

**The innovation and creative-director plugin for Claude and Codex that finds the non-obvious insight, generates past the clichés, and challenges weak ideas before you commit.**

Bring a business challenge, an engineering contradiction, a research question, an inefficient process, an everyday problem or a creative brief. Idea-Man chooses the work and thinking methods to fit the assignment.

[![Website](https://img.shields.io/badge/Live_Site-Idea--Man-26D9E6?style=flat-square&labelColor=25134D)](https://sergey9519546.github.io/idea-man/)
[![Latest Release](https://img.shields.io/github/v/release/sergey9519546/idea-man?style=flat-square&label=Release&color=4B39F2&labelColor=25134D)](https://github.com/sergey9519546/idea-man/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-FF5878?style=flat-square&labelColor=25134D)](#license)

[**Explore the Site**](https://sergey9519546.github.io/idea-man/) · [**Quick Install**](#install) · [**How the Critic Works**](#why-default-ai-brainstorming-fails) · [**Modes**](#five-ways-to-run-the-room) · [**Skills**](#the-11-skill-architecture)

</div>

---

## Why Default AI Brainstorming Fails

Ten options can still hide one familiar idea. Useful exploration changes the mechanism, tests assumptions and keeps the real constraints in view.

**Idea-Man** operates like a seasoned creative director paired with a ruthless editor:

```text
  YOUR TASK
      |
      v
┌─────────────────────────────────────────────────────────────────┐
│ 1. UNDERSTAND THE ASSIGNMENT                                    │
│ Recover the real job, evidence and constraints.                 │
│ Preserve approved choices and successful qualities.             │
├─────────────────────────────────────────────────────────────────┤
│ 2. CHOOSE THE APPROACH                                          │
│ Match diagnosis, research, invention, comparison or             │
│ execution to the actual task.                                   │
├─────────────────────────────────────────────────────────────────┤
│ 3. CHALLENGE THE WORK                                           │
│ Compare mechanisms, usefulness, requirements and evidence.      │
│ Use independent critique when the host supports and permits it. │
│ Scores never compensate for failed hard requirements.           │
├─────────────────────────────────────────────────────────────────┤
│ 4. TEST OR MAKE WHAT COMES NEXT                                 │
│ Separate a promising direction from a supported commitment.     │
│ Carry out authorized work with available tools and inspect it.  │
└─────────────────────────────────────────────────────────────────┘
```

### What You Actually See

An illustrative concept can look like this. The hypothesis is not a customer finding, the concept is unvalidated, and the test has not been run:

> **Working hypothesis:** Some users may abandon onboarding when configuration comes before their first useful result.
>
> **Concept — "The Inverted Trial"**
> Drop the user directly into a pre-populated, live workspace using synthetic data from their industry. Let them break things first; ask for account setup only when they try to export or save.
> * **Primary Risk:** Synthetic data feels too generic to trigger an "aha" moment for niche verticals.
> * **First Test:** Compare a small set of static industry sandboxes with the existing onboarding flow. Observe first useful actions and confusion; use the findings to decide what to prototype next. Treat a small sample as directional evidence.

---

## Install

### Claude Code (CLI)

Add the marketplace, install the plugin, and invoke the creative director directly from your terminal:

```bash
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
```

**Run your first brief:**

```text
/idea-man:creative-director <your brief, problem, or rough draft>
```

### Claude.ai & Cowork (Web / Desktop)

1. Download **`idea-man-1.2.2.zip`** from the [**latest GitHub release**](https://github.com/sergey9519546/idea-man/releases/latest).
2. In Claude, navigate to **Customize → Plugins → Add → Upload plugin**.
3. Select the downloaded `.zip` archive.

### OpenAI Codex

```bash
codex plugin marketplace add sergey9519546/idea-man --ref main
```

> *After registration, open Plugins, install Idea-Man from the registered marketplace, and start a new session. Public-directory approval is separate; registering a marketplace alone does not activate a plugin.*

---

## Five Ways to Run the Room

Start with the outcome in ordinary language; no mode is required. These optional modes adapt the depth and approach to the task:

| Mode | Best Used When... | What Happens Under the Hood |
| :--- | :--- | :--- |
| **`Full`** | You have a raw problem or high-stakes brief and need vetted solutions. | Frames the assignment, explores distinct mechanisms and compares useful directions. Insight work, scores and development depend on the task and delegated scope. |
| **`Spark`** | You have a blank page and need immediate momentum. | Fires a rapid, high-variance burst of lateral angles without heavy preamble. |
| **`Critique`** | You already have an idea (or three) and want the truth before you build. | Rates, compares, stress-tests, or mercifully kills an existing concept—and tells you how to salvage what survives. |
| **`Unstick`** | You've been staring at the same constraint for three days. | Reframes the problem statement, attacks hidden assumptions, and forces orthogonal entry points. |
| **`Room`** | The problem is multidisciplinary and needs clashing perspectives. | Uses bounded independent thinkers and a critic when the host supports and permits them; otherwise disclosed sequential role passes. |

---

## The 11-Skill Architecture

Under the hood, Idea-Man is a modular suite of 11 specialized skills. **`creative-director`** orchestrates them automatically, or you can invoke individual capabilities for targeted work:

### 1. Framing & Strategy
* **`creative-director`** — The master orchestrator. Understands assignments, selects procedures and coordinates the needed skills.
* **`creative-brief`** — Turns vague requests, stakeholder wishes, and messy context into a sharp, actionable brief.
* **`innovation-strategy`** — Handles causal diagnosis, systems, strategic choices, constraints and testable bets.
* **`research-and-writing`** — Synthesizes supplied or researched sources into traceable findings and clear writing.

### 2. Divergence & Development
* **`concept-variations`** — Generates genuinely distinct territories rather than shallow rewordings of one idea.
* **`concept-development`** — Takes a raw spark and builds out the mechanics, edge cases, and user experience.
* **`creative-project`** — Preserves authorized local briefs, constraints, decisions and pending work for resume.

### 3. Rigor, Taste & Handoff
* **`creative-review`** — Compares mechanisms, usefulness, evidence and feasibility; independent critique depends on host support.
* **`artifact-quality`** — Audits final deliverables for craft, clarity, tone, and structural integrity.
* **`execution-handoff`** — Translates approved concepts into concrete specs, experiments, and next actions.
* **`creative-learning`** — Applies explicit corrections and scoped project preferences without automatic global learning.

---

## Repository Layout & Local Development

```text
idea-man/
├── plugins/idea-man/    # Core plugin manifests, prompts, skills, and assets
├── site/                # Source for the public landing page
├── docs/                # Compiled GitHub Pages output (generated from site/)
├── tests/               # Python behavior and integrity regressions
└── eval/                # Offline comparison harness and synthetic task cases
```

**Building and validating the landing page:**

```bash
node site/build.mjs
node site/validate.mjs
```

---

## Updating an existing installation

Claude Code: `claude plugin update idea-man@idea-man-marketplace`, then restart. In Codex, refresh the registered marketplace with `codex plugin marketplace upgrade <configured-marketplace-name>`, apply the available plugin update in Plugins, and start a new session.

## Candidate decisions and local evaluation

The optional [candidate contract](plugins/idea-man/skills/creative-director/references/candidate-decisions.md) separates hard requirements, shared mechanisms, tradeoffs and readiness for the specific next commitment. It validates host-supplied judgments and grants no execution authority. Python helpers require Python 3.9+ and only the standard library; ordinary skill use does not require Python.

The [offline comparison harness](eval/README.md) checks supplied actual captures and supports blinded reviews. Passing local tests does not establish model-quality superiority. Marketplace submission remains separate from this GitHub release.

---

## License

Released under the **MIT License**.

*Idea-Man is an independent open-source project and is not affiliated with or endorsed by Anthropic or OpenAI.*
