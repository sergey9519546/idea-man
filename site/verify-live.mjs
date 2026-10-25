import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const run = promisify(execFile);
const root = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(await readFile(path.join(root, 'site-config.json'), 'utf8'));
assert(config.siteUrl, 'Configure the verified public site URL');
const base = new URL(config.siteUrl);
async function get(url, body = true) {
  const args = ['--silent','--show-error','--fail','--location','--max-time','30'];
  if (!body) args.push('--output', process.platform === 'win32' ? 'NUL' : '/dev/null');
  args.push('--write-out','\n%{http_code}', url);
  const { stdout } = await run(process.platform === 'win32' ? 'curl.exe' : 'curl', args, { maxBuffer: 2000000 });
  const split = stdout.lastIndexOf('\n');
  assert.equal(stdout.slice(split + 1).trim(), '200', 'Expected anonymous HTTP 200: ' + url);
  return stdout.slice(0, split);
}
const routes = ['', 'support/', 'privacy/', 'terms/'];
const results = await Promise.all(routes.map(async route => {
  const url = new URL(route, base).href;
  const html = await get(url);
  assert(html.includes('<h1'), 'Expected page content at ' + url);
  assert(html.includes('href="' + url + '"'), 'Expected canonical URL at ' + url);
  if (route === 'support/') assert(html.includes(config.repositoryUrl.replace(/\/$/, '') + '/issues'), 'Missing public GitHub Issues support link');
  return { route, url, html };
}));
const assets = new Set();
for (const page of results) {
  for (const match of page.html.matchAll(/\b(?:src|href|srcset)="([^"]+)"/g)) {
    for (const candidate of match[1].split(',').map(part => part.trim().split(/\s+/)[0])) {
      if (!candidate || candidate.startsWith('#') || /^(data:|mailto:)/.test(candidate)) continue;
      const url = new URL(candidate, page.url);
      if (url.origin === base.origin && url.pathname.startsWith(base.pathname)) {
        url.hash = '';
        if (/\.(?:css|js|png|webp|svg|ico)$/.test(url.pathname)) assets.add(url.href);
      }
    }
  }
}
const queue = [...assets];
await Promise.all(Array.from({ length: Math.min(4, queue.length) }, async () => {
  while (queue.length) await get(queue.pop(), false);
}));
await get(config.repositoryUrl.replace(/\/$/, '') + '/issues', false);
console.log(JSON.stringify({ checkedAt: new Date().toISOString(), anonymous: true, routes: results.map(({url}) => ({url,status:200})), referencedAssets: assets.size, supportIssuesStatus:200, deployedVersion: results[0].html.match(/Version v(\d+\.\d+\.\d+)/)?.[1] || null, localStagedVersion: config.version }, null, 2));
