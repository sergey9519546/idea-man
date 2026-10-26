# Idea-Man landing site

Dependency-free GitHub Pages site. Source is `site/src/`; build output is `docs/` at the repository root.

```sh
cd site
node build.mjs
node validate.mjs
node --check src/app.js
node verify-live.mjs
```

`site-config.json` sets the verified public repository URL, canonical Pages base URL, and release version displayed by installation instructions. releaseStatus distinguishes an unreleased candidate from a GitHub release. Version 1.2.3 is published on GitHub; marketplace submission is authorized; public-directory approval remains pending. Keep releaseStatus=candidate for future unpublished work.

The public directory listing remains pending unless `marketplacePublicVerified` is explicitly set after actual approval. Repository installation is separate from public-directory approval.

The build copies approved artwork byte for byte from `../plugins/idea-man/assets/` without publishing the internal brand kit. Keep relative links compatible with the `/idea-man/` GitHub Pages base path. No Site registration or separate Sites deployment is needed.

`verify-live.mjs` anonymously checks the four public routes, canonical URLs, the support GitHub Issues link, and referenced same-site assets. It verifies the currently deployed site, which can precede local staged changes. Static checks verify the local build. Browser rendering and interactions require separate visual QA when browser access is available.

When repositoryUrl is null, Claude Code instructions use session-only `claude --plugin-dir "<path-to-unzipped-idea-man-directory>"`. The path must contain `.claude-plugin/plugin.json`; it is a plugin directory, not a marketplace. Verified against local `claude --help` (directory or ZIP, session only).

Run `node --test site/distribution.test.mjs` from the repository root to test configured and absent repositories. Tests build isolated temporary copies and leave tracked docs untouched.
