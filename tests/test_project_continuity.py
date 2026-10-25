"""Actual local CLI continuation journeys; no providers required."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/studio.py'

class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.record = self.folder / 'project.json'
        self.call('init', '--file', self.record, '--title', 'Service delays')
    def call(self, *args, ok=True):
        run = subprocess.run([sys.executable, str(SCRIPT), *map(str,args)],
                             capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(run.returncode, 0 if ok else 2, run.stderr)
        return json.loads(run.stdout if ok else run.stderr)
    def assessment(self):
        return {'schema_version':2,'task_id':'service','objective':'Reduce delays without extra staff',
          'domain':'operations','actions':['diagnose','experiment'],'deliverable':'text',
          'artifact_kind':'experiment_plan','scope':'bounded','stage':'framed',
          'problem':{'kind':'causal','bottleneck':'evidence','novelty':'improve','stakes':'medium','reversibility':'reversible'},
          'evidence_mode':'hypothesis','sources':[],
          'selection':{'status':'not_needed','ids':[],'evidence':''},
          'constraints':[{'id':'staff','text':'No extra staff','kind':'hard','evidence':'User instruction'}],
          'evidence':[{'source':'user','detail':'Reduce delays without extra staff'}],
          'requested_count':3,'acceptance':['Define an observation and decision rule']}
    def append(self,event,revision=0,ok=True):
        path=self.folder/'event.json'
        path.write_text(json.dumps(event),encoding='utf-8')
        return self.call('record','--file',self.record,'--expected-revision',revision,'--event',path,ok=ok)
    def checkpoint(self,a=None,revision=0):
        return self.append({'type':'checkpoint','assessment':a or self.assessment(),
                            'pending_actions':['diagnose','experiment'],'evidence':'User asks to save and continue'},revision)
    def test_cli_round_trip_and_read_only_resume(self):
        a=self.assessment()
        self.checkpoint(a)
        before=self.record.read_bytes()
        packet=self.call('resume','--file',self.record)
        self.assertEqual(before,self.record.read_bytes())
        draft=packet['resume_assessment']
        self.assertFalse(packet['execution_authorized'])
        self.assertFalse(draft['continuity']['source_rechecked'])
        self.assertEqual(draft['requested_count'],3)
        self.assertEqual(draft['constraints'],a['constraints'])
        self.assertEqual(draft['acceptance'],a['acceptance'])
        path=self.folder/'draft.json';path.write_text(json.dumps(draft),encoding='utf-8')
        plan=self.call('plan','--assessment',path)
        self.assertIn('restore_checkpoint',plan['blockers'])
    def test_legacy_and_post_checkpoint_changes(self):
        self.assertIsNone(self.call('resume','--file',self.record)['resume_assessment'])
        self.checkpoint()
        self.append({'type':'brief','text':'A changed objective'},1)
        packet=self.call('resume','--file',self.record)
        self.assertIsNone(packet['resume_assessment'])
        self.assertIn('Record changed',packet['blockers'][0])
    def test_source_drift_and_missing_artifact(self):
        import hashlib
        source=self.folder/'source.txt';source.write_text('before')
        a=self.assessment()
        a['sources']=[{'id':'source','kind':'file','locator':str(source),
                      'revision':hashlib.sha256(source.read_bytes()).hexdigest(),'status':'available','inspected':True}]
        self.append({'type':'artifact','id':'report','path':str(self.folder/'missing.txt'),'status':'tested'})
        self.checkpoint(a,1)
        source.write_text('after')
        packet=self.call('resume','--file',self.record)
        self.assertEqual(packet['observations'][0]['state'],'changed')
        self.assertEqual(packet['observations'][1]['state'],'missing')
        self.assertFalse(packet['resume_assessment']['sources'][0]['inspected'])
        source.unlink()
        self.assertEqual(self.call('resume','--file',self.record)['observations'][0]['state'],'missing')
    def test_old_capabilities_and_choice_authority_not_restored(self):
        a=self.assessment();a['capabilities']=['web','file_write']
        a['selection']={'status':'assistant_authorized','ids':[],'evidence':'Choose for me'}
        self.checkpoint(a)
        draft=self.call('resume','--file',self.record)['resume_assessment']
        self.assertEqual(draft['capabilities'],[])
        self.assertEqual(draft['receipts'],[])
        self.assertEqual(draft['selection']['status'],'none')
    def test_invalid_events_conflicts_and_no_overwrite(self):
        before=self.record.read_bytes()
        for change in [{'pending_actions':['resume']},{'assessment':{'schema_version':2}},{'extra':'bad'}]:
            event={'type':'checkpoint','assessment':self.assessment(),'pending_actions':['diagnose'],'evidence':'Save'}
            event.update(change)
            self.append(event,ok=False)
            self.assertEqual(before,self.record.read_bytes())
        self.checkpoint()
        before=self.record.read_bytes()
        self.append({'type':'note','text':'conflict'},0,ok=False)
        self.call('init','--file',self.record,'--title','overwrite',ok=False)
        self.assertEqual(before,self.record.read_bytes())
    def test_relative_sources_rejected_and_resume_independent_of_cwd(self):
        a=self.assessment()
        a['sources']=[{'id':'s','kind':'file','locator':'relative.txt',
                      'revision':'old','status':'available','inspected':True}]
        self.append({'type':'checkpoint','assessment':a,'pending_actions':['diagnose'],'evidence':'save'},ok=False)
        self.append({'type':'artifact','id':'legacy','path':'relative.txt','status':'tested'})
        self.checkpoint(revision=1)
        other=self.folder/'other';other.mkdir()
        run=subprocess.run([sys.executable,str(SCRIPT),'resume','--file',str(self.record)],
                           cwd=other,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        packet=json.loads(run.stdout)
        self.assertEqual(packet['observations'][0]['state'],'relative_locator_unresolved')
    def test_missing_unresolved_source_and_active_lock(self):
        a=self.assessment()
        a['sources']=[{'id':'unknown','kind':'file','locator':'','revision':'',
                      'status':'missing','inspected':False}]
        self.checkpoint(a)
        packet=self.call('resume','--file',self.record)
        self.assertEqual(packet['observations'][0]['state'],'relative_locator_unresolved')
        before=self.record.read_bytes()
        lock=self.record.with_name(self.record.name+'.lock')
        lock.write_text('active writer')
        self.append({'type':'note','text':'blocked'},1,ok=False)
        self.assertEqual(before,self.record.read_bytes())
        self.assertEqual(lock.read_text(),'active writer')
    def test_sparse_valid_assessment_and_foreign_pending_action(self):
        a=self.assessment();a.pop('acceptance');a.pop('requested_count')
        self.checkpoint(a)
        packet=self.call('resume','--file',self.record)
        self.assertEqual(packet['resume_assessment']['task_id'],'service')
        path=self.folder/'draft.json';path.write_text(json.dumps(packet['resume_assessment']),encoding='utf-8')
        self.call('plan','--assessment',path)
        before=self.record.read_bytes()
        self.append({'type':'checkpoint','assessment':a,'pending_actions':['produce'],'evidence':'save'},1,ok=False)
        self.assertEqual(before,self.record.read_bytes())
    def test_decision_change_invalidates_checkpoint(self):
        self.append({'type':'candidate','id':'a','text':'Pilot A'})
        self.checkpoint(revision=1)
        self.append({'type':'approve','target_id':'a','evidence':'User approves A'},2)
        packet=self.call('resume','--file',self.record)
        self.assertIsNone(packet['resume_assessment'])
        self.assertEqual(packet['project']['items']['a']['status'],'approved')

if __name__ == '__main__':
    unittest.main()
