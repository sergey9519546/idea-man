import { readFile, mkdir, copyFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';

const sha = bytes => createHash('sha256').update(bytes.toString('utf8').replaceAll('\r\n','\n')).digest('hex');
const esc = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

export async function loadEvidence(root) {
  const data = JSON.parse(await readFile(path.join(root, 'eval/examples/results.json'), 'utf8'));
  if (data.evidence_kind !== 'authored_synthetic_worked_examples' || data.status !== 'worked_examples_only' || data.source_hash_algorithm !== 'sha256-utf8-lf' ||
      data.model_runs !== 0 || data.baseline_comparisons !== 0 || data.independent_quality_reviews !== 0) {
    throw new Error('Worked examples cannot be presented as observed model-comparison evidence');
  }
  const required = ['eval/cases.json','eval/worked_examples.py','plugins/idea-man/skills/creative-director/scripts/candidates.py'];
  if (Object.keys(data.source_hashes).sort().join('|') !== required.sort().join('|')) throw new Error('Evidence source set changed');
  for (const file of required) {
    if (sha(await readFile(path.join(root, file))) !== data.source_hashes[file]) throw new Error('Stale evidence source: ' + file);
  }
  if (data.examples.length !== 3 || data.helper_probes.length !== 2) throw new Error('Evidence coverage changed');
  const casebook = JSON.parse(await readFile(path.join(root, 'eval/cases.json'), 'utf8'));
  for (const item of data.examples) {
    const original = casebook.cases.find(c => c.id === item.id);
    if (!original || JSON.stringify(item.conversation) !== JSON.stringify(original.turns)) throw new Error('Example conversation drift');
  }
  return data;
}

export function evidenceBody(data) {
  const examples = data.examples.map((item, index) => `<section class="worked-case" id="${esc(item.id)}">
    <p class="eyebrow">0${index+1} / Synthetic task</p><h2>${esc(item.title)}</h2>
    <details><summary>Read the supplied conversation <span aria-hidden="true">+</span></summary>
    ${item.conversation.map(turn => `<p><strong>${esc(turn.role)}:</strong> ${esc(turn.content)}</p>`).join('')}</details>
    <h3>Why this approach</h3><p>${esc(item.approach)}</p>
    <h3>A worked response</h3><p>${esc(item.worked_response)}</p>
    <details><summary>Inspect the calculated facts <span aria-hidden="true">+</span></summary><pre><code>${esc(JSON.stringify(item.mechanical_checks,null,2))}</code></pre></details>
    <p class="evidence-limit"><strong>What remains unknown:</strong> ${esc(item.limits)}</p></section>`).join('');
  const probes = data.helper_probes.map(probe => `<li><strong>${esc(probe.label)}:</strong> ${esc(probe.output.candidates[0].readiness)}. Eligible candidates: ${esc(probe.output.eligible_for_scoped_next_step.join(', ') || 'none')}.</li>`).join('');
  return `<p class="evidence-notice"><strong>Worked examples, not captured model runs.</strong> These three responses were authored to make the intended standard concrete. Their arithmetic and two executions of the packaged decision helper are reproducible. There are no assistant-versus-plugin results or independent quality ratings here.</p>
  <p>See the starting facts, the reasoning choice and a usable response. Each example comes from a synthetic evaluation task, not a customer case or a measured business result.</p>
  <nav class="evidence-nav" aria-label="Worked examples"><a href="#queue_diagnosis">Diagnosis</a><a href="#choice_sensitivity">Decision</a><a href="#weak_pilot">Pilot review</a><a href="#local-checks">Local checks</a></nav>
  ${examples}
  <section id="local-checks"><h2>What the actual helper did</h2><p>On the supplied pilot judgments, the local Python helper returned:</p><ul>${probes}</ul>
  <p>Both outputs report no selection, no execution authorization and no verification of semantic truth. The input judgments are authored; the helper validates structure and readiness rules. It does not independently discover the facts, interpret the task or prove the method is best.</p>
  <details><summary>Inspect both helper inputs and outputs <span aria-hidden="true">+</span></summary><pre><code>${esc(JSON.stringify(data.helper_probes,null,2))}</code></pre></details></section>
  <h2>Open the evidence</h2><p><a href="results.json" download>Download the complete evidence record (JSON)</a>. Source hashes bind it to the exact cases, generator and helper used.</p>
  <p>Reproduce from the repository with <code>python eval/worked_examples.py --check</code>. This checks calculations and helper behavior; it runs no models.</p>
  <h2>What would substantiate the bigger claims?</h2><p>A controlled comparison needs actual responses from fresh baseline and plugin sessions with matched models, context and tool access, followed by blinded independent reviews. The repository has 14 synthetic cases and an offline import/review harness. No completed paired comparison is claimed. Installation and real customer outcomes need their own verification.</p>
  <p><a href="../#sample-output">Explore the task routes</a> or <a href="../#install">get Idea-Man</a>.</p>`;
}

export async function copyEvidence(root, dist) {
  const dest = path.join(dist, 'evidence');
  await mkdir(dest, {recursive:true});
  await copyFile(path.join(root,'eval/examples/results.json'),path.join(dest,'results.json'));
}
