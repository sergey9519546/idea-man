"""Evidence-bound innovation planning. The host performs semantic recognition.

This module validates its assessment, resolves specialists/methods, composes work,
and checks checkpoint bindings. It never classifies prose or executes a provider.
"""
import copy
import hashlib
import json
import math
import stat
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
                  'audio':'audio_generation','deck':'deck_authoring',
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
        need(p.is_relative_to(PACKAGE.resolve()), 'Specialist file is outside package: '+entry['path'])
        # Availability belongs to the assigned step; an unused missing specialist
        # must not disable an otherwise independent task or portfolio branch.
    return data


def normalize(raw):
    required={'schema_version','task_id','objective','domain','actions','deliverable',
              'artifact_kind','scope','stage','problem','evidence_mode','sources','selection',
              'constraints','evidence'}
    optional={'capabilities','required_capabilities','requested_count','effort','thinking_style',
              'requested_methods','feedback','continuity','receipts','acceptance','material_ambiguity',
              'brief','project_revision','delivery_mode','live_research_dependency'}
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
    a.setdefault('delivery_mode','inline' if a['deliverable']=='text' else 'artifact')
    a.setdefault('live_research_dependency','source_bound' if a['evidence_mode']=='mixed' or a['sources'] else 'independent')
    enum(a['delivery_mode'],{'inline','artifact'},'delivery_mode')
    enum(a['live_research_dependency'],{'independent','source_bound'},'live_research_dependency')
    need(a['delivery_mode']!='inline' or a['deliverable'] in {'text','code'},'Inline delivery supports only text or code')
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
    if actions-{'resume','status','record'} and (a['deliverable']!='text' or a['delivery_mode']=='artifact'):
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
        need(isinstance(receipt,dict) and {'step','binding','evidence','output'}<=set(receipt) and set(receipt)<={'step','binding','evidence','output','transition'},'Invalid receipt')
        need(all(text(receipt[k]) for k in ('step','binding','evidence')) and receipt['step'] not in seen,'Invalid/duplicate receipt')
        seen.add(receipt['step'])
        if 'transition' in receipt:
            t=receipt['transition']
            need(receipt['step']=='revise_source' and isinstance(t,dict) and set(t)=={'snapshot','revision'},'Invalid transition receipt')
            need(text(t['snapshot']) and text(t['revision']),'Invalid transition snapshot identity')
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
            try:
                info=p.stat()
                if not stat.S_ISREG(info.st_mode):
                    item.update(status='missing',inspected=False)
                else:
                    actual=file_hash(p)
                    if item['revision']!=actual: item['inspected']=False
                    item['revision']=actual
            except (FileNotFoundError,NotADirectoryError):
                item.update(status='missing',inspected=False)
            except OSError as error:
                # Keep unknown availability distinct from absence. A transient read
                # failure must not abort unrelated workstreams or preserve inspection.
                item.update(inspected=False,observation_error=type(error).__name__)
        result.append(item)
    return result


def pick_specialist(a):
    actions=set(a['effective_actions'])-{'resume','status','record'}
    if not actions: return 'creative-project' if 'record' in a['effective_actions'] else 'creative-director'
    if 'review' in actions and actions<={'review','produce'}: return 'artifact-quality'
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


def step_specialist(key, primary):
    return {'inspect_context':'creative-director','answer_status':'creative-director',
            'present':'creative-director','resolve_source':'creative-director',
            'record_decisions':'creative-project','prepare_unsaved_recap':'creative-project','restore_checkpoint':'creative-project',
            'clarify_brief':'creative-brief','develop_solution':'concept-development'}.get(key,primary)


def step_capabilities(a,key):
    required=set({'record_decisions':['file_write'],'research_live':['web']}.get(key,[]))
    if key=='produce_artifact':
        required.update(a['required_capabilities'])
        if a['deliverable'] in PRODUCTION_CAP: required.add(PRODUCTION_CAP[a['deliverable']])
        if a['delivery_mode']=='artifact' and a['deliverable'] in {'text','code'}: required.add('file_write')
    return sorted(required)


