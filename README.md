<a id="idea-man"></a>

<p align="center"><a href="https://sergey9519546.github.io/idea-man/"><img src=".github/assets/idea-man-hero-connected.webp" width="100%" align="top" alt="Idea-Man — Every big idea needs a sidekick. The faceless cyan lightbulb hero flies through a looping cyan ribbon on yellow."></a><a href="#01--install"><img src=".github/assets/nav-install.svg" width="25%" height="64" align="top" alt="Install Idea-Man"></a><a href="#02--modes"><img src=".github/assets/nav-modes.svg" width="25%" height="64" align="top" alt="Explore modes"></a><a href="#03--skills"><img src=".github/assets/nav-skills.svg" width="25%" height="64" align="top" alt="Browse skills"></a><a href="https://sergey9519546.github.io/idea-man/"><img src=".github/assets/nav-website.svg" width="25%" height="64" align="top" alt="Visit the website"></a></p>

**Idea-Man is a free innovation plugin for Claude and Codex.** Bring a problem, a rough idea, or something you want to improve. It helps you understand the assignment, find useful approaches, and turn a chosen direction into practical work.

Use it for business, engineering, research, everyday problems, and creative work. Simple requests stay focused; complex ones can combine investigation, analysis, ideas, and verification.

## 01 / Install

### Codex

Register the repository's plugin marketplace:

```bash
codex plugin marketplace add sergey9519546/idea-man --ref main
```

Then open **Plugins**, install **Idea-Man** from that marketplace, and start a new chat. In Codex CLI, open `/plugins`.

Select **Idea-Man - Innovation Conductor**, or invoke it explicitly:

```text
$idea-man:creative-director Help me understand why our repair shop keeps missing promised dates.
```

Registration adds the marketplace; you still need to install the plugin. These repository installation instructions are separate from an OpenAI public-directory listing.

<details>
<summary>Installed, but the wrong skill opens?</summary>

Use the full `$idea-man:creative-director` name. A bare `$creative-director` can select a different skill with the same name.

If an older Idea-Man marketplace installation exposes the same name, disable that old installation and leave the current one enabled. Preserve its files, then start a new chat.

</details>

### Claude Code

```bash
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
```

Start with:

```text
/idea-man:creative-director Help me understand why our repair shop keeps missing promised dates.
```

### Claude.ai / Cowork

