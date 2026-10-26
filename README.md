<a id="idea-man"></a>

<p align="center"><a href="https://sergey9519546.github.io/idea-man/"><img src=".github/assets/idea-man-hero-connected.webp" width="100%" align="top" alt="Idea-Man — Every big idea needs a sidekick. The faceless cyan lightbulb hero flies through a looping cyan ribbon on yellow."></a><a href="#01--install"><img src=".github/assets/nav-install.svg" width="25%" height="64" align="top" alt="Install Idea-Man"></a><a href="#02--modes"><img src=".github/assets/nav-modes.svg" width="25%" height="64" align="top" alt="Explore modes"></a><a href="#03--skills"><img src=".github/assets/nav-skills.svg" width="25%" height="64" align="top" alt="Browse skills"></a><a href="https://sergey9519546.github.io/idea-man/"><img src=".github/assets/nav-website.svg" width="25%" height="64" align="top" alt="Visit the website"></a></p>

**Idea-Man is a free innovation partner for Claude and Codex.** Bring a business problem, an engineering tradeoff, a research question, an everyday roadblock or a creative brief. It helps you understand what needs to change, find different ways forward, and develop the direction you choose.

## See it at work

Two recorded Codex tests using fictional briefs, with Idea-Man 1.2.4. [Full prompts, responses and test limits](eval/captured/README.md).

<table>
<tr><td><img src=".github/assets/demo-diagnosis.svg" width="100%" height="84" alt="Find the real delay. Recorded operations test."></td></tr>
<tr><td>

**The problem**

A repair shop finished 40 jobs; 18 were late. Parts arrived late for 12 of them. For six, parts were ready but work sat for three days. The shop has one scheduler, three mechanics and no hiring or software budget.

</td></tr>
<tr><td>

**The response**

> The evidence shows **two delay points, but doesn’t establish one overall bottleneck**.

The response proposes a seven-day paper-queue test with the existing team. A five-minute morning review gives ready jobs an owner and a start slot. The success measure includes jobs still waiting at the end.

