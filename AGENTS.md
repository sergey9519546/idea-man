# AGENTS.md — Idea-Man

## 1. What This App Is
Idea-Man is a free innovation partner plugin for Claude and Codex. It provides 11 packaged agent skills, 17 thinking methods in an innovation registry, local Python helpers for candidate decision routing and evidence analysis, evaluation suites with worked examples, and a static documentation/preview website generated from `site/` into `docs/`.

## 2. Setup and Run Commands
The repository requires only standard system tools: Python 3.9+ (Python 3.12 verified, standard library only — no external pip dependencies) and Node.js 18+ (Node.js 22 verified).

### Quick Setup
```bash
./scripts/setup.sh
```
Or manually run the setup checks:
```bash
python3 -m unittest discover -s tests
python3 eval/worked_examples.py --check
node site/validate.mjs
node --test site/*.test.mjs
```

### Launch Preview Server
```bash
./scripts/start.sh
```
Or directly:
```bash
node site/preview.mjs
```
The preview server serves the static website on `http://127.0.0.1:4317`.

### Static Site Build
```bash
node site/build.mjs
```
*Note: Edits must be made in `site/`, not directly in `docs/`.*

## 3. Project Structure
- `plugins/idea-man/`: Plugin definition (`plugin.json`), skills (`skills/`), candidate router scripts, brand assets, and innovation references.
- `site/`: Source code for the landing and documentation website (`src/`, `preview.mjs`, `build.mjs`, `validate.mjs`, test suites).
- `docs/`: Generated static distribution website served via GitHub Pages or local preview.
- `eval/`: Evaluation tools, worked examples (`worked_examples.py`), test cases, and captured runs.
- `integrations/`: Host-specific integration entry points (e.g. Codex account entry).
- `tests/`: Python test suite covering guidance contracts, state provenance, decision withdrawal, candidate routing, and more.
- `scripts/`: Environment setup (`setup.sh`) and application start (`start.sh`) scripts.
- `.env.example`: Template for environment variables (defaults to `PORT=4317`).

## 4. Current Status
- **Test suite**: 324 Python unit tests pass (2 skipped intentionally).
- **Worked examples**: Checked and verified without regressions.
- **Static site**: Build and validation passing 100%; preview server verified working on port 4317.
- **Reproducibility & Secrets**: Verified — zero secrets in repo, environment reproducible with one command (`./scripts/setup.sh`).

## 5. Known Issues
- None at this time. All core test suites, static site builds, and preview flows pass.

## 6. Standing Rules
1. **Commit Constantly**: Commit after every working feature or fix with clear plain-English messages, and push to GitHub so no more than ~30 minutes of work is unpushed.
2. **Everything Reproducible**: Maintain `.env.example`, `scripts/setup.sh`, and `scripts/start.sh`. Ensure fresh VM can clone and run with one or two commands.
3. **Maintain AGENTS.md**: Update this file before every push if anything changes.
4. **Secrets Stay Out**: Manage API keys and secrets via environment variables only; never commit secrets.
5. **Prove, Don't Claim**: Always test and exercise the app directly on the VM (run servers, hit endpoints) before reporting completion.
6. **Never Break Working Features**: Re-test all core flows before pushing changes.
