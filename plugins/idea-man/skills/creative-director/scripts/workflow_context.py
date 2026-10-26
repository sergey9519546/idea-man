"""Read only the packaged guidance selected for an actually ready v2 step.

This loads instructions, not providers or user source contents. It never executes
the step, grants authority or certifies a result. Selected content identities bind
receipt reuse; hashes still do not prove that the host followed the instructions.
"""
import copy
import hashlib
from pathlib import Path
import re

PACKAGE = Path(__file__).resolve().parents[3]
PLAYBOOK = 'references/innovation-playbooks.md'
RUBRICS = 'references/artifact-rubrics.md'
OPERATIONS = {
    'frame_problem': 'Frame an unclear or contested problem',
    'clarify_brief': 'Frame an unclear or contested problem',
    'diagnose_problem': 'Diagnose a failure, bottleneck or repeated disappointment',
    'generate_options': 'Invent alternatives under constraints',
    'synthesize_sources': 'Research a question or develop a hypothesis',
    'research_live': 'Research a question or develop a hypothesis',
    'design_experiment': 'Design an informative experiment',
    'select_option': 'Make a decision or choose a strategy',
}
CONTENT_OPERATIONS = {
    'quantitative': 'Calculate, estimate or model a quantity',
    'formal_reasoning': 'Prove or inspect a formal claim',
    'explanation': 'Explain or coach at the requested level',
    'coaching': 'Explain or coach at the requested level',
}


def reference_contracts(key, rubric, methods, actions=None):
    result = []
    if key == 'inspect_context':
        result.append({'path': 'references/recognition-playbook.md', 'selector': {'kind': 'all'}})
    if key in {'record_decisions', 'prepare_unsaved_recap', 'restore_checkpoint'}:
        result.append({'path': 'skills/creative-director/references/project-record.md',
                       'selector': {'kind': 'all'}})
    operation = OPERATIONS.get(key)
    if key == 'design_variations' or (key == 'generate_options' and actions and
                                     'vary' in actions and 'ideate' not in actions):
        operation = 'Controlled variations preserving explicit locks'
    if key in {'produce_artifact', 'verify_output', 'review_source', 'evaluate_options'}:
        operation = CONTENT_OPERATIONS.get(rubric, operation)
    if operation:
        result.append({'path': PLAYBOOK, 'selector': {'kind': 'heading', 'value': operation}})
    if key in {'verify_output', 'review_source', 'evaluate_options'}:
        result.append({'path': RUBRICS, 'selector': {'kind': 'rubric', 'value': rubric}})
    for method in methods:
        result.append({'path': method['reference'], 'selector': {
            'kind': 'method', 'value': method['section_prefix']}})
    return result


def section(text, value, prefix=False):
    headings = list(re.finditer(r'^##(?:[ \t]+([^\r\n]*))?\r?$', text, re.MULTILINE))
    matches = []
    for index, match in enumerate(headings):
        title = (match.group(1) or '').strip()
        # Empty headings still delimit sections, but cannot select a method.
        # Do not index split()[0]: whitespace-only headings are legal Markdown.
        if title and (title == value or prefix and title.split(maxsplit=1)[0] == value):
            matches.append(index)
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous packaged guidance section: ' + value)
    index = matches[0]
    end = headings[index+1].start() if index+1 < len(headings) else len(text)
    return text[headings[index].start():end].strip()


def load_resource(contract, package=None):
    package = PACKAGE if package is None else Path(package)
    locator = contract['path']
    path = (package / locator).resolve()
    if Path(locator).is_absolute() or not path.is_relative_to(package.resolve()) or not path.is_file():
        raise ValueError('Unavailable or outside-package guidance: ' + locator)
    if path.stat().st_size > 256*1024:
        raise ValueError('Packaged guidance exceeds the 256 KiB read limit: ' + locator)
    with path.open('rb') as stream:
        payload = stream.read(256*1024+1)
    if len(payload) > 256*1024:
        raise ValueError('Packaged guidance grew beyond the read limit: ' + locator)
    text = payload.decode('utf-8-sig')
    selector = contract['selector']
    kind = selector['kind']
    if kind == 'all':
        content = text
    elif kind in {'heading', 'method'}:
        content = section(text, selector['value'], prefix=kind == 'method')
        if kind == 'method':
            # Retain the arsenal's scope/precedence guard without loading all modes.
            content = text.splitlines()[0] + '\n\n' + content
    elif kind == 'rubric':
        lines = text.splitlines()
        rows = [line for line in lines if line.startswith('| `'+selector['value']+'` /')]
        if len(rows) != 1:
            raise ValueError('Missing or ambiguous packaged rubric: ' + selector['value'])
        header = [line for line in lines if line.startswith('| Rubric ID') or line.startswith('|---')]
        intro = text.split('## ', 1)[0].split('| Rubric ID', 1)[0].strip()
        content = intro+'\n\n'+'\n'.join(header+rows)+'\n\n'+section(text, 'Method and task fit')+'\n\n'+section(text, 'Shared checks')
    else:
        raise ValueError('Unknown packaged guidance selector: ' + str(kind))
    return {**copy.deepcopy(contract), 'file_sha256': hashlib.sha256(payload).hexdigest(),
            'content_sha256': hashlib.sha256(content.encode('utf-8')).hexdigest(), 'content': content}


def ready_context(raw, step_id, task_id=None):
    from router_v2 import normalize, plan_v2
    plan = plan_v2(raw)
    if 'workstreams' in plan:
        if task_id not in plan['workstreams']:
            raise ValueError('Portfolio context requires a valid --task-id')
        current = plan['workstreams'][task_id]
        target = next(stream['assessment'] for stream in raw['workstreams']
                      if stream['assessment']['task_id'] == task_id)
        node = next((step for step in plan['steps'] if step['id'] == task_id+'/'+step_id), None)
    else:
        if task_id is not None:
            raise ValueError('--task-id requires a portfolio')
        current, target = plan, raw
        node = next((step for step in plan['steps'] if step['id'] == step_id), None)
    if node is None or node['state'] != 'ready':
        raise ValueError('Context requires an actually ready step; resolve dependencies, inputs and capabilities first')
    graph = {step['id']: step for step in plan['steps']}
    inputs = []
    for dependency in node['depends_on']:
        predecessor = graph[dependency]
        if predecessor['state'] != 'done' or not predecessor.get('completion_output'):
            raise ValueError('Ready-step handoff requires accepted predecessor output: ' + dependency)
        inputs.append({'step_id': dependency, 'input_binding': predecessor['input_binding'],
                       'output': copy.deepcopy(predecessor['completion_output']),
                       'evidence': predecessor['completion_evidence']})
    task, _ = normalize(target)
    resources = [load_resource({'path': node['skill_contract']['path'], 'selector': {'kind': 'all'}})]
    resources.extend(load_resource(reference) for reference in node['reference_contracts'])
    identities = [{key:resource[key] for key in ('path','selector','content_sha256')}
                  for resource in resources]
    if identities != node['guidance_content']:
        raise ValueError('Packaged guidance changed during context loading; replan before performing the step')
    return {'schema_version': 1, 'task': {key: copy.deepcopy(value) for key,value in task.items()
                                        if key not in {'receipts','sources'}},
            'sources': current['sources'], 'inputs': inputs, 'step': copy.deepcopy(node), 'resources': resources,
            'read_only': True, 'grants_execution_authority': False, 'execution_complete': False,
            'content_characters': sum(len(resource['content']) for resource in resources),
            'note': 'Instructions and host-asserted capabilities only; perform the work, inspect the actual output and preserve host authorization boundaries. Resource hashes do not prove inspection or correctness.'}
