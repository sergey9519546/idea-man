"""Behavior regressions for method fitness and the public candidate CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_router_v2 import assessment, router
from test_candidates import assessment as candidate_assessment

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT/'plugins/idea-man/skills/creative-director/scripts/studio.py'

class ClaimsIntegrationTests(unittest.TestCase):
    def high_stakes(self, actions):
        a = assessment(actions=actions, effort='quick')
        a['problem'].update(stakes='high', reversibility='irreversible')
        return a

    def test_quick_high_stakes_invention_keeps_a_generating_method(self):
        a = self.high_stakes(['ideate'])
        a['problem'].update(kind='new_possibility', bottleneck='novelty')
        p = router.plan_v2(a)
        ids = {m['id'] for m in p['methods']}
        self.assertTrue(ids & {'L1','L5'}, 'A test method alone cannot supply the requested invention')
        self.assertIn('D2', ids)
        self.assertIn('generate_options', {n['id'] for n in p['steps']})

    def test_quick_high_stakes_diagnosis_keeps_causal_work(self):
        p = router.plan_v2(self.high_stakes(['diagnose']))
        self.assertTrue({'Y2','D2'} <= {m['id'] for m in p['methods']})

    def test_explicit_single_method_remains_authoritative(self):
        a = self.high_stakes(['ideate'])
        a['requested_methods'] = ['S2']
        p = router.plan_v2(a)
        self.assertEqual([m['id'] for m in p['methods']], ['S2'])

    def test_status_does_not_acquire_methods_because_stakes_are_high(self):
        p = router.plan_v2(self.high_stakes(['status']))
        self.assertEqual(p['methods'], [])

    def test_candidate_cli_reads_input_without_selecting_or_writing(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'candidates.json'
            path.write_text(json.dumps(candidate_assessment()), encoding='utf-8')
            before = path.read_bytes()
            run = subprocess.run([sys.executable,str(STUDIO),'compare-candidates','--assessment',str(path)],
                                 capture_output=True,text=True,encoding='utf-8',cwd=d)
            self.assertEqual(run.returncode,0,run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result['eligible_for_scoped_next_step'],['a'])
            self.assertFalse(result['selection_made'])
            self.assertFalse(result['execution_authorized'])
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual([x.name for x in Path(d).iterdir()],['candidates.json'])

    def test_duplicate_candidate_json_rejected_by_public_studio_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'duplicate.json'
            payload = '{"schema_version":1,' + json.dumps(candidate_assessment())[1:]
            path.write_text(payload,encoding='utf-8')
            run = subprocess.run([sys.executable,str(STUDIO),'compare-candidates','--assessment',str(path)],
                                 capture_output=True,text=True,encoding='utf-8',cwd=d)
            self.assertEqual(run.returncode,2)
            self.assertIn('Duplicate',json.loads(run.stderr)['error'])
            self.assertEqual(path.read_text(encoding='utf-8'),payload)

    def test_invalid_candidate_cli_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.json'
            path.write_text('{"schema_version":1}',encoding='utf-8')
            run = subprocess.run([sys.executable,str(STUDIO),'compare-candidates','--assessment',str(path)],
                                 capture_output=True,text=True,encoding='utf-8',cwd=d)
            self.assertEqual(run.returncode,2)
            self.assertIn('error',json.loads(run.stderr))
            self.assertNotIn('Traceback',run.stderr)

if __name__ == '__main__':
    unittest.main()
