<p align="center"><img src="plugins/idea-man/assets/lightbulb-hero-1024.webp" alt="Idea Man: a faceless cyan lightbulb in round violet glasses and a coral cape" width="360"></p>

# Idea Man

**Every big idea needs a sidekick.**

Idea Man is a free creative-director plugin for Claude and Codex. It finds the insight first, then generates far past the obvious with methods drawn from real master thinkers. A blind critic scores every idea, and you only see the ones that score 7+, with their risks and the cheapest test.

Site: https://sergey9519546.github.io/idea-man/

## Install

**Claude Code**

```
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
```

Then run `/idea-man:creative-director <brief>`.

**Claude.ai / Cowork**: Customize → Plugins → Add → Upload plugin, then choose `idea-man-1.2.1.zip` from the [latest GitHub release](https://github.com/sergey9519546/idea-man/releases/latest).

**Codex**

```
codex plugin marketplace add sergey9519546/idea-man --ref main
```

The Codex plugin directory listing is pending review.

## Modes

- **Full**: diagnose, insight, generate, critique, present.
- **Spark**: a quick burst of ideas.
- **Critique**: rate, compare or kill an existing idea.
- **Unstick**: get moving on a stuck problem.
- **Room**: parallel thinkers plus a blind critic.

## Skills

`creative-director`, `creative-brief`, `concept-variations`, `concept-development`, `creative-review`, `artifact-quality`, `research-and-writing`, `innovation-strategy`, `creative-learning`, `execution-handoff`, `creative-project`.

## Repository layout

- `plugins/idea-man/`: the plugin
- `site/`: landing-page source (`node site/build.mjs`, then `node site/validate.mjs`), output in `docs/` for GitHub Pages
- `tests/`: Python tests

## License

MIT. Not affiliated with or endorsed by Anthropic or OpenAI.
