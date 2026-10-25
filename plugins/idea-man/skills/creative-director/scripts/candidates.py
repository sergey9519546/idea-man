"""Evidence-linked candidate readiness for one scoped commitment; standard library only.

The host supplies judgments and source identities. This helper neither inspects source
contents nor generates candidates, verifies semantic truth, selects or executes work.
"""
import argparse
import json
from pathlib import Path
import sys


class CandidateError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise CandidateError(message)


def obj(value, fields, name):
    require(isinstance(value, dict) and set(value) == set(fields),
            name + ' has missing or unknown fields')


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()), name + ' must be nonempty text')


def identifier(value, name):
    text(value, name)
    require(all(c.isalnum() or c in '-_' for c in value), name + ' must be an identifier')


def entries(value, fields, name):
    require(isinstance(value, list), name + ' must be an array')
    seen = set()
    for item in value:
        obj(item, fields, name + ' entry')
        identifier(item['id'], name + ' ID')
        require(item['id'] not in seen, 'Duplicate ' + name + ' ID')
        seen.add(item['id'])
    return seen


def refs(value, sources, name, required=False):
    require(isinstance(value, list) and all(isinstance(v, str) for v in value),
            name + ' must be a source ID array')
    require(len(value) == len(set(value)) and set(value) <= sources,
            name + ' has duplicate or unknown source IDs')
    require(not required or bool(value), name + ' needs source evidence')



def _mechanism_summary(a):
    """Closure of explicit equivalence assertions; no text similarity inference."""
    ids = sorted(c['id'] for c in a['candidates'])
    parent = {key: key for key in ids}

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for comparison in a['comparisons']:
        if comparison['relation'] == 'equivalent':
            left, right = root(comparison['left']), root(comparison['right'])
            parent[max(left, right)] = min(left, right)
    groups = {}
    for key in ids:
        groups.setdefault(root(key), []).append(key)
    for comparison in a['comparisons']:
        require(not (comparison['relation'] == 'distinct' and
                     root(comparison['left']) == root(comparison['right'])),
                'Distinct mechanism relation conflicts with transitive equivalence')
    equivalent_groups = []
    for members in groups.values():
        if len(members) < 2:
            continue
        evidence = set()
        for comparison in a['comparisons']:
            if comparison['relation'] == 'equivalent' and comparison['left'] in members:
                evidence.update(comparison['evidence_refs'])
        equivalent_groups.append({'candidate_ids': members, 'evidence_refs': sorted(evidence),
                                  'basis': 'transitive_host_asserted_equivalence'})
    supplied = {frozenset((c['left'], c['right'])): c for c in a['comparisons']}
    unknown, unassessed = [], []
    for index, left in enumerate(ids):
        for right in ids[index + 1:]:
            relation = supplied.get(frozenset((left, right)))
            pair = {'left': left, 'right': right}
            if relation is None:
                unassessed.append(pair)
            elif relation['relation'] == 'unknown':
                unknown.append(pair)
    return {'equivalent_groups': equivalent_groups,
            'pair_coverage': {'total_pairs': len(ids) * (len(ids) - 1) // 2,
                              'explicit_relations': len(supplied),
                              'unknown_pairs': unknown, 'unassessed_pairs': unassessed}}


