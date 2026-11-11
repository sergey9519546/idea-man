# Idea-Man: Agent Guide (AGENTS.md)

Welcome to **Idea-Man**. This file serves as the definitive briefing for any AI agent or software engineer joining this codebase cold.

---

## 1. What This App Is
Idea-Man is an innovation partner plugin and multi-skill agent system for **Claude Code** and **OpenAI Codex**, paired with a lightweight static documentation and evidence website.
- **Core Functionality**: Helps users frame business, engineering, and creative problems, explore variations, critique ideas against evidence, develop promising concepts, and prepare execution handoffs.
- **Components**:
  - `plugins/idea-man/`: Plugin manifests (`plugin.json`), 11 distinct skills (`creative-director`, `concept-variations`, `artifact-quality`, etc.), agents, reference methodologies, and brand assets.
  - `site/`: Source code for the documentation and evidence website (Vanilla HTML, CSS, JS; Node.js build/validation scripts).
  - `docs/`: Generated static distribution output published via GitHub Pages.
  - `eval/`: Evaluation harnesses, synthetic test cases, multi-turn protocol journeys, and worked examples.
  - `tests/`: Comprehensive Python regression test suite (324 tests).
  - `scripts/`: Project setup (`scripts/setup.sh`) and application launch (`scripts/start.sh`).

---

## 2. Setup and Execution Commands

### Prerequisites
- **Python**: 3.9+ (Python 3.12 recommended). Standard library only; no external `pip` packages required.
- **Node.js**: v18+ (Node.js v22 recommended). Standard library only; no external `npm` packages required.

### Setup Environment
```bash
./scripts/setup.sh
```
This validates the environment, creates `.env` from `.env.example` if missing, builds the static website (`node site/build.mjs`), and validates all links/assets (`node site/validate.mjs`).

### Run the App / Local Preview Server
```bash
./scripts/start.sh
```
Launches the HTTP preview server on port `4317` (configurable via `PORT` in `.env`). Accessible at `http://127.0.0.1:4317`.

### Run All Tests
```bash
# 1. Run Python regression suite
python3 -m unittest discover -s tests

# 2. Run worked examples verification
python3 eval/worked_examples.py --check

# 3. Validate static site integrity
node site/validate.mjs

# 4. Run Node.js distribution tests
node --test site/*.test.mjs
```

---

## 3. Project Structure

```text
├── .env.example             # Template for local environment variables
├── .gitignore               # Ignored files (secrets, caches, build artifacts)
├── AGENTS.md                # This operational guide
├── README.md                # Human-facing project overview and install guide
├── docs/                    # Generated GitHub Pages site (do not edit directly)
├── eval/                    # Evaluation suites, worked examples, journey protocols
├── integrations/            # Host integrations (e.g., Codex account entry)
├── plugins/
│   └── idea-man/            # Plugin package
│       ├── agents/          # Specialized agent configurations
│       ├── assets/          # Brand artwork and guidelines
│       ├── references/      # Innovation rubrics and playbook registries
│       └── skills/          # 11 modular skills (creative-director, etc.)
├── scripts/
│   ├── setup.sh             # Reproducible setup script
│   └── start.sh             # App launcher script (port 4317)
├── site/                    # Source files for static website
│   ├── build.mjs            # Static site generator
│   ├── preview.mjs          # HTTP preview server
│   ├── validate.mjs         # Static link, asset, and hash validator
│   └── src/                 # HTML templates, CSS, client-side JS
└── tests/                   # Python unit and regression tests
```

---

## 4. Current Status
- **Tests**: All 324 Python unit tests and 6 Node.js distribution tests pass completely.
- **Static Site**: Site builds cleanly and passes all validation checks (5 pages, 62 local links, 7 asset references verified).
- **Security**: No secrets or hardcoded credentials in the repository. Environment variable template in place.
- **Reproducibility**: Environment is 100% self-contained using Python and Node.js standard libraries, automated via `scripts/setup.sh` and `scripts/start.sh`.

---

## 5. Known Issues & Limitations
- **Docs Generation**: Never edit `docs/` directly; always edit `site/src/` and run `node site/build.mjs`.
- **Port Usage**: The preview server binds to port 4317 by default. `scripts/start.sh` handles killing existing processes on this port before starting.
- **Host Dependencies**: Running live evaluations against Anthropic or OpenAI models requires setting `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`.

---

## 6. Standing Rules
1. **Commit Constantly**: Commit after every working feature or fix with a clear plain-English message, and push to GitHub so work is never lost.
2. **Everything Reproducible**: Every dependency, configuration, and launch command must be captured in the repository. A brand-new VM should run the app with `./scripts/setup.sh` and `./scripts/start.sh`.
3. **Maintain AGENTS.md**: Keep this file updated before every push whenever changes occur.
4. **Secrets Stay Out of the Repo**: Keep API keys in `.env` only (listed in `.env.example`). Never commit real keys.
5. **Prove, Don't Claim**: Always test and exercise the running app on the VM (hit endpoints, check HTTP codes) before claiming it works.
6. **Never Break Working Features**: Re-run the full test suite before pushing.
