"""Reproducible worked examples, not captured model outputs or quality grades."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/idea-man/skills/creative-director/scripts/candidates.py'
CASES = ROOT / 'eval/cases.json'
EXPECTED_CASES_SHA256 = '63d49949e3f6ec3357087758abd74f59a1773c59c2255b548c864484c26eedf7'

def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()

def run_candidate(assessment):
    import tempfile
    with tempfile.TemporaryDirectory(prefix='idea-man-evidence-') as folder:
        path = Path(folder) / 'assessment.json'
        path.write_text(json.dumps(assessment), encoding='utf-8')
        before = path.read_bytes()
        run = subprocess.run([sys.executable, str(SCRIPT), '--assessment', str(path)],
                             capture_output=True, text=True, encoding='utf-8', check=True)
        if path.read_bytes() != before:
            raise ValueError('Read-only helper modified its input')
        return json.loads(run.stdout)

def build():
    if sha(CASES) != EXPECTED_CASES_SHA256:
        raise ValueError('Source cases changed; review all worked narratives and arithmetic before updating the pinned hash')
    cases = {c['id']: c for c in json.loads(CASES.read_text(encoding='utf-8'))['cases']}
    def example(identity, title, method, result, checks, limits):
        return dict(id=identity, title=title, conversation=cases[identity]['turns'],
                    approach=method, worked_response=result, mechanical_checks=checks, limits=limits)
    weekly = 200
    setup = 4000
    horizon = 26
    threshold = weekly - setup / horizon
    decision = example('choice_sensitivity', 'A recommendation that can change',
        'Decision analysis with sensitivity. Generate alternatives only if they help the actual decision.',
        'The zero-overhead payback is 20 weeks: $4,000 / $200. That is a lower bound, not a launch recommendation. '
        'With $50/week of exceptions and maintenance it becomes 26.67 weeks; at $200/week there is no payback. '
        'For an illustrative 26-week horizon, total weekly overhead must stay below $46.15 to produce positive net savings. '
        'The user did not supply that horizon. Ask for the useful lifetime, then measure exception volume and handling time before committing. '
        'No purchase or implementation is authorized.',
        {'naive_payback_weeks':setup/weekly, 'payback_with_50_weekly_overhead':setup/(weekly-50),
         'illustrative_horizon_weeks':horizon, 'break_even_weekly_overhead':threshold,
         'positive_savings_at_40_overhead':horizon*(weekly-40)-setup,
         'negative_savings_at_50_overhead':horizon*(weekly-50)-setup},
        'Arithmetic is checked. Useful lifetime, exception costs and customer value are not observed. The 26-week scenario is illustrative.')
    diagnosis = example('queue_diagnosis', 'Investigate before redesigning',
        'Queue diagnosis and a bounded test. The user asked what to investigate, not for a new shop concept.',
        'Approval wait is worth investigating: its reported median is two days, versus 10 minutes for intake and 45 for work. '
        'Eight of ten late jobs waited for approval. That is 80% of late jobs, not an 80% risk of lateness and not proof of causation. '
        'We do not know how often on-time jobs also waited. Track ready-for-approval, approval and completion timestamps, '
        'job complexity, and late/on-time status for all jobs. Test one earlier approval check using the existing team, '
        'with workload and overtime monitored. Compare approval wait and missed dates with comparable jobs; '
        'stop if it displaces necessary work. Do not promise a time saving from these summaries.',
        {'late_jobs_waiting_fraction':8/10, 'late_jobs_total':10, 'on_time_approval_denominator_available':False},
        'Reported medians describe different stages; they do not establish the bottleneck or a causal effect. No shop pilot was run.')

    pilot = example('weak_pilot', 'A promising result is not rollout evidence',
        'Evaluate against the original acceptance rule and check comparability before deciding readiness.',
        'Median wait fell from 50 to 35 minutes, a 30% reduction. The observed wait statistic clears the 20% target. '
        'The baseline has 2 errors in 40 jobs (5%); the pilot has 1 in 5 (20%). Raw error counts fell, but the '
        'error rate rose; clarify whether the original safety criterion meant counts or rates before deciding it passed. '
        'Five jobs, a quieter week and the most experienced worker prevent attribution to the new workflow. '
        'Do not call it proven or authorize rollout. Repeat a bounded comparison with normal staffing and comparable load, '
        'record both error counts and denominators, and retain the original wait target. An exploratory repeat can inform '
        'the decision; it cannot silently replace the agreed acceptance rule.',
        {'median_wait_reduction':(50-35)/50, 'baseline_error_rate':2/40, 'pilot_error_rate':1/5,
         'baseline_jobs':40, 'pilot_jobs':5, 'observed_wait_target_met':(50-35)/50 >= .2},
        'These are sample statistics, not a causal estimate or proof that the error rate truly increased. No new pilot was executed.')
    source = {'id':'brief', 'locator':'eval/cases.json#weak_pilot', 'revision':sha(CASES)}
    assessment = {'schema_version':1, 'decision':'Determine readiness after a confounded pilot',
        'commitment':{'level':'test', 'text':'Evaluate a bounded repeat proposal; this is not permission to run it',
                      'evidence_refs':['brief']},
        'sources':[source], 'constraints':[{'id':'staff','text':'Use existing staff'}], 'criteria':[],
        'candidates':[{'id':'repeat', 'mechanism':'Compare under comparable load and normal staffing',
            'checks':[{'constraint_id':'staff','status':'pass','evidence_refs':['brief'],
                       'detail':'The authored repeat proposal uses existing staff'}],
            'ratings':[], 'assumptions':[{'id':'effect','text':'The workflow causes the wait improvement without safety loss',
                'status':'unresolved','critical':True,'evidence_refs':[]}],
            'next_test':{'hypothesis':'The improvement persists under comparable conditions',
                         'observation':'Record wait, error counts and denominators, workload and staffing',
                         'decision_rule':'Retain the wait target, clarify safety measure before testing, and do not roll out from this small confounded sample'}}],
        'comparisons':[]}
    test_input = json.loads(json.dumps(assessment))
    test_result = run_candidate(test_input)
    assessment['commitment'] = {'level':'make','text':'Consider broad rollout','evidence_refs':['brief']}
    make_result = run_candidate(assessment)
    if test_result['eligible_for_scoped_next_step'] != ['repeat']:
        raise ValueError('Expected conditional test readiness')
    if make_result['eligible_for_scoped_next_step'] != []:
        raise ValueError('Rollout must remain gated')
    for result in [test_result, make_result]:
        if result['selection_made'] or result['execution_authorized'] or result['semantic_truth_verified']:
            raise ValueError('Helper exceeded its evidence scope')
    return {'schema_version':1, 'evidence_kind':'authored_synthetic_worked_examples',
        'model_runs':0, 'baseline_comparisons':0, 'independent_quality_reviews':0,
        'status':'worked_examples_only',
        'scope':'Authored responses with checked arithmetic and actual local helper execution. Not captured plugin/model conversations or evidence of superiority.',
        'source_hash_algorithm':'sha256-utf8-lf',
        'source_hashes':{'eval/cases.json':sha(CASES),
                         'eval/worked_examples.py':sha(Path(__file__)),
                         str(SCRIPT.relative_to(ROOT)).replace(chr(92),'/'):sha(SCRIPT)},
        'examples':[diagnosis, decision, pilot],
        'helper_probes':[
            {'label':'Bounded repeat proposal','input':test_input,'output':test_result},
            {'label':'Broad rollout proposal','input':assessment,'output':make_result}],
        'helper_limit':'Inputs and evidence judgments are authored. The helper checks structure and readiness rules; it does not inspect source truth or choose the method.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify committed results match source and execution')
    args = parser.parse_args()
    output = ROOT / 'eval/examples/results.json'
    result = build()
    text = json.dumps(result, indent=2, ensure_ascii=True) + '\n'
    if args.check:
        if not output.exists() or output.read_text(encoding='utf-8') != text:
            parser.exit(1, 'Worked evidence is stale. Run python eval/worked_examples.py and review changes.\n')
        print('Verified three worked examples and two local helper probes; zero model comparisons.')
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix('.json.pending')
        temporary.write_text(text, encoding='utf-8')
        temporary.replace(output)
        print(output)

if __name__ == '__main__':
    main()
