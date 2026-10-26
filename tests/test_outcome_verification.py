"""Local CLI journeys for evidence-first repair and acceptance-bound reports.

These exercise actual temporary source/output files and receipt invalidation. They
do not classify natural-language conversations or measure model output quality.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_router_v2 import assessment


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'


class OutcomeVerificationJourneys(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-runs' / 'local-temp'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.environment = dict(os.environ, TEMP=str(self.folder), TMP=str(self.folder))
        self.source = self.write('source.txt', 'Requests: 20\nCompleted: 15\n')
        self.contract = self.folder / 'assessment.json'

    def write(self, name, text):
        path = self.folder / name
        path.write_text(text, encoding='utf-8')
        return path

    def task(self, **overrides):
        values = dict(actions=['review'], scope='bounded', evidence_mode='supplied',
                      sources=[{'id': 'queue', 'kind': 'file', 'locator': str(self.source),
                                'revision': hashlib.sha256(self.source.read_bytes()).hexdigest(),
                                'status': 'available', 'inspected': True}],
                      acceptance=['Preserve the supplied counts and distinguish inference'])
        values.update(overrides)
        return assessment(**values)

    def call(self, *arguments):
        run = subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                             capture_output=True, text=True, encoding='utf-8',
                             env=self.environment)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def plan(self, task):
        self.contract.write_text(json.dumps(task), encoding='utf-8')
        return self.call('plan', '--assessment', self.contract)

    def finish(self, task, step, output, evidence):
        self.plan(task)
        note = self.write(step + '-evidence.txt', evidence)
        receipt = self.call('receipt', '--assessment', self.contract, '--step', step,
                            '--artifact', output, '--evidence-file', note)
        task.setdefault('receipts', []).append(receipt)
        return self.plan(task)

    @staticmethod
    def node(plan, step):
        return next(row for row in plan['steps'] if row['id'] == step)

    def inspect(self, task):
        contract = self.write('inspected-contract.txt',
                              'Source queue has 20 requests and 15 completions. Preserve counts.\n')
        return self.finish(task, 'inspect_context', contract,
                           'Read source.txt and the requested scope; no source mutation authorized by review alone.')

    def test_audit_precedes_repair_and_changed_findings_invalidate_downstream(self):
        task = self.task(actions=['review', 'revise'], scope='exact',
                         acceptance=['Correct the heading only; preserve both supplied counts'])
        original = self.source.read_bytes()
        plan = self.inspect(task)
        summary = self.write('repair-source-summary.txt', 'Requests: 20; Completed: 15. Preserve both counts.\n')
        plan = self.finish(task, 'synthesize_sources', summary,
                           'Read source.txt and retained the authoritative values before the repair review.')
        self.assertEqual(self.node(plan, 'review_source')['state'], 'ready')
        self.assertEqual(self.node(plan, 'revise_source')['state'], 'waiting')
        self.assertEqual(self.source.read_bytes(), original)
        findings = self.write('findings.txt',
                              'Heading Requests should be Arrivals; the supplied counts are unchanged.\n')
        plan = self.finish(task, 'review_source', findings,
                           'Read the actual source. The requested bounded repair changes one heading.')
        self.assertEqual(self.node(plan, 'revise_source')['state'], 'ready')
        revised = self.write('revised.txt', self.source.read_text(encoding='utf-8').replace('Requests:', 'Arrivals:'))
        plan = self.finish(task, 'revise_source', revised,
                           'Created an out-of-place revised file from the inspected source; changed the heading only.')
        self.assertEqual(self.node(plan, 'verify_output')['state'], 'ready')
        self.assertEqual(self.node(plan, 'verify_output')['acceptance'], task['acceptance'])
        self.assertEqual(revised.read_text(encoding='utf-8'), 'Arrivals: 20\nCompleted: 15\n')
        self.assertEqual(self.source.read_bytes(), original)
        checked = self.write('verification.txt', 'Heading corrected. Counts remain 20 and 15. Source preserved.\n')
        plan = self.finish(task, 'verify_output', checked,
                           'Read revised.txt and compared it with source.txt; only Requests became Arrivals.')
        self.assertEqual(self.node(plan, 'verify_output')['state'], 'done')
        findings.write_text('Changed repair finding; the old downstream check is obsolete.\n', encoding='utf-8')
        plan = self.plan(task)
        self.assertEqual(self.node(plan, 'review_source')['state'], 'ready')
        self.assertEqual(self.node(plan, 'revise_source')['state'], 'waiting')
        self.assertEqual(self.node(plan, 'verify_output')['state'], 'waiting')
        self.assertIn('verify_output', {row['step'] for row in plan['ignored_receipts']})

    def test_research_and_brief_outputs_have_acceptance_bound_checks(self):
        for action, artifact, work_step, output_text in [
                ('research', 'research_brief', 'synthesize_sources',
                 '20 requests; 15 completions. A five-request difference is observed; its cause is unknown.\n'),
                ('brief', 'brief', 'frame_problem',
                 'Explain the gap between 20 requests and 15 completions; preserve staffing and inspect causes.\n')]:
            with self.subTest(action=action):
                task = self.task(actions=[action], artifact_kind=artifact)
                before = self.source.read_bytes()
                plan = self.inspect(task)
                self.assertEqual(self.node(plan, work_step)['state'], 'ready')
                work = self.write(action + '-result.txt', output_text)
                plan = self.finish(task, work_step, work,
                                   'Read source.txt. This output preserves the supplied counts and does not invent a cause.')
                if action == 'brief':
                    summary = self.write('brief-source-summary.txt', 'Supplied counts remain 20 requests and 15 completions.\n')
                    plan = self.finish(task, 'synthesize_sources', summary,
                                       'Inspected the supplied source against the framed problem.')
                verify = self.node(plan, 'verify_output')
                self.assertEqual(verify['state'], 'ready')
                self.assertEqual(verify['acceptance'], task['acceptance'])
                self.assertNotIn('produce_artifact', {row['id'] for row in plan['steps']})
                check = self.write(action + '-check.txt', 'Counts match the inspected source; uncertain cause remains explicit.\n')
                plan = self.finish(task, 'verify_output', check,
                                   'Inspected the written result against the source and the requested acceptance conditions.')
                self.assertEqual(self.node(plan, 'verify_output')['state'], 'done')
                self.assertEqual(self.source.read_bytes(), before)

    def test_standalone_review_checks_acceptance_without_production_or_duplicate_critique(self):
        task = self.task(acceptance=['Report findings only; preserve source.txt'])
        before = self.source.read_bytes()
        plan = self.inspect(task)
        self.assertEqual([row['id'] for row in plan['steps']],
                         ['inspect_context', 'synthesize_sources', 'evaluate_options', 'present'])
        summary = self.write('review-source-summary.txt', '20 requests and 15 completions; no measured cause supplied.\n')
        plan = self.finish(task, 'synthesize_sources', summary,
                           'Read the supplied source; preserve the counts and the evidence boundary.')
        review = self.node(plan, 'evaluate_options')
        self.assertEqual(review['acceptance'], task['acceptance'])
        findings = self.write('review.txt', 'Finding: the source does not establish a cause for the five-request gap.\n')
        plan = self.finish(task, 'evaluate_options', findings,
                           'Reviewed the source and checked that the findings-only report preserves it.')
        self.assertEqual(self.node(plan, 'evaluate_options')['state'], 'done')
        self.assertNotIn('produce_artifact', {row['id'] for row in plan['steps']})
        self.assertEqual(self.source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
