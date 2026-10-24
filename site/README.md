# Idea Man landing site

Dependency-free static site. Build output is `../docs/`; no server runtime or external font/analytics dependencies.

```powershell
node build.mjs
node validate.mjs
```

Update `site-config.json` with verified public URLs before the final build. `repositoryUrl` accepts an HTTPS GitHub repository URL. `marketplaceUrl` is emitted only when `marketplacePublicVerified` is true. `siteUrl` supplies optional canonical metadata after hosting identity is known. Missing URLs produce honest status text, never dummy links.

The build copies the approved PNG assets byte for byte from `../../release-1.2.1/idea-man/assets/`. The source package is not modified.

Sites deployment is owned by the parent task. Register the Site, persist the returned identity with the Sites `set-project-id.mjs` helper using `--static-directory docs`, then package and publish through the Sites workflow. No project identity or remote repository was created by this implementation task.

Browser QA should cover desktop and mobile layouts, all six domain selectors, both copy buttons, the methods disclosure, keyboard focus and configured external links.
