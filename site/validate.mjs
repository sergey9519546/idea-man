import { readFile, access, readdir, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const root = path.dirname(fileURLToPath(import.meta.url));
const dist = path.resolve(root, '../docs');
const assetSource = path.resolve(root, '../plugins/idea-man/assets');
const config = JSON.parse(await readFile(path.join(root, 'site-config.json'), 'utf8'));
const hash = content => createHash('sha256').update(content).digest('hex');

async function htmlFiles(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await htmlFiles(full));
    else if (entry.name.endsWith('.html')) out.push(full);
  }
  return out;
}
const pages = await htmlFiles(dist);
assert(pages.length >= 5, 'Expected index, support, privacy and terms pages');
let checkedRefs = 0, checkedImgs = 0;
for (const file of pages) {
  const rel = path.relative(dist, file);
  const html = await readFile(file, 'utf8');
  assert(!html.includes('{{'), `${rel}: unresolved template token`);
  assert(!/href=["'](?:#|javascript:|https:\/\/example\.)["']/i.test(html), `${rel}: invalid link target`);
  assert.equal((html.match(/<h1[ >]/g) || []).length, 1, `${rel}: exactly one primary heading required`);
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(item => item[1]);
  assert.equal(new Set(ids).size, ids.length, `${rel}: duplicate element ID`);
  // every local src/href/srcset resolves inside dist
  const refs = [];
  for (const m of html.matchAll(/\b(?:src|href)="([^"]*)"/g)) refs.push(m[1]);
  for (const m of html.matchAll(/\bsrcset="([^"]*)"/g)) refs.push(...m[1].split(',').map(part => part.trim().split(/\s+/)[0]));
  for (const ref of refs) {
    if (!ref || /^(https?:|mailto:|data:)/.test(ref)) continue;
    if (ref.startsWith('#')) { assert(ids.includes(ref.slice(1)), `${rel}: missing anchor ${ref}`); continue; }
    const clean = ref.split('#')[0].split('?')[0];
    let target = path.resolve(path.dirname(file), clean);
    assert(target === dist || target.startsWith(dist + path.sep), `${rel}: ${ref} escapes dist`);
    if ((await stat(target).catch(() => null))?.isDirectory()) target = path.join(target, 'index.html');
    await access(target).catch(() => assert.fail(`${rel}: ${ref} does not exist in dist`));
    checkedRefs++;
  }
  // every img has alt; empty alt only with adjacent brand text
  for (const m of html.matchAll(/<img\b[^>]*>/g)) {
    const tag = m[0];
    assert(/\salt="/.test(tag), `${rel}: <img> without alt: ${tag.slice(0, 80)}`);
    const alt = tag.match(/\salt="([^"]*)"/)[1];
    if (alt === '' && !rel.startsWith('brand')) {
      const after = html.slice(m.index + tag.length, m.index + tag.length + 220).replace(/<[^>]+>/g, ' ');
      assert(/idea\s*man/i.test(after), `${rel}: decorative <img alt=""> not adjacent to brand text`);
    }
    checkedImgs++;
  }
}
assert(await access(path.join(dist, '.nojekyll')).then(() => true, () => false), 'docs/.nojekyll missing');
assert(!await access(path.join(dist, 'CNAME')).then(() => true, () => false), 'CNAME must not exist');
assert(!/(?:src|href)="\//.test((await Promise.all(pages.map(f => readFile(f, 'utf8')))).join('')), 'root-absolute URL found');
const index = await readFile(path.join(dist, 'index.html'), 'utf8');
assert(!index.includes('Brainstorm. Sharpen. Create.'), 'Retired subtitle present');
for (const m of index.matchAll(/<a\b[^>]*class="[^"]*(?:button|nav-cta)[^"]*"[^>]*>\s*Get Idea Man/g)) assert(/href="#install"/.test(m[0]), 'Get Idea Man CTA must target #install');
if (!config.repositoryUrl) assert(!/github/i.test(index), 'GitHub wording visible while repositoryUrl is null');
for (const sel of ['id="sample-output"', 'id="install"']) assert(index.includes(sel), `Missing section ${sel}`);
assert.equal((index.match(/class="install-host"/g) || []).length, 3, 'Three install-host blocks required');
// shipped art must match the plugin assets byte for byte
for (const file of ['invisible-nerd.png', 'lightbulb-hero.png', 'invisible-nerd-1024.webp', 'lightbulb-hero-1024.webp', 'mark.svg', 'icon.png']) {
  assert.equal(hash(await readFile(path.join(assetSource, file))), hash(await readFile(path.join(dist, 'assets', file))), `Asset differs from plugin source: ${file}`);
}
assert(!index.includes('plugins_6adbe347257481919f70f99db17daa40') || config.marketplacePublicVerified, 'Private listing exposed');
if (!config.marketplacePublicVerified) assert(!index.includes('>Install Idea Man '), 'Unverified marketplace install claim');
console.log(`Static checks passed: ${pages.length} pages, ${checkedRefs} local references and ${checkedImgs} images verified, anchors resolve, CTAs point to #install, GitHub hidden while repositoryUrl is null, asset hashes match.`);
