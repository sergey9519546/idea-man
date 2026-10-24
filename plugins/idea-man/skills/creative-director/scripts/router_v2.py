"""Evidence-bound innovation planning. The host performs semantic recognition.

This module validates its assessment, resolves specialists/methods, composes work,
and checks checkpoint bindings. It never classifies prose or executes a provider.
"""
import copy
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[3]
ACTIONS = {'brief','diagnose','ideate','vary','revise','review','decide','develop',
           'experiment','handoff','produce','research','resume','status','record'}
DOMAINS = {'general','business','operations','engineering','research','product',
           'service','learning','personal','policy','story','visual','campaign','game'}
CAPS = {'web','image_generation','video_generation','audio_generation','file_write',
        'code_execution','deck_authoring','document_authoring','subagents'}
OUTPUTS = {'text','image','video','audio','code','deck','document','mixed'}
PRODUCTION_CAP = {'image':'image_generation','video':'video_generation',
                  'audio':'audio_generation','code':'file_write','deck':'deck_authoring',
                  'document':'document_authoring'}
KINDS = {'unclear','causal','optimization','tradeoff','new_possibility','combination',
         'uncertainty','adoption','communication','execution'}
STYLES = {'adaptive','analytical','experimental','systemic','human_centered',
          'contrarian','analogical','constraint_driven','combinatorial','playful'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return isinstance(value,str) and bool(value.strip())


def enum(value, choices, field):
    need(isinstance(value,str) and value in choices, 'Invalid '+field)


def array(value, choices, field):
    need(isinstance(value,list) and all(isinstance(x,str) for x in value), field+' must be a string array')
    need(len(value)==len(set(value)) and set(value)<=choices, 'Invalid '+field)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()


def file_hash(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            result.update(chunk)
    return result.hexdigest()


def registry():
    data=json.loads((PACKAGE/'references/innovation-registry.json').read_text(encoding='utf-8'))
    for entry in data['specialists'].values():
        p=(PACKAGE/entry['path']).resolve()
        need(p.is_relative_to(PACKAGE.resolve()) and p.is_file(), 'Specialist file is unavailable: '+entry['path'])
    return data


def normalize(raw):
    required={'schema_version','task_id','objective','domain','actions','deliverable',
              'artifact_kind','scope','stage','problem','evidence_mode','sources','selection',
              'constraints','evidence'}
    optional={'capabilities','required_capabilities','requested_count','effort','thinking_style',
              'requested_methods','feedback','continuity','receipts','acceptance','material_ambiguity',
              'brief','project_revision'}
    need(isinstance(raw,dict), 'Assessment must be an object')
    need(required<=raw.keys() and raw.keys()<=required|optional, 'Missing or unknown v2 assessment fields')
    a=copy.deepcopy(raw)
    need(type(a['schema_version']) is int and a['schema_version']==2, 'Expected schema_version 2')
    for name in ('task_id','objective','artifact_kind'):
        need(text(a[name]), name+' is required')
    need(all(c.isalnum() or c in '-_' for c in a['task_id']), 'task_id must be an identifier')
    enum(a['domain'],DOMAINS,'domain'); enum(a['deliverable'],OUTPUTS,'deliverable')
    enum(a['scope'],{'exact','bounded','open'},'scope')
    enum(a['stage'],{'unclear','framed','evidence','options','selected','executing','checking'},'stage')
    enum(a['evidence_mode'],{'none','supplied','live','mixed','canon','hypothesis'},'evidence_mode')
    array(a['actions'],ACTIONS,'actions'); need(a['actions'],'At least one action required')
    defaults={'capabilities':[],'required_capabilities':[],'requested_count':None,'effort':'standard',
              'thinking_style':'adaptive','requested_methods':[],'feedback':{'verdict':'none','reason':None},
              'continuity':None,'receipts':[],'acceptance':[],'material_ambiguity':False,
              'brief':'sufficient','project_revision':None}
    for k,v in defaults.items(): a.setdefault(k,v)
    array(a['capabilities'],CAPS,'capabilities'); array(a['required_capabilities'],CAPS,'required_capabilities')
    enum(a['effort'],{'quick','standard','deep'},'effort'); enum(a['thinking_style'],STYLES,'thinking_style')
    enum(a['brief'],{'sufficient','assumptions_ok','blocked'},'brief')
    need(type(a['material_ambiguity']) is bool,'material_ambiguity must be boolean')
    need(a['requested_count'] is None or type(a['requested_count']) is int and 1<=a['requested_count']<=10000,'Invalid requested_count')
    need(a['project_revision'] is None or type(a['project_revision']) is int and a['project_revision']>=0,'Invalid project revision')
    p=a['problem']
    need(isinstance(p,dict) and set(p)=={'kind','bottleneck','novelty','stakes','reversibility'},'Invalid problem shape')
    enum(p['kind'],KINDS,'problem.kind')
    enum(p['bottleneck'],{'framing','evidence','assumptions','complexity','conflict','novelty','selection','implementation','feedback'},'bottleneck')
    enum(p['novelty'],{'none','improve','explore'},'novelty')
    enum(p['stakes'],{'low','medium','high'},'stakes')
    enum(p['reversibility'],{'reversible','costly','irreversible'},'reversibility')
    need(isinstance(a['evidence'],list) and a['evidence'],'Routing evidence required')
    for e in a['evidence']:
        need(isinstance(e,dict) and set(e)=={'source','detail'} and text(e['detail']),'Invalid evidence')
        enum(e['source'],{'user','artifact','inference'},'evidence.source')
    need(any(e['source']=='user' for e in a['evidence']),'User instruction evidence required')
    s=a['selection']
    need(isinstance(s,dict) and set(s)=={'status','ids','evidence'},'Invalid selection')
    enum(s['status'],{'user','assistant_authorized','none','not_needed'},'selection.status')
    need(isinstance(s['ids'],list) and all(text(i) for i in s['ids']) and len(set(s['ids']))==len(s['ids']),'Invalid selected IDs')
    need(isinstance(s['evidence'],str),'Selection evidence must be text')
    if s['status']=='user': need(s['ids'] and text(s['evidence']),'User selection needs IDs and evidence')
    if s['status']=='assistant_authorized': need(text(s['evidence']),'Delegated selection needs user evidence')
    if s['status'] in {'none','not_needed'}: need(not s['ids'],'Unselected state cannot include selected IDs')
    need(isinstance(a['sources'],list),'sources must be an array')
    seen=set()
    for source in a['sources']:
        need(isinstance(source,dict) and set(source)=={'id','kind','locator','revision','status','inspected'},'Invalid source')
        need(text(source['id']) and source['id'] not in seen,'Duplicate/empty source ID'); seen.add(source['id'])
        enum(source['kind'],{'file','provided','url'},'source.kind')
        enum(source['status'],{'available','missing'},'source.status')
        need(all(isinstance(source[k],str) for k in ('locator','revision')) and type(source['inspected']) is bool,'Invalid source identity')
        if source['status']=='available': need(text(source['locator']) and text(source['revision']),'Available source needs locator and revision')
        if source['status']=='missing': need(not source['inspected'],'Missing source cannot be inspected')
    need(isinstance(a['constraints'],list),'constraints must be an array')
    seen=set()
    for c in a['constraints']:
        need(isinstance(c,dict) and set(c)=={'id','text','kind','evidence'},'Invalid constraint')
        need(all(text(c[k]) for k in ('id','text','evidence')) and c['id'] not in seen,'Invalid constraint identity/evidence'); seen.add(c['id'])
        enum(c['kind'],{'hard','soft'},'constraint.kind')
    need(isinstance(a['acceptance'],list) and all(text(x) for x in a['acceptance']),'Invalid acceptance conditions')
    f=a['feedback']
    need(isinstance(f,dict) and set(f)=={'verdict','reason'},'Invalid feedback')
    enum(f['verdict'],{'none','approval','rejection'},'feedback.verdict')
    need(f['reason'] is None or text(f['reason']),'Invalid feedback reason')
    cont=a['continuity']
    if cont is not None:
        need(isinstance(cont,dict) and set(cont)=={'task_id','objective','pending_actions','evidence','source_rechecked'},'Invalid continuity checkpoint')
        need(cont['task_id']==a['task_id'] and cont['objective']==a['objective'],'Checkpoint belongs to another task/objective')
        array(cont['pending_actions'],ACTIONS-{'resume','status','record'},'pending_actions')
        need(text(cont['evidence']) and type(cont['source_rechecked']) is bool,'Checkpoint needs evidence and recheck state')
    actions=set(a['actions'])
    # A status request does not implicitly execute pending work; resume does.
    if 'resume' in actions and cont and cont['source_rechecked']:
        actions.update(cont['pending_actions'])
    if a['deliverable']!='text' and actions & {'ideate','vary','revise','develop'}:
        actions.add('produce')
    if a['scope']=='exact': need(not actions & {'ideate','vary'},'Exact scope conflicts with ideation/variation')
    if a['deliverable']=='mixed' and 'produce' in actions:
        need(a['required_capabilities'],'Mixed production requires explicit tool classes even when production is implicit')
    a['effective_actions']=sorted(actions)
    if 'research' in actions:
        need(a['evidence_mode'] in {'supplied','live','mixed','canon'},'Research requires an explicit evidence mode')
    data=registry()
    array(a['requested_methods'],set(data['methods']),'requested_methods')
    need(isinstance(a['receipts'],list),'receipts must be an array')
    seen=set()
    for receipt in a['receipts']:
        need(isinstance(receipt,dict) and set(receipt)=={'step','binding','evidence','output'},'Invalid receipt')
        need(all(text(receipt[k]) for k in ('step','binding','evidence')) and receipt['step'] not in seen,'Invalid/duplicate receipt')
        seen.add(receipt['step'])
        out=receipt['output']
        need(isinstance(out,dict) and set(out)=={'kind','locator','revision'},'Invalid receipt output')
        enum(out['kind'],{'file','provided','url'},'receipt.output.kind')
        need(text(out['locator']) and text(out['revision']),'Receipt output needs identity/version')
    return a,data


def live_sources(sources):
    result=[]
    for source in sources:
        item=dict(source)
        if item['kind']=='file' and item['status']=='available':
            p=Path(item['locator'])
            if not p.is_file():
                item.update(status='missing',inspected=False)
            else:
                actual=file_hash(p)
                if item['revision']!=actual: item['inspected']=False
                item['revision']=actual
        result.append(item)
    return result


def pick_specialist(a):
    actions=set(a['effective_actions'])-{'resume','status','record'}
    if not actions: return 'creative-learning' if 'record' in a['effective_actions'] else 'creative-director'
    if actions=={'review'}: return 'artifact-quality'
    if a['scope']=='exact' and actions<= {'revise','produce'}: return 'execution-handoff'
    if actions<= {'handoff','produce'}: return 'execution-handoff'
    if actions & {'diagnose','decide','experiment'} and a['domain'] not in {'story','visual','campaign','game'}:
        return 'innovation-strategy'
    if a['artifact_kind'] in {'article','memo','report','explainer','research_brief'} and a['evidence_mode'] in {'supplied','live','mixed'}:
        return 'research-and-writing'
    if a['domain'] in {'business','operations','engineering','research','product','service','learning','personal','policy','general'}:
        return 'innovation-strategy'
    if 'vary' in actions: return 'concept-variations'
    if 'develop' in actions: return 'concept-development'
    return 'creative-director'


def pick_methods(a,data):
    acts=set(a['effective_actions']); p=a['problem']
    reasoning=acts & {'brief','diagnose','ideate','vary','decide','experiment'}
    if 'develop' in acts and p['novelty']!='none' and p['kind']!='execution': reasoning.add('develop')
    if a['scope']=='exact' or not reasoning: return []
    if a['requested_methods']:
        chosen=a['requested_methods']; reason='Explicit user-requested methods; apply within scope'
    else:
        choices={'unclear':['L1'],'causal':['Y2','Y1'],'optimization':['Y1','L3'],
                 'tradeoff':['S2','Y2'],'new_possibility':['L1','L5'],
                 'combination':['L5','D1'],'uncertainty':['D2','L1'],
                 'adoption':['H1','H2'],'communication':['H2','L1'],'execution':[]}
        chosen=list(choices[p['kind']])
        if 'experiment' in acts or p['bottleneck']=='evidence': chosen=['D2']+chosen
        if 'decide' in acts: chosen=['D2']+chosen
        if 'vary' in acts: chosen=['D1']+chosen
        styles={'analytical':'Y2','experimental':'D2','systemic':'Y1','human_centered':'H1',
                'contrarian':'L2','analogical':'L5','constraint_driven':'S3','combinatorial':'L5','playful':'L4'}
        if a['thinking_style'] in styles: chosen=[styles[a['thinking_style']]]+chosen
        if a['feedback']['verdict']=='rejection' and p['bottleneck']=='novelty': chosen=['L2','L5']+chosen
        if acts & {'decide','experiment'} or p['bottleneck']=='evidence' or p['stakes']=='high' or p['reversibility']=='irreversible':
            chosen=['D2']+chosen
        chosen=list(dict.fromkeys(chosen))[:{'quick':1,'standard':2,'deep':3}[a['effort']]]
        reason='Problem: '+p['kind']+'; bottleneck: '+p['bottleneck']+'; style: '+a['thinking_style']
    return [{'id':m,'reason':reason,'procedure':data['methods'][m]['procedure'],
             'output':data['methods'][m]['output'],'reference':data['methods'][m]['reference']} for m in chosen]


def binding_for(a,sources,specialist,methods,rubric,upstream):
    keys=('task_id','objective','domain','artifact_kind','scope','problem','effective_actions','deliverable',
          'selection','constraints','requested_count','evidence_mode','capabilities','required_capabilities',
          'acceptance','feedback','project_revision','thinking_style','effort','brief','material_ambiguity')
    value={k:a[k] for k in keys}
    value['effective_actions']=[x for x in a['effective_actions'] if x not in {'resume','status','record'}]
    # Stage/receipt list are execution bookkeeping; semantic inputs remain bound.
    value.update(sources=sources,specialist=specialist,methods=[m['id'] for m in methods],rubric=rubric,upstream=upstream)
    return digest(value)


def output_current(out):
    if out['kind']=='file':
        p=Path(out['locator'])
        return p.is_file() and file_hash(p)==out['revision']
    # Remote/context versions require host inspection; no fabricated remote checks.
    return False


def plan_single(raw,upstream=None):
    a,data=normalize(raw); acts=set(a['effective_actions']); sources=live_sources(a['sources'])
    specialist=pick_specialist(a); methods=pick_methods(a,data)
    rubric=data['domain_rubrics'][a['domain']]
    if a['domain']=='engineering' and a['deliverable']!='code': rubric='analysis'
    if a['deliverable']=='code': rubric='code'
    if a['deliverable']=='image': rubric='visual'
    if a['deliverable'] in {'deck','document'}: rubric='presentation'
    if specialist=='research-and-writing': rubric='factual_writing'
    if a['artifact_kind'] in {'decision','decision_memo'}: rubric='decision'
    if a['artifact_kind']=='experiment_plan': rubric='experiment'
    binding=binding_for(a,sources,specialist,methods,rubric,upstream or [])
    steps=[]; by_id={}; receipts={r['step']:r for r in a['receipts']}; ignored=[]
    def add(key,reason,depends=(),output=None,state=None,skill=None):
        need(key not in by_id,'Duplicate step '+key)
        deps=list(dict.fromkeys(depends)); need(all(d in by_id for d in deps),'Missing or unordered dependency')
        node={'id':key,'depends_on':deps,'reason':reason,'output':output or reason,'state':state or 'pending',
              'skill':skill or specialist,'acceptance':a['acceptance'] if key=='verify_output' else []}
        old=receipts.get(key)
        if old and key!='present' and state is None:
            if old['binding']==binding and output_current(old['output']) and all(by_id[d]['state']=='done' for d in deps):
                node.update(state='done',completion_evidence=old['evidence'])
            else: ignored.append({'step':key,'reason':'Changed task/source/output, unmet dependency, or non-file evidence requires reinspection'})
        if node['state']=='pending': node['state']='ready' if all(by_id[d]['state']=='done' for d in deps) else 'waiting'
        steps.append(node); by_id[key]=node
        return key
    inspect=add('inspect_context','Inspect active task, authoritative sources, approvals and actual capabilities',output='Verified task contract')
    if 'status' in acts: add('answer_status','Report current evidence and preserve the unfinished objective',[inspect])
    if 'record' in acts: add('record_decisions','Save authorized scoped decisions, or deliver an explicitly unsaved recap',[inspect],state=None if 'file_write' in a['capabilities'] else 'unavailable',skill='creative-learning')
    creative=acts-{'resume','status','record'}
    if 'resume' in acts and not (a['continuity'] and a['continuity']['source_rechecked']):
        add('restore_checkpoint','Inspect the project record and reconstruct pending actions before planning dependent work',[inspect],state='needs_input')
    if not creative:
        add('present','Deliver requested status/record or identify the missing resume checkpoint',list(by_id))
    else:
        base=[inspect]
        needs_source=bool(acts & {'revise','review'}) or a['selection']['status']=='user' or a['evidence_mode'] in {'supplied','mixed','canon'}
        missing=[s['id'] for s in sources if s['status']=='missing']
        if missing or needs_source and not sources:
            base.append(add('resolve_source','Locate exact required sources: '+(', '.join(missing) or 'none identified'),[inspect],state='needs_input'))
        if a['brief']=='blocked' or a['material_ambiguity']:
            base.append(add('clarify_brief','Resolve only the consequential ambiguity; continue independent work',[inspect],state='needs_input'))
        if 'resume' in acts and 'restore_checkpoint' in by_id: base.append('restore_checkpoint')
        if 'brief' in acts or a['brief']=='assumptions_ok':
            base=[add('frame_problem','Define outcome, system boundary, hard constraints and assumptions',base,skill='creative-brief')]
        if a['evidence_mode'] in {'supplied','mixed','canon'}:
            # Source-dependent synthesis does not need a web capability.
            base.append(add('synthesize_sources','Inspect supplied material; distinguish observation, inference and canon',base,skill='research-and-writing'))
        if a['evidence_mode'] in {'live','mixed'}:
            # External evidence can proceed even when a separate local source is missing.
            base.append(add('research_live','Retrieve current external evidence for material claims',[inspect],state=None if 'web' in a['capabilities'] else 'unavailable',skill='research-and-writing'))
        if a['feedback']['verdict']=='rejection':
            base=[add('diagnose_feedback','Distinguish wrong goal, mechanism, taste and execution; unknown reasons remain unknown',base,skill='creative-learning')]
        cursor=base
        if 'diagnose' in acts:
            cursor=[add('diagnose_problem','Model causes, alternatives and a discriminating check before prescribing solutions',cursor,output='Evidence-linked diagnosis and unresolved competing explanations')]
        if acts & {'ideate','vary'}:
            if 'vary' in acts: cursor=[add('design_variations','Lock invariants and vary mechanism-level dimensions',cursor,skill='concept-variations')]
            count=a['requested_count'] if a['requested_count'] is not None else 3
            cursor=[add('generate_options','Generate distinct feasible or clearly hypothetical mechanisms',cursor,output=str(count)+' requested options')]
            by_id[cursor[0]]['requested_count']=count
        if 'revise' in acts:
            cursor=[add('revise_source','Apply only requested changes to the authoritative source',cursor)]
        if acts & {'review','decide','ideate','vary'}:
            cursor=[add('evaluate_options','Check relevant criteria, evidence, tradeoffs and assumptions',cursor,skill='artifact-quality')]
        downstream=bool(acts & {'develop','handoff','produce','experiment'})
        if downstream and a['selection']['status']=='none':
            cursor=[add('resolve_selection','Resolve the required undelegated selection',cursor,state='needs_input')]
        elif a['selection']['status']=='assistant_authorized' and (downstream or 'decide' in acts):
            cursor=[add('select_option','Choose within delegated authority and explain the tradeoff',cursor)]
        if 'develop' in acts:
            cursor=[add('develop_solution','Develop the chosen mechanism into the requested usable result',cursor)]
        if 'experiment' in acts:
            cursor=[add('design_experiment','Specify hypothesis, falsifier, cheapest informative test and decision rule',cursor,output='Executable experiment plan with unknowns; no invented results')]
        if acts & {'handoff','produce'}:
            cursor=[add('prepare_handoff','Bind inputs, constraints, owner/recipient and acceptance conditions',cursor,skill='execution-handoff')]
        if 'produce' in acts:
            required=set(a['required_capabilities'])
            if a['deliverable'] in PRODUCTION_CAP: required.add(PRODUCTION_CAP[a['deliverable']])
            gaps=sorted(required-set(a['capabilities']))
            cursor=[add('produce_artifact','Use available tools to create the actual requested deliverable',cursor,
                        state='unavailable' if gaps else None,output='Requested '+a['deliverable'],skill='execution-handoff')]
            by_id[cursor[0]]['missing_capabilities']=gaps
        if acts-{'research','brief','record','status','resume','review'}:
            cursor=[add('verify_output','Inspect the actual result against scoped acceptance conditions and rubric',cursor,skill='artifact-quality')]
        add('present','Deliver requested result, evidence and material limits; distinguish plans from executed work',list(by_id))
    # Procedures belong inside substantive work, not a duplicate ceremony after it.
    for method in methods:
        priorities=(['design_experiment','evaluate_options','diagnose_problem','generate_options','frame_problem','develop_solution']
                    if method['id']=='D2' else
                    ['diagnose_problem','design_variations','generate_options','frame_problem','evaluate_options','develop_solution','design_experiment'])
        target=next((key for key in priorities if key in by_id),None)
        if target: by_id[target].setdefault('method_contracts',[]).append(method)
    unknown=set(receipts)-set(by_id)
    need(not unknown,'Receipts refer to unknown steps: '+', '.join(sorted(unknown)))
    services=[]
    if a['evidence_mode'] in {'supplied','live','mixed'}: services.append('research-and-writing')
    if any(s['skill']=='artifact-quality' for s in steps): services.append('artifact-quality')
    if a['feedback']['verdict']!='none' or acts & {'record','resume'}: services.append('creative-learning')
    return {'schema_version':2,'task_id':a['task_id'],'objective':a['objective'],'domain':a['domain'],
            'effective_actions':a['effective_actions'],'specialist':{'id':specialist,**data['specialists'][specialist]},
            'services':services,'methods':methods,'rubric':rubric,'input_binding':binding,
            'sources':sources,'steps':steps,'ignored_receipts':ignored,
            'blockers':[s['id'] for s in steps if s['state'] in {'needs_input','unavailable'}],
            'execution_complete':False,'semantic_assessment':'supplied_by_host_model',
            'note':'Plan validation is not proof of semantic recognition, tool execution or output quality.'}


def plan_v2(raw):
    if not isinstance(raw,dict) or 'workstreams' not in raw:
        return plan_single(raw)
    need(set(raw)=={'schema_version','workstreams'} and raw['schema_version']==2,'Invalid portfolio envelope')
    streams=raw['workstreams']; need(isinstance(streams,list) and streams,'Empty workstreams')
    by={}
    for stream in streams:
        need(isinstance(stream,dict) and set(stream)=={'assessment','depends_on'},'Invalid workstream')
        need(isinstance(stream['assessment'],dict) and text(stream['assessment'].get('task_id')),'Workstream task_id required')
        key=stream['assessment']['task_id']; need(key not in by,'Duplicate task_id'); by[key]=stream
    for key,stream in by.items():
        array(stream['depends_on'],set(by),'workstream dependencies'); need(key not in stream['depends_on'],'Self dependency')
    ordered=[]; visiting=set(); visited=set()
    def visit(key):
        need(key not in visiting,'Cyclic workstream dependencies')
        if key in visited:return
        visiting.add(key)
        for dep in by[key]['depends_on']: visit(dep)
        visiting.remove(key); visited.add(key); ordered.append(key)
    for key in by: visit(key)
    plans={}; terminal={}
    for key in ordered:
        upstream=[]
        for dep in by[key]['depends_on']:
            receipt=next((r for r in by[dep]['assessment'].get('receipts',[]) if r['step']==terminal[dep]),None)
            upstream.append({'task_id':dep,'binding':plans[dep]['input_binding'],
                             'output':receipt['output'] if receipt else None})
        plans[key]=plan_single(by[key]['assessment'],upstream)
        terminal[key]=next(s['id'] for s in reversed(plans[key]['steps']) if s['id']!='present')
    nodes=[]; completed_tasks={}
    for key in ordered:
        dependencies_done=all(completed_tasks[d] for d in by[key]['depends_on'])
        for item in plans[key]['steps']:
            node=copy.deepcopy(item); node['id']=key+'/'+item['id']
            node['depends_on']=[key+'/'+d for d in item['depends_on']]
            if item['id']=='inspect_context':
                node['depends_on'] += [d+'/'+terminal[d] for d in by[key]['depends_on']]
                if not dependencies_done and node['state'] in {'ready','done'}: node['state']='waiting'
            # Task-local receipt completion cannot bypass portfolio dependencies.
            if not dependencies_done and node['state']=='done':
                node['state']='waiting'; node.pop('completion_evidence',None)
            nodes.append(node)
        completed_tasks[key]=dependencies_done and next(s for s in plans[key]['steps'] if s['id']==terminal[key])['state']=='done'
    return {'schema_version':2,'workstreams':plans,'steps':nodes,'execution_complete':False,
            'blockers':[n['id'] for n in nodes if n['state'] in {'needs_input','unavailable'}]}
