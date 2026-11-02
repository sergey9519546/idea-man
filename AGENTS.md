# AGENTS.md — Idea-Man

## 1. What This App Is

**Idea-Man** is a free innovation partner and creative director plugin designed for Claude Code and OpenAI Codex.
It helps users work through business problems, engineering tradeoffs, research investigations, and creative briefs by structuring ideation into clear phases:
1. **Understand**
2. **Explore**
3. **Critique**
4. **Develop**
5. **Make**

The repository contains:
- **`plugins/idea-man/`**: The core plugin configuration, 11 packaged agent skills (e.g. `creative-director`, `concept-variations`, `artifact-quality`), prompt instructions, references, and local Python tools (`router_v2.py`, `studio.py`, `draw.py`, `build_room_protocol.py`).
- **`site/`**: Source files for the official landing, support, terms, privacy, and evidence pages (`build.mjs`, `validate.mjs`, templates, styles).
- **`docs/`**: Generated static website served on GitHub Pages.
- **`eval/`**: Evaluation suite, synthetic cases, and worked example verifications (`worked_examples.py`, `paired_eval.py`).
- **`tests/`**: Unit and regression test suite (324 Python tests covering routers, validators, schemas, guidance contracts, and boundary conditions).
- **`scripts/`**: Reproducibility scripts (`setup.sh` and `start.sh`).

---

## 2. Setup and Run Commands

### Prerequisites
- Python 3.9+ (standard library only; no external pip dependencies needed for core execution)
- Node.js 18+ and npm (for static site building and local preview server)

### Reproducible Setup
Run the setup script from the repository root:
```bash
./scripts/setup.sh
```
This verifies Python and Node versions and builds the static site assets.

### Running the App / Preview Server
To run the local preview server for the documentation and site:
```bash
./scripts/start.sh
```
The server will run on `http://127.0.0.1:4317`.

### Running Tests and Verifications
Run all checks before pushing or submitting:
```bash
# 1. Run Python unit & contract tests (324 tests)
python3 -m unittest discover -s tests

# 2. Check worked examples & local helper contracts
python3 eval/worked_examples.py --check

# 3. Build & validate documentation website
node site/build.mjs
node site/validate.mjs
```

---

## 3. Project Structure

```text
idea-man/
├── .agents/plugins/            Marketplace registration definitions
├── .claude-plugin/             Claude Code marketplace registration definitions
├── docs/                       Generated static website for GitHub Pages (DO NOT EDIT DIRECTLY)
├── eval/                       Evaluation cases, worked examples, and synthetic test suites
├── integrations/               Codex entry skill integrations
├── plugins/idea-man/           Core plugin, 11 skills, Python router/studio helpers, and brand assets
│   ├── skills/                 Packaged skills (creative-director, concept-variations, etc.)
│   └── references/             Innovation registry and reference documentation
├── scripts/                    Automation scripts (setup.sh, start.sh)
├── site/                       Landing page and documentation source (edit here, then run build.mjs)
│   ├── build.mjs               Static site generator
│   └── validate.mjs            Static validation script
├── tests/                      Python test suite
├── .env.example                Template environment configuration
├── AGENTS.md                   This instruction and state survival file
└── README.md                   Project overview and installation instructions
```

---

## 4. Current Status & Known Issues

### Current Status
- **Core skills and local planners**: Fully functional and covered by 324 passing tests.
- **Static documentation site**: Configured and validated; generated to `docs/`.
- **Environment reproducibility**: Setup and start scripts created (`scripts/setup.sh` and `scripts/start.sh`).
- **Secrets audit**: Clean. No secrets, credentials, or API keys are committed. Template provided in `.env.example`.

### Known Issues & Limitations
- `docs/` is generated from `site/`. Never edit files in `docs/` directly; always edit `site/` and run `node site/build.mjs`.
- Core tools are designed to work purely using the Python standard library; avoid introducing external package dependencies without strong architectural reasons.

---

## 5. Standing Rules for Future Agents

1. **COMMIT CONSTANTLY**: Commit after every working feature or fix with clear plain-English commit messages. Never allow work to remain uncommitted or unpushed.
2. **EVERYTHING REPRODUCIBLE**: Ensure any dependency, configuration, or execution command is documented and captured in `scripts/setup.sh`, `scripts/start.sh`, and dependency files.
3. **MAINTAIN AGENTS.md**: Update this file before every push whenever changes to commands, structure, status, or issues occur.
4. **SECRETS STAY OUT**: No API keys or credentials in the repo. Keep `.env.example` updated with placeholders.
5. **PROVE, DON'T CLAIM**: Always execute commands, run tests, spin up servers, and query endpoints directly. Verify actual results rather than assuming correctness.
6. **NEVER BREAK WORKING FEATURES**: Always re-test the entire test suite before finalizing changes.