def pick_methods(a,data):
    acts=set(a['effective_actions']); p=a['problem']
    reasoning=acts & {'brief','diagnose','ideate','vary','decide','experiment'}
    if 'develop' in acts and p['novelty']!='none' and p['kind']!='execution': reasoning.add('develop')
    if a['scope']=='exact' and not a['requested_methods']:
        # Exact scope suppresses automatic method casting, not an explicitly
        # requested procedure within the protected delta. normalize() still
        # rejects ideation/variation; phase assignment adds no new work stages.
        return []
    if a['requested_methods']:
        chosen=a['requested_methods']; reason='Explicit user-requested methods; apply within scope'
    else:
        if not reasoning: return []
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
        ordered=list(dict.fromkeys(chosen))
        budget={'quick':1,'standard':2,'deep':3}[a['effort']]
        # Effort limits optional breadth, not the requested operation. A required
        # evidence lens cannot replace invention or causal diagnosis altogether.
        substantive=next((m for m in ordered if m!='D2'),None)
        if budget==1 and ordered[0]=='D2' and substantive and acts & {'ideate','vary','diagnose'}:
            chosen=[substantive,'D2']
        else:
            chosen=ordered[:budget]
        reason='Problem: '+p['kind']+'; bottleneck: '+p['bottleneck']+'; style: '+a['thinking_style']
    return [{'id':m,'reason':reason,'procedure':data['methods'][m]['procedure'],
             'output':data['methods'][m]['output'],'reference':data['methods'][m]['reference'],
             'section_prefix':data['methods'][m]['section_prefix']} for m in chosen]


def binding_for(a,sources,specialist,methods,rubric,upstream):
    keys=('task_id','objective','domain','artifact_kind','scope','problem','effective_actions','deliverable',
          'selection','constraints','requested_count','evidence_mode','capabilities','required_capabilities',
          'acceptance','feedback','project_revision','thinking_style','effort','brief','material_ambiguity',
          'delivery_mode','live_research_dependency','evidence')
    value={k:a[k] for k in keys}
    value['effective_actions']=[x for x in a['effective_actions'] if x not in {'resume','status','record'}]
    # Stage/receipt list are execution bookkeeping; semantic inputs remain bound.
    # Bind only resolved selected contracts, not unrelated registry cards. Selected
    # packaged content is bound separately per step by the shared context selector.
    contracts=[{key:method[key] for key in ('id','procedure','output','reference','section_prefix')} for method in methods]
    value.update(sources=sources,specialist=specialist,methods=contracts,rubric=rubric,upstream=upstream)
    return digest(value)


def output_current(out):
    if out['kind']=='file':
        p=Path(out['locator'])
        try:
            return p.is_file() and file_hash(p)==out['revision']
        except OSError:
            # An unavailable prior observation is not reusable completion evidence.
            return False
    # Remote/context versions require host inspection; no fabricated remote checks.
    return False


def step_binding(task_binding, key, predecessors, contract=None):
    """Bind this step to accepted predecessor identities, transitively.

    Legacy task-wide receipt bindings deliberately do not match this namespace.
    Replan and remint ready steps; accepting old bindings would bypass output checks.
    """
    value={'version':'step-output-v1','task_binding':task_binding,'step':key,
                   'predecessors':[{'step':node['id'],'binding':node['input_binding'],
                       'output':node.get('completion_output') if node['state']=='done' else None}
                       for node in predecessors]}
    if contract: value['contract']=contract
    return digest(value)


def pick_rubric(a,data,specialist):
    """Verify task substance first; a file extension does not define the job."""
    if a['deliverable']=='code': return 'code'
    if a['deliverable']=='image': return 'visual'
    kinds={'analysis':'analysis','diagnosis':'analysis','causal_analysis':'analysis',
           'decision':'decision','decision_memo':'decision',
           'experiment_plan':'experiment','test_protocol':'experiment',
           'process':'process','process_spec':'process','operating_procedure':'process',
           'article':'factual_writing','research_brief':'factual_writing',
           'calculation':'quantitative','estimate':'quantitative','optimization':'quantitative',
           'statistical_analysis':'quantitative',
           'proof':'formal_reasoning','formal_proof':'formal_reasoning','derivation':'formal_reasoning',
           'explanation':'explanation','explainer':'explanation',
           'coaching':'coaching','coaching_turn':'coaching',
           'presentation':'presentation','pitch_deck':'presentation'}
    if a['artifact_kind'] in kinds: return kinds[a['artifact_kind']]
    if specialist=='research-and-writing': return 'factual_writing'
    if a['deliverable']=='deck': return 'presentation'
    return data['domain_rubrics'][a['domain']]


def needs_source_review(actions):
    return 'review' in actions and bool(actions & {
        'diagnose','ideate','vary','revise','decide','develop','experiment','handoff'})


