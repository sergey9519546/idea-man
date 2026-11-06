# AGENTS.md — Idea-Man Agent Guide

This file provides critical context and operating instructions for any AI agent working on this repository.

## 1. Project Overview

**Idea-Man** is a free innovation partner plugin for Claude and OpenAI Codex. It helps users unpack business problems, explore alternatives, critique options, and develop concepts across 11 agent skills and 17 thinking methods.

In addition to the plugin source, the repository includes:
- A dependency-free static landing site generator (`site/` source, `docs/` GitHub Pages output).
- Comprehensive Python test suites and worked-example evaluations.

## 2. Standing Rules for All Sessions

1. **Commit Constantly:** After every working feature or fix, commit with a clear, plain-English message and push. Never let more than ~30 minutes of work sit unpushed.
2. **Everything Reproducible:** Any dependency, configuration, or run command must be in the repo. Maintain `scripts/setup.sh` and `scripts/start.sh` so a fresh VM can run the app with one command.
3. **Maintain AGENTS.md:** Always keep this file up to date before every push.
4. **Secrets Stay Out:** Real API keys and passwords never enter git. Use environment variables and `.env.example`.
5. **Prove, Don't Claim:** Always execute code on the VM and verify outputs (start server, test endpoints/scripts, run tests).
6. **Never Break Working Features:** Always run regression tests before pushing.

## 3. Environment & Setup

- **Python:** 3.9+ (Python 3.12 installed). Standard library only (`requirements.txt`).
- **Node.js:** 18+ (Node.js 22 installed). No external npm dependencies needed for the landing site.

### One-Command Setup & Run

- **Setup:**
  ```bash
  bash scripts/setup.sh
  ```
  Checks runtime versions, builds the site (`node site/build.mjs`), and validates the build (`node site/validate.mjs`).

- **Start Preview Server:**
  ```bash
  bash scripts/start.sh
  ```
  Launches preview server at `http://127.0.0.1:4317` serving `docs/`.

## 4. Project Structure

```text
.
├── .agents/            Host agent configurations
├── .claude-plugin/     Claude Code plugin metadata
├── .env.example        Template for environment variables
├── AGENTS.md           Agent orientation, operational rules, and project status
├── LICENSE             MIT license
├── README.md           Public documentation and user guide
├── docs/               Generated static site (GitHub Pages destination)
├── eval/               Evaluation benchmarks, worked examples, and paired evaluation
├── integrations/       Platform integrations (e.g., Codex account entry)
├── plugins/idea-man/   Core Idea-Man plugin definitions, skills, references, and assets
├── requirements.txt    Python runtime requirements documentation
├── scripts/            Reproducibility scripts (setup.sh, start.sh)
├── site/               Landing site source (site/src/), build scripts, and tests
└── tests/              Python unit test suite (324+ tests)
```

## 5. Verification & Testing Commands

Run all of these commands before committing or pushing changes:

1. **Python Unit Tests:**
   ```bash
   python3 -m unittest discover -s tests
   ```
2. **Worked Examples Check:**
   ```bash
   python3 eval/worked_examples.py --check
   ```
3. **Site Static Validation:**
   ```bash
   node site/validate.mjs
   ```
4. **Site Distribution & Unit Tests:**
   ```bash
   node --test site/*.test.mjs
   ```
5. **Setup Script & Live Server Proof:**
   ```bash
   bash scripts/setup.sh
   bash scripts/start.sh &
   curl -I http://127.0.0.1:4317/
   ```

## 6. Current Status & Known Issues

- **Current Status:**
  - Plugin version: `v1.2.4` published.
  - Python test suite: 324 tests passing (2 skipped as intended).
  - Worked examples evaluation: 3 examples verified, 2 local helper probes verified.
  - Site build & tests: Static validation and distribution tests passing.
  - Environment reproducibility: `scripts/setup.sh` and `scripts/start.sh` added and verified.
  - Secret scanning: Clean. No secrets or tokens stored in repo.

- **Known Notes:**
  - `docs/` is generated output. Never edit `docs/` directly; always edit in `site/src/` and run `node site/build.mjs`.
