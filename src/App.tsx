import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { Activity, ArrowDown, ArrowLeftRight, ArrowRight, ArrowUpRight, BookOpen, Check, CheckCheck, ChevronDown, ChevronRight, CircleHelp, Clock3, Database, Download, Droplets, FlaskConical, GitBranch, History, LayoutGrid, LoaderCircle, Pause, Play, Plus, RotateCcw, ShieldCheck, SlidersHorizontal, Sparkles, Stethoscope, X } from 'lucide-react';
import { api } from './api';
import ForecastAlert from './ForecastAlert';
import GuidedTour, { tourSteps } from './GuidedTour';
import type { WorkspacePage } from './Experience';
import type { Twin, Scenario, PatientSummary, Review, Branch, Outcome, Evaluation, ModelCard, ObservedEvaluation, Status } from './types';

type Page = WorkspacePage;
const Trajectory = lazy(() => import('./Trajectory'));
const MechanismLab = lazy(() => import('./MechanismLab'));
const EvidenceJourney = lazy(() => import('./EvidenceJourney'));
const statusText: Record<Status, string> = { monitor: 'Monitoring', review: 'Review forecast', insufficient: 'Insufficient data', current_event: 'Current low BP', complete: 'Session complete' };
const format = (n: number) => Math.round(n).toLocaleString('en-IN');
const pages = [{id:'investigation' as Page,title:'Evidence journey',icon:GitBranch},{ id: 'cockpit' as Page, title: 'Patient twin', icon: Activity }, { id: 'mechanisms' as Page, title: 'Mechanism lab', icon: Sparkles }, { id: 'unit' as Page, title: 'Unit overview', icon: LayoutGrid }, { id: 'history' as Page, title: 'Session memory', icon: History }, { id: 'evidence' as Page, title: 'Model & evidence', icon: FlaskConical }];

function FluidVessel({ label, value, fraction, kind }: { label: string; value: string; fraction: number; kind: string }) {
  return <div className={`fluid-compartment ${kind}`}><div className="vessel"><div className="vessel-rim" /><div className="fluid" style={{ height: `${Math.max(8, Math.min(92, fraction * 100))}%` }} /><div className="glass-reflection" /><div className="vessel-graduations"><span /><span /><span /></div></div><strong>{value}</strong><span>{label}</span></div>;
}

function SmallTrace({ stable }: { stable: boolean }) {
  return <svg viewBox="0 0 160 50" role="img" aria-label={stable ? 'Stable illustrative trace' : 'Declining illustrative trace'}><path d={stable ? 'M0 28 L20 22 L40 25 L60 18 L80 23 L100 19 L120 26 L140 22 L160 24' : 'M0 9 L20 13 L40 14 L60 20 L80 25 L100 29 L120 35 L140 39 L160 44'} fill="none" stroke="currentColor" strokeWidth="2" /></svg>;
}

