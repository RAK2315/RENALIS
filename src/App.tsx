import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { Activity, ArrowDown, ArrowLeftRight, ArrowRight, ArrowUpRight, BookOpen, Check, CheckCheck, ChevronDown, ChevronRight, CircleHelp, Clock3, Database, Download, Droplets, FlaskConical, GitBranch, History, LayoutGrid, LoaderCircle, Pause, Play, Plus, RotateCcw, ShieldCheck, SlidersHorizontal, Sparkles, Stethoscope, X } from 'lucide-react';
import { api } from './api';
import ForecastAlert from './ForecastAlert';
import { AlarmDots } from './Figures';
import GuidedTour, { tourSteps } from './GuidedTour';
import type { WorkspacePage } from './Experience';
import type { Twin, Scenario, PatientSummary, Review, Branch, Outcome, Evaluation, ModelCard, ObservedV04, Status } from './types';
import { modelName } from './plain';
import { HealthRecordCard } from './HealthRecord';
import { WarningsInContext, currentWarning, type Warnings } from './RealDataFindings';

type Page = WorkspacePage;
const Trajectory = lazy(() => import('./Trajectory'));
const MechanismLab = lazy(() => import('./MechanismLab'));
const EvidenceJourney = lazy(() => import('./EvidenceJourney'));
const statusText: Record<Status, string> = { monitor: 'Stable', review: 'Drop likely soon', insufficient: 'Needs a fresh reading', current_event: 'BP already low', complete: 'Session finished' };
const format = (n: number) => Math.round(n).toLocaleString('en-IN');
const pages = [{id:'investigation' as Page,title:'Step-by-step story',icon:GitBranch},{ id: 'cockpit' as Page, title: 'Patient twin', icon: Activity }, { id: 'mechanisms' as Page, title: 'Mechanism lab', icon: Sparkles }, { id: 'unit' as Page, title: 'All patients', icon: LayoutGrid }, { id: 'history' as Page, title: 'Past sessions', icon: History }, { id: 'evidence' as Page, title: 'How we tested it', icon: FlaskConical }];
const pageCopy: Record<Page, [string, string, string]> = {
  investigation: ['THE FULL STORY, ONE STEP AT A TIME', 'Why is her blood pressure falling?', 'Follow one patient from her past sessions to the next useful check. Scroll down, or use the guided demo.'],
  cockpit: ['LIVE VIEW OF ONE PATIENT', 'Before the pressure falls.', 'Where the water is right now, and what blood pressure is likely to do in the next 30 minutes.'],
  mechanisms: ['MECHANISM LAB', 'Test the four causes yourself.', 'Change the machine setting, take extra measurements, and watch which cause pulls ahead.'],
  unit: ['THE WHOLE WARD', 'Every patient at a glance.', 'Four made-up patients on the same clock, each reacting differently to dialysis.'],
  history: ['WHAT THE TWIN REMEMBERS', 'Learning from earlier sessions.', 'Previous sessions, saved “what if” scenarios, and review notes.'],
  evidence: ['HOW WE TESTED IT', 'How much should you trust it?', 'What the model is, what data it uses, and how accurate it was in testing.'],
};

function FluidVessel({ label, value, fraction, kind }: { label: string; value: string; fraction: number; kind: string }) {
  return <div className={`fluid-compartment ${kind}`}><div className="vessel"><div className="vessel-rim" /><div className="fluid" style={{ height: `${Math.max(8, Math.min(92, fraction * 100))}%` }} /><div className="glass-reflection" /><div className="vessel-graduations"><span /><span /><span /></div></div><strong>{value}</strong><span>{label}</span></div>;
}

function SmallTrace({ stable }: { stable: boolean }) {
  return <svg viewBox="0 0 160 50" role="img" aria-label={stable ? 'Stable illustrative trace' : 'Declining illustrative trace'}><path d={stable ? 'M0 28 L20 22 L40 25 L60 18 L80 23 L100 19 L120 26 L140 22 L160 24' : 'M0 9 L20 13 L40 14 L60 20 L80 25 L100 29 L120 35 L140 39 L160 44'} fill="none" stroke="currentColor" strokeWidth="2" /></svg>;
}