def methods_by_phase(a,methods):
    """Assign supplied procedures to work they support, not just the first node."""
    acts=set(a['effective_actions']); available=set()
    for action,step in [('diagnose','diagnose_problem'),('revise','revise_source'),
                        ('develop','develop_solution'),('experiment','design_experiment')]:
        if action in acts: available.add(step)
    if acts & {'ideate','vary'}: available.add('generate_options')
    if 'vary' in acts: available.add('design_variations')
    if acts & {'decide','ideate','vary'} or 'review' in acts and not needs_source_review(acts):
        available.add('evaluate_options')
    if 'brief' in acts or a['brief']=='assumptions_ok': available.add('frame_problem')
    if 'produce' in acts: available.add('produce_artifact')
    # Research is substantive work even when its answer stays inline. Attach a
    # requested procedure to evidence work, never merely to report packaging.
    if 'research' in acts:
        available.add('research_live' if a['evidence_mode'] in {'live','mixed'} else 'synthesize_sources')
    assignments={}
    applications={
        'diagnose_problem':'Use the procedure to distinguish causes, alternatives and evidence gaps.',
        'design_variations':'Use the procedure to define useful varying axes while protecting invariants.',
        'generate_options':'Use the procedure to derive distinct useful interventions or mechanisms, not more cause labels.',
        'evaluate_options':'Use the procedure to examine relevant evidence, tradeoffs and failure conditions.',
        'design_experiment':'Use the procedure to specify a discriminating observation and prospective decision rule.',
        'frame_problem':'Use the procedure to establish the outcome, boundary and decisive assumptions.',
        'revise_source':'Apply the procedure only within the authorized bounded revision.',
        'develop_solution':'Use the procedure to develop the selected mechanism and its consequential edge cases.',
        'synthesize_sources':'Apply the requested procedure to the supplied evidence; distinguish source support, assumptions and unknowns without inventing observations.',
        'research_live':'Apply the requested procedure while gathering and synthesizing relevant evidence; preserve source support, freshness, confounds and uncertainty. A hypothesis or proposed test is not an executed experiment.',
        'produce_artifact':'Apply the explicitly requested procedure within the actual output task; preserve its format, factual, quantitative or formal checks. An analogy or heuristic does not substitute for calculation, evidence or proof.'}
    if 'vary' in acts and 'ideate' not in acts:
        applications['generate_options']='Use the procedure to derive meaningful variants within permitted axes; preserve explicit locks, including a chosen mechanism when fixed. Shared locked properties do not make variants duplicates.'
    for method in methods:
        if method['id']=='D2':
            priorities=['design_experiment','evaluate_options','diagnose_problem','generate_options',
                        'frame_problem','revise_source','develop_solution']
        elif method['id'] in {'Y1','Y2','H1','H2','H3'}:
            priorities=['diagnose_problem','design_variations','generate_options','frame_problem',
                        'evaluate_options','revise_source','develop_solution','design_experiment']
        else:
            priorities=['design_variations','generate_options','diagnose_problem','frame_problem',
                        'evaluate_options','revise_source','develop_solution','design_experiment']
        target=next((key for key in priorities+['research_live','synthesize_sources','produce_artifact'] if key in available),None)
        need(target is not None,'Requested thinking method has no compatible substantive step; clarify the operation or remove requested_methods')
        targets=[target]
        # Causal/system procedures also generate interventions; a diagnosis pass
        # cannot consume the later phase's required generating work.
        if 'generate_options' in available and method['id']!='D2':
            if target=='design_variations' or target=='diagnose_problem' and method['id'] in {'Y1','Y2','H1','H2','H3'}:
                targets.append('generate_options')
        for key in targets:
            assignments.setdefault(key,[]).append({**method,'application':applications[key]})
    return assignments