export default function App({initialPage='cockpit',initialPatient='RNL-014',initialMinute=90,startTour=false,initialTourStep=0,onHome,onResearch}:{initialPage?:WorkspacePage;initialPatient?:string;initialMinute?:number;startTour?:boolean;initialTourStep?:number;onHome:()=>void;onResearch:()=>void}) {
  const [page, setPage] = useState<Page>(startTour?tourSteps[initialTourStep][0]:initialPage);
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
  const [observed, setObserved] = useState<ObservedEvaluation | null>(null);
  const [toast, setToast] = useState('');
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(()=>{const params=new URLSearchParams({view:page,patient:patientId,minute:String(cutoff)});if(tourOpen){params.set('tour','1');params.set('step',String(tourStep));}window.history.replaceState(null,'',`/workspace?${params}`);},[page,patientId,cutoff,tourOpen,tourStep]);
  function goTour(step:number){setPlaying(false);setPatientId('RNL-014');setCutoff(80);setPage(tourSteps[step][0]);setTourStep(step);setTourOpen(true);}
  function showTourArea(){(document.querySelector(tourSteps[tourStep][4])??document.querySelector('.page-heading'))?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});}

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
    api<ObservedEvaluation>('/observed-evaluation', { signal: controller.signal }).then(setObserved)
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

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="/" onClick={e => { e.preventDefault(); onHome(); }} aria-label="RENALIS home"><span className="brand-symbol"><Droplets size={21} strokeWidth={1.6} /></span><div>RENALIS<small>Patient × machine</small></div></a>
      <div className="sidebar-label">CLINICAL WORKSPACE</div>
      <nav aria-label="Workspace navigation">{pages.map(item => <button key={item.id} className={`nav-item ${page === item.id ? 'active' : ''}`} onClick={() => setPage(item.id)} aria-current={page === item.id ? 'page' : undefined}><item.icon size={18} /><span>{item.title}</span>{item.id === 'unit' && <span className="nav-count">{patients.length || 4}</span>}</button>)}</nav>
      <div className="sidebar-divider" /><div className="sidebar-label">ACTIVE SESSION</div>
      <button className="sidebar-patient" onClick={() => setPage('cockpit')}><span className="avatar small">{p?.name.split(' ').map(n => n[0]).join('') || 'MR'}</span><span>{p?.name || 'Meera Rao'}<small>{patientId}</small></span><ChevronRight size={14} /></button>
      <div className="sidebar-bottom"><div className="model-indicator"><span />Research engine <small>v0.4</small></div><button onClick={() => setPage('evidence')} className="help-button"><CircleHelp size={16} /> Model & provenance</button><div className="clinician-avatar"><span className="avatar">DR</span><div>Clinician workspace<small>Local demonstration</small></div></div></div>
    </aside>
    <div className="workspace">
      <header className="topbar"><div className="breadcrumbs"><button onClick={onHome}>Overview</button><ChevronRight size={13} /><span>{pages.find(item => item.id === page)?.title}</span></div><div className="topbar-actions"><button className="workspace-guide-link" onClick={onResearch}><BookOpen size={14}/><span>Research guide</span></button><button className="workspace-guide-link" onClick={()=>goTour(0)}><Play size={13}/><span>Walkthrough</span></button><button className="sandbox-tag" onClick={() => setPage('evidence')}><FlaskConical size={13} /> Synthetic research sandbox</button><button className="icon-button" aria-label="Export research snapshot" disabled={!ready || busy} onClick={exportSnapshot}><Download size={17} /></button></div></header>
      <main className="main-content">
        {error && <div className="error-banner" role="alert"><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError('')}><X size={16} /></button></div>}
        <div className="page-heading"><div><div className="eyebrow">RENALIS / {page === 'investigation' ? 'ONE PATIENT / ONE EVIDENCE CUTOFF' : page === 'mechanisms' ? 'MECHANISM & MEASUREMENT LAB' : page === 'cockpit' ? 'DIALYSIS DIGITAL TWIN' : page === 'unit' ? 'SYNCHRONIZED PATIENT REPLAY' : page === 'history' ? 'PATIENT-SPECIFIC MEMORY' : 'TRANSPARENT RESEARCH'}</div><h1>{page === 'investigation' ? 'A clearer next evidence question.' : page === 'mechanisms' ? 'When explanations disagree.' : page === 'cockpit' ? 'Before the pressure falls.' : page === 'unit' ? 'Every session. In perspective.' : page === 'history' ? 'A twin that remembers.' : 'Evidence behind the estimate.'}</h1><p>{page === 'investigation' ? 'Learn from the past, inspect the model, and discover what the available evidence can settle.' : page === 'mechanisms' ? 'Explore competing mechanisms and the observation that could clarify the comparison.' : page === 'cockpit' ? 'Understand the patient state. Explore the next thirty minutes.' : page === 'unit' ? 'Four fictional patients, one shared replay clock, distinct physiological responses.' : page === 'history' ? 'Historical responses, saved scenarios, and traceable clinical review.' : 'Computed sandbox results, model assumptions, and the path to observed-data validation.'}</p></div><div className="heading-actions">{page === 'cockpit' && <button className="button light" onClick={() => { setPlaying(false); setNote(''); dialog.current?.showModal(); }} disabled={!ready || busy}><Stethoscope size={15} /> Record review</button>}<button className="button subtle" onClick={exportSnapshot} disabled={!ready || busy}><Download size={15} /> Export snapshot</button></div></div>
        {tourOpen&&<GuidedTour step={tourStep} onStep={goTour} onClose={()=>setTourOpen(false)} onShow={showTourArea}/>}
        {(page === 'cockpit' || page === 'unit' || page === 'history' || page === 'mechanisms' || page === 'investigation') && <div className="session-toolbar"><div className="patient-select"><label htmlFor="patient">Patient</label><div><span className="avatar small">{p?.name.split(' ').map(n => n[0]).join('') || 'MR'}</span><select id="patient" value={patientId} onChange={e => { setPatientId(e.target.value); setPlaying(false); }}>{(patients.length ? patients : [{ id: 'RNL-014', name: 'Meera Rao' }]).map(v => <option key={v.id} value={v.id}>{v.name} · {v.id}</option>)}</select><ChevronDown size={14} /></div></div><div className="replay-control"><button className="icon-button" onClick={() => setPlaying(!playing)} disabled={cutoff >= 240} aria-label={playing ? 'Pause replay' : 'Play replay'}>{playing ? <Pause size={16} /> : <Play size={16} />}</button><div><label htmlFor="clock">Replay clock <strong>{cutoff} / 240 min</strong></label><input id="clock" type="range" min={0} max={240} step={5} value={cutoff} onChange={e => { setPlaying(false); setCutoff(Number(e.target.value)); }} /></div><button className="icon-button" onClick={() => { setPlaying(false); setCutoff(0); }} aria-label="Reset replay"><RotateCcw size={15} /></button></div><div className="replay-provenance"><span className={`live-dot ${playing ? 'running' : ''}`} />{playing ? 'Replaying observations' : 'Available-time replay'}<small>{busy ? 'Updating twin…' : 'Future observations withheld'}</small></div></div>}
        {!twin && !error && <div className="loading-state"><LoaderCircle className="spin" size={28} /><h2>Initializing patient twins</h2><p>Loading historical priors and available sensor observations.</p></div>}
        {twin && page === 'cockpit' && <div className={`cockpit ${busy ? 'updating' : ''}`} aria-busy={busy}>
          <div className="primary-column">
            <section className="patient-banner"><div className="patient-identity"><span className="avatar large">{p!.name.split(' ').map(n => n[0]).join('')}</span><div><h2>{p!.name} <span>{p!.age}y · {p!.sex}</span></h2><p>Maintenance hemodialysis <span>·</span> {patientId}</p></div></div><span className={`status-badge ${twin.alert.status}`}><span />{statusText[twin.alert.status]}</span><div className="patient-facts"><div><span>Dry weight</span><strong>{p!.dry_weight} <small>kg</small></strong></div><div><span>Historical sessions</span><strong>{p!.prior_sessions}</strong></div><div><span>Diabetes history</span><strong>{p!.diabetes ? 'Present' : 'Absent'}</strong></div><div><span>Latest valid BP</span><strong>{twin.latest.sbp} <small>mmHg</small></strong></div></div></section>
            <section className="panel physiology-panel"><div className="panel-heading"><div><div className="eyebrow">UPDATING PHYSIOLOGICAL STATE</div><h2>A balance inside the patient.</h2></div><span className="quiet-badge">Estimated, not imaged</span></div><div className="fluid-system"><FluidVessel label="Tissue excess" value={`${twin.compartments.tissue_l.toFixed(2)} L`} fraction={twin.compartments.tissue_l / (p!.target_ml / 1000)} kind="tissue" /><div className="fluid-transfer"><div className="flow-line"><ArrowRight size={18} /></div><span>Vascular refill</span><strong>{twin.compartments.refill_l_h.toFixed(2)} L/h</strong></div><FluidVessel label="Circulating volume" value={`${twin.compartments.plasma_l.toFixed(2)} L`} fraction={twin.compartments.plasma_l / p!.initial_plasma} kind="circulation" /><div className="fluid-transfer"><div className="flow-line"><ArrowRight size={18} /></div><span>Machine removal</span><strong>{(twin.current_machine.uf_ml_h / 1000).toFixed(2)} L/h</strong></div><FluidVessel label="Removed this session" value={`${(twin.compartments.removed_ml / 1000).toFixed(2)} L`} fraction={twin.compartments.removed_ml / p!.target_ml} kind="removed" /></div><div className="physiology-foot"><span><Database size={13} /> Historical priors + available BP & machine readings</span><span><Clock3 size={13} /> BP age: {twin.bp_age_minutes} min</span></div></section>
            <section className="panel forecast-panel"><div className="panel-heading"><div><div className="eyebrow">FACTUAL FORECAST & HYPOTHETICAL BRANCH</div><h2>One patient. Parallel futures.</h2></div><button className="text-button" onClick={outcome ? () => setOutcome(null) : reveal} disabled={busy || complete}>{outcome ? 'Hide outcome' : 'Reveal later readings'}<ArrowUpRight size={14} /></button></div>{insufficient && <div className="inline-notice">BP is stale. The physiological projection is shown for inspection; alerting and scenario ranking are withheld.</div>}{twin.alert.status === 'current_event' && <div className="inline-notice">The current reading is already low. This state is not counted as an advance warning.</div>}{complete && <div className="inline-notice">Session complete. No further dialysis trajectory is forecast.</div>}<Suspense fallback={<div className="trajectory loading-state compact">Preparing trajectory…</div>}><Trajectory twin={twin} scenario={scenario} outcome={outcome} /></Suspense><div className="chart-legend"><span><b className="observed" />Available synthetic BP</span><span><b className="current" />Current profile</span>{scenario && <span><b className="alternative" />Alternative profile</span>}{outcome && <span><b className="revealed" />Revealed outcome</span>}<span className="legend-caption">Shading: uncalibrated particle range</span></div>{outcome && <div className="outcome-note"><CheckCheck size={16} /><span>{outcome.event ? `Later synthetic event observed at session minute ${outcome.first_event_minute}.` : 'No low-BP event in the revealed synthetic readings.'} These readings were excluded from the forecast.</span></div>}</section>
          </div>
          <aside className="scenario-column">
            <ForecastAlert twin={twin} />
            <section className="panel scenario-panel"><div className="panel-heading"><div><div className="eyebrow">HYPOTHETICAL WORKBENCH</div><h2>Explore an alternative.</h2></div><SlidersHorizontal size={18} /></div><div className="scenario-input"><label htmlFor="rate">Fluid-removal rate <span>mL/h</span></label><div className="rate-value">{format(rate)}<span>{scenarioBusy && <LoaderCircle className="spin" size={14} />}</span></div><input id="rate" type="range" min={300} max={1400} step={50} value={rate} disabled={insufficient || complete || currentEvent || busy} onChange={e => setRate(Number(e.target.value))} /><div className="range-labels"><span>300</span><span>1,400</span></div></div><div className="profile-switch" aria-label="Removal profile"><button className={profile === 'constant' ? 'selected' : ''} onClick={() => setProfile('constant')} disabled={insufficient || complete || currentEvent || busy}>Constant</button><button className={profile === 'step_down' ? 'selected' : ''} onClick={() => setProfile('step_down')} disabled={insufficient || complete || currentEvent || busy}>Step down at +15m</button></div>{scenario && !currentEvent && <div className="scenario-results"><div><span>Alternative crossing fraction</span><strong>{Math.round(scenario.crossing_fraction * 100)}% <small>of particles</small></strong></div><div><span>Fluid removed in next {twin.horizon}m</span><strong>{format(scenario.fluid_removed_next_ml)} <small>mL</small></strong></div><div><span>Remaining fluid target</span><strong>{format(scenario.remaining_target_ml)} <small>mL</small></strong></div><div className="tradeoff-note"><ArrowLeftRight size={15} /><span>{scenario.additional_remaining_ml === 0 ? 'Same modeled fluid removal as the current profile.' : `${format(Math.abs(scenario.additional_remaining_ml))} mL ${scenario.additional_remaining_ml > 0 ? 'more' : 'less'} fluid remains than with the current profile.`}</span></div></div>}{insufficient && <p className="empty-note">A fresh valid BP reading is needed before scenario comparison.</p>}{currentEvent&&<p className="empty-note">Current low BP is an existing event. Alternative-profile comparisons are withheld.</p>}<button className="button primary full" disabled={!scenario || currentEvent || saving || busy || scenarioBusy} onClick={saveBranch}>{saving ? <LoaderCircle className="spin" size={15} /> : <GitBranch size={15} />} Save scenario branch</button><p className="scenario-disclaimer">Research simulation. Alternative outcomes are not observed, and no machine setting is changed.</p></section>
            <section className="evidence-teaser"><ShieldCheck size={19} /><div><h3>Every estimate has a trail.</h3><p>{twin.model.particles} particles. Past observations only. Trace the assumptions and benchmark.</p><button className="text-button" onClick={() => setPage('evidence')}>Inspect model & evidence <ArrowRight size={14} /></button><button className="text-button lab-preview-link" onClick={() => { setPlaying(false); setPage('mechanisms'); }}>Compare physiological explanations <ArrowRight size={14} /></button></div></section>
          </aside>
        </div>}
        {twin && page === 'investigation' && <Suspense fallback={<div className="loading-state">Opening the evidence journey…</div>}><EvidenceJourney patientId={patientId} cutoff={cutoff} onAdvance={setCutoff} onPause={()=>setPlaying(false)} onToast={setToast}/></Suspense>}
        {twin && page === 'mechanisms' && <Suspense fallback={<div className="loading-state"><LoaderCircle className="spin" /><p>Loading the mechanism workspace…</p></div>}><MechanismLab patientId={patientId} cutoff={cutoff} onAdvance={setCutoff} onPause={() => setPlaying(false)} onError={setError} onToast={setToast} /></Suspense>}
        {page === 'unit' && <section className="unit-view"><div className="section-summary"><span><span className="live-dot" /> {patients.length} synthetic sessions</span><span>{patients.filter(v => v.status === 'review').length} forecast reviews · {patients.filter(v => v.status === 'insufficient').length} stale-reading cases</span></div><div className="unit-grid">{patients.map(v => <button className="unit-patient panel" key={v.id} onClick={() => { setPatientId(v.id); setPage('cockpit'); }}><div className="unit-patient-head"><span className="avatar">{v.name.split(' ').map(n => n[0]).join('')}</span><span className={`status-badge ${v.status}`}><span />{statusText[v.status]}</span></div><h2>{v.name}</h2><p>{v.age}y · {v.sex} · {v.id}</p><SmallTrace stable={v.status === 'monitor'} /><span className="trace-label">Illustrative phenotype trace</span><div className="unit-numbers"><div><span>Latest BP</span><strong>{v.sbp}<small> mmHg</small></strong></div><div><span>Current removal</span><strong>{format(v.uf_ml_h)}<small> mL/h</small></strong></div></div><div className="unit-patient-foot"><span>{v.phenotype}</span><ArrowUpRight size={17} /></div></button>)}</div></section>}
        {twin && page === 'history' && <div className="history-layout"><section className="panel history-panel"><div className="panel-heading"><div><div className="eyebrow">HISTORICAL EHR STREAM</div><h2>Previous session responses.</h2></div><BookOpen size={19} /></div><p className="section-description">The refill prior is learned from these preceding synthetic BP trajectories, with population shrinkage and retained uncertainty. Post-session observations from today are never used at an earlier cutoff.</p><div className="table-wrap"><table><thead><tr><th>Session</th><th>Mean removal</th><th>Minimum BP</th><th>Refill estimate</th></tr></thead><tbody>{twin.sessions.map(s => <tr key={s.session}><td><strong>{s.session}</strong><small>{s.label}</small></td><td>{format(s.mean_uf_ml_h)} mL/h</td><td>{s.min_sbp} mmHg</td><td>{s.refill_estimate_l_h} L/h</td></tr>)}</tbody></table></div><div className="panel-bottom-note"><Database size={13} />Synthetic historical records · {p!.prior_sessions} prior sessions in patient profile</div></section><section className="panel"><div className="panel-heading"><h2>Saved scenario branches</h2><GitBranch size={18} /></div>{branches.length === 0 ? <div className="empty-state"><GitBranch size={25} /><h3>No branches saved yet.</h3><p>Compare a profile in the patient twin and save its state.</p><button className="button light" onClick={() => setPage('cockpit')}>Open workbench <ArrowRight size={14} /></button></div> : <div className="record-list">{branches.map(b => <div key={b.id}><GitBranch size={16} /><div><strong>{format(b.rate)} mL/h · {b.profile === 'constant' ? 'constant' : 'step down'}</strong><small>Branch #{b.id} · cutoff minute {b.cutoff}</small></div><button className="text-button" onClick={() => { setCutoff(b.cutoff); setRate(b.rate); setProfile(b.profile); setPage('cockpit'); setPlaying(false); }}>Restore <ArrowUpRight size={13} /></button></div>)}</div>}</section><section className="panel review-history"><div className="panel-heading"><h2>Clinical review notes</h2><button className="text-button" onClick={() => { setPlaying(false); setNote(''); dialog.current?.showModal(); }}><Plus size={14} /> Add note</button></div>{reviews.length === 0 ? <p className="section-description">No review notes yet. Notes are stored locally with the patient and replay cutoff.</p> : reviews.map(r => <article className="review-note" key={r.id}><span className="quiet-badge">Session minute {r.cutoff}</span><p>{r.note}</p><small>{new Date(r.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST</small></article>)}</section></div>}
        {page === 'evidence' && <div className="evidence-view"><section className="research-banner"><FlaskConical size={25} /><div><h2>A research model, with visible boundaries.</h2><p>The app currently runs synthetic EHRs and sensor streams. Forecasts and benchmarks are computed; they are not clinical performance claims. HEMOBP preparation and observed-data evaluation are separate.</p></div></section>{!evaluation || !modelCard ? <div className="loading-state compact"><LoaderCircle className="spin" size={22} /><p>Computing the fixed sandbox benchmark…</p></div> : <><div className="evidence-grid"><section className="panel"><div className="panel-heading"><h2>What powers the twin</h2><Activity size={18} /></div><dl className="model-details"><div><dt>Model</dt><dd>{modelCard.method}</dd></div><div><dt>Endpoint</dt><dd>{modelCard.event}</dd></div><div><dt>Data</dt><dd>{modelCard.data}</dd></div><div><dt>Version</dt><dd><code>{modelCard.version}</code></dd></div></dl><h3 className="subheading">Historical + dynamic inputs</h3><ul className="check-list">{modelCard.inputs.map(text => <li key={text}><Check size={14} />{text}</li>)}</ul></section><section className="panel"><div className="panel-heading"><h2>Computed baseline comparison</h2><ArrowDown size={17} /></div><p className="section-description">BP forecast MAE · {evaluation.eligible_windows} eligible synthetic windows · lower is better.</p><div className="benchmark-bars">{evaluation.models.map(m => <div key={m.key}><div><span>{m.label}</span><strong>{m.mae_mm_hg?.toFixed(2) ?? '—'} <small>mmHg</small></strong></div><div className="benchmark-track"><div className={m.key === 'fused' ? 'fused' : ''} style={{ width: `${((m.mae_mm_hg ?? 0) / Math.max(...evaluation.models.map(v => v.mae_mm_hg ?? 0), 1)) * 100}%` }} /></div></div>)}</div><p className="small-print">{evaluation.provenance}. Shared generator/model structure can make this benchmark optimistic.</p></section></div><section className="panel"><div className="panel-heading"><h2>Availability, uncertainty, and limits</h2><ShieldCheck size={18} /></div><div className="limits-columns"><div><h3>Model safeguards</h3><ul className="check-list">{modelCard.exclusions.map(text => <li key={text}><Check size={14} />{text}</li>)}</ul></div><div><h3>What the benchmark cannot establish</h3><ul className="plain-list">{evaluation.limitations.map(text => <li key={text}>{text}</li>)}</ul></div></div></section><section className="panel sources-panel"><div className="panel-heading"><h2>Observed-data research foundation</h2><Database size={18} /></div>{modelCard.references.map(s => <a key={s.url} href={s.url} target="_blank" rel="noreferrer"><span>{s.title}</span><ArrowUpRight size={17} /></a>)}<p className="small-print">HEMOBP's native sampling and repeated measurement identifiers require a separate data audit. The five-minute sandbox cuff cadence is not attributed to that dataset.</p></section></>}</div>}
        {page === 'evidence' && observed && <section className="panel observed-panel"><div className="panel-heading"><div><div className="eyebrow">SEPARATE OBSERVED-DATA BASELINE</div><h2>HEMOBP · patient-held-out evaluation</h2></div><span className="quiet-badge"><Database size={12} />Observed retrospective data</span></div>{observed.status === 'not_run' ? <p className="section-description">{observed.message}</p> : <><p className="section-description">{observed.dataset}. {format(observed.test_rows)} held-out next-reading windows across {observed.test_patients} patients. Patient overlap: {observed.patient_overlap}.</p><div className="observed-metrics">{observed.models.map(m => <div key={m.label}><span>{m.label}</span><strong>{m.mae_mm_hg.toFixed(2)} <small>mmHg MAE</small></strong></div>)}</div><p className="small-print">{observed.task}. Median forecast gap: {observed.median_next_reading_minutes} minutes. These baseline models have not replaced the synthetic physiological twin.</p><details><summary>Read observed-data audit limitations</summary><ul className="plain-list">{observed.limitations.map(text => <li key={text}>{text}</li>)}</ul></details><a className="text-button" href={observed.source} target="_blank" rel="noreferrer">Versioned dataset · {observed.license} <ArrowUpRight size={14} /></a></>}</section>}
        {page === 'evidence' && observed?.status === 'evaluated' && observed.event_model && <section className="panel observed-panel"><div className="panel-heading"><h2>Observed low-BP event baseline</h2><span className="quiet-badge">Threshold chosen on separate patients</span></div><div className="observed-metrics"><div><span>Held-out sensitivity</span><strong>{Math.round(observed.event_model.test_sensitivity * 100)}%<small> of next-low-BP windows</small></strong></div><div><span>Positive predictive value</span><strong>{(observed.event_model.test_ppv * 100).toFixed(1)}%<small> of flagged windows</small></strong></div><div><span>False-positive windows</span><strong>{format(observed.event_model.test_false_positive_windows)}</strong></div></div><p className="small-print">The false-positive burden remains substantial. These are retrospective window-level results, not clinical alert performance. {observed.event_model.score_calibration}. {observed.event_model.alert_accounting}.</p></section>}
        <footer className="workspace-footer"><span>RENALIS <span>·</span> A localized patient digital twin</span><span><ShieldCheck size={12} /> Synthetic research demonstration. No clinical deployment.</span></footer>
      </main>
    </div>
    {toast && <div className="toast" role="status"><Check size={17} />{toast}</div>}
    <dialog ref={dialog} className="review-dialog"><form onSubmit={saveReview}><div className="panel-heading"><div><div className="eyebrow">LOCAL REVIEW AUDIT</div><h2>Record a clinical review.</h2></div><button type="button" className="icon-button" aria-label="Close review dialog" onClick={() => dialog.current?.close()}><X size={18} /></button></div><p>{p?.name} · session minute {cutoff}</p><label htmlFor="review-note">Review note</label><textarea id="review-note" value={note} onChange={e => setNote(e.target.value)} maxLength={2000} rows={5} required placeholder="Describe the observations, uncertainty, and next measurement to review…" /><p className="small-print">Stored in this local research workspace. No external message or treatment command is sent.</p><button className="button primary full" type="submit" disabled={saving || !note.trim()}>{saving ? <LoaderCircle className="spin" size={15} /> : <Check size={15} />}Save review note</button></form></dialog>
  </div>;
}
