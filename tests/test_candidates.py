"""Adversarial subprocess checks for evidence-linked candidate comparisons."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'plugins/idea-man/skills/creative-director/scripts/candidates.py'


def assessment():
    return {'schema_version':1, 'decision':'Choose a bounded service-delay pilot',
      'commitment':{'level':'test','text':'Run a reversible one-day scheduling pilot','evidence_refs':['brief']},
      'sources':[{'id':'brief','locator':'conversation:approved-brief','revision':'turn-3'}],
      'constraints':[{'id':'staff','text':'No additional staff'}],
      'criteria':[], 'candidates':[candidate('a')], 'comparisons':[]}


def candidate(identity):
    return {'id':identity,'mechanism':'Move one existing handoff earlier in the day',
      'checks':[{'constraint_id':'staff','status':'pass','evidence_refs':['brief'],
                 'detail':'The proposed pilot uses the current team'}],
      'ratings':[], 'assumptions':[], 'next_test':{
          'hypothesis':'Earlier handoff reduces delay without overtime',
          'observation':'Compare handoff delay and overtime against the prior baseline',
          'decision_rule':'Continue only if delay falls without added overtime'}}


def rating(identity, value):
    return {'criterion_id':identity,'value':value,'evidence_refs':['brief'],
            'detail':'Host judgment against the stated criterion'}


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'assessment.json'

    def cli(self, data, ok=True):
        self.path.write_text(json.dumps(data,allow_nan=True),encoding='utf-8')
        before=self.path.read_bytes()
        existing=set(self.path.parent.iterdir())
        run=subprocess.run([sys.executable,str(SCRIPT),'--assessment',str(self.path)],
                           cwd=self.path.parent,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0 if ok else 2,run.stderr)
        self.assertEqual(before,self.path.read_bytes())
        self.assertEqual(existing,set(self.path.parent.iterdir()))
        return json.loads(run.stdout if ok else run.stderr)

    def test_single_modest_practical_idea_no_scoring_or_agents(self):
        result=self.cli(assessment())
        self.assertEqual(result['eligible_for_scoped_next_step'],['a'])
        self.assertEqual(result['rating_comparison']['status'],'not_requested')
        self.assertFalse(result['selection_made'])
        self.assertFalse(result['execution_authorized'])
        self.assertFalse(result['semantic_truth_verified'])
        self.assertEqual(result['readiness_basis'],'conditional_on_host_reported_evidence')

    def test_high_ratings_cannot_overrule_failed_hard_constraint(self):
        a=assessment()
        a['criteria']=[{'id':'benefit','text':'Expected practical usefulness'}]
        a['candidates'][0]['ratings']=[rating('benefit',5)]
        a['candidates'][0]['checks'][0]['status']='fail'
        b=candidate('b');b['ratings']=[rating('benefit',1)]
        a['candidates'].append(b)
        result=self.cli(a)
        self.assertEqual(result['eligible_for_scoped_next_step'],['b'])
        self.assertEqual(result['candidates'][0]['readiness'],'blocked')
        self.assertEqual(result['rating_comparison']['frontier'],['b'])

    def test_missing_or_unresolved_constraint_gates_current_commitment(self):
        for level in ['explore','test','make']:
            for checks in [[],[{'constraint_id':'staff','status':'unresolved',
                              'evidence_refs':[],'detail':'Not checked'}]]:
                a=assessment();a['commitment']['level']=level
                a['candidates'][0]['checks']=checks
                result=self.cli(a)
                self.assertEqual(result['eligible_for_scoped_next_step'],[])
                self.assertEqual(result['candidates'][0]['unresolved_constraints'],['staff'])

    def test_critical_uncertainty_gates_make_but_allows_informative_test(self):
        a=assessment()
        item={'id':'effect','text':'Earlier handoff reduces delay','status':'unresolved',
              'critical':True,'evidence_refs':[]}
        a['candidates'][0]['assumptions']=[item]
        a['candidates'][0]['next_test']={'hypothesis':item['text'],
           'observation':'Compare handoff delay with the prior baseline',
           'decision_rule':'Continue only if delay falls without overtime'}
        self.assertEqual(self.cli(a)['eligible_for_scoped_next_step'],['a'])
        a['commitment']={'level':'make','text':'Deploy the workflow broadly','evidence_refs':['brief']}
        self.assertEqual(self.cli(a)['candidates'][0]['readiness'],'needs_evidence')
        item['status']='refuted';item['evidence_refs']=['brief']
        self.assertEqual(self.cli(a)['candidates'][0]['readiness'],'blocked')
        # The critical flag applies to this commitment, not to all future production.
        item['critical']=False
        self.assertEqual(self.cli(a)['eligible_for_scoped_next_step'],['a'])

    def test_ties_tradeoffs_and_incomplete_ratings(self):
        a=assessment()
        a['criteria']=[{'id':'benefit','text':'Usefulness'},{'id':'ease','text':'Simplicity'}]
        a['candidates']=[candidate(x) for x in ['a','b','c','d']]
        for c,values in zip(a['candidates'],[(4,2),(4,2),(2,4),(None,None)]):
            c['ratings']=[rating(k,v) for k,v in zip(['benefit','ease'],values) if v is not None]
        result=self.cli(a)['rating_comparison']
        self.assertEqual(result['status'],'incomplete')
        self.assertEqual(result['frontier'],['a','b','c'])
        self.assertEqual(result['unranked'],['d'])
        relations={tuple((p['left'],p['right'])):p['relation'] for p in result['pairs']}
        self.assertEqual(relations[('a','b')],'tied')
        self.assertEqual(relations[('a','c')],'incomparable_tradeoff')
        self.assertEqual(relations[('a','d')],'unknown_missing_ratings')

    def test_mechanism_relation_is_explicit_not_keyword_similarity(self):
        a=assessment();a['candidates'].append(candidate('b'))
        a['comparisons']=[{'left':'a','right':'b','relation':'distinct',
                          'evidence_refs':['brief'],'detail':'Host identifies a different causal intervention'}]
        self.assertEqual(self.cli(a)['mechanism_comparisons'],a['comparisons'])
        a['comparisons'][0]['evidence_refs']=[]
        self.cli(a,ok=False)
        a['comparisons'][0]['relation']='unknown'
        self.cli(a)
        a['comparisons'].append({'left':'b','right':'a','relation':'equivalent',
                                'evidence_refs':['brief'],'detail':'Conflicting reverse pair'})
        self.cli(a,ok=False)

    def test_transitive_equivalence_conflict_is_rejected(self):
        a=assessment();a['candidates']=[candidate(x) for x in ['a','b','c']]
        a['comparisons']=[
            {'left':'b','right':'c','relation':'equivalent','evidence_refs':['brief'],'detail':'Same mechanism'},
            {'left':'a','right':'b','relation':'equivalent','evidence_refs':['brief'],'detail':'Same mechanism'},
            {'left':'a','right':'c','relation':'distinct','evidence_refs':['brief'],'detail':'Conflicting assertion'}]
        error=self.cli(a,ok=False)
        self.assertIn('transitive equivalence',error['error'])

    def test_equivalent_groups_preserve_unknown_and_unassessed_pair_coverage(self):
        a=assessment();a['candidates']=[candidate(x) for x in ['d','c','b','a']]
        a['comparisons']=[
            {'left':'b','right':'c','relation':'equivalent','evidence_refs':['brief'],'detail':'Same mechanism'},
            {'left':'a','right':'b','relation':'equivalent','evidence_refs':['brief'],'detail':'Same mechanism'},
            {'left':'a','right':'c','relation':'unknown','evidence_refs':[],'detail':'Pair not independently checked'}]
        result=self.cli(a)
        groups=result['equivalent_mechanism_groups']
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['candidate_ids'],['a','b','c'])
        self.assertEqual(groups[0]['evidence_refs'],['brief'])
        coverage=result['mechanism_pair_coverage']
        self.assertEqual(coverage['total_pairs'],6)
        self.assertEqual(coverage['explicit_relations'],3)
        self.assertEqual(coverage['unknown_pairs'],[{'left':'a','right':'c'}])
        self.assertEqual(coverage['unassessed_pairs'],
            [{'left':'a','right':'d'},{'left':'b','right':'d'},{'left':'c','right':'d'}])
        self.assertEqual(result['mechanism_comparisons'][2]['relation'],'unknown')
        # Identical wording alone never creates equivalence evidence.
        a['comparisons']=[]
        result=self.cli(a)
        self.assertEqual(result['equivalent_mechanism_groups'],[])
        self.assertEqual(len(result['mechanism_pair_coverage']['unassessed_pairs']),6)

    def test_missing_evidence_and_dangling_links_fail_validation(self):
        mutations=[]
        a=assessment();a['candidates'][0]['checks'][0]['evidence_refs']=[];mutations.append(a)
        a=assessment();a['candidates'][0]['checks'][0]['evidence_refs']=['absent'];mutations.append(a)
        a=assessment();a['sources'][0]['revision']='';mutations.append(a)
        a=assessment();a['candidates'][0]['checks'][0]['constraint_id']='absent';mutations.append(a)
        a=assessment();a['criteria']=[{'id':'fit','text':'Fit'}]
        a['candidates'][0]['ratings']=[rating('absent',3)];mutations.append(a)
        a=assessment();a['candidates'][0]['assumptions']=[{
            'id':'risk','text':'Critical unknown','status':'unresolved','critical':True,'evidence_refs':[]}]
        a['candidates'][0]['next_test']=None
        mutations.append(a)
        for refs in [['absent'],['brief','brief'],True]:
            a=assessment();a['commitment']['evidence_refs']=refs;mutations.append(a)
        for a in mutations:
            with self.subTest(a=a):self.cli(a,ok=False)

    def test_unknown_fields_duplicates_and_bad_types(self):
        mutations=[]
        a=assessment();a['extra']='unknown';mutations.append(a)
        a=assessment();a['candidates'][0]['checks'].append(copy.deepcopy(a['candidates'][0]['checks'][0]));mutations.append(a)
        a=assessment();a['sources'].append(copy.deepcopy(a['sources'][0]));mutations.append(a)
        a=assessment();a['candidates'].append(copy.deepcopy(a['candidates'][0]));mutations.append(a)
        for value in [True,1.5,float('nan'),float('inf'),-1,6]:
            a=assessment();a['criteria']=[{'id':'fit','text':'Fit'}]
            a['candidates'][0]['ratings']=[rating('fit',value)];mutations.append(a)
        for status in [True,{},'approved']:
            a=assessment();a['candidates'][0]['checks'][0]['status']=status;mutations.append(a)
        a=assessment();item={'id':'same','text':'Assumption','status':'supported','critical':False,'evidence_refs':['brief']}
        a['candidates'][0]['assumptions']=[item,copy.deepcopy(item)];mutations.append(a)
        for a in mutations:
            with self.subTest(a=a):self.cli(a,ok=False)

    def test_consequential_commitment_needs_linked_source_evidence(self):
        for level in ['test','make']:
            a=assessment();a['commitment']['level']=level
            a['sources']=[];a['constraints']=[];a['candidates'][0]['checks']=[]
            a['commitment'].pop('evidence_refs',None)
            result=self.cli(a)['candidates'][0]
            self.assertEqual(result['readiness'],'needs_evidence')
            self.assertIn('commitment_source_evidence',result['readiness_gaps'])
        # An unused source registry is not evidence for a commitment.
        a=assessment();a['commitment'].pop('evidence_refs')
        result=self.cli(a)['candidates'][0]
        self.assertIn('commitment_source_evidence',result['readiness_gaps'])
        a['commitment']['evidence_refs']=['brief']
        a['candidates'][0]['next_test']={'hypothesis':'Earlier handoff reduces delay',
           'observation':'Compare delay and overtime with baseline',
           'decision_rule':'Retain only if delay falls without overtime'}
        self.assertEqual(self.cli(a)['eligible_for_scoped_next_step'],['a'])

    def test_test_commitment_needs_observable_protocol(self):
        a=assessment();a['candidates'][0]['next_test']=None
        result=self.cli(a)['candidates'][0]
        self.assertEqual(result['readiness'],'needs_evidence')
        self.assertIn('test_protocol',result['readiness_gaps'])
        # Source-free exploration remains valid without a forced scorecard/protocol.
        a['commitment']={'level':'explore','text':'Consider one possible mechanism'}
        a['sources']=[];a['constraints']=[];a['candidates'][0]['checks']=[]
        self.assertEqual(self.cli(a)['eligible_for_scoped_next_step'],['a'])

    def test_raw_duplicate_json_fields_rejected_without_writes(self):
        raw=json.dumps(assessment())
        variants=[
            raw.replace('"schema_version": 1', '"schema_version": 2, "schema_version": 1'),
            raw.replace('"status": "pass"', '"status": "fail", "status": "pass"')]
        for malformed in variants:
            self.path.write_text(malformed,encoding='utf-8')
            before=self.path.read_bytes()
            existing=set(self.path.parent.iterdir())
            run=subprocess.run([sys.executable,str(SCRIPT),'--assessment',str(self.path)],
                               capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(run.returncode,2,run.stderr)
            self.assertIn('Duplicate JSON field',json.loads(run.stderr)['error'])
            self.assertEqual(before,self.path.read_bytes())
            self.assertEqual(existing,set(self.path.parent.iterdir()))

    def test_deterministic_output(self):
        a=assessment()
        self.path.write_text(json.dumps(a),encoding='utf-8')
        args=[sys.executable,str(SCRIPT),'--assessment',str(self.path)]
        first=subprocess.run(args,capture_output=True,text=True,check=True).stdout
        second=subprocess.run(args,capture_output=True,text=True,check=True).stdout
        self.assertEqual(first,second)


if __name__=='__main__':
    unittest.main()