def validate(raw):
    obj(raw, {'schema_version', 'decision', 'commitment', 'sources', 'constraints',
              'criteria', 'candidates', 'comparisons'}, 'Assessment')
    require(type(raw['schema_version']) is int and raw['schema_version'] == 1,
            'Expected schema_version 1')
    text(raw['decision'], 'decision')
    commitment = raw['commitment']
    require(isinstance(commitment, dict) and {'level', 'text'} <= set(commitment) and
            set(commitment) <= {'level', 'text', 'evidence_refs'},
            'commitment has missing or unknown fields')
    require(isinstance(raw['commitment']['level'], str) and
            raw['commitment']['level'] in {'explore', 'test', 'make'}, 'Invalid commitment level')
    text(raw['commitment']['text'], 'commitment.text')
    source_ids = entries(raw['sources'], {'id', 'locator', 'revision'}, 'sources')
    for source in raw['sources']:
        text(source['locator'], 'source locator')
        text(source['revision'], 'source revision')
    refs(commitment.get('evidence_refs', []), source_ids, 'commitment evidence')
    constraint_ids = entries(raw['constraints'], {'id', 'text'}, 'constraints')
    criterion_ids = entries(raw['criteria'], {'id', 'text'}, 'criteria')
    for item in raw['constraints'] + raw['criteria']:
        text(item['text'], 'criterion/constraint text')
    candidate_ids = entries(raw['candidates'], {'id', 'mechanism', 'checks', 'ratings',
                            'assumptions', 'next_test'}, 'candidates')
    require(candidate_ids, 'At least one candidate required')
    for candidate in raw['candidates']:
        text(candidate['mechanism'], 'candidate mechanism')
        require(isinstance(candidate['checks'], list), 'checks must be an array')
        seen = set()
        for check in candidate['checks']:
            obj(check, {'constraint_id', 'status', 'evidence_refs', 'detail'}, 'check')
            key = check['constraint_id']
            require(isinstance(key, str) and key in constraint_ids and key not in seen,
                    'Duplicate or unknown constraint ID')
            seen.add(key)
            require(isinstance(check['status'], str) and
                    check['status'] in {'pass', 'fail', 'unresolved'}, 'Invalid constraint status')
            text(check['detail'], 'check detail')
            refs(check['evidence_refs'], source_ids, 'check evidence',
                 check['status'] in {'pass', 'fail'})
        require(isinstance(candidate['ratings'], list), 'ratings must be an array')
        seen = set()
        for rating in candidate['ratings']:
            obj(rating, {'criterion_id', 'value', 'evidence_refs', 'detail'}, 'rating')
            key = rating['criterion_id']
            require(isinstance(key, str) and key in criterion_ids and key not in seen,
                    'Duplicate or unknown criterion ID')
            seen.add(key)
            value = rating['value']
            require(type(value) is int and 0 <= value <= 5,
                    'Rating must be an ordinal integer from 0 to 5')
            text(rating['detail'], 'rating detail')
            refs(rating['evidence_refs'], source_ids, 'rating evidence', True)
        require(isinstance(candidate['assumptions'], list), 'assumptions must be an array')
        assumption_ids = set()
        for assumption in candidate['assumptions']:
            obj(assumption, {'id', 'text', 'status', 'critical', 'evidence_refs'}, 'assumption')
            identifier(assumption['id'], 'assumption ID')
            require(assumption['id'] not in assumption_ids, 'Duplicate assumption ID')
            assumption_ids.add(assumption['id'])
            text(assumption['text'], 'assumption text')
            require(isinstance(assumption['status'], str) and
                    assumption['status'] in {'supported', 'unresolved', 'refuted'},
                    'Invalid assumption status')
            require(type(assumption['critical']) is bool, 'critical must be boolean')
            refs(assumption['evidence_refs'], source_ids, 'assumption evidence',
                 assumption['status'] in {'supported', 'refuted'})
        test = candidate['next_test']
        if test is not None:
            obj(test, {'hypothesis', 'observation', 'decision_rule'}, 'next_test')
            for value in test.values():
                text(value, 'next_test field')
        unresolved = any(a['status'] != 'supported' and a['critical']
                         for a in candidate['assumptions'])
        require(not unresolved or test is not None,
                'Unresolved/refuted critical assumptions need a next informative test')
    require(isinstance(raw['comparisons'], list), 'comparisons must be an array')
    pairs = set()
    for comparison in raw['comparisons']:
        obj(comparison, {'left', 'right', 'relation', 'evidence_refs', 'detail'}, 'comparison')
        left, right = comparison['left'], comparison['right']
        require(isinstance(left, str) and isinstance(right, str) and left != right and
                left in candidate_ids and right in candidate_ids, 'Unknown/self comparison IDs')
        key = frozenset((left, right))
        require(key not in pairs, 'Duplicate/reversed mechanism comparison')
        pairs.add(key)
        require(isinstance(comparison['relation'], str) and
                comparison['relation'] in {'equivalent', 'distinct', 'unknown'},
                'Invalid mechanism relation')
        text(comparison['detail'], 'comparison detail')
        refs(comparison['evidence_refs'], source_ids, 'comparison evidence',
             comparison['relation'] != 'unknown')
    _mechanism_summary(raw)
    return raw


