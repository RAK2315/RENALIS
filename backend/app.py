from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timezone
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Literal
from .model import PATIENTS, MODEL_VERSION, snapshot, scenario, patient_list, revealed_outcome, evaluation
from .mechanisms import analyze, CHANNELS, VERSION as LAB_VERSION
from .measurement_fixtures import acquire_fixture
from .challenges import run_challenges

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "renalis.sqlite"
DB_PATH.parent.mkdir(exist_ok=True)
app = FastAPI(title="RENALIS research twin", version="0.4.0")
_schema_lock=threading.RLock()


def connection():
    # First page load makes concurrent requests; schema migration must be serialized.
    with _schema_lock:
        return _connection()


def _connection():
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, patient_id TEXT, cutoff INTEGER, note TEXT, created_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS branches (id INTEGER PRIMARY KEY, patient_id TEXT, cutoff INTEGER, rate INTEGER, profile TEXT, result TEXT, created_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS measurements (id INTEGER PRIMARY KEY, patient_id TEXT, request_cutoff INTEGER, available_minute INTEGER, channel TEXT, value REAL, unit TEXT, source TEXT, active INTEGER DEFAULT 1, created_at TEXT)")
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS active_measurement_channel ON measurements(patient_id,available_minute,channel) WHERE active=1")
    db.execute("CREATE TABLE IF NOT EXISTS lab_runs (id INTEGER PRIMARY KEY, patient_id TEXT, cutoff INTEGER, revision TEXT, settings TEXT, result TEXT, created_at TEXT)")
    fields={r[1] for r in db.execute('PRAGMA table_info(measurements)')}
    for name,definition in [('observed_minute','INTEGER'),('quality',"TEXT NOT NULL DEFAULT 'valid'"),('noise_sd','REAL'),('supersedes','INTEGER'),('correction_reason','TEXT'),('archived','INTEGER NOT NULL DEFAULT 0')]:
        if name not in fields:db.execute(f'ALTER TABLE measurements ADD COLUMN {name} {definition}')
    db.execute('CREATE TABLE IF NOT EXISTS acquisitions (id INTEGER PRIMARY KEY, patient_id TEXT, request_cutoff INTEGER, available_minute INTEGER, channel TEXT, status TEXT, failure_probability REAL, burden REAL, measurement_id INTEGER, active INTEGER DEFAULT 1, created_at TEXT)')
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS active_acquisition ON acquisitions(patient_id,request_cutoff,available_minute,channel) WHERE active=1')
    db.commit()
    return db


def require_patient(pid):
    if pid not in PATIENTS:
        raise HTTPException(404, "Patient not found")


@app.get("/api/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION, "data_mode": "synthetic"}


@app.get('/api/demo-example')
@lru_cache(maxsize=1)
def demo_example():
    # A read-only BP-only example for the introduction, independent of acquired
    # workspace evidence. No experiment or audit row is written by a page view.
    return analyze('RNL-014',90,650,'constant',list(CHANNELS),[])


PROJECT_DOCUMENTS={
    'architecture-pdf':('Architecture with adaptive evidence planning','output/pdf/RENALIS_Architecture_v05.pdf','PDF','application/pdf'),
    'architecture-pptx':('Editable submission architecture','output/presentations/RENALIS_Architecture_v05_Release_Final.pptx','PPTX','application/vnd.openxmlformats-officedocument.presentationml.presentation'),
    'presentation-pdf':('Submission presentation and actual outcomes','output/pdf/RENALIS_Project_Presentation_v05.pdf','PDF','application/pdf'),
    'presentation-pptx':('Editable submission presentation','output/presentations/RENALIS_Project_Presentation_v05_Release_Final.pptx','PPTX','application/vnd.openxmlformats-officedocument.presentationml.presentation'),
    'implementation-decisions':('Implementation decisions and reasons','docs/implementation-decisions-v04.md','Markdown','text/markdown'),
    'submission-checklist':('Submission and release checklist','docs/submission-checklist.md','Markdown','text/markdown'),
    'master-report':('Research, decisions and master plan','output/pdf/RENALIS_Research_Strategy_and_Master_Plan.pdf','PDF','application/pdf'),
    'release-plan':('Release 0.4 implementation and evidence ledger','docs/release-v04.md','Markdown','text/markdown'),
    'clinical-protocol':('Proposed clinical and human-factors protocol','docs/clinical-study-protocol.md','Markdown','text/markdown'),
    'observed-v04':('Audited observed-data evaluation 0.4','docs/observed-v04.json','JSON','application/json'),
    'policy-v04':('Independent policy validation 0.4','docs/policy-validation-v04.json','JSON','application/json'),
    'project-guide':('RENALIS project guide','docs/project-guide.md','Markdown','text/markdown'),
    'research-review':('Evidence review and validation protocol','docs/research-review-2026-10.md','Markdown','text/markdown'),
    'execution-plan':('Requirements, execution plan, and 20-minute storyboard','docs/execution-and-validation-plan.md','Markdown','text/markdown'),
    'walkthrough':('Click-by-click demonstration walkthrough 0.4','docs/demo-walkthrough-v04.md','Markdown','text/markdown'),
    'model-card':('Model card and scientific boundaries','docs/model-card.md','Markdown','text/markdown'),
    'architecture':('Architecture and data provenance','public/renalis-architecture.svg','SVG','image/svg+xml'),
    'challenge-results':('Every scored independent challenge case','docs/originality-challenges.json','JSON','application/json'),
    'observed-results':('Observed HEMOBP baseline results','docs/observed-baseline.json','JSON','application/json'),
    'license':('MIT code license','LICENSE','Text','text/plain'),
}


@app.get('/api/project-documents')
def project_documents():
    return [{'id':key,'title':title,'format':kind,'bytes':(ROOT/path).stat().st_size,'url':f'/api/project-documents/{key}'}
            for key,(title,path,kind,mime) in PROJECT_DOCUMENTS.items() if (ROOT/path).is_file()]


@app.get('/api/project-documents/{document_id}')
def project_document(document_id: str):
    if document_id not in PROJECT_DOCUMENTS:
        raise HTTPException(404,'Project document not found')
    title,path,kind,mime=PROJECT_DOCUMENTS[document_id]
    target=ROOT/path
    if not target.is_file():
        raise HTTPException(404,'Project document is not available in this installation')
    return FileResponse(target,media_type=mime,headers={'X-Content-Type-Options':'nosniff'})


@app.get("/api/patients")
def patients(cutoff: int = Query(90, ge=0, le=240)):
    return patient_list(cutoff)


@app.get("/api/patients/{pid}/twin")
def twin(pid: str, cutoff: int = Query(90, ge=0, le=240)):
    require_patient(pid)
    return snapshot(pid, cutoff)


class ScenarioInput(BaseModel):
    cutoff: int = Field(ge=0, le=240)
    rate_ml_h: int = Field(ge=300, le=1400)
    profile: Literal["constant", "step_down"] = "constant"


@app.post("/api/patients/{pid}/scenario")
def compare(pid: str, body: ScenarioInput):
    require_patient(pid)
    if snapshot(pid, body.cutoff)["alert"]["status"] in ("insufficient", "complete", "current_event"):
        raise HTTPException(409, "Scenario comparison requires fresh BP, an active session, and no current low-BP event")
    return scenario(pid, body.cutoff, body.rate_ml_h, body.profile)


@app.post("/api/patients/{pid}/branches")
def save_branch(pid: str, body: ScenarioInput):
    require_patient(pid)
    if snapshot(pid, body.cutoff)["alert"]["status"] in ("insufficient", "complete", "current_event"):
        raise HTTPException(409, "Cannot save a ranked scenario with stale BP, a current low-BP event, or a completed session")
    result = scenario(pid, body.cutoff, body.rate_ml_h, body.profile)
    with connection() as db:
        cursor = db.execute("INSERT INTO branches (patient_id,cutoff,rate,profile,result,created_at) VALUES (?,?,?,?,?,?)",
                            (pid, body.cutoff, body.rate_ml_h, body.profile, json.dumps(result), datetime.now(timezone.utc).isoformat()))
        return {"id": cursor.lastrowid, "result": result}


@app.get("/api/patients/{pid}/branches")
def branches(pid: str):
    require_patient(pid)
    with connection() as db:
        return [dict(row) for row in db.execute("SELECT id,patient_id,cutoff,rate,profile,created_at FROM branches WHERE patient_id=? ORDER BY id DESC LIMIT 20", (pid,))]


@app.get("/api/patients/{pid}/outcome")
def outcome(pid: str, cutoff: int = Query(90, ge=0, le=240)):
    require_patient(pid)
    return revealed_outcome(pid, cutoff)


class ReviewInput(BaseModel):
    cutoff: int = Field(ge=0, le=240)
    note: str = Field(min_length=1, max_length=2000)


@app.post("/api/patients/{pid}/reviews")
def add_review(pid: str, body: ReviewInput):
    require_patient(pid)
    if not body.note.strip():
        raise HTTPException(422, "Review note cannot be blank")
    with connection() as db:
        cursor = db.execute("INSERT INTO reviews (patient_id,cutoff,note,created_at) VALUES (?,?,?,?)",
                            (pid, body.cutoff, body.note.strip(), datetime.now(timezone.utc).isoformat()))
        return {"id": cursor.lastrowid, "status": "recorded"}


@app.get("/api/patients/{pid}/reviews")
def reviews(pid: str):
    require_patient(pid)
    with connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM reviews WHERE patient_id=? ORDER BY id DESC LIMIT 30", (pid,))]


@lru_cache(maxsize=1)
def cached_evaluation():
    return evaluation()


@app.get("/api/evaluation")
def benchmark():
    return cached_evaluation()


@app.get("/api/model-card")
def model_card():
    return {"version": MODEL_VERSION, "population": "Four fictional maintenance-hemodialysis patients",
            "inputs": ["Historical baseline and refill priors", "Patient/session fluid target", "Past valid systolic BP", "Past/current ultrafiltration rate"],
            "method": "Patient twin: 192-particle Bayesian state estimator + conservative two-compartment fluid model. Mechanism lab: 192 compatibility particles across four research families, observation-value quadrature, and contradiction checks.",
            "mechanism_lab": {"version":LAB_VERSION,"optional_channels":["Repeat cuff BP","Relative blood volume","Noninvasive cardiac output"],"weights":"Conditional model compatibility, not diagnostic probabilities","evaluation":"Frozen 108-case diagnostic plus a new 192-case mixed/omitted/failed-acquisition study; superiority is not established"},
            "event": "New systolic BP ≤90 mmHg within a 30-minute forecast",
            "clinical_use": "Not validated for clinical use or autonomous treatment control",
            "data": "Synthetic EHR and device streams. HEMOBP adapter is separate and has not fitted this model.",
            "exclusions": ["Future BP and machine changes are not available to the estimator.", "Already hypotensive states do not produce advance alerts.", "BP older than 15 minutes withholds the event alert.", "Artifact readings are excluded."],
            "references": [{"title": "HEMOBP dataset", "url": "https://figshare.com/articles/dataset/Hemrec_VIP_csv/6260654/3"},
                           {"title": "HEMOBP data publication", "url": "https://www.nature.com/articles/s41597-019-0319-8"},
                           {"title": "Monitoring in Dialysis study", "url": "https://pubmed.ncbi.nlm.nih.gov/32381584/"}]}


@app.get("/api/observed-evaluation")
def observed_evaluation():
    path = ROOT / "data" / "models" / "hemo_metrics.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "status": "not_run", "message": "Run the HEMOBP audit and baseline pipeline to evaluate observed data."}


@app.get('/api/originality-evaluation')
def originality_evaluation():
    # Historical negative results are frozen, not silently recomputed with a new engine.
    return json.loads((ROOT/'docs/originality-challenges.json').read_text(encoding='utf-8'))


class LabInput(ScenarioInput):
    channels: list[Literal['repeat_bp','relative_blood_volume','cardiac_output']] = ['repeat_bp','relative_blood_volume','cardiac_output']
    net_gain_ml: int = Field(1200,ge=0,le=4000)
    burden_weight: float = Field(.5,ge=0,le=3)
    noise_multiplier: float = Field(1.,ge=1,le=4)
    failure_probability: float = Field(0.,ge=0,le=1)
    latency_minutes: Literal[0,5,10] = 0
    equipment: Literal['custom','basic','equipped','research'] = 'custom'


def released_evidence(pid,cutoff):
    with connection() as db:
        return evidence_rows(db,pid,cutoff)


def evidence_rows(db,pid,cutoff):
    return [dict(row) for row in db.execute('''SELECT m.id,m.available_minute,COALESCE(m.observed_minute,m.available_minute) AS observed_minute,m.channel,m.value,m.unit,m.source,m.quality,m.noise_sd,m.supersedes,m.correction_reason
      FROM measurements m WHERE m.patient_id=? AND m.archived=0 AND m.available_minute<=?
      AND NOT EXISTS(SELECT 1 FROM measurements n WHERE n.supersedes=m.id AND n.archived=0 AND n.available_minute<=?)
      ORDER BY m.available_minute,m.id''',(pid,cutoff,cutoff))]


def compute_lab(pid,body):
    require_patient(pid)
    allowed={'basic':['repeat_bp'],'equipped':['repeat_bp','relative_blood_volume'],'research':list(CHANNELS),'custom':list(CHANNELS)}[body.equipment]
    channels=sorted(set(body.channels)&set(allowed))
    result=analyze(pid,body.cutoff,body.rate_ml_h,body.profile,channels,released_evidence(pid,body.cutoff),body.net_gain_ml,body.burden_weight,
        noise_multiplier=body.noise_multiplier,failure_probability=body.failure_probability,latency_minutes=body.latency_minutes)
    result['equipment']=body.equipment
    result['request_settings']={name:getattr(body,name) for name in LabInput.model_fields}
    result['acquisition_log']=acquisition_log(pid,body.cutoff)
    import hashlib
    result['revision']=hashlib.sha256(json.dumps({'engine':result['revision'],'acquisition_log':result['acquisition_log']},sort_keys=True).encode()).hexdigest()[:16]
    return result


@app.post('/api/patients/{pid}/mechanisms')
def mechanisms(pid: str, body: LabInput):
    return compute_lab(pid,body)


class MeasurementInput(LabInput):
    channel: Literal['repeat_bp','relative_blood_volume','cardiac_output']
    offset_minutes: int = Field(0,ge=0,le=30)
    source: Literal['synthetic_device','manual'] = 'synthetic_device'
    value: float | None = None
    observed_minute: int | None = Field(None,ge=0,le=240)
    quality: Literal['valid','artifact'] = 'valid'


@app.post('/api/patients/{pid}/measurements')
def acquire_measurement(pid: str, body: MeasurementInput):
    require_patient(pid)
    if body.channel not in body.channels:
        raise HTTPException(409,'This measurement channel is marked unavailable.')
    allowed={'basic':['repeat_bp'],'equipped':['repeat_bp','relative_blood_volume'],'research':list(CHANNELS),'custom':list(CHANNELS)}[body.equipment]
    if body.channel not in allowed:raise HTTPException(409,'This equipment configuration cannot acquire that channel.')
    available=body.cutoff+body.offset_minutes
    spec=CHANNELS[body.channel]
    if body.source=='manual' and body.value is None:
        raise HTTPException(422,'Provide a value for a manually entered research observation.')
    value=acquire_fixture(pid,available,body.channel) if body.source=='synthetic_device' else body.value
    import math
    if value is None or not math.isfinite(value) or not spec['range'][0]<=value<=spec['range'][1]:
        raise HTTPException(422,f"Value outside the sandbox range for {spec['label']}: {spec['range']} {spec['unit']}")
    with connection() as db:
        existing=db.execute('SELECT * FROM measurements WHERE patient_id=? AND available_minute=? AND channel=? AND active=1',(pid,available,body.channel)).fetchone()
    if existing:
        if body.source=='manual' and abs(existing['value']-value)>1e-9:
            raise HTTPException(409,'A different observation already exists for this channel/time; reset the experiment before replacing it.')
        return {'record':dict(existing),'available_minute':available,'reused':True}
    result=compute_lab(pid,body)
    if result['authority'] != 'inspect':
        raise HTTPException(409,'Measurement experiments are withheld for current low BP, stale observations, model contradiction, or a completed session.')
    valid_candidate=any(c['channel']==body.channel and c['offset_minutes']==body.offset_minutes for c in result['measurement_candidates'])
    if not valid_candidate:
        raise HTTPException(409,'This measurement time is outside the active horizon or would wait past modeled instability.')
    observed=available if body.observed_minute is None else body.observed_minute
    if observed>available:raise HTTPException(422,'Observation time cannot follow its availability time.')
    with connection() as db:
        # Repeated clicks reuse the same observation rather than count it as new evidence.
        db.execute('BEGIN IMMEDIATE')
        request=db.execute('SELECT * FROM acquisitions WHERE patient_id=? AND request_cutoff=? AND available_minute=? AND channel=? AND active=1',(pid,body.cutoff,available,body.channel)).fetchone()
        if request and request['status']=='failed' and body.source=='synthetic_device':
            return {'record':dict(request),'available_minute':available,'status':'failed','reused':True}
        if request and request['status']=='failed' and body.source=='manual':
            # A separately obtained manual reading can follow a failed device
            # request. Retain its burden/audit row while freeing the active slot.
            db.execute('UPDATE acquisitions SET active=0 WHERE id=?',(request['id'],))
        existing=db.execute('SELECT * FROM measurements WHERE patient_id=? AND available_minute=? AND channel=? AND active=1',(pid,available,body.channel)).fetchone()
        if existing:
            if body.source=='manual' and abs(existing['value']-value)>1e-9:
                raise HTTPException(409,'A different observation already exists for this channel/time; reset the experiment before replacing it.')
            return {'record':dict(existing),'available_minute':available,'reused':True}
        import hashlib
        draw=int.from_bytes(hashlib.sha256(f'{pid}:{body.cutoff}:{available}:{body.channel}'.encode()).digest()[:4],'big')/2**32
        failed=body.source=='synthetic_device' and draw<body.failure_probability
        now=datetime.now(timezone.utc).isoformat()
        if failed:
            cursor=db.execute('INSERT INTO acquisitions (patient_id,request_cutoff,available_minute,channel,status,failure_probability,burden,created_at) VALUES (?,?,?,?,?,?,?,?)',
                (pid,body.cutoff,available,body.channel,'failed',body.failure_probability,spec['cost']*body.burden_weight,now))
            return {'record':dict(db.execute('SELECT * FROM acquisitions WHERE id=?',(cursor.lastrowid,)).fetchone()),'available_minute':available,'status':'failed','reused':False}
        cursor=db.execute('INSERT INTO measurements (patient_id,request_cutoff,observed_minute,available_minute,channel,value,unit,source,quality,noise_sd,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (pid,body.cutoff,observed,available,body.channel,value,spec['unit'],body.source,body.quality,spec['noise']*body.noise_multiplier,now))
        record=dict(db.execute('SELECT * FROM measurements WHERE id=?',(cursor.lastrowid,)).fetchone())
        db.execute('INSERT INTO acquisitions (patient_id,request_cutoff,available_minute,channel,status,failure_probability,burden,measurement_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
            (pid,body.cutoff,available,body.channel,'artifact' if body.quality=='artifact' else 'success',body.failure_probability,spec['cost']*body.burden_weight,record['id'],now))
    return {'record':record,'available_minute':available,'status':'success','reused':False}


@app.post('/api/patients/{pid}/measurements/reset')
def reset_measurements(pid: str):
    require_patient(pid)
    with connection() as db:
        cursor=db.execute('UPDATE measurements SET active=0,archived=1 WHERE patient_id=? AND archived=0',(pid,))
        count=cursor.rowcount
        db.execute('UPDATE acquisitions SET active=0 WHERE patient_id=? AND active=1',(pid,))
    return {'archived':count,'retained_for_audit':True}


class SaveLabInput(LabInput):
    expected_revision: str = Field(min_length=16,max_length=16)
    capture_kind: Literal['mechanism','investigation'] = 'mechanism'


@app.post('/api/patients/{pid}/lab-runs')
def save_lab(pid: str,body: SaveLabInput):
    result=investigation(pid,body) if body.capture_kind=='investigation' else compute_lab(pid,body)
    if body.expected_revision!=result['revision']:
        raise HTTPException(409,'The evidence changed. Refresh the comparison before saving this run.')
    with connection() as db:
        db.execute('BEGIN IMMEDIATE')
        active_ids=[r['id'] for r in evidence_rows(db,pid,body.cutoff) if r['quality']=='valid']
        if active_ids!=[e['id'] for e in result['evidence']]:
            raise HTTPException(409,'The evidence changed while saving. Refresh the comparison before saving this run.')
        request_ids=[r[0] for r in db.execute('SELECT id FROM acquisitions WHERE patient_id=? AND request_cutoff<=? ORDER BY id',(pid,body.cutoff))]
        if request_ids!=[r['id'] for r in result['acquisition_log']]:
            raise HTTPException(409,'The acquisition ledger changed while saving. Refresh the comparison.')
        cursor=db.execute('INSERT INTO lab_runs (patient_id,cutoff,revision,settings,result,created_at) VALUES (?,?,?,?,?,?)',
            (pid,body.cutoff,result['revision'],body.model_dump_json(exclude={'expected_revision'}),json.dumps(result),datetime.now(timezone.utc).isoformat()))
    return {'id':cursor.lastrowid,'revision':result['revision']}


@app.get('/api/patients/{pid}/lab-runs')
def lab_runs(pid: str):
    require_patient(pid)
    with connection() as db:
        return [dict(row) for row in db.execute('SELECT id,cutoff,revision,settings,created_at FROM lab_runs WHERE patient_id=? ORDER BY id DESC LIMIT 20',(pid,))]


@app.get('/api/patients/{pid}/lab-runs/{run_id}')
def lab_run(pid: str,run_id: int):
    require_patient(pid)
    with connection() as db:
        row=db.execute('SELECT * FROM lab_runs WHERE id=? AND patient_id=?',(run_id,pid)).fetchone()
    if row is None:
        raise HTTPException(404,'Saved comparison not found for this patient.')
    record=dict(row)
    record['settings']=json.loads(record['settings'])
    record['result']=json.loads(record['result'])
    return record


def acquisition_log(pid,cutoff):
    with connection() as db:
        rows=[dict(r) for r in db.execute('SELECT a.*,m.value,m.unit,m.observed_minute,m.quality FROM acquisitions a LEFT JOIN measurements m ON m.id=a.measurement_id WHERE a.patient_id=? AND a.request_cutoff<=? ORDER BY a.id',(pid,cutoff))]
    for row in rows:
        if row['available_minute']>cutoff:
            row.update(status='pending',value=None,observed_minute=None,quality=None)
    return rows


@app.post('/api/patients/{pid}/investigation')
def investigation(pid: str,body: LabInput):
    from .history import patient_history,ablation
    from .insights import explain
    from .discrimination import plan
    from .mechanisms import base_cloud,assimilate,project,decision_losses
    result=compute_lab(pid,body)
    cloud=base_cloud(pid,body.cutoff);weights,_=assimilate(cloud,released_evidence(pid,body.cutoff))
    rates=sorted(set([350,500,650,800,950,1100,1250,1400,body.rate_ml_h,cloud.current_rate]))
    losses=__import__('numpy').column_stack([decision_losses(project(cloud,r,delay_minutes=body.latency_minutes),cloud.removed_ml,PATIENTS[pid].target_ml) for r in rates])
    result['counterevidence']=explain(cloud,weights,losses,body.noise_multiplier,rates,body.cutoff+body.latency_minutes) if result['authority']=='inspect' else []
    result['discrimination_plan']=plan(cloud,weights,result,body.failure_probability)
    result['historical_learning']=patient_history(pid)
    result['history_ablation']=ablation(pid)
    valid=[r for r in cloud.history if r['sbp'] is not None and r['quality']=='valid']
    earlier=[r for r in valid[:-1] if r['sbp']<=90]
    result['event_context']={'current_low_bp':valid[-1]['sbp']<=90,'prior_low_readings':len(earlier),
        'task':'recurrent-event context' if earlier else 'no earlier measured low BP',
        'endpoint':'Future model SBP <=90 over up to 30 minutes; retrospective next-reading benchmark is separate',
        'symptoms':'Record symptoms in review notes; this numeric research endpoint is not a complete clinical assessment.'}
    result['state']={'plasma_l':round(float(weights@cloud.plasma_history[-1]),3),
        'tissue_l':round(float(weights@cloud.tissue_history[-1]),3),'refill_l_h':round(float(weights@cloud.refill),3),
        'removed_ml':cloud.removed_ml,'source':'Weighted Mechanism lab state at the shared cutoff'}
    return result


class CorrectionInput(BaseModel):
    cutoff:int=Field(ge=0,le=240)
    value:float=Field(allow_inf_nan=False)
    reason:str=Field(min_length=3,max_length=500)


@app.post('/api/patients/{pid}/measurements/{measurement_id}/corrections')
def correct_measurement(pid:str,measurement_id:int,body:CorrectionInput):
    require_patient(pid)
    if not body.reason.strip():raise HTTPException(422,'A correction reason is required.')
    with connection() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT * FROM measurements WHERE id=? AND patient_id=? AND active=1',(measurement_id,pid)).fetchone()
        if row is None:raise HTTPException(404,'Active observation not found for this patient.')
        if body.cutoff<row['available_minute']:raise HTTPException(409,'A future observation cannot be corrected before it is available.')
        if not CHANNELS[row['channel']]['range'][0]<=body.value<=CHANNELS[row['channel']]['range'][1]:raise HTTPException(422,'Correction outside the declared channel range.')
        other=db.execute('SELECT id FROM measurements WHERE patient_id=? AND channel=? AND available_minute=? AND active=1 AND id<>?',(pid,row['channel'],body.cutoff,measurement_id)).fetchone()
        if other:raise HTTPException(409,'A reading already exists at the correction availability time.')
        db.execute('UPDATE measurements SET active=0 WHERE id=?',(measurement_id,))
        cursor=db.execute('INSERT INTO measurements (patient_id,request_cutoff,observed_minute,available_minute,channel,value,unit,source,quality,noise_sd,supersedes,correction_reason,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (pid,body.cutoff,row['observed_minute'] if row['observed_minute'] is not None else row['available_minute'],body.cutoff,row['channel'],body.value,row['unit'],'manual correction','valid',row['noise_sd'],measurement_id,body.reason.strip(),datetime.now(timezone.utc).isoformat()))
        return {'id':cursor.lastrowid,'supersedes':measurement_id,'available_minute':body.cutoff,'original_retained':True}


@app.get('/api/release-evaluation')
def release_evaluation():
    paths={'observed':'docs/observed-v04.json','policy':'docs/policy-validation-v04.json'}
    return {key:json.loads((ROOT/path).read_text(encoding='utf-8')) if (ROOT/path).exists() else {'status':'not_run'} for key,path in paths.items()}


class LongitudinalInput(LabInput):
    profile: Literal['constant'] = 'constant'
    interval_hours:int=Field(48,ge=12,le=96)
    intake_ml:int=Field(2400,ge=0,le=6000)
    residual_ml:int=Field(800,ge=0,le=4000)
    cycles:int=Field(3,ge=1,le=4)


@app.post('/api/patients/{pid}/longitudinal')
def longitudinal(pid:str,body:LongitudinalInput):
    from .longitudinal import simulate
    if compute_lab(pid,body)['authority']!='inspect':raise HTTPException(409,'Conditional future transport is withheld for this observation state.')
    return simulate(pid,body.cutoff,body.rate_ml_h,body.interval_hours,body.intake_ml,body.residual_ml,body.cycles,released_evidence(pid,body.cutoff))


@app.get('/api/patients/{pid}/fhir')
def fhir_example(pid:str,cutoff:int=Query(90,ge=0,le=240)):
    from datetime import timedelta
    require_patient(pid);s=snapshot(pid,cutoff);p=PATIENTS[pid]
    start=datetime.fromisoformat('2026-10-17T08:00:00+05:30')
    instant=(start+timedelta(minutes=s['latest']['minute'])).isoformat()
    patient={'resourceType':'Patient','id':pid,'active':True,'name':[{'text':p.name}],'gender':'female' if p.sex=='F' else 'male'}
    device={'resourceType':'Device','id':'synthetic-cuff','status':'active','deviceName':[{'name':'RENALIS fictional cuff replay','type':'user-friendly-name'}]}
    observation={'resourceType':'Observation','id':f'{pid}-sbp-{s["latest"]["minute"]}','status':'final',
        'code':{'coding':[{'system':'http://loinc.org','code':'8480-6','display':'Systolic blood pressure'}]},
        'subject':{'reference':f'Patient/{pid}'},'device':{'reference':'Device/synthetic-cuff'},
        'effectiveDateTime':instant,'issued':instant,
        'valueQuantity':{'value':s['latest']['sbp'],'unit':'mmHg','system':'http://unitsofmeasure.org','code':'mm[Hg]'},
        'note':[{'text':'Fictional patient and synthetic observation. Structural FHIR R4 example only; ABDM profile conformance and integration are not established.'}]}
    return {'resourceType':'Bundle','type':'collection','timestamp':(start+timedelta(minutes=cutoff)).isoformat(),
        'entry':[{'fullUrl':f'https://example.org/renalis/{r["resourceType"]}/{r["id"]}','resource':r} for r in [patient,device,observation]]}