export default function App({initialPage='cockpit',initialPatient='RNL-014',initialMinute=90,startTour=false,initialTourStep=0,onHome,onResearch}:{initialPage?:WorkspacePage;initialPatient?:string;initialMinute?:number;startTour?:boolean;initialTourStep?:number;onHome:()=>void;onResearch:()=>void}) {
  const [page, setPage] = useState<Page>(startTour?tourSteps[initialTourStep].page:initialPage);
  const [patientId, setPatientId] = useState(startTour?'RNL-014':initialPatient);
  const [cutoff, setCutoff] = useState(startTour?90:initialMinute);
  const [tourOpen,setTourOpen]=useState(startTour);
  const [tourStep,setTourStep]=useState(initialTourStep);
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [twin, setTwin] = useState<Twin | null>(null);
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [rate, setRate] = useState(650);
  const [profile, setProfile] = useState('constant');
  const [playing, setPlaying] = useState(false);
  const [busy, setBusy] = useState(true);
  const [scenarioBusy, setScenarioBusy] = useState(false);
  const [error, setError] = useState('');
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [modelCard, setModelCard] = useState<ModelCard | null>(null);
  const [observed, setObserved] = useState<ObservedV04 | null>(null);
  const [warnings, setWarnings] = useState<Warnings | undefined>();
  const [toast, setToast] = useState('');
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(()=>{const params=new URLSearchParams({view:page,patient:patientId,minute:String(cutoff)});if(tourOpen){params.set('tour','1');params.set('step',String(tourStep));}window.history.replaceState(null,'',`/workspace?${params}`);},[page,patientId,cutoff,tourOpen,tourStep]);
  function goTour(step:number){setPlaying(false);setPatientId('RNL-014');setCutoff(80);setPage(tourSteps[step].page);setTourStep(step);setTourOpen(true);}
  function showTourArea(){(document.querySelector(tourSteps[tourStep].selector)??document.querySelector('.page-heading'))?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});}

  useEffect(() => {
    const controller = new AbortController();
    setBusy(true); setError(''); setOutcome(null); setScenario(null);
    Promise.all([api<Twin>(`/patients/${patientId}/twin?cutoff=${cutoff}`, { signal: controller.signal }), api<PatientSummary[]>(`/patients?cutoff=${cutoff}`, { signal: controller.signal })])
      .then(([value, list]) => { setTwin(value); setPatients(list); })
      .catch(e => { if (e.name !== 'AbortError') setError(e.message); })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [patientId, cutoff]);

  useEffect(() => {
    if (!twin || twin.cutoff !== cutoff || twin.patient.id !== patientId || twin.alert.status === 'insufficient' || twin.alert.status === 'complete' || twin.alert.status === 'current_event') { setScenario(null); setScenarioBusy(false); return; }
    const controller = new AbortController(); setScenarioBusy(true);
    const timer = setTimeout(() => {
      api<Scenario>(`/patients/${patientId}/scenario`, { method: 'POST', body: JSON.stringify({ cutoff, rate_ml_h: rate, profile }), signal: controller.signal })
        .then(setScenario).catch(e => { if (e.name !== 'AbortError') setError(e.message); })
        .finally(() => { if (!controller.signal.aborted) setScenarioBusy(false); });
    }, 180);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [twin, cutoff, patientId, rate, profile]);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([api<Review[]>(`/patients/${patientId}/reviews`, { signal: controller.signal }), api<Branch[]>(`/patients/${patientId}/branches`, { signal: controller.signal })])
      .then(([r, b]) => { setReviews(r); setBranches(b); }).catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => controller.abort();
  }, [patientId]);

  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(() => setCutoff(value => { if (value >= 235) { setPlaying(false); return 240; } return value + 5; }), 1800);
    return () => clearInterval(timer);
  }, [playing]);
  useEffect(() => { if (!toast) return; const timer = setTimeout(() => setToast(''), 4000); return () => clearTimeout(timer); }, [toast]);
  useEffect(() => {
    if (page !== 'evidence' || evaluation) return;
    const controller = new AbortController();
    Promise.all([api<Evaluation>('/evaluation', { signal: controller.signal }), api<ModelCard>('/model-card', { signal: controller.signal })])
      .then(([e, m]) => { setEvaluation(e); setModelCard(m); }).catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => controller.abort();
  }, [page, evaluation]);
  useEffect(() => {
    if (page !== 'evidence') return;
    const controller = new AbortController();
    api<{ observed: ObservedV04; warnings?: Warnings }>('/release-evaluation', { signal: controller.signal }).then(r => { setObserved(r.observed); setWarnings(r.warnings); })
      .catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => controller.abort();
  }, [page]);

  async function refreshRecords() {
    const [r, b] = await Promise.all([api<Review[]>(`/patients/${patientId}/reviews`), api<Branch[]>(`/patients/${patientId}/branches`)]);
    setReviews(r); setBranches(b);
  }
  async function saveBranch() {
    setSaving(true);
    try { await api(`/patients/${patientId}/branches`, { method: 'POST', body: JSON.stringify({ cutoff, rate_ml_h: rate, profile }) }); await refreshRecords(); setToast('Scenario saved with its patient state and prediction cutoff.'); }
    catch (e) { setError((e as Error).message); } finally { setSaving(false); }
  }
  async function saveReview(event: React.FormEvent) {
    event.preventDefault(); setSaving(true);
    try { await api(`/patients/${patientId}/reviews`, { method: 'POST', body: JSON.stringify({ cutoff, note }) }); await refreshRecords(); dialog.current?.close(); setNote(''); setToast('Review note saved locally.'); }
    catch (e) { setError((e as Error).message); } finally { setSaving(false); }
  }
  async function reveal() {
    try { setPlaying(false); setOutcome(await api<Outcome>(`/patients/${patientId}/outcome?cutoff=${cutoff}`)); }
    catch (e) { setError((e as Error).message); }
  }
  function exportSnapshot() {
    if (!twin || busy) return;
    const blob = new Blob([JSON.stringify({ title: 'RENALIS research snapshot', twin, scenario, reviews, provenance: 'Synthetic research sandbox; not a clinical record', exported_at: new Date().toISOString() }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url; link.download = `renalis-${patientId}-minute-${cutoff}.json`; link.click(); URL.revokeObjectURL(url); setToast('Research snapshot exported.');
  }
  const ready = twin && twin.cutoff === cutoff && twin.patient.id === patientId;
  const insufficient = twin?.alert.status === 'insufficient';
  const complete = twin?.alert.status === 'complete';
  const currentEvent=twin?.alert.status==='current_event';
  const p = twin?.patient;
  const latestHr = twin ? [...twin.history].reverse().find(r => r.hr != null)?.hr ?? null : null;
  const hrChange = latestHr != null && twin?.history[0]?.hr != null ? latestHr - twin.history[0].hr : null;

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="/" onClick={e => { e.preventDefault(); onHome(); }} aria-label="RENALIS home"><span className="brand-symbol"><Droplets size={21} strokeWidth={1.6} /></span><div>RENALIS<small>Dialysis digital twin</small></div></a>
      <div className="sidebar-label">SCREENS</div>
      <nav aria-label="Workspace navigation">{pages.map(item => <button key={item.id} className={`nav-item ${page === item.id ? 'active' : ''}`} onClick={() => setPage(item.id)} aria-current={page === item.id ? 'page' : undefined}><item.icon size={18} /><span>{item.title}</span>{item.id === 'unit' && <span className="nav-count">{patients.length || 4}</span>}</button>)}</nav>
      <div className="sidebar-divider" /><div className="sidebar-label">CURRENT PATIENT</div>
      <button className="sidebar-patient" onClick={() => setPage('cockpit')}><span className="avatar small">{p?.name.split(' ').map(n => n[0]).join('') || 'MR'}</span><span>{p?.name || 'Meera Rao'}<small>{patientId}</small></span><ChevronRight size={14} /></button>
      <div className="sidebar-bottom"><div className="model-indicator"><span />Research engine <small>v0.4</small></div><button onClick={() => setPage('evidence')} className="help-button"><CircleHelp size={16} /> How it was tested</button><div className="clinician-avatar"><span className="avatar">DR</span><div>Doctor’s view<small>Demo with made-up patients</small></div></div></div>
    </aside>
    <div className="workspace">
      <header className="topbar"><div className="breadcrumbs"><button onClick={onHome}>Overview</button><ChevronRight size={13} /><span>{pages.find(item => item.id === page)?.title}</span></div><div className="topbar-actions"><button className="workspace-guide-link" onClick={onResearch}><BookOpen size={14}/><span>Research guide</span></button><button className="workspace-guide-link" onClick={()=>goTour(0)}><Play size={13}/><span>Guided demo</span></button><button className="sandbox-tag" onClick={() => setPage('evidence')}><FlaskConical size={13} /> <span>Made-up patients · demo</span></button><button className="icon-button" aria-label="Export research snapshot" disabled={!ready || busy} onClick={exportSnapshot}><Download size={17} /></button></div></header>
      <main className="main-content">
        {error && <div className="error-banner" role="alert"><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError('')}><X size={16} /></button></div>}
        <div className="page-heading"><div><div className="eyebrow">{pageCopy[page][0]}</div><h1>{pageCopy[page][1]}</h1><p>{pageCopy[page][2]}</p></div><div className="heading-actions">{page === 'cockpit' && <button className="button light" onClick={() => { setPlaying(false); setNote(''); dialog.current?.showModal(); }} disabled={!ready || busy}><Stethoscope size={15} /> Add a note</button>}<button className="button subtle" onClick={exportSnapshot} disabled={!ready || busy}><Download size={15} /> Export snapshot</button></div></div>
        {tourOpen&&<GuidedTour step={tourStep} onStep={goTour} onClose={()=>setTourOpen(false)} onShow={showTourArea}/>}
        {(page === 'cockpit' || page === 'unit' || page === 'history' || page === 'mechanisms' || page === 'investigation') && <div className="session-toolbar"><div className="patient-select"><label htmlFor="patient">Patient</label><div><span className="avatar small">{p?.name.split(' ').map(n => n[0]).join('') || 'MR'}</span><select id="patient" value={patientId} onChange={e => { setPatientId(e.target.value); setPlaying(false); }}>{(patients.length ? patients : [{ id: 'RNL-014', name: 'Meera Rao' }]).map(v => <option key={v.id} value={v.id}>{v.name} · {v.id}</option>)}</select><ChevronDown size={14} /></div></div><div className="replay-control"><button className="icon-button" onClick={() => setPlaying(!playing)} disabled={cutoff >= 240} aria-label={playing ? 'Pause replay' : 'Play replay'}>{playing ? <Pause size={16} /> : <Play size={16} />}</button><div><label htmlFor="clock">Session time <strong>{cutoff} of 240 min</strong></label><input id="clock" type="range" min={0} max={240} step={5} value={cutoff} onChange={e => { setPlaying(false); setCutoff(Number(e.target.value)); }} /></div><button className="icon-button" onClick={() => { setPlaying(false); setCutoff(0); }} aria-label="Reset replay"><RotateCcw size={15} /></button></div><div className="replay-provenance"><span className={`live-dot ${playing ? 'running' : ''}`} />{playing ? 'Playing the session' : 'Paused'}<small>{busy ? 'Updating twin…' : 'The twin only sees readings up to now'}</small></div></div>}
        {!twin && !error && <div className="loading-state"><LoaderCircle className="spin" size={28} /><h2>Loading the patients</h2><p>Reading past sessions and live machine readings. The free server may take up to a minute to wake up.</p></div>}
        {twin && page === 'cockpit' && <div className={`cockpit ${busy ? 'updating' : ''}`} aria-busy={busy}>
          <div className="primary-column">
            <section className="patient-banner"><div className="patient-identity"><span className="avatar large">{p!.name.split(' ').map(n => n[0]).join('')}</span><div><h2>{p!.name} <span>{p!.age}y · {p!.sex}</span></h2><p>On regular dialysis <span>·</span> {patientId}</p></div></div><span className={`status-badge ${twin.alert.status}`}><span />{statusText[twin.alert.status]}</span><div className="patient-facts"><div><span>Target weight (no extra water)</span><strong>{p!.dry_weight} <small>kg</small></strong></div><div><span>Past sessions</span><strong>{p!.prior_sessions}</strong></div><div><span>Diabetes</span><strong>{p!.diabetes ? 'Yes' : 'No'}</strong></div><div><span>Latest blood pressure</span><strong>{twin.latest.sbp} <small>mmHg</small></strong></div><div><span>Heart rate (smartwatch)</span><strong>{latestHr ?? '–'} <small>bpm</small></strong>{hrChange != null && <small className="fact-note">{hrChange >= 0 ? '+' : ''}{hrChange} since start</small>}</div></div>{p!.record && <HealthRecordCard record={p!.record} />}</section>
            <section className="panel physiology-panel"><div className="panel-heading"><div><div className="eyebrow">WHERE THE WATER IS RIGHT NOW</div><h2>Water moving through the body.</h2></div><span className="quiet-badge">Model estimate, not a scan</span></div><div className="fluid-system"><FluidVessel label="Extra water in tissues" value={`${twin.compartments.tissue_l.toFixed(2)} L`} fraction={twin.compartments.tissue_l / (p!.target_ml / 1000)} kind="tissue" /><div className="fluid-transfer"><div className="flow-line"><ArrowRight size={18} /></div><span>Body refilling the blood</span><strong>{twin.compartments.refill_l_h.toFixed(2)} L/h</strong></div><FluidVessel label="Water in the blood" value={`${twin.compartments.plasma_l.toFixed(2)} L`} fraction={twin.compartments.plasma_l / p!.initial_plasma} kind="circulation" /><div className="fluid-transfer"><div className="flow-line"><ArrowRight size={18} /></div><span>Machine taking water out</span><strong>{(twin.current_machine.uf_ml_h / 1000).toFixed(2)} L/h</strong></div><FluidVessel label="Removed so far" value={`${(twin.compartments.removed_ml / 1000).toFixed(2)} L`} fraction={twin.compartments.removed_ml / p!.target_ml} kind="removed" /></div><div className="physiology-foot"><span><Database size={13} /> Based on past sessions + live BP and machine readings</span><span><Clock3 size={13} /> Last BP reading: {twin.bp_age_minutes} min ago</span></div></section>
            <section className="panel forecast-panel"><div className="panel-heading"><div><div className="eyebrow">BLOOD PRESSURE FORECAST</div><h2>The next 30 minutes.</h2></div><button className="text-button" onClick={outcome ? () => setOutcome(null) : reveal} disabled={busy || complete}>{outcome ? 'Hide what happened' : 'Show what really happened'}<ArrowUpRight size={14} /></button></div>{insufficient && <div className="inline-notice">The last blood pressure reading is too old. The forecast is shown, but warnings are switched off until a fresh reading arrives.</div>}{twin.alert.status === 'current_event' && <div className="inline-notice">Blood pressure is already low, so this is not an early warning any more.</div>}{complete && <div className="inline-notice">The session is over. Nothing left to forecast.</div>}<Suspense fallback={<div className="trajectory loading-state compact">Preparing trajectory…</div>}><Trajectory twin={twin} scenario={scenario} outcome={outcome} /></Suspense><div className="chart-legend"><span><b className="observed" />Measured BP</span><span><b className="current" />Forecast at current machine setting</span>{scenario && <span><b className="alternative" />Forecast at your “what if” setting</span>}{outcome && <span><b className="revealed" />What really happened</span>}<span className="legend-caption">Shaded band: range of likely values</span></div>{outcome && <div className="outcome-note"><CheckCheck size={16} /><span>{outcome.event ? `Blood pressure did fall below 90 at minute ${outcome.first_event_minute}.` : 'Blood pressure stayed above 90.'} The twin never saw these later readings when it made the forecast.</span></div>}</section>
          </div>
          <aside className="scenario-column">
            <ForecastAlert twin={twin} />
            <section className="panel scenario-panel"><div className="panel-heading"><div><div className="eyebrow">TRY A “WHAT IF”</div><h2>What if the machine went slower?</h2></div><SlidersHorizontal size={18} /></div><div className="scenario-input"><label htmlFor="rate">Water removal speed <span>mL per hour</span></label><div className="rate-value">{format(rate)}<span>{scenarioBusy && <LoaderCircle className="spin" size={14} />}</span></div><input id="rate" type="range" min={300} max={1400} step={50} value={rate} disabled={insufficient || complete || currentEvent || busy} onChange={e => setRate(Number(e.target.value))} /><div className="range-labels"><span>300</span><span>1,400</span></div></div><div className="profile-switch" aria-label="Removal profile"><button className={profile === 'constant' ? 'selected' : ''} onClick={() => setProfile('constant')} disabled={insufficient || complete || currentEvent || busy}>Constant</button><button className={profile === 'step_down' ? 'selected' : ''} onClick={() => setProfile('step_down')} disabled={insufficient || complete || currentEvent || busy}>Slow down after 15 min</button></div>{scenario && !currentEvent && <div className="scenario-results"><div><span>Chance BP drops below 90</span><strong>{Math.round(scenario.crossing_fraction * 100)}%</strong></div><div><span>Water removed in next {twin.horizon} min</span><strong>{format(scenario.fluid_removed_next_ml)} <small>mL</small></strong></div><div><span>Water still to remove this session</span><strong>{format(scenario.remaining_target_ml)} <small>mL</small></strong></div><div className="tradeoff-note"><ArrowLeftRight size={15} /><span>{scenario.additional_remaining_ml === 0 ? 'Removes the same amount of water as the current setting.' : `Trade-off: ${format(Math.abs(scenario.additional_remaining_ml))} mL ${scenario.additional_remaining_ml > 0 ? 'more' : 'less'} water left in the body than at the current setting.`}</span></div></div>}{insufficient && <p className="empty-note">Needs a fresh blood pressure reading before comparing settings.</p>}{currentEvent&&<p className="empty-note">Blood pressure is already low, so “what if” comparisons are switched off.</p>}<button className="button primary full" disabled={!scenario || currentEvent || saving || busy || scenarioBusy} onClick={saveBranch}>{saving ? <LoaderCircle className="spin" size={15} /> : <GitBranch size={15} />} Save this scenario</button><p className="scenario-disclaimer">This is a simulation. It does not change any real machine setting.</p></section>
            <section className="evidence-teaser"><ShieldCheck size={19} /><div><h3>How the forecast works.</h3><p>The twin runs {twin.model.particles} slightly different versions of this patient at once. The risk % is the share that end up below 90.</p><button className="text-button" onClick={() => setPage('evidence')}>How we tested it <ArrowRight size={14} /></button><button className="text-button lab-preview-link" onClick={() => { setPlaying(false); setPage('mechanisms'); }}>Compare the four possible causes <ArrowRight size={14} /></button></div></section>
          </aside>
        </div>}
        {twin && page === 'investigation' && <Suspense fallback={<div className="loading-state">Opening the evidence journey…</div>}><EvidenceJourney patientId={patientId} cutoff={cutoff} onAdvance={setCutoff} onPause={()=>setPlaying(false)} onToast={setToast}/></Suspense>}
        {twin && page === 'mechanisms' && <Suspense fallback={<div className="loading-state"><LoaderCircle className="spin" /><p>Loading the mechanism workspace…</p></div>}><MechanismLab patientId={patientId} cutoff={cutoff} onAdvance={setCutoff} onPause={() => setPlaying(false)} onError={setError} onToast={setToast} /></Suspense>}
        {page === 'unit' && <section className="unit-view"><div className="section-summary"><span><span className="live-dot" /> {patients.length} made-up patients on dialysis</span><span>{patients.filter(v => v.status === 'review').length} likely to drop soon · {patients.filter(v => v.status === 'insufficient').length} need a fresh reading</span></div><div className="unit-grid">{patients.map(v => <button className="unit-patient panel" key={v.id} onClick={() => { setPatientId(v.id); setPage('cockpit'); }}><div className="unit-patient-head"><span className="avatar">{v.name.split(' ').map(n => n[0]).join('')}</span><span className={`status-badge ${v.status}`}><span />{statusText[v.status]}</span></div><h2>{v.name}</h2><p>{v.age}y · {v.sex} · {v.id}</p><SmallTrace stable={v.status === 'monitor'} /><span className="trace-label">Typical blood pressure pattern</span><div className="unit-numbers"><div><span>Latest BP</span><strong>{v.sbp}<small> mmHg</small></strong></div><div><span>Water removal</span><strong>{format(v.uf_ml_h)}<small> mL/h</small></strong></div></div><div className="unit-patient-foot"><span>{v.phenotype}</span><ArrowUpRight size={17} /></div></button>)}</div></section>}
        {twin && page === 'history' && <div className="history-layout"><section className="panel history-panel"><div className="panel-heading"><div><div className="eyebrow">PAST HEALTH RECORDS</div><h2>How earlier sessions went.</h2></div><BookOpen size={19} /></div><p className="section-description">The twin learns this patient’s refill speed (how fast her body moves water back into the blood) from these earlier sessions. With only a few sessions, it leans towards the average patient. It never peeks at readings from later in today’s session.</p><div className="table-wrap"><table><thead><tr><th>Session</th><th>Average water removal</th><th>Lowest BP</th><th>Learned refill speed</th></tr></thead><tbody>{twin.sessions.map(s => <tr key={s.session}><td><strong>{s.session}</strong><small>{s.label}</small></td><td>{format(s.mean_uf_ml_h)} mL/h</td><td>{s.min_sbp} mmHg</td><td>{s.refill_estimate_l_h} L/h</td></tr>)}</tbody></table></div><div className="panel-bottom-note"><Database size={13} />Made-up records · {p!.prior_sessions} past sessions on file</div></section><section className="panel"><div className="panel-heading"><h2>Saved “what if” scenarios</h2><GitBranch size={18} /></div>{branches.length === 0 ? <div className="empty-state"><GitBranch size={25} /><h3>No scenarios saved yet.</h3><p>Try a different water removal speed on the Patient twin screen and save it.</p><button className="button light" onClick={() => setPage('cockpit')}>Open workbench <ArrowRight size={14} /></button></div> : <div className="record-list">{branches.map(b => <div key={b.id}><GitBranch size={16} /><div><strong>{format(b.rate)} mL/h · {b.profile === 'constant' ? 'constant' : 'step down'}</strong><small>Scenario #{b.id} · saved at minute {b.cutoff}</small></div><button className="text-button" onClick={() => { setCutoff(b.cutoff); setRate(b.rate); setProfile(b.profile); setPage('cockpit'); setPlaying(false); }}>Restore <ArrowUpRight size={13} /></button></div>)}</div>}</section><section className="panel review-history"><div className="panel-heading"><h2>Doctor’s notes</h2><button className="text-button" onClick={() => { setPlaying(false); setNote(''); dialog.current?.showModal(); }}><Plus size={14} /> Add note</button></div>{reviews.length === 0 ? <p className="section-description">No notes yet. Each note is saved with the patient and the session time.</p> : reviews.map(r => <article className="review-note" key={r.id}><span className="quiet-badge">Session minute {r.cutoff}</span><p>{r.note}</p><small>{new Date(r.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST</small></article>)}</section></div>}
        {page === 'evidence' && <div className="evidence-view"><section className="research-banner"><FlaskConical size={25} /><div><h2>A research prototype, with its limits on show.</h2><p>Everything in the app runs on made-up patients and simulated machine readings. The accuracy numbers below come from tests, not from real clinical use. We tested separately on a real hospital dataset (HEMOBP), shown further down.</p></div></section>{!evaluation || !modelCard ? <div className="loading-state compact"><LoaderCircle className="spin" size={22} /><p>Running the accuracy test…</p></div> : <><div className="evidence-grid"><section className="panel"><div className="panel-heading"><h2>What is inside the twin</h2><Activity size={18} /></div><dl className="model-details"><div><dt>Model</dt><dd>192 slightly different versions of the patient, each with its own refill speed, plus a simple two-tank water model.</dd></div><div><dt>What it predicts</dt><dd>Top blood pressure falling to 90 or below within 30 minutes.</dd></div><div><dt>Data</dt><dd>Made-up patient records and machine readings. The real-data test below uses a separate model.</dd></div><div><dt>Version</dt><dd><code>{modelCard.version}</code></dd></div></dl><h3 className="subheading">What it reads</h3><ul className="check-list">{['Her blood test (albumin) and medicines', 'Her usual blood pressure and refill speed, from past sessions', 'Today’s water removal target', 'Blood pressure readings so far (faulty ones dropped)', 'How fast the machine is removing water, before and now', 'Heart rate from a smartwatch, every 5 minutes'].map(text => <li key={text}><Check size={14} />{text}</li>)}</ul></section><section className="panel"><div className="panel-heading"><h2>Twin vs simpler methods</h2><ArrowDown size={17} /></div><p className="section-description">Average miss of the blood pressure forecast, in mmHg (lower is better). Tested on {evaluation.eligible_windows} moments from the made-up sessions.</p><div className="benchmark-bars">{evaluation.models.map(m => <div key={m.key}><div><span>{({ persistence: 'Repeat the last reading', static: 'Past sessions + machine only', dynamic: 'Average patient + live readings', no_watch: 'RENALIS twin without the smartwatch', fused: 'RENALIS twin (personal)' } as Record<string, string>)[m.key] ?? m.label}</span><strong>{m.mae_mm_hg?.toFixed(2) ?? '—'} <small>mmHg</small></strong></div><div className="benchmark-track"><div className={m.key === 'fused' ? 'fused' : ''} style={{ width: `${((m.mae_mm_hg ?? 0) / Math.max(...evaluation.models.map(v => v.mae_mm_hg ?? 0), 1)) * 100}%` }} /></div></div>)}</div><p className="small-print">Caution: the test patients were made with the same equations the twin uses, so this result is likely too optimistic.</p></section></div><section className="panel"><div className="panel-heading"><h2>Safety checks and limits</h2><ShieldCheck size={18} /></div><div className="limits-columns"><div><h3>Built-in safety checks</h3><ul className="check-list">{['Future readings are never used', 'No early warning when pressure is already low', 'Readings older than 15 minutes pause the warning', 'Faulty readings are ignored'].map(text => <li key={text}><Check size={14} />{text}</li>)}</ul></div><div><h3>What this test cannot prove</h3><ul className="plain-list">{['That it works in a real hospital', 'That it is accurate: the same team made the test patients and the model', 'That the risk % matches real-world odds'].map(text => <li key={text}>{text}</li>)}</ul></div></div></section><section className="panel sources-panel"><div className="panel-heading"><h2>Research papers and datasets we used</h2><Database size={18} /></div>{modelCard.references.map(s => <a key={s.url} href={s.url} target="_blank" rel="noreferrer"><span>{s.title}</span><ArrowUpRight size={17} /></a>)}</section></>}</div>}
        {page === 'evidence' && observed?.status === 'evaluated' && <section className="panel observed-panel"><div className="panel-heading"><div><div className="eyebrow">TESTED ON REAL HOSPITAL DATA</div><h2>Real dialysis records, patients it never saw</h2></div><span className="quiet-badge"><Database size={12} />HEMOBP · Taiwan</span></div><p className="section-description">A public dataset of real dialysis sessions. The model learned from {observed.split.fit_patients} patients, was tuned on {observed.split.calibration_patients} more, and was tested on {observed.split.test_patients} others across {format(observed.test_sessions)} sessions.</p><h3 className="observed-subhead">Predicting the next blood pressure reading</h3><div className="observed-metrics">{observed.models.map(m => <div key={m.label}><span>{modelName[m.label] ?? m.label}</span><strong>{m.mae_mm_hg.toFixed(1)} <small>mmHg average miss</small></strong></div>)}</div><h3 className="observed-subhead">Warning before a drop to 90 or below</h3>{(() => { const w = currentWarning(warnings, observed.event_model)!; return <><div className="observed-metrics"><div><span>Drops it warned about</span><strong>{Math.round(w.sensitivity * 100)}%</strong></div><div><span>Warnings that were right</span><strong>{Math.round(w.ppv * 100)}%</strong></div></div><AlarmDots sensitivity={w.sensitivity} ppv={w.ppv}/></>; })()}<WarningsInContext data={warnings}/><p className="small-print">These are the same results as Step 6 of the step-by-step story.</p><details><summary>Limits of this test</summary><ul className="plain-list">{observed.limitations.map(text => <li key={text}>{text}</li>)}</ul></details><a className="text-button" href="https://figshare.com/articles/dataset/Hemrec_VIP_csv/6260654/3" target="_blank" rel="noreferrer">The dataset (CC BY 4.0) <ArrowUpRight size={14} /></a></section>}
        <footer className="workspace-footer"><span>RENALIS <span>·</span> A digital twin for dialysis</span><span><ShieldCheck size={12} /> Research demo with made-up patients. Not used on real patients.</span></footer>
      </main>
    </div>
    {toast && <div className="toast" role="status"><Check size={17} />{toast}</div>}
    <dialog ref={dialog} className="review-dialog"><form onSubmit={saveReview}><div className="panel-heading"><div><div className="eyebrow">DOCTOR’S NOTE</div><h2>Write a note.</h2></div><button type="button" className="icon-button" aria-label="Close review dialog" onClick={() => dialog.current?.close()}><X size={18} /></button></div><p>{p?.name} · session minute {cutoff}</p><label htmlFor="review-note">Review note</label><textarea id="review-note" value={note} onChange={e => setNote(e.target.value)} maxLength={2000} rows={5} required placeholder="What did you notice? What is still unclear? What should be checked next?" /><p className="small-print">Saved in this demo only. Nothing is sent anywhere and no treatment is changed.</p><button className="button primary full" type="submit" disabled={saving || !note.trim()}>{saving ? <LoaderCircle className="spin" size={15} /> : <Check size={15} />}Save review note</button></form></dialog>
  </div>;
}
