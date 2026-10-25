import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, cp, mkdir, readFile, writeFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
for (const releaseStatus of ['candidate','released'])
for (const repositoryUrl of ['https://github.com/sergey9519546/idea-man', null]) {
  test(releaseStatus + ' installation with repository ' + repositoryUrl, async () => {
    const temporary = await mkdtemp(path.join(os.tmpdir(), 'idea-man-distribution-'));
    try {
      await cp(path.join(root, 'site'), path.join(temporary, 'site'), { recursive: true });
      await mkdir(path.join(temporary, 'plugins/idea-man'), { recursive: true });
      await cp(path.join(root, 'plugins/idea-man/assets'), path.join(temporary, 'plugins/idea-man/assets'), { recursive: true });
      const configPath = path.join(temporary, 'site/site-config.json');
      const config = JSON.parse(await readFile(configPath, 'utf8'));
      Object.assign(config, { repositoryUrl, releaseStatus, version: '1.2.2', marketplaceUrl: null, marketplacePublicVerified: false });
      await writeFile(configPath, JSON.stringify(config));
      execFileSync(process.execPath, ['site/build.mjs'], { cwd: temporary });
      execFileSync(process.execPath, ['site/validate.mjs'], { cwd: temporary });
      const html = await readFile(path.join(temporary, 'docs/index.html'), 'utf8');
      if (releaseStatus === 'candidate') assert(html.includes('This candidate is unpublished'));
      else { assert(!html.includes('This candidate is unpublished')); assert(html.includes('Version v1.2.2.')); }
      assert(!html.includes('idea-man-1.2.2.zip'));
      assert(!html.includes('/releases/latest'));
      assert(!html.includes('>Install Idea-Man '));
      const commands = [...html.matchAll(/<pre><code>([\s\S]*?)<\/code><\/pre>/g)].map(x => x[1]).filter(x => /claude|codex/.test(x));
      if (repositoryUrl) {
        assert.deepEqual(commands, [
          'claude plugin marketplace add sergey9519546/idea-man\nclaude plugin install idea-man@idea-man-marketplace',
          'codex plugin marketplace add sergey9519546/idea-man --ref main'
        ]);
        assert(html.includes('href="' + repositoryUrl + '/releases"'));
        assert((await readFile(path.join(temporary, 'docs/support/index.html'), 'utf8')).includes('href="' + repositoryUrl + '/issues"'));
      } else {
        assert.deepEqual(commands, ['claude --plugin-dir &quot;&lt;path-to-unzipped-idea-man-directory&gt;&quot;']);
        assert(html.includes('.claude-plugin/plugin.json'));
        assert(html.includes('for this session only'));
        assert(!html.includes('marketplace add'));
        assert(!html.includes('github.com'));
        assert(!html.includes('idea-man@idea-man-marketplace'));
      }
      for (const link of html.matchAll(/href="(https:[^"]+)"/g)) {
        const url = new URL(link[1]);
        assert(['github.com', 'sergey9519546.github.io'].includes(url.hostname), 'Unexpected external installation link ' + url);
      }
    } finally {
      assert(path.basename(temporary).startsWith('idea-man-distribution-'));
      assert.equal(path.dirname(temporary), os.tmpdir());
      await rm(temporary, { recursive: true, force: true });
    }
  });
}