def verification_for_step(a,key,rubric):
    """Required checks are task contracts; optional method breadth cannot remove them."""
    checks={
        'prepare_unsaved_recap':['explicitly_unsaved_recap','requested_persistence_remains_blocked'],
        'diagnose_problem':['observations_vs_causes','competing_explanations_and_discriminating_evidence'],
        'generate_options':['distinct_useful_mechanisms','hard_constraints_and_hypothetical_effects','resource_totals_and_existing_baseline'],
        'design_variations':['protected_invariants_and_meaningful_axes'],
        'design_experiment':['hypothesis_observation_confounds_decision_rule','planned_vs_executed_results'],
        'synthesize_sources':['source_support_coverage_and_missing_material'],
        'research_live':['source_support_freshness_and_scope'],
        'frame_problem':['requested_outcome_constraints_and_decisive_unknown'],
        'revise_source':['authorized_delta_and_protected_properties'],
        'develop_solution':['selected_mechanism_dependencies_and_failure_limits','resource_totals_and_existing_baseline']}.get(key,[])
    checks=list(checks)
    if key=='generate_options' and 'vary' in a['effective_actions'] and 'ideate' not in a['effective_actions']:
        checks=[check for check in checks if check!='distinct_useful_mechanisms']
        checks[:0]=['distinct_useful_variants_within_permitted_axes','explicit_locks_and_authorized_variation_scope']
    if key in {'verify_output','evaluate_options','review_source','produce_artifact'}:
        checks += ['requested_scope_count_format','protected_constraints_and_authority','actual_output_and_evidence_limits']
        checks += {
            'quantitative':['quantity_model_inputs_units','calculation_validity','bounds_sanity_precision','compared_quantities_use_same_basis_when_applicable'],
            'formal_reasoning':['definitions_claim_and_assumptions','assumptions_inference_cases_counterexamples','proof_vs_computation_or_conjecture'],
            'explanation':['requested_question_level_and_accuracy','examples_and_material_limits'],
            'coaching':['requested_learning_interaction_no_premature_solution','feedback_on_actual_attempt','next_interaction_addresses_first_material_error'],
            'analysis':['source_support_and_valid_quantities','observations_vs_causes','competing_explanations_and_discriminating_evidence'],
            'experiment':['hypothesis_observation_confounds_decision_rule','planned_vs_executed_results'],
            'decision':['criteria_tradeoffs_sensitivity_and_commitment_scope'],
            'process':['owners_handoffs_exceptions_and_shifted_burden'],
            'code':['requested_behavior_errors_and_executed_check_limits'],
            'visual':['delivered_pixels_and_approved_reference_fidelity']}.get(rubric,[])
        if a['artifact_kind']=='statistical_analysis':
            checks.append('sample_comparison_confounds_and_inference_limits')
        if a['evidence_mode'] in {'supplied','live','mixed','canon'}:
            checks.append('claims_match_inspected_sources_and_evidence_mode')
    if checks and (a['problem']['stakes']=='high' or a['problem']['reversibility']=='irreversible'):
        checks.append('consequential_uncertainty_and_failure_limits')
    return {'rubric':rubric,'checks':list(dict.fromkeys(checks))} if checks else None


