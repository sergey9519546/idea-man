<a id="idea-man"></a>

<p align="center"><a href="https://sergey9519546.github.io/idea-man/"><img src=".github/assets/idea-man-hero-connected.webp" width="100%" align="top" alt="Idea-Man — Every big idea needs a sidekick. The faceless cyan lightbulb hero flies through a looping cyan ribbon on yellow."></a><a href="#01--install"><img src=".github/assets/nav-install.svg" width="25%" height="64" align="top" alt="Install Idea-Man"></a><a href="#02--modes"><img src=".github/assets/nav-modes.svg" width="25%" height="64" align="top" alt="Explore modes"></a><a href="#03--skills"><img src=".github/assets/nav-skills.svg" width="25%" height="64" align="top" alt="Browse skills"></a><a href="https://sergey9519546.github.io/idea-man/"><img src=".github/assets/nav-website.svg" width="25%" height="64" align="top" alt="Visit the website"></a></p>

## The Promise

<table>
<tr>
<td width="52%" valign="top">

### **Insight first. Only ideas worth making.**

**Idea-Man** is a free innovation and creative-director plugin for Claude and Codex. It understands the assignment, chooses useful thinking methods, and challenges weak ideas before you commit. Bring a business challenge, an engineering contradiction, a research question, an inefficient process, an everyday problem or a creative brief.

Independent thinkers and a separate critic join when your host supports and permits them; otherwise role passes are disclosed as sequential. Scores are optional judgments, not guarantees. Hard requirements and evidence govern which direction is ready for the next step.

Bring a half-formed thought, a rough draft, or a direction you already love. Idea-Man helps you find the next useful step—and carry the idea further.

</td>
<td width="48%" valign="top">

<sub><b>A JOURNEY THAT FITS THE TASK</b></sub>

### **BIG IDEA. NEXT MOVE.**

![](https://img.shields.io/badge/01-Understand-F6F43C?style=flat-square&labelColor=25134D) **`→`** ![](https://img.shields.io/badge/02-Explore-26D9E6?style=flat-square&labelColor=25134D) **`→`** ![](https://img.shields.io/badge/03-Critique-FF5878?style=flat-square&labelColor=25134D) **`→`** ![](https://img.shields.io/badge/04-Develop-4B39F2?style=flat-square&labelColor=25134D) **`→`** ![](https://img.shields.io/badge/05-Make-F6F43C?style=flat-square&labelColor=25134D)

1. **Understand** — Recover the real job, evidence and constraints. Preserve approved choices and the qualities that already work.
2. **Explore** — Research, diagnose or develop distinct mechanisms using the methods the task needs.
3. **Critique** — Compare usefulness, requirements, mechanisms and evidence. Surface weak assumptions and useful tradeoffs.
4. **Develop** — Sharpen the direction you choose without displacing approved decisions or constraints.
5. **Make** — Carry out authorized work with available tools, inspect the result, or prepare a clear handoff.

<sub><i>Need research, a decision, a precise edit or the finished work? Take the route that fits. Simple requests stay focused. Save project decisions locally when you authorize it.</i></sub>

</td>
</tr>
</table>

---

## 01 / Install

<table width="100%">
<tr><th align="left" width="100%"><img src="https://img.shields.io/badge/CLAUDE_CODE-CLI-F6F43C?style=flat-square&labelColor=25134D" alt="Claude Code"></th></tr>
<tr><td>

Add the marketplace and install the plugin:

```bash
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
```

Then run:

```text
/idea-man:creative-director <brief>
```

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

<table width="100%">
<tr><th align="left" width="100%"><img src="https://img.shields.io/badge/OPENAI-CODEX-26D9E6?style=flat-square&labelColor=25134D" alt="Codex"></th></tr>
<tr><td>

Add the plugin marketplace from `main`:

```bash
codex plugin marketplace add sergey9519546/idea-man --ref main
```

<br>

After registration, open Plugins, install Idea-Man from the registered marketplace, and start a new session. In Codex CLI, open `/plugins`.

Select **Idea-Man - Innovation Conductor**, or start with `$idea-man:creative-director` followed by your task. A bare `$creative-director` can select another skill. If an older Idea-Man marketplace installation exposes the same name, disable that old installation and keep the current one enabled; preserve its files.

<sub><i>Registration adds the marketplace; you still need to install the plugin and start a new chat. Repository installation is separate from a public-directory listing.</i></sub>

</td></tr>
</table>

<details>
<summary><b>Try a task</b></summary>

Start with what you want to accomplish. You can add constraints or choose a mode:

- **Investigate:** “Our repair shop keeps missing promised dates. We can't hire anyone this month. What should we check before changing the schedule?”
- **Explore:** “Spark: give me four ways our library could reduce no-shows for free workshops, without adding staff.”
- **Review:** “Critique this proposal using only the notes below. Tell me what holds up, what's uncertain, and what needs changing. Don't rewrite it yet.”

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

## 03 / Skills

**11 specialized skills** spanning innovation, research, decisions and creative work. The conductor selects the useful specialists; you can also invoke one directly:

Seventeen thinking methods cover reframing, inversion, subtraction, analogy, systems reasoning, first principles, contradiction resolution and experiments. Use what helps the assignment; no fixed method count or score ceremony is required.

| Studio Stage | Skills | Role in the Studio |
| :--- | :--- | :--- |
| ![](https://img.shields.io/badge/01-Understand-F6F43C?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/creative-director/SKILL.md"><kbd>creative-director</kbd></a> <a href="plugins/idea-man/skills/creative-brief/SKILL.md"><kbd>creative-brief</kbd></a> <a href="plugins/idea-man/skills/research-and-writing/SKILL.md"><kbd>research-and-writing</kbd></a> <a href="plugins/idea-man/skills/innovation-strategy/SKILL.md"><kbd>innovation-strategy</kbd></a> | Orchestrate the room, sharpen the brief, synthesize research, and set strategy. |
| ![](https://img.shields.io/badge/02-Explore-26D9E6?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/concept-variations/SKILL.md"><kbd>concept-variations</kbd></a> | Generate distinct directions that change the idea—not just the wording. |
| ![](https://img.shields.io/badge/03-Critique-FF5878?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/creative-review/SKILL.md"><kbd>creative-review</kbd></a> <a href="plugins/idea-man/skills/artifact-quality/SKILL.md"><kbd>artifact-quality</kbd></a> | Compare usefulness, evidence, tradeoffs and hard requirements; inspect the actual deliverable. |
| ![](https://img.shields.io/badge/04-Develop-4B39F2?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/concept-development/SKILL.md"><kbd>concept-development</kbd></a> <a href="plugins/idea-man/skills/creative-learning/SKILL.md"><kbd>creative-learning</kbd></a> | Build around approved strengths; apply explicit feedback with its scope and exceptions. |
| ![](https://img.shields.io/badge/05-Make-F6F43C?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/execution-handoff/SKILL.md"><kbd>execution-handoff</kbd></a> | Produce the authorized result or prepare a concrete handoff with the available tools. |
| ![](https://img.shields.io/badge/06-Continue-26D9E6?style=flat-square&labelColor=25134D) | <a href="plugins/idea-man/skills/creative-project/SKILL.md"><kbd>creative-project</kbd></a> | Save authorized local decisions, preserve history, and resume from inspected project records. |

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