def assess(raw):
    a = validate(raw)
    mechanisms = _mechanism_summary(a)
    required = {c['id'] for c in a['constraints']}
    results = []
    for candidate in a['candidates']:
        checks = {c['constraint_id']: c for c in candidate['checks']}
        failed = sorted(k for k, c in checks.items() if c['status'] == 'fail')
        unresolved = sorted(required - set(checks) |
                            {k for k, c in checks.items() if c['status'] == 'unresolved'})
        critical = [x for x in candidate['assumptions']
                    if x['critical'] and x['status'] != 'supported']
        readiness_gaps = []
        if a['commitment']['level'] in {'test', 'make'} and not a['commitment'].get('evidence_refs'):
            readiness_gaps.append('commitment_source_evidence')
        if a['commitment']['level'] == 'test' and candidate['next_test'] is None:
            readiness_gaps.append('test_protocol')
        status = 'blocked' if failed else 'needs_evidence' if unresolved else 'ready_for_scoped_next_step'
        if a['commitment']['level'] == 'make' and critical and not failed:
            status = 'blocked' if any(x['status'] == 'refuted' for x in critical) else 'needs_evidence'
        if readiness_gaps and status == 'ready_for_scoped_next_step':
            status = 'needs_evidence'
        results.append({'id': candidate['id'], 'readiness': status,
                        'readiness_gaps': readiness_gaps,
                        'mechanism': candidate['mechanism'], 'checks': candidate['checks'],
                        'ratings': candidate['ratings'], 'assumptions': candidate['assumptions'],
                        'failed_constraints': failed, 'unresolved_constraints': unresolved,
                        'critical_assumptions': critical, 'next_test': candidate['next_test']})
    eligible = {r['id'] for r in results if r['readiness'] == 'ready_for_scoped_next_step'}
    candidates = {c['id']: c for c in a['candidates']}
    criterion_ids = {c['id'] for c in a['criteria']}
    pairs = []
    dominated = set()
    for index, left in enumerate(a['candidates']):
        for right in a['candidates'][index + 1:]:
            lid, rid = left['id'], right['id']
            scores_l = {r['criterion_id']: r['value'] for r in left['ratings']}
            scores_r = {r['criterion_id']: r['value'] for r in right['ratings']}
            relation = 'not_eligible'
            if lid in eligible and rid in eligible:
                if not criterion_ids:
                    relation = 'not_requested'
                elif set(scores_l) != criterion_ids or set(scores_r) != criterion_ids:
                    relation = 'unknown_missing_ratings'
                else:
                    differences = [scores_l[k] - scores_r[k] for k in sorted(criterion_ids)]
                    if all(d == 0 for d in differences):
                        relation = 'tied'
                    elif all(d >= 0 for d in differences):
                        relation = 'left_dominates'; dominated.add(rid)
                    elif all(d <= 0 for d in differences):
                        relation = 'right_dominates'; dominated.add(lid)
                    else:
                        relation = 'incomparable_tradeoff'
            pairs.append({'left': lid, 'right': rid, 'relation': relation})
    comparable = {key for key in eligible if criterion_ids and
                  {r['criterion_id'] for r in candidates[key]['ratings']} == criterion_ids}
    complete = bool(eligible) and bool(criterion_ids) and comparable == eligible
    return {'schema_version': 1, 'decision': a['decision'], 'commitment': a['commitment'],
            'sources': a['sources'], 'constraints': a['constraints'], 'criteria': a['criteria'],
            'candidates': results, 'eligible_for_scoped_next_step': sorted(eligible),
            'rating_comparison': {'status': 'no_eligible_candidates' if not eligible else 'complete' if complete else
                                 'incomplete' if criterion_ids else 'not_requested',
                                 'frontier': sorted(comparable - dominated),
                                 'unranked': sorted(eligible - comparable) if criterion_ids else [],
                                 'pairs': pairs},
            'mechanism_comparisons': a['comparisons'],
            'equivalent_mechanism_groups': mechanisms['equivalent_groups'],
            'mechanism_pair_coverage': mechanisms['pair_coverage'],
            'readiness_basis': 'conditional_on_host_reported_evidence',
            'selection_made': False, 'execution_authorized': False,
            'semantic_truth_verified': False,
            'note': 'Host judgments and supplied source identities only. Ratings are subjective; '
                    'readiness applies only to this commitment. No result proves novelty or demand.'}


def reject_constant(value):
    raise CandidateError('Non-finite JSON number: ' + value)


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field: ' + key)
        result[key] = value
    return result


def load_assessment(path):
    """Load one assessment without ambiguous duplicate fields or JSON constants."""
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      parse_constant=reject_constant, object_pairs_hook=reject_duplicate_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assessment', required=True)
    args = parser.parse_args()
    try:
        raw = load_assessment(args.assessment)
        print(json.dumps(assess(raw), ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    except (CandidateError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
