"""Idea Man: structured workflow planning and portable, append-only project records.

Standard library only. This helper does not classify prose or invoke external services.
The host model supplies an evidence-backed assessment; plan() validates and orders it.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile


class StudioError(ValueError):
    pass


ACTIONS = {'brief', 'ideate', 'vary', 'revise', 'review', 'develop', 'handoff',
           'produce', 'research', 'resume', 'status', 'record'}
CAPABILITIES = {'web', 'image_generation', 'video_generation', 'audio_generation',
                'file_write', 'code_execution', 'deck_authoring', 'document_authoring',
                'subagents'}
OUTPUTS = {'text', 'image', 'video', 'audio', 'code', 'deck', 'document', 'mixed'}
CHANGES = {'goal', 'audience', 'constraints', 'selection', 'feedback', 'capabilities'}
CAPABILITY_FOR = {'image': 'image_generation', 'video': 'video_generation',
                  'audio': 'audio_generation', 'code': 'file_write',
                  'deck': 'deck_authoring', 'document': 'document_authoring'}
ALL_STEPS = {'inspect_context', 'answer_status', 'record_decisions', 'resolve_source',
             'clarify_brief', 'form_brief', 'research', 'diagnose_rejection',
             'extract_insight', 'design_variations', 'generate_concepts',
             'revise_source', 'compare_concepts', 'select_concept',
             'resolve_selection', 'develop_concept', 'prepare_handoff',
             'produce_artifact', 'verify_output', 'present'}


def require(condition, message):
    if not condition:
        raise StudioError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def unique_list(value, allowed, name):
    require(isinstance(value, list) and all(isinstance(v, str) for v in value),
            name + ' must be a string array')
    require(len(value) == len(set(value)), name + ' contains duplicates')
    require(set(value) <= allowed, name + ' contains unsupported values')
    return value


def assess(raw):
    require(isinstance(raw, dict), 'Assessment must be an object')
    required = {'schema_version', 'objective', 'actions', 'deliverable', 'scope',
                'selection', 'source', 'brief', 'confidence', 'evidence'}
    optional = {'effort', 'feedback', 'rejection_count', 'requested_count',
                'capabilities', 'required_capabilities', 'changes', 'completed',
                'material_ambiguity'}
    require(required <= raw.keys(), 'Missing fields: ' + ', '.join(sorted(required - raw.keys())))
    require(raw.keys() <= required | optional, 'Unknown assessment fields')
    a = dict(raw)
    require(type(a['schema_version']) is int and a['schema_version'] == 1, 'Unsupported assessment version')
    require(nonempty(a['objective']), 'Objective must be nonempty')
    unique_list(a['actions'], ACTIONS, 'actions')
    require(a['actions'], 'At least one action is required')
    require(a['deliverable'] in OUTPUTS, 'Unsupported deliverable')
    for name, choices in {'scope': {'exact', 'bounded', 'open'},
                          'selection': {'user', 'assistant_authorized', 'none', 'not_needed'},
                          'source': {'available', 'missing', 'not_needed'},
                          'brief': {'sufficient', 'assumptions_ok', 'blocked'}}.items():
        require(a[name] in choices, 'Unsupported ' + name)
    require(type(a['confidence']) in (int, float) and 0 <= a['confidence'] <= 1,
            'Confidence must be a number from 0 to 1')
    evidence = a['evidence']
    require(isinstance(evidence, list) and evidence, 'Evidence is required')
    for item in evidence:
        require(isinstance(item, dict) and set(item) == {'source', 'detail'}, 'Invalid evidence entry')
        require(item['source'] in {'user', 'artifact', 'inference'} and nonempty(item['detail']),
                'Evidence needs source and detail')
    require(any(e['source'] == 'user' for e in evidence), 'At least one user instruction is required')
    defaults = {'effort': 'standard', 'feedback': 'none', 'rejection_count': 0,
                'requested_count': None, 'capabilities': [], 'required_capabilities': [],
                'changes': [], 'completed': [], 'material_ambiguity': False}
    for key, value in defaults.items():
        a.setdefault(key, value)
    require(a['effort'] in {'quick', 'standard', 'deep'}, 'Unsupported effort')
    require(a['feedback'] in {'none', 'rejection', 'approval'}, 'Unsupported feedback')
    require(type(a['rejection_count']) is int and a['rejection_count'] >= 0, 'Invalid rejection count')
    require(a['requested_count'] is None or
            (type(a['requested_count']) is int and 1 <= a['requested_count'] <= 10000),
            'Requested count must be 1..10000 or null; use batches for large counts')
    require(type(a['material_ambiguity']) is bool, 'material_ambiguity must be boolean')
    unique_list(a['capabilities'], CAPABILITIES, 'capabilities')
    unique_list(a['required_capabilities'], CAPABILITIES, 'required_capabilities')
    unique_list(a['changes'], CHANGES, 'changes')
    require(isinstance(a['completed'], list), 'completed must be an array')
    seen = set()
    for item in a['completed']:
        require(isinstance(item, dict) and set(item) == {'step', 'evidence'}, 'Invalid completion receipt')
        require(item['step'] in ALL_STEPS and nonempty(item['evidence']), 'Invalid completion evidence')
        require(item['step'] not in seen, 'Duplicate completion receipt')
        seen.add(item['step'])
    if 'revise' in a['actions']:
        require(a['source'] != 'not_needed', 'Revision requires an identified source')
    if a['scope'] == 'exact':
        require(not ({'ideate', 'vary'} & set(a['actions'])),
                'Exact revision conflicts with ideation/variation; split independent workstreams')
    if a['deliverable'] == 'mixed' and ({'produce', 'ideate', 'vary', 'revise', 'develop'} & set(a['actions'])):
        require(a['required_capabilities'], 'Mixed production needs explicit required_capabilities')
    return a


def invalidated(changes):
    all_work = ALL_STEPS - {'answer_status', 'record_decisions'}
    if {'goal', 'audience'} & set(changes):
        return all_work
    result = set()
    if {'constraints', 'feedback'} & set(changes):
        result |= all_work - {'form_brief', 'research'}
    if 'selection' in changes:
        result |= {'inspect_context', 'resolve_source', 'select_concept', 'resolve_selection',
                   'develop_concept', 'prepare_handoff', 'produce_artifact', 'verify_output', 'present'}
    if 'capabilities' in changes:
        result |= {'prepare_handoff', 'produce_artifact', 'verify_output', 'present'}
    return result


def plan(raw):
    if isinstance(raw, dict) and raw.get('schema_version') == 2:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from router_v2 import plan_v2
        return plan_v2(raw)
    a = assess(raw)
    actions = set(a['actions'])
    # The requested return format is an artifact, not merely a topic being discussed.
    if a['deliverable'] != 'text' and actions & {'ideate', 'vary', 'revise', 'develop'}:
        actions.add('produce')
    steps = []
    receipts = {r['step']: r['evidence'] for r in a['completed']}
    invalid = invalidated(a['changes'])

    def add(key, reason, needs=(), state=None, output=None):
        if any(s['id'] == key for s in steps):
            return key
        if key == 'present':
            needs = [s['id'] for s in steps]
        node = {'id': key, 'depends_on': list(dict.fromkeys(needs)), 'reason': reason,
                'output': output or reason, 'state': state or 'pending'}
        if key in receipts and key not in invalid and key != 'present' and state is None:
            node['state'] = 'done'
            node['completion_evidence'] = receipts[key]
        steps.append(node)
        return key

    inspect = add('inspect_context', 'Inspect current objective, sources and approved decisions')
    if 'status' in actions:
        add('answer_status', 'Answer from current evidence; preserve the active objective', [inspect])
    if 'record' in actions:
        add('record_decisions', 'Capture requested decisions; persist only in an authorized local record', [inspect])
    creative = actions - {'status', 'record', 'resume'}
    if not creative:
        add('present', 'Report current state or verified resume checkpoint', [s['id'] for s in steps])
        return finish_plan(a, steps)

    base = [inspect]
    needs_source = bool(actions & {'revise', 'review', 'develop', 'vary', 'handoff'}) or a['selection'] == 'user'
    if needs_source and a['source'] == 'missing':
        base.append(add('resolve_source', 'Locate or request the exact source before dependent work',
                        [inspect], 'needs_input', 'Authoritative source/version'))
    if a['brief'] == 'blocked' or a['material_ambiguity']:
        base.append(add('clarify_brief', 'Ask the consequential missing question; continue independent branches',
                        [inspect], 'needs_input', 'Resolved ambiguity'))
    elif 'brief' in actions or (a['brief'] == 'assumptions_ok' and actions & {'ideate', 'vary', 'develop'}):
        base.append(add('form_brief', 'Make a compact brief; label reasonable assumptions', [inspect]))

    if 'research' in actions:
        research = add('research', 'Check requested external evidence; do not invent findings', [inspect],
                       None if 'web' in a['capabilities'] else 'unavailable', 'Sources and bounded conclusions')
        base.append(research)

    if a['feedback'] == 'rejection' or a['rejection_count'] >= 2:
        base.append(add('diagnose_rejection', 'Distinguish concept failure from execution drift; unknown reasons stay unknown', base))

    cursor = base
    generating = bool(actions & {'ideate', 'vary'})
    if 'vary' in actions:
        cursor = [add('design_variations', 'Lock approved elements and choose meaningfully different variation axes', cursor)]
    elif 'ideate' in actions:
        cursor = [add('extract_insight', 'Find the relevant human/system tension; separate hypotheses from evidence', cursor)]
    if generating:
        count = a['requested_count'] if a['requested_count'] is not None else 3
        key = add('generate_concepts', 'Generate distinct mechanisms while preserving invariants', cursor,
                  output=str(count) + ' labeled concepts (exploratory when appropriate)')
        steps[-1]['requested_count'] = count
        cursor = [key]
    if 'revise' in actions:
        cursor = [add('revise_source', 'Specify only requested changes and execute bounded text/source edits; media edits go through produce_artifact', cursor)]
    if generating or 'review' in actions:
        cursor = [add('compare_concepts', 'Check actual brief compliance, differences, evidence and tradeoffs', cursor)]

    downstream = bool(actions & {'develop', 'handoff', 'produce'})
    if downstream and a['selection'] == 'none':
        cursor = [add('resolve_selection', 'A necessary selection has not been made or delegated', cursor,
                      'needs_input', 'User selection or explicit delegation')]
    elif downstream and a['selection'] == 'assistant_authorized':
        cursor = [add('select_concept', 'Select with a short rationale under the user\'s delegation', cursor)]
    if 'develop' in actions:
        cursor = [add('develop_concept', 'Develop the selected mechanism into its domain-specific concrete pack', cursor)]
    if actions & {'handoff', 'produce'}:
        cursor = [add('prepare_handoff', 'Prepare source-linked execution instructions, invariants and acceptance criteria', cursor)]
    if 'produce' in actions:
        needed = set(a['required_capabilities'])
        if a['deliverable'] in CAPABILITY_FOR:
            needed.add(CAPABILITY_FOR[a['deliverable']])
        missing = sorted(needed - set(a['capabilities']))
        key = add('produce_artifact', 'Use actual host tools; a prompt alone is not a produced artifact', cursor,
                  'unavailable' if missing else None, 'Actual requested ' + a['deliverable'])
        if missing:
            steps[-1]['missing_capabilities'] = missing
        cursor = [key]
    if actions & {'produce', 'revise', 'develop', 'ideate', 'vary'}:
        cursor = [add('verify_output', 'Inspect the actual output against scope, count, invariants and acceptance conditions', cursor)]
    add('present', 'Deliver the result and material limitations; do not claim planned work is complete', cursor)
    return finish_plan(a, steps)


def finish_plan(a, steps):
    by_id = {}
    for node in steps:
        require(all(dep in by_id for dep in node['depends_on']), 'Plan dependency is missing or out of order')
        if node['state'] == 'done' and any(by_id[d]['state'] != 'done' for d in node['depends_on']):
            node['prior_completion_evidence'] = node.pop('completion_evidence')
            node['state'] = 'pending'
        if node['state'] == 'pending':
            node['state'] = 'ready' if all(by_id[d]['state'] == 'done' for d in node['depends_on']) else 'waiting'
        by_id[node['id']] = node
    return {'schema_version': 1, 'objective': a['objective'], 'effort': a['effort'],
            'routing_confidence': a['confidence'], 'steps': steps,
            'blockers': [s['id'] for s in steps if s['state'] in {'needs_input', 'unavailable'}],
            'assumptions_required': a['brief'] == 'assumptions_ok',
            'execution_complete': False,
            'note': 'Advisory plan only. Semantic assessment and execution belong to the host; completed steps require inspected evidence.'}


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def apply_event(view, event):
    require(isinstance(event, dict), 'Event must be an object')
    kind = event.get('type')
    specs = {'brief': ({'text'}, set()), 'note': ({'text'}, set()),
             'next_step': ({'text'}, set()),
             'candidate': ({'id', 'text'}, {'artifact'}),
             'constraint': ({'id', 'text', 'evidence'}, set()),
             'approve': ({'target_id', 'evidence'}, set()),
             'reject': ({'target_id', 'evidence'}, {'reason'}),
             'supersede': ({'target_id', 'replacement_id', 'evidence'}, {'reason'}),
             'artifact': ({'id', 'path', 'status'}, {'note'})}
    require(kind in specs, 'Unknown event type')
    required, optional = specs[kind]
    require(required <= event.keys() and event.keys() <= required | optional | {'type'}, 'Invalid event fields')
    for key in required:
        require(nonempty(event[key]), 'Event ' + key + ' must be nonempty')
    for key in optional:
        if key in event:
            require(event[key] is None or nonempty(event[key]), 'Optional event field must be text or null')
    if kind in {'brief', 'next_step'}:
        view[kind] = event['text']
    elif kind == 'note':
        view['notes'].append(event['text'])
    elif kind in {'candidate', 'constraint'}:
        require(event['id'] not in view['items'], 'Duplicate item ID')
        view['items'][event['id']] = {**event, 'status': 'approved' if kind == 'constraint' else 'proposed'}
    elif kind in {'approve', 'reject', 'supersede'}:
        item = view['items'].get(event['target_id'])
        require(item is not None, 'Unknown decision target')
        require(item['status'] != 'superseded', 'Cannot change a superseded item')
        if kind == 'reject':
            require(item['status'] != 'approved', 'Approved decisions require explicit supersede, not silent rejection')
            item['status'] = 'rejected'
            item['reason'] = event.get('reason')
        elif kind == 'approve':
            item['status'] = 'approved'
            item.pop('reason', None)
        else:
            replacement = view['items'].get(event['replacement_id'])
            require(replacement is not None and replacement is not item, 'Invalid replacement')
            require(replacement['status'] in {'proposed', 'approved'}, 'Replacement must be active')
            require(item['type'] == replacement['type'], 'Replacement must have the same item type')
            item['status'] = 'superseded'
            item['replacement_id'] = event['replacement_id']
            replacement['status'] = 'approved'
        item['decision_evidence'] = event['evidence']
    elif kind == 'artifact':
        require(event['id'] not in view['artifacts'], 'Duplicate artifact ID; use a new version ID')
        require(event['status'] in {'prepared', 'generated', 'inspected', 'tested', 'published'}, 'Invalid artifact status')
        view['artifacts'][event['id']] = event


def project_view(data):
    require(isinstance(data, dict) and set(data) == {'schema_version', 'title', 'revision', 'events'}, 'Invalid project structure')
    require(type(data['schema_version']) is int and data['schema_version'] == 1, 'Unsupported project version')
    require(nonempty(data['title']), 'Project title is required')
    require(type(data['revision']) is int and data['revision'] >= 0, 'Invalid project revision')
    require(isinstance(data['events'], list) and len(data['events']) == data['revision'], 'Revision/history mismatch')
    view = {'title': data['title'], 'revision': data['revision'], 'brief': '', 'next_step': '',
            'items': {}, 'artifacts': {}, 'notes': []}
    for number, item in enumerate(data['events'], 1):
        require(isinstance(item, dict) and set(item) == {'revision', 'at', 'event'}, 'Invalid history entry')
        require(type(item['revision']) is int and item['revision'] == number and nonempty(item['at']), 'Invalid history sequence')
        apply_event(view, item['event'])
    return view


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def record_path(raw):
    path = Path(raw).absolute()
    require(path.suffix.lower() == '.json', 'Project record must use a .json extension')
    require(not path.is_symlink(), 'Refusing a symlink project record')
    require(path.parent.is_dir(), 'Project directory must already exist')
    return path


@contextmanager
def locked(path):
    lock = path.with_name(path.name + '.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise StudioError('Record is locked; re-read later. Do not remove an active writer\'s lock.') from exc
    try:
        os.write(fd, str(os.getpid()).encode('ascii'))
        os.close(fd)
        fd = None
        yield
    finally:
        if fd is not None:
            os.close(fd)
        lock.unlink()


def atomic_write(path, data):
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=path.parent, prefix=path.name + '.', suffix='.tmp', delete=False) as f:
            name = f.name
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        name = None
    finally:
        if name is not None:
            Path(name).unlink(missing_ok=True)


def init_project(raw_path, title):
    require(nonempty(title), 'Title is required')
    path = record_path(raw_path)
    with locked(path):
        require(not path.exists(), 'Project already exists; refusing to overwrite')
        data = {'schema_version': 1, 'title': title, 'revision': 0, 'events': []}
        atomic_write(path, data)
    return project_view(data)


def record_event(raw_path, expected_revision, event):
    path = record_path(raw_path)
    require(type(expected_revision) is int and expected_revision >= 0, 'Expected revision is required')
    with locked(path):
        data = read_json(path)
        view = project_view(data)
        require(data['revision'] == expected_revision, 'Revision conflict; re-read and reconcile before retrying')
        apply_event(view, event)
        data['revision'] += 1
        data['events'].append({'revision': data['revision'], 'at': utcnow(), 'event': event})
        project_view(data)
        atomic_write(path, data)
    return project_view(data)


def markdown(view):
    # Values are user text, not executable HTML. Keep each entry on one line.
    def safe(value):
        return str(value).replace('<', '&lt;').replace('>', '&gt;').replace('\r', ' ').replace('\n', ' ')
    lines = ['# ' + safe(view['title']), '', 'Local record revision: ' + str(view['revision']),
             '', 'Brief: ' + safe(view['brief']), '', '## Decisions', '']
    for key, item in view['items'].items():
        lines.append('- ' + safe(key) + ' [' + item['status'] + ']: ' + safe(item['text']))
        if item['status'] == 'rejected':
            lines.append('  Reason: ' + safe(item.get('reason') or 'not supplied'))
    lines += ['', '## Artifacts', '']
    for key, item in view['artifacts'].items():
        lines.append('- ' + safe(key) + ' [' + item['status'] + ']: ' + safe(item['path']))
    lines += ['', '## Scoped notes', '']
    lines += ['- ' + safe(note) for note in view['notes']]
    lines += ['', 'Next: ' + safe(view['next_step']), '', 'Saved observations must be rechecked on resume.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('plan')
    p.add_argument('--assessment', required=True)
    p = commands.add_parser('fingerprint')
    p.add_argument('--file', required=True)
    p = commands.add_parser('receipt')
    p.add_argument('--assessment', required=True)
    p.add_argument('--step', required=True)
    p.add_argument('--task-id')
    p.add_argument('--artifact', required=True)
    p.add_argument('--evidence-file', required=True)
    p = commands.add_parser('init')
    p.add_argument('--file', required=True)
    p.add_argument('--title', required=True)
    p = commands.add_parser('record')
    p.add_argument('--file', required=True)
    p.add_argument('--expected-revision', required=True, type=int)
    p.add_argument('--event', required=True)
    for command in ('show', 'validate', 'export'):
        p = commands.add_parser(command)
        p.add_argument('--file', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'plan':
            result = plan(read_json(args.assessment))
        elif args.command in {'fingerprint', 'receipt'}:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from router_v2 import file_hash
            source_path = Path(args.file if args.command == 'fingerprint' else args.artifact).resolve()
            output = {'kind': 'file', 'locator': str(source_path), 'revision': file_hash(source_path)}
            if args.command == 'fingerprint':
                result = output
            else:
                portfolio = plan(read_json(args.assessment))
                require(portfolio.get('schema_version') == 2, 'Receipt requires a v2 assessment')
                if 'workstreams' in portfolio:
                    require(args.task_id in portfolio['workstreams'], 'Portfolio receipt requires a valid --task-id')
                    current = portfolio['workstreams'][args.task_id]
                    node = next((s for s in portfolio['steps'] if s['id'] == args.task_id + '/' + args.step), None)
                else:
                    current = portfolio
                    node = next((s for s in current['steps'] if s['id'] == args.step), None)
                require(node is not None and node['state'] == 'ready' and args.step != 'present', 'Receipt requires a ready executable step')
                evidence = Path(args.evidence_file).read_text(encoding='utf-8-sig').strip()
                require(nonempty(evidence), 'Inspection evidence required')
                result = {'step': args.step, 'binding': current['input_binding'], 'evidence': evidence, 'output': output}
        elif args.command == 'init':
            result = init_project(args.file, args.title)
        elif args.command == 'record':
            result = record_event(args.file, args.expected_revision, read_json(args.event))
        else:
            result = project_view(read_json(args.file))
            if args.command == 'export':
                print(markdown(result), end='')
                return
            if args.command == 'validate':
                result = {'valid': True, 'revision': result['revision']}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (StudioError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()