def plan_single(raw,upstream=None,upstream_ready=True):
    from workflow_context import reference_contracts, load_resource
    a,data=normalize(raw); acts=set(a['effective_actions']); sources=live_sources(a['sources'])
    for receipt in a['receipts']:
        if 'transition' in receipt:
            frozen=transition_preimage(raw,receipt)
            if frozen is not None:
                sources=[copy.deepcopy(frozen) if src['id']==frozen['id'] else src for src in sources]
    specialist=pick_specialist(a); methods=pick_methods(a,data)
    rubric=pick_rubric(a,data,specialist)
    phase_methods=methods_by_phase(a,methods)
    binding=binding_for(a,sources,specialist,methods,rubric,upstream or [])
    steps=[]; by_id={}; receipts={r['step']:r for r in a['receipts']}; ignored=[]
    guidance_cache={}
    def add(key,reason,depends=(),output=None,state=None,skill=None):
        need(key not in by_id,'Duplicate step '+key)
        deps=list(dict.fromkeys(depends)); need(all(d in by_id for d in deps),'Missing or unordered dependency')
        node={'id':key,'depends_on':deps,'reason':reason,'output':output or reason,'state':state or 'pending',
              'skill':skill or step_specialist(key,specialist),'acceptance':a['acceptance'] if key=='verify_output' or
                      key=='evaluate_options' and acts-{'status','resume','record'}=={'review'} else []}
        need(node['skill'] in data['specialists'],'Unregistered step specialist: '+node['skill'])
        registered=data['specialists'][node['skill']]
        need(registered['path']=='skills/'+node['skill']+'/SKILL.md','Step specialist path does not match its identity')
        node['skill_contract']={'id':node['skill'],**registered}
        node['required_capabilities']=step_capabilities(a,key)
        node['missing_capabilities']=sorted(set(node['required_capabilities'])-set(a['capabilities']))
        if node['missing_capabilities'] and state is None: node['state']='unavailable'
        if key in phase_methods: node['method_contracts']=copy.deepcopy(phase_methods[key])
        node['reference_contracts']=reference_contracts(key,rubric,node.get('method_contracts',[]),actions=acts)
        guidance=[{'path':registered['path'],'selector':{'kind':'all'}}]+node['reference_contracts']
        node['guidance_content']=[]
        for resource in guidance:
            cache_key=digest(resource)
            if cache_key not in guidance_cache:
                try:
                    loaded=load_resource(resource,package=PACKAGE)
                    guidance_cache[cache_key]={**copy.deepcopy(resource),'content_sha256':loaded['content_sha256']}
                except (OSError,ValueError,UnicodeError) as error:
                    guidance_cache[cache_key]={**copy.deepcopy(resource),'error':str(error)}
            identity=copy.deepcopy(guidance_cache[cache_key])
            node['guidance_content'].append(identity)
            if 'error' in identity:
                node['state']='unavailable'
        verification=verification_for_step(a,key,rubric)
        if verification: node['verification_contract']=verification
        contract={name:node[name] for name in ('skill_contract','reference_contracts','guidance_content','required_capabilities','method_contracts','verification_contract') if name in node}
        node['input_binding']=step_binding(binding,key,[by_id[d] for d in deps],contract)
        dependencies_ready=all(by_id[d]['state']=='done' for d in deps)
        if key=='inspect_context': dependencies_ready=dependencies_ready and upstream_ready
        old=receipts.get(key)
        if old and key!='present' and state is None:
            if node['state']!='unavailable' and not node['missing_capabilities'] and old['binding']==node['input_binding'] and output_current(old['output']) and dependencies_ready and ('transition' not in old or transition_preimage(raw,old) is not None):
                node.update(state='done',completion_evidence=old['evidence'],
                            completion_output=copy.deepcopy(old['output']))
            else: ignored.append({'step':key,'reason':'Changed task/source/predecessor/output, unmet dependency, legacy binding, or non-file evidence requires reinspection'})
        if node['state']=='pending': node['state']='ready' if dependencies_ready else 'waiting'
        steps.append(node); by_id[key]=node
        return key
    def add_record(depends):
        key=add('record_decisions','Save the accepted scoped results and decisions',depends)
        if 'file_write' not in a['capabilities']:
            add('prepare_unsaved_recap','Provide an explicitly unsaved recap while requested persistence remains blocked',depends,
                output='Unsaved recap only; file_write is unavailable and the requested durable save is still unfulfilled')
        return key
    inspect=add('inspect_context','Inspect active task, authoritative sources, approvals and actual capabilities',output='Verified task contract')
    creative=acts-{'resume','status','record'}
    if 'status' in acts: add('answer_status','Report current evidence and preserve the unfinished objective',[inspect])
    if 'record' in acts and not creative: add_record([inspect])
    if 'resume' in acts and not (a['continuity'] and a['continuity']['source_rechecked']):
        add('restore_checkpoint','Inspect the project record and reconstruct pending actions before planning dependent work',[inspect],state='needs_input')
    if not creative:
        add('present','Deliver requested status/record or identify the missing resume checkpoint',list(by_id))
    else:
        base=[inspect]
        source_bound_live=a['evidence_mode'] in {'live','mixed'} and a['live_research_dependency']=='source_bound'
        needs_source=bool(acts & {'revise','review','vary'}) or a['selection']['status']=='user' or a['evidence_mode'] in {'supplied','mixed','canon'} or source_bound_live
        missing=[s['id'] for s in sources if s['status']=='missing']
        unreadable=[s['id'] for s in sources if s.get('observation_error')]
        if missing or unreadable or needs_source and not sources:
            detail='; '.join(filter(None,['missing: '+', '.join(missing) if missing else '',
                                          'unreadable: '+', '.join(unreadable) if unreadable else '']))
            base.append(add('resolve_source','Resolve exact required sources: '+(detail or 'none identified'),[inspect],
                            state='unavailable' if unreadable else 'needs_input'))
        if a['brief']=='blocked' or a['material_ambiguity']:
            base.append(add('clarify_brief','Resolve only the consequential ambiguity; continue independent work',[inspect],state='needs_input'))
        if 'resume' in acts and 'restore_checkpoint' in by_id: base.append('restore_checkpoint')
        if 'brief' in acts or a['brief']=='assumptions_ok':
            base=[add('frame_problem','Define outcome, system boundary, hard constraints and assumptions',base,skill='creative-brief')]
        if a['evidence_mode'] in {'supplied','mixed','canon'} or source_bound_live:
            # Source-dependent synthesis does not need a web capability.
            base.append(add('synthesize_sources','Inspect supplied material; distinguish observation, inference and canon',base,skill='research-and-writing'))
        if a['evidence_mode'] in {'live','mixed'}:
            # Only explicitly independent queries bypass supplied-source preparation.
            live_deps=list(base) if source_bound_live else [inspect]
            base.append(add('research_live','Retrieve current external evidence for material claims',live_deps,skill='research-and-writing'))
        if a['feedback']['verdict']=='rejection':
            base=[add('diagnose_feedback','Distinguish wrong goal, mechanism, taste and execution; unknown reasons remain unknown',base,skill='creative-learning')]
        cursor=base
        if needs_source_review(acts):
            cursor=[add('review_source','Inspect the authoritative source and establish evidence-linked findings before subsequent requested work',cursor,
                        output='Read-only findings and scoped implications for the inspected source',skill='artifact-quality')]
        if 'diagnose' in acts:
            cursor=[add('diagnose_problem','Model causes, alternatives and a discriminating check before prescribing solutions',cursor,output='Evidence-linked diagnosis and unresolved competing explanations')]
        if acts & {'ideate','vary'}:
            if 'vary' in acts: cursor=[add('design_variations','Preserve explicit locks and identify meaningful permitted variation axes',cursor,skill='concept-variations')]
            count=a['requested_count'] if a['requested_count'] is not None else 3
            variation_only='vary' in acts and 'ideate' not in acts
            reason='Generate meaningful variants within permitted axes while preserving explicit locks' if variation_only else 'Generate distinct feasible or clearly hypothetical mechanisms'
            cursor=[add('generate_options',reason,cursor,output=str(count)+' requested options')]
            by_id[cursor[0]]['requested_count']=count
        if 'revise' in acts:
            cursor=[add('revise_source','Apply only requested changes to the authoritative source',cursor)]
        if acts & {'decide','ideate','vary'} or 'review' in acts and not needs_source_review(acts):
            cursor=[add('evaluate_options','Check relevant criteria, evidence, tradeoffs and assumptions',cursor,
                        skill='creative-review' if acts & {'ideate','vary','decide'} else 'artifact-quality')]
        report_actions=acts-{'produce','status','resume','record'}
        report_only=bool(report_actions) and report_actions<={'brief','diagnose','research','review','decide'}
        # Authoring a recommendation/report does not commit to its subject.
        downstream=bool(acts & {'develop','handoff','produce','experiment'}) and not report_only
        if downstream and a['selection']['status']=='none':
            cursor=[add('resolve_selection','Resolve the required undelegated selection',cursor,state='needs_input')]
        elif a['selection']['status']=='assistant_authorized' and (downstream or 'decide' in acts):
            cursor=[add('select_option','Choose within delegated authority and explain the tradeoff',cursor)]
        if 'develop' in acts:
            cursor=[add('develop_solution','Develop the chosen mechanism into the requested usable result',cursor)]
        if 'experiment' in acts:
            cursor=[add('design_experiment','Specify hypothesis, falsifier, cheapest informative test and decision rule',cursor,output='Executable experiment plan with unknowns; no invented results')]
        direct_inline=acts-{'status','resume','record'}=={'produce'} and a['delivery_mode']=='inline' and a['deliverable']=='text' and rubric in {'quantitative','formal_reasoning','explanation','coaching'}
        if 'handoff' in acts or 'produce' in acts and not direct_inline:
            cursor=[add('prepare_handoff','Bind inputs, constraints, owner/recipient and acceptance conditions',cursor,skill='execution-handoff')]
        if 'produce' in acts:
            cursor=[add('produce_artifact','Use available tools to create the actual requested deliverable',cursor,
                        output='Requested '+a['deliverable']+' ('+a['delivery_mode']+')',skill='execution-handoff')]
        if acts-{'record','status','resume','review'}:
            cursor=[add('verify_output','Inspect the actual result against scoped acceptance conditions and rubric',cursor,skill='artifact-quality')]
        if 'record' in acts:
            cursor=[add_record(cursor)]
        add('present','Deliver requested result, evidence and material limits; distinguish plans from executed work',list(by_id))
    need(set(phase_methods)<=set(by_id),'Assigned thinking method has no actual work step')
    unknown=set(receipts)-set(by_id)
    supported={'inspect_context','answer_status','record_decisions','prepare_unsaved_recap','restore_checkpoint','resolve_source','clarify_brief',
               'frame_problem','synthesize_sources','research_live','diagnose_feedback','review_source','diagnose_problem',
               'design_variations','generate_options','revise_source','evaluate_options','resolve_selection',
               'select_option','develop_solution','design_experiment','prepare_handoff','produce_artifact','verify_output','present'}
    need(unknown<=supported,'Receipts refer to unknown steps: '+', '.join(sorted(unknown-supported)))
    ignored.extend({'step':key,'reason':'Step is absent from the current plan; obsolete receipt'} for key in sorted(unknown))
    services=[]
    for service in ('research-and-writing','artifact-quality','creative-learning','creative-project'):
        if any(s['skill']==service for s in steps): services.append(service)
    return {'schema_version':2,'task_id':a['task_id'],'objective':a['objective'],'domain':a['domain'],
            'effective_actions':a['effective_actions'],'delivery_mode':a['delivery_mode'],
            'live_research_dependency':a['live_research_dependency'],'specialist':{'id':specialist,**data['specialists'][specialist]},
            'services':services,'methods':methods,'rubric':rubric,'input_binding':binding,
            'effort_policy':{'optional_method_budget':{'quick':1,'standard':2,'deep':3}[a['effort']],
                             'required_checks_reduced':False,
                             'basis':'Scope, evidence, dependencies, stakes and acceptance govern required work; effort limits optional breadth and does not set response length.'},
            'sources':sources,'steps':steps,'ignored_receipts':ignored,
            'receipt_binding_version':'step-output-v1',
            'method_contract_coverage':'Selected method/section content, assigned skill content, reference selectors, phase applications and required check contracts are bound. Hashes do not prove host inspection or correctness.',
            'receipt_compatibility':'Receipts predating selected-content binding or using legacy task-wide v2 bindings are ignored; actually reinspect affected work and remint ready steps using their input_binding.',
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
    for root in by:
        stack=[(root,False)]
        while stack:
            key,finish=stack.pop()
            if key in visited: continue
            if finish:
                visiting.remove(key); visited.add(key); ordered.append(key)
                continue
            need(key not in visiting,'Cyclic workstream dependencies')
            visiting.add(key); stack.append((key,True))
            stack.extend((dep,False) for dep in reversed(by[key]['depends_on']))
    plans={}; terminal={}
    for key in ordered:
        upstream=[]; dependencies_done=True
        for dep in by[key]['depends_on']:
            frontier=[s for s in plans[dep]['steps'] if s['id']!='present']
            dependencies_done=dependencies_done and all(n['state']=='done' for n in frontier)
            # Include every required branch, even independently blocked siblings.
            for node in frontier:
                upstream.append({'task_id':dep,'step':node['id'],'binding':node['input_binding'],
                                 'output':node.get('completion_output') if node['state']=='done' else None})
        # Gate before evaluating receipts so local and flattened descendants agree.
        plans[key]=plan_single(by[key]['assessment'],upstream,dependencies_done)
        terminal[key]=[s['id'] for s in plans[key]['steps'] if s['id']!='present']
    nodes=[]
    for key in ordered:
        for item in plans[key]['steps']:
            node=copy.deepcopy(item); node['id']=key+'/'+item['id']
            node['depends_on']=[key+'/'+d for d in item['depends_on']]
            if item['id']=='inspect_context':
                node['depends_on'] += [d+'/'+step for d in by[key]['depends_on'] for step in terminal[d]]
            nodes.append(node)
    return {'schema_version':2,'workstreams':plans,'steps':nodes,'execution_complete':False,
            'blockers':[n['id'] for n in nodes if n['state'] in {'needs_input','unavailable'}]}

def execution_contract(raw):
    a,_=normalize(raw)
    return {k:v for k,v in a.items() if k not in {'receipts','stage'}}


def load_snapshot(path,revision):
    p=Path(path)
    payload=p.read_bytes()
    need(hashlib.sha256(payload).hexdigest()==revision,'Execution snapshot changed or missing')
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'Duplicate JSON key: '+key)
            result[key]=value
        return result
    def finite_number(token):
        value=float(token)
        need(math.isfinite(value),'Non-finite JSON number: '+token)
        return value
    def constant(token):
        raise ValueError('Non-finite JSON constant: '+token)
    snap=json.loads(payload.decode('utf-8-sig'),object_pairs_hook=pairs,
                    parse_float=finite_number,parse_constant=constant)
    need(isinstance(snap,dict) and set(snap)=={'version','assessment','source_id','binding','task_id'},'Invalid execution snapshot')
    need(type(snap['version']) is int and snap['version']==1 and text(snap['source_id']) and text(snap['binding']),'Invalid execution snapshot')
    normalized,_=normalize(snapshot_target(snap))
    need(not any('transition' in r for r in normalized['receipts']),'Nested transitions unsupported')
    return snap


