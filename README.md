<p align="center"><img src="plugins/idea-man/assets/lightbulb-hero-1024.webp" alt="Idea-Man: a faceless cyan lightbulb in round violet glasses and a coral cape" width="360"></p>

# Idea-Man

**Every big idea needs a sidekick.**

Idea-Man is a free innovation and creative-director plugin for Claude and Codex. It helps find the insight, develop distinct approaches and choose practical next steps. Independent thinker and blind-critic passes are optional and depend on the host's agent capabilities. When independent agents are unavailable, the workflow can use sequential role passes and states that limitation. Creative scores are judgments, not measured audience results.

Site: https://sergey9519546.github.io/idea-man/

## Install

**Claude Code**

```
claude plugin marketplace add sergey9519546/idea-man
claude plugin install idea-man@idea-man-marketplace
```

Then run `/idea-man:creative-director <brief>`.

**Claude.ai / Cowork**: Download an available plugin ZIP from the [GitHub Releases page](https://github.com/sergey9519546/idea-man/releases), then choose Customize > Plugins > Add > Upload plugin. Version 1.2.2 is available from GitHub Releases.

**Codex**

```
codex plugin marketplace add sergey9519546/idea-man --ref main
```

After adding the marketplace, restart the desktop app, select the Idea-Man marketplace in the Plugins Directory and install Idea-Man. In Codex CLI, open /plugins. Start a new session before using the bundled skills. Public-directory publication follows a separate review process.

## Updating an existing installation

Claude Code: run `claude plugin update idea-man@idea-man-marketplace`, then restart.
In Codex, refresh the registered marketplace with `codex plugin marketplace upgrade <configured-marketplace-name>`, apply the available plugin update in Plugins, then start a new session. Refreshing a snapshot alone is not proof the active session uses the new version.

## Modes

- **Full**: substantial exploration using methods selected for the task; development within requested or delegated scope.
- **Spark**: a quick burst of ideas.
- **Critique**: challenge weak ideas, compare useful differences and identify what deserves improving or testing.
- **Unstick**: get moving on a stuck problem.
- **Room**: optional independent thinkers and blind critique where the host supports agents; otherwise disclosed sequential role passes.

## Skills

`creative-director`, `creative-brief`, `concept-variations`, `concept-development`, `creative-review`, `artifact-quality`, `research-and-writing`, `innovation-strategy`, `creative-learning`, `execution-handoff`, `creative-project`.

## Optional local helpers

The planner and local project-record helpers require Python 3.9 or newer and use the standard library. The skills themselves can run without Python; the host applies their decision rules directly when code execution is unavailable.

## Repository layout

- `plugins/idea-man/`: the plugin
- `site/`: landing-page source (`node site/build.mjs`, then `node site/validate.mjs`), output in `docs/` for GitHub Pages
- `tests/`: Python tests
- `eval/`: offline paired-output harness and synthetic conversation cases

## License

MIT. Not affiliated with or endorsed by Anthropic or OpenAI.

## Candidate decisions and evaluation

Version 1.2.2 includes optional evidence-linked comparisons: hard constraints,
mechanism groups, tradeoffs and readiness for the next stated commitment. Ratings never
compensate for a hard failure and the helper grants no execution authority. See
[the candidate contract](plugins/idea-man/skills/creative-director/references/candidate-decisions.md).

[The offline comparison harness](eval/README.md) distinguishes local mechanical checks
from output quality. No baseline win or measured originality gain is claimed without
comparable captured responses and appropriate review. Marketplace submission remains on hold.