If your client offers plugin ZIP uploads, download the **plugin ZIP** from [GitHub Releases](https://github.com/sergey9519546/idea-man/releases/latest) and use its plugin-upload flow. Choose the release asset, not GitHub's **Source code (zip)** archive.

### Try a task

Start with what you want to accomplish. You can add constraints or choose a mode:

- **Investigate:** “Our repair shop keeps missing promised dates. We can't hire anyone this month. What should we check before changing the schedule?”
- **Explore:** “Spark: give me four ways our library could reduce no-shows for free workshops, without adding staff.”
- **Review:** “Critique this proposal using only the notes below. Tell me what holds up, what's uncertain, and what needs changing. Don't rewrite it yet.”

## 02 / Modes

Start in plain language. For a particular kind of help, add one of these mode names:

- **Full** — Work through a substantial new problem: clarify the assignment, explore distinct approaches, and compare them. Develop a chosen direction when requested.
- **Spark** — Get a quick burst of alternatives or a fresh riff. You set the count and constraints.
- **Critique** — Review existing work: what's strong, what falls short, and what needs evidence. Review alone doesn't authorize a rewrite.
- **Unstick** — Find the assumption or repeated approach that's keeping you stuck, then try a useful change.
- **Room** — Bring in independent perspectives when host agents are available and authorized. Otherwise, Idea-Man makes clear that it's using sequential self-review.

Modes guide the approach while preserving your constraints. Calculations, evidence reviews, and precise edits keep the workflows they need.

[Read the mode guidance](plugins/idea-man/skills/creative-director/references/ideation-engine.md#choose-the-work) · [Agent and Room boundaries](plugins/idea-man/skills/creative-director/references/room-protocol.md)

## 03 / Skills

The conductor selects the specialists needed for the task. All **11 skills** are also available individually:

- [**creative-director**](plugins/idea-man/skills/creative-director/SKILL.md) — Understand the assignment and coordinate the work.
- [**creative-brief**](plugins/idea-man/skills/creative-brief/SKILL.md) — Clarify the outcome, constraints, and decisive unknowns.
- [**innovation-strategy**](plugins/idea-man/skills/innovation-strategy/SKILL.md) — Work through systems, causes, tradeoffs, decisions, and experiments.
- [**research-and-writing**](plugins/idea-man/skills/research-and-writing/SKILL.md) — Synthesize evidence and write with traceable sources.
- [**concept-variations**](plugins/idea-man/skills/concept-variations/SKILL.md) — Explore alternatives while preserving what you've locked.
- [**creative-review**](plugins/idea-man/skills/creative-review/SKILL.md) — Compare ideas against the assignment and its requirements.
- [**artifact-quality**](plugins/idea-man/skills/artifact-quality/SKILL.md) — Check the actual deliverable for defects and gaps.
- [**concept-development**](plugins/idea-man/skills/concept-development/SKILL.md) — Develop the chosen direction while preserving approved strengths.
- [**creative-learning**](plugins/idea-man/skills/creative-learning/SKILL.md) — Apply feedback within its stated scope and exceptions.
- [**execution-handoff**](plugins/idea-man/skills/execution-handoff/SKILL.md) — Produce authorized work or prepare a concrete handoff.
- [**creative-project**](plugins/idea-man/skills/creative-project/SKILL.md) — Save authorized local project records and resume from them.

The [17 thinking methods](plugins/idea-man/references/innovation-registry.json) include reframing, inversion, subtraction, analogy, systems reasoning, first principles, contradiction resolution, and experiments. The task determines which methods help; scores are optional.

## What to expect

- **Work matched to the request.** A brief answer can stay brief. A difficult problem may need investigation, calculation, alternatives, and checks in different phases.
- **Your choices stay yours.** Approved decisions and constraints are preserved. A recommendation isn't permission to execute it.
- **Evidence stays visible.** Ideas, predictions, and scores are judgments until supported by evidence. A plan isn't an executed test.
- **Tools come from the host.** Idea-Man has no separate hosted service. Production and agent work depend on the tools and permissions available in your session.
- **Continuity has limits.** Authorized local records can support return visits. Idea-Man can't recover unseen chat history or guarantee that context is never lost.

## Evidence and limitations

The [evaluation tools](eval/README.md) check supplied captures and support blinded review. Passing local tests does not establish superior ideas or successful activation in every host.

The [worked examples](eval/examples/README.md) cover diagnosis, decision sensitivity, and pilot review, with checked arithmetic and local readiness-helper results. They are authored synthetic examples, not captured model runs or customer validation. The [evidence page](https://sergey9519546.github.io/idea-man/evidence/) links the source conversations and their limits.

## Development

**Current release: [v1.2.4](https://github.com/sergey9519546/idea-man/releases/tag/v1.2.4).** Repository changes reach installed copies only through a separate plugin update.

```text
plugins/idea-man/   Plugin instructions, skills, helpers, and assets
site/              Landing-page source
docs/              Generated GitHub Pages output
tests/             Python regression tests
eval/              Evaluation tools and worked examples
```

Generate the website from `site/`; don't edit the generated `docs/` files directly:

```bash
node site/build.mjs
node site/validate.mjs
```

Run the local checks:

```bash
python -m unittest discover -s tests
python eval/worked_examples.py --check
```

Ordinary skill use doesn't require Python. Optional local helpers require Python 3.9+ and the standard library. See the [candidate contract](plugins/idea-man/skills/creative-director/references/candidate-decisions.md) for the helper's evidence and readiness boundaries.

<details>
<summary>Update an existing installation</summary>

**Claude Code:** run `claude plugin update idea-man@idea-man-marketplace`, then restart.

**Codex:** refresh the registered marketplace with `codex plugin marketplace upgrade <configured-marketplace-name>`, apply the available update in **Plugins**, and start a new session.

</details>

Brand artwork and usage rules live in the [brand guide](plugins/idea-man/assets/brand-guide.md). The public website excludes the brand-kit page.

## License

[MIT](LICENSE). Not affiliated with or endorsed by Anthropic or OpenAI.
