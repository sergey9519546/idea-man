import { createHash } from 'node:crypto';
import { loadEvidence, evidenceBody, copyEvidence } from './evidence.mjs';
import { readFile, writeFile, mkdir, copyFile, access, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(await readFile(path.join(root, 'site-config.json'), 'utf8'));
function verifiedUrl(value, host) {
  if (value === null) return null;
  const url = new URL(value);
  if (url.protocol !== 'https:' || url.username || url.password || (host && url.hostname !== host)) throw new Error('Invalid public URL configuration');
  return url.href;
}
const repository = verifiedUrl(config.repositoryUrl, 'github.com');
const marketplace = config.marketplacePublicVerified ? verifiedUrl(config.marketplaceUrl, 'chatgpt.com') : null;
const site = verifiedUrl(config.siteUrl);
const escape = value => value.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;');
const repositoryLink = repository ? `<a class="text-link" href="${escape(repository)}" target="_blank" rel="noopener noreferrer">View on GitHub <span aria-hidden="true">↗</span></a>` : '<p class="availability">Public repository is not configured.</p>';
const marketplaceLink = marketplace ? `<a class="button button-dark" href="${escape(marketplace)}" target="_blank" rel="noopener noreferrer">Install Idea-Man <span aria-hidden="true">↗</span></a>` : repository ? `<a class="button button-dark" href="${escape(repository.replace(/\/$/, '') + '/releases')}" target="_blank" rel="noopener noreferrer">Get the plugin ZIP <span aria-hidden="true">↗</span></a>` : '';
const installation = '';
const repositoryPath = repository ? new URL(repository).pathname.replace(/^\//, '').replace(/\/$/, '') : null;
const codexInstall = repositoryPath ? `<ol class="install-steps"><li><p>Add the repository marketplace from your terminal.</p><pre><code>codex plugin marketplace add ${escape(repositoryPath)} --ref main</code></pre></li><li><p>Restart the desktop app. Open the Plugins Directory, choose the Idea-Man marketplace, and install Idea-Man. In Codex CLI, open <code>/plugins</code>.</p></li><li><p>Start a new chat with Idea-Man enabled, then send your brief.</p></li></ol><p class="host-note">This uses the repository marketplace. A public directory listing is not required.</p>` : '<p>A public installation source is not configured yet. Check with the publisher for a plugin ZIP or marketplace source.</p>';
const claudeInstallLocal = '<p>Public repository is not configured. If you received the plugin ZIP, unzip it and load the directory containing <code>.claude-plugin/plugin.json</code> for this Claude Code session:</p><pre><code>claude --plugin-dir &quot;&lt;path-to-unzipped-idea-man-directory&gt;&quot;</code></pre><p>This loads the plugin for this session only. Then run <code>/idea-man:creative-director</code> followed by your brief.</p>';
const claudeInstall = repositoryPath ? `<ol class="install-steps"><li><p>Add the marketplace and install Idea-Man from your terminal.</p><pre><code>claude plugin marketplace add ${escape(repositoryPath)}\nclaude plugin install idea-man@idea-man-marketplace</code></pre></li><li><p>Start a new Claude Code session. Run <code>/idea-man:creative-director</code> followed by your brief.</p></li></ol>` : claudeInstallLocal;
const ctaLabel = repository ? 'Get Idea-Man' : 'Install steps';
const releaseStatus = config.releaseStatus ?? 'candidate';
if (!['candidate','released'].includes(releaseStatus)) throw new Error('Invalid releaseStatus');
const releaseNotice = releaseStatus === 'released' ? `Version v${escape(String(config.version))}.` : `Local candidate v${escape(String(config.version))}. This candidate is unpublished; public releases may contain an earlier version.`;
const claudeAiInstall = (repository ? `<ol class="install-steps"><li><p>Download the plugin ZIP from <a href="${escape(repository.replace(/\/$/, '') + '/releases')}" target="_blank" rel="noopener noreferrer">GitHub Releases</a>. Choose the plugin asset, rather than GitHub’s source-code archive.</p></li><li><p>Open <strong>Customize → Plugins → Add → Upload plugin</strong> and choose the ZIP. In Cowork, open the Cowork tab first.</p></li><li><p>In a conversation, type <code>/</code> to choose an Idea-Man skill, then send your brief.</p></li></ol><p class="host-note">Requires a paid Claude plan with plugin access.</p>` : '<p>If you received a plugin ZIP, use <strong>Customize → Plugins → Add → Upload plugin</strong> and select that ZIP. Requires a paid Claude plan with plugin access.</p>');
let html = await readFile(path.join(root, 'src', 'index.html'), 'utf8');
for (const [key, value] of Object.entries({ REPOSITORY_LINK: repositoryLink, RELEASE_STATUS: releaseNotice, MARKETPLACE_LINK: marketplaceLink, INSTALLATION_STEPS: installation, CODEX_INSTALL: codexInstall, CTA_LABEL: ctaLabel, CLAUDEAI_INSTALL: claudeAiInstall, INSTALL_HEADING: repository ? 'GET Idea-Man.' : 'INSTALL STEPS.', CLAUDE_INSTALL: claudeInstall, VERSION: escape(String(config.version)), CANONICAL: site ? `<link rel="canonical" href="${escape(site)}"><meta property="og:url" content="${escape(site)}">` : '' })) html = html.replaceAll(`{{${key}}}`, value);
const scriptVersion = createHash('sha256').update(await readFile(path.join(root,'src/app.js'))).digest('hex').slice(0,12);
const styleVersion = createHash('sha256').update(await readFile(path.join(root,'src/styles.css'))).update(await readFile(path.join(root,'src/document.css'))).digest('hex').slice(0,12);
html = html.replace('src="app.js"', 'src="app.js?v=' + scriptVersion + '"').replace('href="styles.css"', 'href="styles.css?v=' + styleVersion + '"');
const evidence = await loadEvidence(path.dirname(root));
const dist = path.resolve(root, '../docs');
if (dist !== path.join(path.dirname(root), 'docs')) throw new Error('Unexpected build output path');
if (await import('node:fs/promises').then(({lstat}) => lstat(dist).then(s => s.isSymbolicLink(), () => false))) throw new Error('Build output must not be a symlink or junction');
await rm(dist, { recursive: true, force: true });
await mkdir(path.join(dist, 'assets'), { recursive: true });
await writeFile(path.join(dist, '.nojekyll'), '');
await writeFile(path.join(dist, 'index.html'), html);
for (const file of ['styles.css', 'app.js']) await copyFile(path.join(root, 'src', file), path.join(dist, file));
await writeFile(path.join(dist, 'styles.css'), (await readFile(path.join(root, 'src/styles.css'), 'utf8')) + '\n' + (await readFile(path.join(root, 'src/document.css'), 'utf8')));
const assetSource = path.resolve(root, '../plugins/idea-man/assets');
const siteAssets = ['idea-man-logo-transparent.png', 'mark.svg', 'icon-32.png', 'icon-16.png', 'icon-48.png', 'icon-128.png', 'icon-256.png', 'icon.png', 'apple-touch-icon.png', 'invisible-nerd-1024.webp', 'lightbulb-hero-1024.webp', 'invisible-nerd.png', 'lightbulb-hero.png', 'invisible-nerd-cutout.png', 'lightbulb-hero-cutout.png'];
for (const file of siteAssets) {
  const from = path.join(assetSource, file);
  try { await access(from); } catch { throw new Error(`Missing required asset: ${from}`); }
  await copyFile(from, path.join(dist, 'assets', file));
}
await copyFile(path.join(assetSource, 'favicon.ico'), path.join(dist, 'favicon.ico'));
const supportLink = repository ? `<a class="button button-dark" href="${escape(repository.replace(/\/$/, '') + '/issues')}" target="_blank" rel="noopener noreferrer">Open a GitHub issue <span aria-hidden="true">↗</span></a>` : '<p class="status-label">Support opens with the public release.</p>';
await copyEvidence(path.dirname(root), dist);
const pages = {
  evidence: { title: 'Show your work', subtitle: 'See the facts. Follow the reasoning. Check the limits.', body: evidenceBody(evidence) },
  support: {
    title: 'Support', subtitle: 'Let’s get you unstuck.',
    body: `<h2>Get help with Idea-Man</h2><p>Idea-Man is published by Sergey Avetisyan as a free plugin. ${repository ? 'Use the public GitHub issue tracker for installation problems, reproducible bugs, feature requests or questions about the packaged skills.' : 'Support opens with the public release. Until then, there is no public support channel.'}</p>${supportLink}<h2>Include what helps</h2><ul><li>Your host application and version, operating system, and Idea-Man version.</li><li>The steps that led to the issue, what you expected, and what happened.</li><li>A small, non-sensitive example and relevant error text.</li></ul><p>${repository ? 'GitHub issues are public. ' : ''}Do not post passwords, API keys, private documents, personal information, or confidential conversation history. Redact sensitive details before sharing.</p><h2>Host or connected-service questions</h2><p>Account access, billing, host availability, model behavior and third-party tool connections are managed by their respective providers. Contact the relevant provider when an issue is outside Idea-Man’s packaged skills or local planner.</p><p>Support is provided as available; no response-time or availability guarantee is offered.</p>`
  },
  privacy: {
    title: 'Privacy', subtitle: 'Know where your work goes.',
    body: '<p class="document-date">Effective October 23, 2026</p><h2>What Idea-Man provides</h2><p>Idea-Man, published by Sergey Avetisyan, is a package of agent skills, reference material, and an optional local Python planner. It does not operate an Idea-Man backend or a separate account system.</p><h2>Your host handles your conversations</h2><p>Your requests, files and generated outputs are processed by the host application and model you use. If you authorize connected tools or external services, those services may receive the information needed for the task. Their terms, privacy policies, settings and retention practices apply. Check those policies before sharing sensitive information.</p><h2>Optional local records</h2><p>Idea-Man can help save and resume project records locally when you authorize that workflow. These records may contain project context and scoped correction notes. You control the local files and can inspect or delete them using your normal file tools. The packaged plugin does not install a background observer, raw-prompt logger, model training process, automatic global learning, or cross-chat synchronization.</p><h2>This website</h2><p>This static website includes no Idea-Man analytics, advertising trackers, third-party font scripts, contact form, or payment collection. Prompt-copy controls use your browser’s clipboard only when you activate them. The hosting provider may process ordinary request information such as IP addresses and request logs under its own policies.</p><h2>Public support</h2><p>GitHub issues and contributions are public and governed by GitHub’s policies. Do not include secrets, private documents or personal information. A support request may be used to investigate and address the issue you report.</p><h2>Questions or changes</h2><p>Use the <a href="../support/">support page</a> for privacy questions about Idea-Man. This page may change as the plugin evolves; the effective date will reflect updates.</p>'
  },
  terms: {
    title: 'Terms', subtitle: 'Free to use. Use good judgment.',
    body: '<p class="document-date">Effective October 23, 2026</p><h2>Publisher and service</h2><p>Idea-Man is published by Sergey Avetisyan. It is a free collection of agent skills and local workflow tools for innovation, problem solving, research and creative development. Idea-Man includes no charges, subscriptions, payments or in-plugin purchases.</p><h2>Software license</h2><p>The Idea-Man software is made available under the MIT License included with the public repository. The license governs use, copying, modification and distribution of the software, including its warranty disclaimer and limitation of liability. These website terms do not replace the repository’s license.</p><h2>Host terms and costs</h2><p>You need a compatible host to use the plugin. That host, its model provider, and any connected services have their own terms, account requirements and possible fees. Idea-Man does not provide or pay for those services. Availability can vary by account, host and location.</p><h2>Review outputs and verify execution</h2><p>AI-generated ideas, analysis, causal explanations and artifacts can be incomplete or incorrect. Use your own judgment, inspect evidence, and perform appropriate testing before acting. A generated plan is not proof that work was executed, a test passed, or a result was published. High-stakes decisions require suitable professional review.</p><h2>Your responsibilities</h2><p>Use information you are authorized to share and comply with applicable laws, rights, host rules and connected-service policies. You decide whether to use an output and whether to authorize tool actions or local project records.</p><h2>Availability and support</h2><p>The plugin may be updated, changed or discontinued. No uptime, support response, fitness for a particular purpose, or specific outcome is promised. See the <a href="../support/">support page</a> for help and the <a href="../privacy/">privacy page</a> for data-handling details.</p>'
  }
};
for (const [slug, page] of Object.entries(pages)) {
  const pageCanonical = site ? `<link rel="canonical" href="${escape(new URL(`${slug}/`, site.endsWith('/') ? site : site + '/').href)}">` : '';
  const document = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#F6F43C"><title>${page.title} — Idea-Man</title><meta name="description" content="Idea-Man ${page.title.toLowerCase()} information. Published by Sergey Avetisyan.">${pageCanonical}<link rel="icon" href="../favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="32x32" href="../assets/icon-32.png"><link rel="apple-touch-icon" href="../assets/apple-touch-icon.png"><link rel="stylesheet" href="../styles.css?v=${styleVersion}"></head><body><a class="skip" href="#main">Skip to content</a><header class="header"><nav class="wrap navigation" aria-label="Main navigation"><a class="brand" href="../"><img src="../assets/mark.svg" width="44" height="44" alt=""><span>Idea-Man<span class="brand-dot">.</span></span></a><a class="nav-cta" href="../#install">Get Idea-Man ↗</a></nav></header><main id="main"><section class="document-hero"><div class="wrap"><p class="eyebrow">Idea-Man / ${page.title}</p><h1>${page.title.toUpperCase()}.</h1><p>${page.subtitle}</p></div></section><article class="wrap document-body">${page.body}</article></main><footer class="footer"><div class="wrap footer-top"><a class="brand" href="../">Idea-Man.</a><nav class="legal-links" aria-label="Information"><a href="../support/">Support</a><a href="../privacy/">Privacy</a><a href="../terms/">Terms</a></nav><p>Published by Sergey Avetisyan</p></div></footer></body></html>`;
  await mkdir(path.join(dist, slug), { recursive: true });
  await writeFile(path.join(dist, slug, 'index.html'), document);
}
for (const rel of ['index.html', ...Object.keys(pages).map(slug => `${slug}/index.html`)]) {
  const page = await readFile(path.join(dist, rel), 'utf8');
  for (const match of page.matchAll(/(?:src|href|srcset)="([^"]*assets\/[^"]+)"/g)) {
    for (const candidate of match[1].split(',').map(part => part.trim().split(/\s+/)[0])) {
      const target = path.resolve(path.dirname(path.join(dist, rel)), candidate);
      try { await access(target); } catch { throw new Error(`Built page ${rel} references missing asset ${candidate}`); }
    }
  }
}
console.log(`Built static site in ${dist}; repository ${repository ? 'configured' : 'pending'}; public marketplace ${marketplace ? 'verified' : 'pending'}.`);

