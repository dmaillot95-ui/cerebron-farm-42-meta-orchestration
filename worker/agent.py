import hashlib,json,os,pathlib,subprocess,sys
sys.path.append('worker')
from registry_loader import load_registry
PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']
def run(cmd,timeout=240):
    return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
def payload_for(spec,prompt):
    p={}; set_prompt=False
    for x in spec.get('parameters',[]):
        n=x.get('name',''); l=n.lower(); req=bool(x.get('required',False)); default=x.get('default'); typ=(x.get('type') or {}).get('type')
        if l in {'message','prompt','text','query','input','instruction','user_message'}: p[n]=prompt; set_prompt=True
        elif l in {'chat_history','history','messages'}: p[n]=[]
        elif l in {'max_new_tokens','max_tokens','maximum_new_tokens'}: p[n]=600
        elif l=='temperature': p[n]=0.1
        elif l=='top_p': p[n]=0.9
        elif l=='top_k': p[n]=40
        elif l in {'system','system_prompt'}: p[n]='CEREBRON C42.1. REALITY>COHERENCE. EVIDENCE>CONFIDENCE. CLAIM<=EVIDENCE. UNKNOWN REMAINS UNKNOWN. CONSENSUS!=TRUTH. AGENT COUNT!=INTELLIGENCE. SAME MODEL/DATA!=INDEPENDENT EVIDENCE. CONSCIOUSNESS_STATUS=UNRESOLVED.'
        elif req and default is None:
            if typ=='string' and not set_prompt: p[n]=prompt; set_prompt=True
            else: return None
    return p if set_prompt else None
def extract(raw):
    raw=raw.strip()
    try:
        o=json.loads(raw)
        if isinstance(o,dict):
            for k in ('Response','response','text','output','message'):
                if isinstance(o.get(k),str): return o[k].strip()
    except: pass
    return raw
def invoke(space,prompt):
    info=run(['hf-gradio','info',space],120)
    if info.returncode!=0: return False,'',{'error':info.stderr[-4000:]}
    api=json.loads(info.stdout); eps=list(api.items()); eps.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0]))
    errors=[]
    for ep,spec in eps:
        payload=payload_for(spec,prompt)
        if payload is None: continue
        pred=run(['hf-gradio','predict',space,ep,json.dumps(payload,ensure_ascii=False)],240)
        if pred.returncode==0 and pred.stdout.strip():
            text=extract(pred.stdout)
            if text: return True,text,{'endpoint':ep,'sha256':hashlib.sha256(text.encode()).hexdigest()}
        errors.append((ep,(pred.stderr or pred.stdout)[-2000:]))
    return False,'',{'errors':errors}
role=os.environ['ROLE']; model=os.environ['MODEL']
registry_context,registry_meta=load_registry(['constitution','meta_core','macrograins','disciplines','super_disciplines','supra','keys','banks'])
prompt=f'''You are FARM 42 META-ORCHESTRATION role {role}, operating under CEREBRON C42.1. Audit orchestration quality across multi-agent/multi-model systems. Examine routing, sequencing, dependency structure, duplicated evidence, contradiction handling, stopping rules, failure recovery, bottlenecks, verification gates, and whether parallelism creates real independent evidence. Never equate agent count with intelligence or consensus with truth. Distinguish established facts, derived conclusions, assumptions, unknowns, and recommendations.\n\nMANDATORY FIRST LINES IN EVERY RESPONSE:\nCEREBRON_MODE: FULL\nCEREBRON_VERSION: C42.1\nROLE: {role}\nEVIDENCE_STATUS: UNREVIEWED_EXTERNAL_AGENT_OUTPUT\n\nThen return: TARGET, CLAIM, METHOD, ASSUMPTIONS, EVIDENCE, COUNTEREVIDENCE, DEPENDENCIES, PROVENANCE, COST, FAILURE_MODES, CONTRADICTIONS, MINORITY_BLOCKERS, RESIDUAL, SMALLEST_REMAINING_GAP, NEXT_DECISIVE_TEST, STOP_CONDITIONS, UNCERTAINTIES. Preserve material minority objections. Functional performance, self-report, memory, self-model or multi-agent consensus never proves phenomenal consciousness; CONSCIOUSNESS_STATUS remains UNRESOLVED.

C42 SHARED CONTEXT — guidance only; not self-certifying evidence:
{registry_context}'''
ok,text,meta=invoke(model,prompt)
out={'farm':42,'role':role,'model':model,'inference_success':ok,'status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'EXTERNAL_INFERENCE_FAILED','output':text,'meta':meta,'registry_runtime':registry_meta}
pathlib.Path('result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))