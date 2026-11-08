# AGENTS.md — Idea-Man Agent Guide

Welcome to **Idea-Man**. Read this guide before taking any action in this repository.

---

## 1. What This App Is

**Idea-Man** is a free innovation partner plugin for Claude and OpenAI Codex (CLI and web hosts), accompanied by a static documentation and showcase website.
- It helps users structure business problems, explore distinct creative or strategic alternatives, critique directions against constraints, and make actionable artifacts.
- It includes 11 packaged skills (e.g. `creative-director`, `concept-variations`, `creative-brief`, `artifact-quality`, etc.) and 17 thinking methods configured in standard JSON and Markdown formats.
- An optional local Python planner / evaluation engine runs purely on the standard library (Python 3.9+ / 3.12, no third-party pip dependencies).
- The web preview and landing site source lives in `site/` and is built into `docs/` for GitHub Pages hosting using native Node.js (no external npm dependencies).

---

## 2. Setup and Run Commands

### Environment Requirements
- **Python**: 3.9+ (running Python 3.12 on this VM, standard library only)
- **Node.js**: v20+ (running Node.js v22 on this VM, standard library only)

### Setup from scratch (single command)
```bash
./scripts/setup.sh
```
This verifies Python 3 and Node.js versions, creates `.env` from `.env.example` if missing, builds the static site into `docs/`, and runs the static validator.

### Start the local preview server
```bash
./scripts/start.sh
```
This builds static assets and starts the local HTTP preview server at `http://127.0.0.1:4317/`.

---

## 3. Project Structure

```text
├── .agents/                 Host-specific agent configuration
├── .claude-plugin/          Claude plugin integration metadata
├── .env.example             Template for environment variables (fake values only)
├── docs/                    Generated static site published to GitHub Pages (do not edit directly)
├── eval/                    Evaluation framework, worked examples, and synthetic test cases
│   ├── captured/            Captured Codex test runs with synthetic briefs
│   ├── cases.json           Evaluation case definitions
│   ├── paired_eval.py       Paired evaluation script
│   └── worked_examples.py   Worked example verification script
├── integrations/            External host integration adapters (e.g. codex-account-entry)
├── plugins/                 Packaged agent skills, references, and assets
│   └── idea-man/
│       ├── agents/          Agent personas (idea-critic, room-thinker)
│       ├── assets/          Brand artwork, logos, icons, fonts
│       ├── references/      Innovation playbooks, registry, and contracts
│       ├── skills/          The 11 core skills and local helper scripts
│       │   └── creative-director/scripts/  (router_v2, studio, candidates, draw)
│       └── plugin.json      Plugin manifest
├── scripts/
│   ├── setup.sh             Reproducible environment check and build script
│   └── start.sh             Server launcher script (port 4317)
├── site/                    Static site source files
│   ├── build.mjs            Build script generating docs/
│   ├── validate.mjs         HTML and anchor validator
│   ├── preview.mjs          Local HTTP server
│   ├── verify-live.mjs      Live site verification against GitHub Pages
│   └── src/                 HTML templates, styles, and client scripts
├── tests/                   Python test suite (324 unit tests covering router, studio, contracts)
└── AGENTS.md                This file
```

---

## 4. Current Status

- **Unit tests**: 324 passing unit tests (`python3 -m unittest discover -s tests`).
  - 2 tests (`test_checkpoint_export` and `test_state_provenance_export`) are intentionally skipped when an optional local Markdown renderer is unavailable; this is expected behavior.
- **Worked examples**: Checked and verified (`python3 eval/worked_examples.py --check`).
- **Static validation**: All 5 pages, 62 local references, and 7 images pass validation (`node site/validate.mjs`).
- **Site test suite**: All 6 tests pass (`node --test site/*.test.mjs`).
- **Local preview**: Launches reliably on `http://127.0.0.1:4317/` via `./scripts/start.sh`.

---

## 5. Known Issues & Skipped Tests

- **Markdown rendering in tests**: `test_rendered_checkpoint_cannot_inject_images_links_or_formatting` and `test_rendered_export_has_no_injected_images_links_or_formatting` skip gracefully when external local markdown formatters are not present.
- **Docs directory is generated**: Never edit files in `docs/` directly; always edit in `site/src/` and run `node site/build.mjs` (or `./scripts/setup.sh`).

---

## 6. Standing Rules (Never Violate)

1. **Commit Constantly**: Commit after every working feature or fix with clear plain-English messages, and push to GitHub so no more than ~30 minutes of work is unpushed.
2. **Everything Reproducible**: Every dependency, configuration, and launch command must be captured in the repository. A brand-new VM cloning this repo can run `./scripts/setup.sh` and `./scripts/start.sh`.
3. **Maintain AGENTS.md**: Update this file before every push if anything changes.
4. **Secrets Stay Out of the Repo**: API keys and passwords belong in environment variables only. Keep `.env.example` up to date with fake values. Never commit `.env` or real credentials.
5. **Prove, Don't Claim**: Always run the app, run the test suites, hit the endpoints, and report actual outputs. "It should work" is banned.
6. **Never Break Working Features**: Re-test all core flows before pushing (run Python tests, worked examples, site validation, and node tests).
