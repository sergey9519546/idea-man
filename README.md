<div align="center">

<img src="plugins/idea-man/assets/lightbulb-hero-1024.webp" alt="Idea Man: a faceless cyan lightbulb in round violet glasses and a coral cape" width="280" />

# IDEA MAN

### **Every big idea needs a sidekick.**

**The creative-director plugin for Claude and Codex that finds the non-obvious insight, generates past the clichés, and uses a blind critic to kill weak ideas before you ever see them.**

[![Website](https://img.shields.io/badge/Live_Site-idea--man-06B6D4?style=flat-square&labelColor=0F172A)](https://sergey9519546.github.io/idea-man/)
[![Latest Release](https://img.shields.io/github/v/release/sergey9519546/idea-man?style=flat-square&label=Release&color=7C3AED&labelColor=0F172A)](https://github.com/sergey9519546/idea-man/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-FF6B6B?style=flat-square&labelColor=0F172A)](#license)

[**Explore the Site**](https://sergey9519546.github.io/idea-man/) · [**Quick Install**](#install) · [**How the Critic Works**](#why-default-ai-brainstorming-fails) · [**Modes**](#five-ways-to-run-the-room) · [**Skills**](#the-11-skill-architecture)

</div>

---

## Why Default AI Brainstorming Fails

Ask a standard LLM for ten ideas and you get ten polite variations of the first cliché in its training data. It optimizes for agreement, not breakthroughs.

**Idea Man** operates like a seasoned creative director paired with a ruthless editor:

```text
  YOUR BRIEF
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. DIAGNOSE & INSIGHT                                           │
│    Strips away surface symptoms to isolate the real tension.    │
├─────────────────────────────────────────────────────────────────┤
│ 2. LATERAL GENERATION                                           │
│    Pushes past the obvious using frameworks from master         │
│    thinkers, strategists, and inventors.                        │
├─────────────────────────────────────────────────────────────────┤
│ 3. THE BLIND CRITIC (The 7+ Filter)                             │
│    An independent evaluator scores every candidate cold.        │
│    Anything scoring below 7/10 is killed on the cutting-room    │
│    floor. You only see the survivors.                           │
├─────────────────────────────────────────────────────────────────┤
│ 4. PRE-MORTEM & CHEAPEST TEST                                   │
│    Every surviving idea ships with its biggest failure risk     │
│    and the fastest, lowest-cost way to prove it works.          │
└─────────────────────────────────────────────────────────────────┘
```

### What You Actually See

Instead of a wall of generic bullet points, a typical survivor looks like this:

> **The Insight:** Users don't abandon onboarding because it's too long; they abandon it because it asks for configuration before delivering a single moment of value.
>
> **Concept — "The Inverted Trial" (Critic Score: 8.4/10)**
> Drop the user directly into a pre-populated, live workspace using synthetic data from their industry. Let them break things first; ask for account setup only when they try to export or save.
> * **Primary Risk:** Synthetic data feels too generic to trigger an "aha" moment for niche verticals.
> * **Cheapest Test:** Build 3 static industry sandboxes in Figma/HTML and run 5 unmoderated 3-minute user sessions before touching backend auth.

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

1. Download **`idea-man-1.2.1.zip`** from the [**latest GitHub release**](https://github.com/sergey9519546/idea-man/releases/latest).
2. In Claude, navigate to **Customize → Plugins → Add → Upload plugin**.
3. Select the downloaded `.zip` archive.

### OpenAI Codex

```bash
codex plugin marketplace add sergey9519546/idea-man --ref main
```

> *Note: The official Codex plugin directory listing is currently pending review. Direct installation via `--ref main` works today.*

---

## Five Ways to Run the Room

Idea Man adapts to where you are in the creative process. Trigger a specific mode depending on whether you need a full campaign or a brutal reality check:

| Mode | Best Used When... | What Happens Under the Hood |
| :--- | :--- | :--- |
| **`Full`** | You have a raw problem or high-stakes brief and need vetted solutions. | Runs the complete sequence: **Diagnose → Insight → Generate → Blind Critique (7+) → Present** with risks and cheapest tests. |
| **`Spark`** | You have a blank page and need immediate momentum. | Fires a rapid, high-variance burst of lateral angles without heavy preamble. |
| **`Critique`** | You already have an idea (or three) and want the truth before you build. | Rates, compares, stress-tests, or mercifully kills an existing concept—and tells you how to salvage what survives. |
| **`Unstick`** | You've been staring at the same constraint for three days. | Reframes the problem statement, attacks hidden assumptions, and forces orthogonal entry points. |
| **`Room`** | The problem is multidisciplinary and needs clashing perspectives. | Spins up parallel thinkers with distinct mental models simultaneously, refereed by a blind critic. |

---

## The 11-Skill Architecture

Under the hood, Idea Man is a modular suite of 11 specialized creative skills. **`creative-director`** orchestrates them automatically, or you can invoke individual capabilities for targeted work:

### 1. Framing & Strategy
* **`creative-director`** — The master orchestrator. Routes briefs, selects modes, and enforces the quality bar.
* **`creative-brief`** — Turns vague requests, stakeholder wishes, and messy context into a sharp, actionable brief.
* **`innovation-strategy`** — Maps market tensions, competitive blind spots, and high-leverage strategic bets.
* **`research-and-writing`** — Synthesizes background domain knowledge and sharpens narrative arguments.

### 2. Divergence & Development
* **`concept-variations`** — Generates genuinely distinct territories rather than shallow rewordings of one idea.
* **`concept-development`** — Takes a raw spark and builds out the mechanics, edge cases, and user experience.
* **`creative-project`** — Structures multi-step creative initiatives across phases and deliverables.

### 3. Rigor, Taste & Handoff
* **`creative-review`** — Runs the blind critic loop to score, compare, and prune concepts below the 7+ threshold.
* **`artifact-quality`** — Audits final deliverables for craft, clarity, tone, and structural integrity.
* **`execution-handoff`** — Translates approved concepts into concrete specs, experiments, and next actions.
* **`creative-learning`** — Captures post-mortem insights and patterns to sharpen future creative cycles.

---

## Repository Layout & Local Development

```text
idea-man/
├── plugins/idea-man/    # Core plugin manifests, prompts, skills, and assets
├── site/                # Source for the public landing page
├── docs/                # Compiled GitHub Pages output (generated from site/)
└── tests/               # Python test suite validating plugin structure & integrity
```

**Building and validating the landing page:**

```bash
node site/build.mjs
node site/validate.mjs
```

---

## License

Released under the **MIT License**.

*Idea Man is an independent open-source project and is not affiliated with or endorsed by Anthropic or OpenAI.*
