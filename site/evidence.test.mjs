import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,cp,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {loadEvidence,evidenceBody} from './evidence.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
test('public worked examples disclose limits and escape response text',async()=>{
 const data=await loadEvidence(root);
 const html=evidenceBody(data);
 assert(html.includes('not captured model runs'));
 assert(html.includes('No completed paired comparison is claimed'));
 const altered=structuredClone(data);
 altered.examples[0].worked_response='<script>alert("bad")</script>';
 const safe=evidenceBody(altered);
 assert(!safe.includes('<script>'));
 assert(safe.includes('&lt;script&gt;'));
});
test('source drift or model-result relabeling cannot enter the web build',async()=>{
 const temp=await mkdtemp(path.join(os.tmpdir(),'idea-man-evidence-'));
 try{
  await cp(path.join(root,'eval'),path.join(temp,'eval'),{recursive:true});
  await cp(path.join(root,'plugins'),path.join(temp,'plugins'),{recursive:true});
  await loadEvidence(temp);
  const sourceFile=path.join(temp,'eval/cases.json');
  const sourceText=await readFile(sourceFile,'utf8');
  await writeFile(sourceFile,sourceText.replace(/\r?\n/g,'\r\n'));
  await loadEvidence(temp);

  const file=path.join(temp,'eval/examples/results.json');
  const data=JSON.parse(await readFile(file,'utf8'));
  data.model_runs=1;
  await writeFile(file,JSON.stringify(data));
  await assert.rejects(loadEvidence(temp),/cannot be presented/);
  data.model_runs=0;
  await writeFile(file,JSON.stringify(data));
  await writeFile(path.join(temp,'eval/cases.json'),'{}');
  await assert.rejects(loadEvidence(temp),/Stale evidence source/);
 }finally{
  assert.equal(path.dirname(temp),os.tmpdir());
  assert(path.basename(temp).startsWith('idea-man-evidence-'));
  await rm(temp,{recursive:true,force:true});
 }
});