[Read the captured response →](eval/captured/README.md#noncreative-diagnosis)

</td></tr>
</table>

<table>
<tr><td colspan="2"><img src=".github/assets/demo-concepts.svg" width="100%" height="84" alt="Give a brief three lives. Recorded creative test."></td></tr>
<tr><td colspan="2">

**The brief:** three poster concepts for a free neighborhood repair café. Keep the event details. No tools in the artwork, no nostalgia, and no guaranteed-repair promise.

The recorded response offered three different visual approaches:

</td></tr>
<tr><td width="35%" valign="top"><b>Bring Your Broken</b></td><td>A single dented toaster photographed against coral.</td></tr>
<tr><td valign="top"><b>Neighbors Helping Neighbors</b></td><td>An overhead illustration of people around a repair table.</td></tr>
<tr><td valign="top"><b>Let’s Take a Look</b></td><td>A cobalt question mark with a kettle forming its dot.</td></tr>
<tr><td colspan="2">

The event details stay in all three directions. The response leaves the choice to the user; it supplies concepts, not finished posters.

[Read the captured response →](eval/captured/README.md#constrained-creative)

</td></tr>
</table>

## 01 / Install

Choose the host you use. Install Idea-Man there, then start a fresh chat.

<table width="100%">
<tr><th align="left" width="100%"><img src="https://img.shields.io/badge/OPENAI-CODEX-26D9E6?style=flat-square&labelColor=25134D" alt="Codex"></th></tr>
<tr><td>

Add the plugin marketplace from `main`:

```bash
codex plugin marketplace add sergey9519546/idea-man --ref main
```

Open **Plugins** (or `/plugins` in Codex CLI), install **Idea-Man**, and start a new chat.

Select **Idea-Man - Innovation Conductor**, or type `$idea-man:creative-director` followed by your task.

Registration adds the marketplace; installation enables the plugin. This repository route is separate from public-directory approval.

</td></tr>
</table>

<table width="100%">
<tr><th align="left" width="100%"><img src="https://img.shields.io/badge/CLAUDE_CODE-CLI-F6F43C?style=flat-square&labelColor=25134D" alt="Claude Code"></th></tr>
<tr><td>

Add the marketplace and install the plugin:

```bash
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
```

Then use `/idea-man:creative-director` followed by your task.

</td></tr>
</table>

<table width="100%">
<tr><th align="left" width="100%"><img src="https://img.shields.io/badge/CLAUDE.AI_%2F_COWORK-ZIP-FF5878?style=flat-square&labelColor=25134D" alt="Claude.ai / Cowork"></th></tr>
<tr><td>

If your client offers plugin ZIP uploads, download the **plugin ZIP** from [**GitHub Releases ↗**](https://github.com/sergey9519546/idea-man/releases/latest) and use its plugin-upload flow. Choose the release asset rather than **Source code (zip)**.

<br>

[![Download Latest Release](https://img.shields.io/badge/Download-Plugin_ZIP_%E2%86%93-F6F43C?style=flat-square&labelColor=25134D)](https://github.com/sergey9519546/idea-man/releases/latest)

</td></tr>
</table>

<details>
<summary><b>Your first task</b></summary>

Describe what you want and what must stay fixed. For example:

> Spark: give me four ways our library could reduce workshop no-shows without adding staff.

Or bring work you want reviewed:

> Critique the proposal below using only my notes. Show me what holds up and what needs changing. Don’t rewrite it yet.

</details>

<details>
<summary><b>Installed, but the wrong skill opens?</b></summary>

In Codex, use the full `$idea-man:creative-director` name. A bare `$creative-director` can select a different skill. If an older Idea-Man installation exposes the same name, disable that old installation, preserve its files, and start a new chat with the current version enabled.

</details>

---

## 02 / Modes

Start with the outcome in ordinary language, or name a mode. Your task and constraints still govern the work.

<table>
<tr>
<td width="50%" valign="top">

![Mode 01: Full](https://img.shields.io/badge/MODE_01-FULL-F6F43C?style=flat-square&labelColor=25134D)

### Full
Frame a substantial assignment, explore distinct approaches, and compare them. Develop a chosen direction within the scope you've given.

</td>
<td width="50%" valign="top">

![Mode 02: Spark](https://img.shields.io/badge/MODE_02-SPARK-26D9E6?style=flat-square&labelColor=25134D)

### Spark
A quick burst of alternatives or a fresh riff. You set the count and constraints.

</td>
</tr>
<tr>
<td width="50%" valign="top">

![Mode 03: Critique](https://img.shields.io/badge/MODE_03-CRITIQUE-FF5878?style=flat-square&labelColor=25134D)

### Critique
Review existing work: what's strong, what falls short, and what needs evidence. Review alone doesn't authorize a rewrite.

</td>
<td width="50%" valign="top">

![Mode 04: Unstick](https://img.shields.io/badge/MODE_04-UNSTICK-4B39F2?style=flat-square&labelColor=25134D)

### Unstick
Find the assumption or repeated approach that's keeping you stuck, then try a useful change.

</td>
</tr>
<tr>
<td colspan="2" valign="top">

![Mode 05: Room](https://img.shields.io/badge/MODE_05-ROOM-F6F43C?style=flat-square&labelColor=25134D)

### Room
Independent perspectives when host agents are available and authorized. Otherwise, Idea-Man makes clear that it's using sequential self-review.

</td>
</tr>
</table>

Calculations, evidence reviews, and precise edits keep the workflows they need. [Read the mode guidance](plugins/idea-man/skills/creative-director/references/ideation-engine.md#choose-the-work).

---

<a id="the-promise"></a>

## How it works

<table>
<tr>
<td width="45%" valign="top">

### Insight first. Only ideas worth making.

Bring a half-formed thought, a rough draft, or a direction you already love. Idea-Man starts by working out what you need: an answer, an investigation, new approaches, a decision, or help making the next piece.

Tell it what must stay. An approved choice, a budget, a source restriction, or a detail you love should shape what happens next.

The task determines the depth. A calculation or precise edit can stay brief. A harder assignment can combine research, analysis, ideas and checks.

</td>
<td width="55%" valign="top">

### Big idea. Next move.

![Understand](https://img.shields.io/badge/01-Understand-F6F43C?style=flat-square&labelColor=25134D) → ![Explore](https://img.shields.io/badge/02-Explore-26D9E6?style=flat-square&labelColor=25134D) → ![Critique](https://img.shields.io/badge/03-Critique-FF5878?style=flat-square&labelColor=25134D) → ![Develop](https://img.shields.io/badge/04-Develop-4B39F2?style=flat-square&labelColor=25134D) → ![Make](https://img.shields.io/badge/05-Make-F6F43C?style=flat-square&labelColor=25134D)

1. **Understand** what you’re trying to accomplish and what’s getting in the way.
2. **Explore** useful approaches, with research or different thinking methods where they help.
3. **Critique** the options against your requirements and the available evidence.
4. **Develop** the direction you choose, keeping approved strengths intact.
5. **Make** the result with available tools, or prepare a clear handoff.

These stages are selected to fit the task. You don’t need to work through all five for every request.

</td>
</tr>
</table>

---

## 03 / Skills

**11 skills** support the work behind the scenes. Idea-Man selects the useful ones for your task; each is also linked below if you want to inspect or invoke it directly.

The [17 thinking methods](plugins/idea-man/references/innovation-registry.json) include reframing, analogy, systems reasoning, first principles and experiments. The task determines which methods help; scores are optional.

| Stage | Skills | What they help with |
| :--- | :--- | :--- |
| ![](https://img.shields.io/badge/01-Understand-F6F43C?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/creative-director/SKILL.md"><kbd>creative-director</kbd></a> <a href="plugins/idea-man/skills/creative-brief/SKILL.md"><kbd>creative-brief</kbd></a> <a href="plugins/idea-man/skills/research-and-writing/SKILL.md"><kbd>research-and-writing</kbd></a> <a href="plugins/idea-man/skills/innovation-strategy/SKILL.md"><kbd>innovation-strategy</kbd></a> | Work out the task, clarify the brief, examine evidence and choose an approach. |
| ![](https://img.shields.io/badge/02-Explore-26D9E6?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/concept-variations/SKILL.md"><kbd>concept-variations</kbd></a> | Explore different approaches, or vary only the details you allow. |
| ![](https://img.shields.io/badge/03-Critique-FF5878?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/creative-review/SKILL.md"><kbd>creative-review</kbd></a> <a href="plugins/idea-man/skills/artifact-quality/SKILL.md"><kbd>artifact-quality</kbd></a> | Compare options and check the actual work against your requirements. |
| ![](https://img.shields.io/badge/04-Develop-4B39F2?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/concept-development/SKILL.md"><kbd>concept-development</kbd></a> <a href="plugins/idea-man/skills/creative-learning/SKILL.md"><kbd>creative-learning</kbd></a> | Develop your chosen direction and apply feedback without losing what works. |
| ![](https://img.shields.io/badge/05-Make-F6F43C?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/execution-handoff/SKILL.md"><kbd>execution-handoff</kbd></a> | Make the requested result with available tools, or give the next person a usable brief. |
| ![](https://img.shields.io/badge/06-Continue-26D9E6?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/creative-project/SKILL.md"><kbd>creative-project</kbd></a> | Save project decisions locally when you authorize it, then resume from those records. |

<details>
<summary><b>View flat list of all 11 skills</b></summary>
<br>

`creative-director`, `creative-brief`, `concept-variations`, `concept-development`, `creative-review`, `artifact-quality`, `research-and-writing`, `innovation-strategy`, `creative-learning`, `execution-handoff`, `creative-project`.

</details>

---

## 04 / Voice

<table>
<tr>
<td width="42%" valign="top">

### **Curious. Candid. Useful.**

A sharp creative partner with a sense of play. Ask the question that matters. Explain the choice. Give the person something they can use.

<br>

> *Keep the superhero spirit in the imagery. In conversation, use plain language and honest judgments.*

</td>
<td width="58%" valign="top">

![](https://img.shields.io/badge/INVITATION-F6F43C?style=flat-square&labelColor=25134D)

**“Give me the rough version.”**

![](https://img.shields.io/badge/EXPLORATION-26D9E6?style=flat-square&labelColor=25134D)

**“Six directions. Each changes the idea, not just the wording.”**

![](https://img.shields.io/badge/CRITIQUE-FF5878?style=flat-square&labelColor=25134D)

**“The hook works. The payoff needs a clearer turn.”**

![](https://img.shields.io/badge/DEVELOPMENT-4B39F2?style=flat-square&labelColor=25134D)

**“Keep the part you love. Let's build the next piece around it.”**


</td>
</tr>
</table>

---

## Evidence and limitations

The [captured examples](eval/captured/README.md) record two existing Codex tests with synthetic prompts. They show those sessions’ responses and observed guidance reads, not a general success rate or a comparison with an ordinary assistant. No customer outcomes are claimed.

The [evaluation tools](eval/README.md) support comparisons using actual captures. Local checks alone do not establish superior ideas or activation in every host.

The [worked examples](eval/examples/README.md) cover diagnosis, decision sensitivity, and pilot review, with checked arithmetic and local readiness-helper results. They are authored synthetic examples, not captured model runs or customer validation. The [evidence page](https://sergey9519546.github.io/idea-man/evidence/) links the source conversations and their limits.

## Support

For installation help, see the [support guide](https://sergey9519546.github.io/idea-man/support/). Report a reproducible problem through [GitHub Issues](https://github.com/sergey9519546/idea-man/issues).

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
