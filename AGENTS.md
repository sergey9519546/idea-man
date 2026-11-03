# AGENTS.md — Idea-Man

This repository is maintained autonomously. Any agent or engineer reading this file can understand the application, environment setup, project layout, testing procedure, current status, and rules of engagement.

---

## 1. What This App Is

**Idea-Man** is an innovation partner plugin and creative director system designed for LLM hosts (OpenAI Codex, Claude Code, and Claude.ai / Cowork), accompanied by a dependency-free static documentation & landing site published to GitHub Pages.

It provides 11 specialized skills (including `creative-director`, `creative-brief`, `concept-variations`, `concept-development`, `creative-review`, `artifact-quality`, `research-and-writing`, `innovation-strategy`, `creative-learning`, `execution-handoff`, `creative-project`) and 17 structured thinking methods.

---

## 2. Environment Setup & Run Commands

The repository requires **Python 3.9+** (core helpers and unit tests use Python standard library only) and **Node.js 18+** (for static site building, validation, and preview).

### One-Command Setup
```bash
./scripts/setup.sh
```
This script checks the required runtimes, verifies Python dependencies via `requirements.txt`, builds the static site into `docs/`, and runs static site validation.

### Run Local Preview Server
```bash
./scripts/start.sh
```
Starts the local preview HTTP server on `http://127.0.0.1:4317` (configurable via `PORT` and `HOST` environment variables in `.env`).

### Run Test Suite
```bash
# Python regression tests (324 tests)
python3 -m unittest discover -s tests

# Evaluation & worked examples checks
python3 eval/worked_examples.py --check

# Site validation
node site/validate.mjs

# Site distribution & evidence unit tests
node --test site/distribution.test.mjs
node --test site/evidence.test.mjs
```

### Static Site Build
```bash
node site/build.mjs
node site/validate.mjs
```
*Note: Never manually edit files in `docs/` directly; `docs/` is the generated artifact from `site/src/`.*

---

## 3. Project Structure

```text
idea-man/
├── .agents/                        # Agent plugin marketplace metadata
├── .claude-plugin/                 # Claude plugin manifest (plugin.json)
├── .github/                        # GitHub issue templates and repository assets
├── docs/                           # Generated GitHub Pages website output (DO NOT EDIT DIRECTLY)
├── eval/                           # Evaluation harness, synthetic worked examples, protocols
├── integrations/                   # Host integrations (e.g., Codex account entry)
├── plugins/
│   └── idea-man/                  # Plugin manifest, skills (11 skills), references, assets
├── scripts/
│   ├── setup.sh                    # Environment initialization and check script
│   └── start.sh                    # App / local preview start script
├── site/                           # Static site source and build scripts
│   ├── src/                        # HTML, CSS, client JS, font source files
│   ├── build.mjs                   # Site generator (site/src -> docs)
│   ├── preview.mjs                 # Local preview server
│   ├── validate.mjs                # Static site integrity linter
│   └── site-config.json            # Site URLs and version configuration
├── tests/                          # 324 Python unit and contract tests
├── .env.example                    # Template for environment configuration
├── .gitignore                      # Git exclusion rules
├── AGENTS.md                       # Machine & agent instructions (this file)
├── LICENSE                         # MIT License
├── README.md                       # Project overview and user documentation
└── requirements.txt                # Python environment requirements
```

---

## 4. Current Status

- **What works:**
  - All 324 Python tests pass cleanly (`Ran 324 tests, OK (skipped=2)`).
  - Worked examples verification passes (`python3 eval/worked_examples.py --check`).
  - Site build and static validation pass completely (all routes, local references, image hashes, anchor links).
  - Site distribution and evidence tests pass (`site/distribution.test.mjs`, `site/evidence.test.mjs`).
  - Local HTTP preview server functions correctly on `http://127.0.0.1:4317` (returns HTTP 200).
  - Reproducibility scripts (`scripts/setup.sh` and `scripts/start.sh`) are tested and functional.
  - Zero secrets or sensitive credentials present in repo; template documented in `.env.example`.
- **What's broken:**
  - None detected. The entire test suite and build pipeline pass.
- **What's unfinished / Pending:**
  - Public ChatGPT/Codex marketplace directory listing is pending external platform review (`marketplacePublicVerified: false`). Repository installation via `--ref main` is the active install path.
  - Release status is currently maintained as `released` v1.2.4 on GitHub; any new unpublished features must adhere to candidate flags as documented in `site/README.md`.

---

## 5. Standing Rules

1. **COMMIT CONSTANTLY**: Commit after every working feature or fix with plain-English descriptions and push to GitHub so work is never stranded on a VM.
2. **EVERYTHING REPRODUCIBLE**: All dependencies, setup steps, and start commands must live in the repository (`requirements.txt`, `scripts/setup.sh`, `scripts/start.sh`).
3. **MAINTAIN AGENTS.MD**: Keep `AGENTS.md` up to date before every push if status, architecture, or instructions change.
4. **SECRETS STAY OUT**: API keys, passwords, and tokens must only live in environment variables or `.env` (ignored by git). Document variables in `.env.example`.
5. **PROVE, DON'T CLAIM**: Run code on the VM, start servers, ping endpoints, and run test suites before claiming anything works.
6. **NEVER BREAK WORKING FEATURES**: Always re-run the full regression suite before pushing changes.
