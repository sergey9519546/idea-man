"""Distinguish committed writes from cleanup failures without duplicating state."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('postcommit_studio',
    ROOT/'plugins/idea-man/skills/creative-director/scripts/studio.py')
studio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(studio)


class PostCommitRecoveryTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT/'test-runs/local-temp'
        parent.mkdir(parents=True,exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.record = Path(temporary.name)/'project.json'
        self.lock = self.record.with_name(self.record.name+'.lock')

    def failed_cleanup(self):
        original = Path.unlink
        target = self.lock
        def unlink(path,*args,**kwargs):
            if path == target:
                raise PermissionError('Injected owned-lock cleanup failure')
            return original(path,*args,**kwargs)
        return patch.object(Path,'unlink',new=unlink)

    def test_committed_append_reports_success_with_explicit_cleanup_warning(self):
        studio.init_project(self.record,'Fixture')
        event = {'type':'note','text':'Save exactly once'}
        with self.failed_cleanup():
            result = studio.record_event(self.record,0,event)
        self.assertEqual(result['revision'],1)
        self.assertEqual(result['write_status']['state'],'committed')
        self.assertEqual(result['write_status']['lock_cleanup'],'failed')
        self.assertEqual(result['write_status']['lock_path'],str(self.lock))
        self.assertEqual(studio.project_view(studio.read_json(self.record))['notes'],['Save exactly once'])
        self.assertTrue(self.lock.exists())
        with self.assertRaisesRegex(studio.StudioError,'locked'):
            studio.record_event(self.record,1,event)
        # This fixture owns the completed writer; it can establish safe recovery.
        self.lock.unlink()
        with self.assertRaisesRegex(studio.StudioError,'Revision conflict'):
            studio.record_event(self.record,0,event)
        self.assertEqual(studio.project_view(studio.read_json(self.record))['notes'],['Save exactly once'])

    def test_initialization_commit_is_not_reported_as_a_failed_init(self):
        with self.failed_cleanup():
            result = studio.init_project(self.record,'Fixture')
        self.assertEqual(result['revision'],0)
        self.assertEqual(result['write_status']['state'],'committed')
        self.assertTrue(self.record.exists())
        self.assertTrue(self.lock.exists())

    def test_validation_failure_cannot_be_reported_as_a_committed_write(self):
        studio.init_project(self.record,'Fixture')
        before = self.record.read_bytes()
        with self.failed_cleanup():
            with self.assertRaisesRegex(studio.LockCleanupError,'Revision conflict'):
                studio.record_event(self.record,9,{'type':'note','text':'Do not save'})
        self.assertEqual(self.record.read_bytes(),before)
        self.assertTrue(self.lock.exists())

    def test_public_cli_reports_committed_state_when_only_lock_cleanup_fails(self):
        studio.init_project(self.record,'Fixture')
        event = self.record.parent/'event.json'
        event.write_text(json.dumps({'type':'note','text':'Exactly one committed CLI note'}),encoding='utf-8')
        script = str(ROOT/'plugins/idea-man/skills/creative-director/scripts/studio.py')
        driver = (
            "from pathlib import Path\nimport runpy,sys\nfrom unittest.mock import patch\n"
            "script,record,event=sys.argv[1:]\n"
            "lock=Path(record+'.lock');original=Path.unlink\n"
            "def fail(path,*args,**kwargs):\n"
            " if path==lock:raise PermissionError('Injected lock cleanup failure')\n"
            " return original(path,*args,**kwargs)\n"
            "sys.argv=[script,'record','--file',record,'--expected-revision','0','--event',event]\n"
            "with patch.object(Path,'unlink',new=fail):runpy.run_path(script,run_name='__main__')\n"
        )
        result = subprocess.run([sys.executable,'-c',driver,script,str(self.record),str(event)],
                                capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        saved = json.loads(result.stdout)
        self.assertEqual(saved['write_status']['state'],'committed')
        self.assertEqual(saved['write_status']['revision'],1)
        self.assertEqual(saved['notes'],['Exactly one committed CLI note'])
        self.assertTrue(self.lock.exists())
        stored = studio.read_json(self.record)
        self.assertNotIn('write_status',stored)
        self.assertEqual(len(stored['events']),1)


if __name__=='__main__':
    unittest.main()