def snapshot_preimage(raw,snap):
    need(execution_contract(raw)==execution_contract(snapshot_target(snap)),'Snapshot belongs to changed task or operation')
    current={r['step']:r for r in raw.get('receipts',[])}
    need(all(current.get(r['step'])==r for r in snapshot_target(snap).get('receipts',[])),
         'Snapshot predecessor receipts changed')
    source=next((s for s in snapshot_target(snap)['sources'] if s['id']==snap['source_id']),None)
    need(source is not None and source['kind']=='file' and source['status']=='available','Invalid snapshot source')
    return source


def transition_preimage(raw,receipt):
    try:
        t=receipt['transition']; snap=load_snapshot(t['snapshot'],t['revision'])
        source=snapshot_preimage(raw,snap)
        need(receipt['binding']==snap['binding'],'Transition binding changed')
        need(receipt['output']['kind']=='file' and Path(receipt['output']['locator']).resolve()==Path(source['locator']).resolve(),
             'Transition output is not the authorized source')
        need(output_current(receipt['output']),'Transition postimage changed')
        return source
    except (ValueError,OSError,KeyError,TypeError):
        return None


def snapshot_target(snap):
    raw=snap['assessment']
    need(isinstance(raw,dict),'Invalid snapshot assessment')
    task_id=snap['task_id']
    if 'workstreams' in raw:
        need(text(task_id),'Portfolio snapshot requires task_id')
        # Validate the envelope shape and target without refreshing its pre-edit files.
        need(set(raw)=={'schema_version','workstreams'} and raw['schema_version']==2 and isinstance(raw['workstreams'],list),
             'Invalid snapshot portfolio')
        matches=[stream['assessment'] for stream in raw['workstreams']
                 if isinstance(stream,dict) and isinstance(stream.get('assessment'),dict)
                 and stream['assessment'].get('task_id')==task_id]
        need(len(matches)==1,'Snapshot target task is missing or duplicated')
        return matches[0]
    need(task_id is None,'Single-workstream snapshot cannot carry task_id')
    return raw


