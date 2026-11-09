# AGENTS.md — Idea-Man Agent Guide

This file is the single source of truth for AI agents operating on this repository across VM sessions.

## 1. What This App Is

**Idea-Man** is an innovation partner plugin and creative skill set for Claude Code and OpenAI Codex.
- **Plugin core (`plugins/idea-man/`)**: 11 modular skills, guidance protocols, and optional local Python helpers (Python 3.9+ standard library, zero external runtime packages).
- **Evaluation suite (`eval/`)**: Verification protocols, captured model interaction examples, and test journeys.
- **Showcase & Documentation Site (`site/`, `docs/`)**: Static site source in `site/` compiled via Node.js into GitHub Pages distribution in `docs/`.
- **Integrations (`integrations/`)**: Codex account entry and host integrations.
- **Tests (`tests/`)**: Regression tests covering routing contracts, state exports, prompt boundaries, and candidate evaluation.

## 2. Setup and Run Commands

A fresh VM or clone runs with standard tools (Python 3.12, Node.js v22).

- **Environment Setup**:
  ```bash
  ./scripts/setup.sh
  ```
  This verifies Python and Node.js runtimes, copies `.env.example` to `.env` if missing, and compiles `site/` to `docs/`.

- **Start Preview Server**:
  ```bash
  ./scripts/start.sh
  ```
  Launches preview HTTP server on `http://127.0.0.1:4317` (or configured `$PORT`).

- **Verification and Test Suite**:
  ```bash
  # 1. Run Python unit test suite
  python3 -m unittest discover -s tests

  # 2. Check worked examples
  python3 eval/worked_examples.py --check

  # 3. Validate static site integrity
  node site/validate.mjs

  # 4. Run site unit and distribution tests
  node --test site/*.test.mjs
  ```

## 3. Project Structure

```text
├── plugins/idea-man/    # Core plugin definitions, skills, assets, references
├── site/               # Source for static website, preview server, and validation
├── docs/               # Generated static website deployed to GitHub Pages (do not edit directly)
├── eval/               # Evaluation protocols, captures, and worked examples
├── tests/              # Python test suite (324+ tests)
├── integrations/       # Host integration scripts and skill adapters
├── scripts/            # Reproducibility scripts (setup.sh, start.sh)
├── .env.example        # Environment variable template
├── AGENTS.md           # Instructions, status, and rules for agents
└── README.md           # Public documentation and usage guide
```

## 4. Current Status

- **Status**: Stable v1.2.4 release codebase.
- **Tests**: 324 Python tests passing (2 skipped), static site validation passing, 6 Node test suites passing.
- **Reproducibility**: `scripts/setup.sh` and `scripts/start.sh` are verified working.
- **Security**: No secrets or hardcoded credentials in repo; `.env.example` provided; `.env*` ignored in `.gitignore`.

## 5. Known Issues and Limits

- `docs/` is a build artifact generated from `site/build.mjs`. Never edit files in `docs/` directly; always edit in `site/` and run `node site/build.mjs`.
- Optional Python helpers in `plugins/` rely strictly on standard library — do not add unnecessary third-party dependencies unless explicitly required.
- Preview server runs in foreground if not launched with `&`. Always terminate or handle background processes cleanly.

## 6. Standing Rules (Never Violate)

1. **Commit Constantly**: Commit after every working feature or fix with plain-English messages, and push to GitHub. Never let >30 minutes of work sit unpushed.
2. **Everything Reproducible**: Every configuration and dependency must be captured in the repo. Maintain `scripts/setup.sh` and `scripts/start.sh`.
3. **Maintain AGENTS.md**: Keep this file updated before every push when anything changes.
4. **Secrets Stay Out**: Keep credentials in environment variables and update `.env.example` as needed.
5. **Prove, Don't Claim**: Always test and run features on the VM before declaring success. "It should work" is banned.
6. **Never Break Working Features**: Re-test core test flows before pushing changes.