def selected_assessment(raw,task_id):
    if 'workstreams' in raw:
        need(text(task_id),'Portfolio snapshot requires --task-id')
        matches=[stream['assessment'] for stream in raw['workstreams'] if stream['assessment'].get('task_id')==task_id]
        need(len(matches)==1,'Unknown snapshot task_id')
        return matches[0]
    need(task_id is None,'--task-id requires a portfolio')
    return raw


def begin_step(raw,source_id,task_id=None):
    p=plan_v2(raw)
    current=p['workstreams'][task_id] if 'workstreams' in p and task_id in p['workstreams'] else p
    target=selected_assessment(raw,task_id)
    a,_=normalize(target)
    need(not any('transition' in r for r in a['receipts']),'Rebase completed transitions before beginning another edit')
    node=next((n for n in current['steps'] if n['id']=='revise_source'),None)
    need(node is not None and node['state']=='ready','Snapshot requires ready revise_source')
    source=next((s for s in current['sources'] if s['id']==source_id),None)
    original=next((s for s in a['sources'] if s['id']==source_id),None)
    need(source is not None and source['kind']=='file' and source['status']=='available' and source==original,
         'Snapshot requires an unchanged identified file source')
    flat_id=task_id+'/revise_source' if 'workstreams' in p else 'revise_source'
    graph={n['id']:n for n in p['steps']}
    predecessors=set(); pending=list(graph[flat_id]['depends_on'])
    while pending:
        dependency=pending.pop()
        if dependency not in predecessors:
            predecessors.add(dependency)
            pending.extend(graph[dependency]['depends_on'])
    target_path=Path(source['locator']).resolve()
    for key in predecessors:
        output=graph[key].get('completion_output',{})
        if output.get('kind')!='file':
            continue
        predecessor_path=Path(output['locator']).resolve()
        try:
            same=predecessor_path==target_path or predecessor_path.samefile(target_path)
        except OSError as error:
            raise ValueError('Cannot verify in-place target file identity; preserve predecessor evidence and retry after resolving access') from error
        need(not same,
             'In-place target is an accepted predecessor output; preserve immutable predecessor evidence and revise a separate working copy')
    return {'version':1,'assessment':copy.deepcopy(raw),'source_id':source_id,'binding':node['input_binding'],'task_id':task_id}


def receipt_from_snapshot(raw,snapshot_path,output,evidence,revision,task_id=None):
    snap=load_snapshot(snapshot_path,revision)
    need(snap['task_id']==task_id,'Snapshot task_id differs')
    target=selected_assessment(raw,task_id)
    source=snapshot_preimage(target,snap)
    need(output['kind']=='file' and Path(output['locator']).resolve()==Path(source['locator']).resolve(),
         'Snapshot output must be the authorized source')
    need(output_current(output),'Output changed during receipt creation')
    receipt={'step':'revise_source','binding':snap['binding'],'evidence':evidence,'output':output,
             'transition':{'snapshot':str(Path(snapshot_path).resolve()),'revision':revision}}
    candidate=copy.deepcopy(raw)
    candidate_target=selected_assessment(candidate,task_id)
    candidate_target['receipts']=[r for r in candidate_target.get('receipts',[]) if r['step']!='revise_source']+[receipt]
    p=plan_v2(candidate)
    current=p['workstreams'][task_id] if 'workstreams' in p else p
    node=next(n for n in current['steps'] if n['id']=='revise_source')
    need(node['state']=='done','Snapshot inputs or completed dependencies changed')
    return receipt
