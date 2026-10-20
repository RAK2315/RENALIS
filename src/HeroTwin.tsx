import { useEffect, useState } from 'react';
import { Activity, ArrowRight, Database, LoaderCircle, RefreshCcw, Waves } from 'lucide-react';
import { api } from './api';
import type { LabAnalysis } from './mechanismTypes';

const palette={volume:'#a9d799',vascular:'#e3b689',cardiac:'#c0b0e4'};
const names={volume:'Volume / refill',vascular:'Vascular response',cardiac:'Cardiac response'};
type Hypothesis=keyof typeof palette;
export default function HeroTwin(){
  const [data,setData]=useState<LabAnalysis|null>(null);
  const [focus,setFocus]=useState<Hypothesis>('volume');
  const [error,setError]=useState('');
  const [attempt,setAttempt]=useState(0);
  useEffect(()=>{const controller=new AbortController();setError('');api<LabAnalysis>('/demo-example',{signal:controller.signal}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(e.message);});return()=>controller.abort();},[attempt]);
  const observations=data?.observations.filter(r=>r.minute>=65&&r.sbp!==null&&r.quality==='valid')??[];
  const points=data?.trajectories??[];
  const min=Math.min(80,...points.map(p=>Math.min(p.volume,p.vascular,p.cardiac)))-4;
  const max=Math.max(120,...observations.map(p=>p.sbp??0))+4;
  const y=(value:number)=>230-(value-min)/(max-min)*160;
  const x=(minute:number)=>55+(minute-65)/55*420;
  const path=(id:Hypothesis)=>points.map((p,i)=>`${i?'L':'M'}${x(p.minute).toFixed(1)},${y(p[id]).toFixed(1)}`).join(' ');
  const observed=observations.map((p,i)=>`${i?'L':'M'}${x(p.minute).toFixed(1)},${y(p.sbp!).toFixed(1)}`).join(' ');
  const family=data?.families.find(f=>f.id===focus);
  return <div className="hero-twin" aria-label="Computed synthetic example of competing physiological models"><div className="twin-card-top"><span><i/>COMPUTED SYNTHETIC EXAMPLE</span><span>Meera · minute 90</span></div><div className="twin-data-flow"><div><Database size={16}/><span>Historical EHR<small>Learned preceding-session prior</small></span></div><ArrowRight size={18}/><div><Activity size={16}/><span>Device replay<small>Available readings only</small></span></div></div><div className="hero-chart"><div className="hero-chart-label"><span>Systolic BP</span><span>mmHg</span></div>{!data?<div className="hero-preview-state">{error?<><Waves size={29}/><p>The computed example is currently unavailable.</p><button onClick={()=>setAttempt(v=>v+1)}><RefreshCcw size={13}/>Try again</button></>:<><LoaderCircle className="spin" size={24}/><p>Computing possible futures…</p></>}</div>:<svg viewBox="0 0 520 280" role="img" aria-label="Available blood pressure followed by three differing model projections for the same alternative removal profile">{[80,100,120].filter(v=>v>=min&&v<=max).map(v=><g key={v}><line x1="55" x2="478" y1={y(v)} y2={y(v)} stroke="#42604f" strokeWidth=".7"/><text x="20" y={y(v)+4} fill="#a3b8a3" fontSize="10">{v}</text></g>)}<line x1="55" x2="478" y1={y(90)} y2={y(90)} stroke="#b99c77" strokeDasharray="4 5"/><text x="477" y={y(90)-8} textAnchor="end" fill="#cfb68f" fontSize="9">Research threshold · 90</text><line x1={x(90)} x2={x(90)} y1="60" y2="234" stroke="#829981" strokeDasharray="3 4"/><path d={observed} stroke="#e1e9d7" strokeWidth="2.4" fill="none"/>{(['volume','vascular','cardiac'] as Hypothesis[]).map(id=><path key={id} d={path(id)} fill="none" stroke={palette[id]} strokeWidth={focus===id?3:1.6} opacity={focus===id?1:.35}/>)}<circle cx={x(90)} cy={y(observations.at(-1)?.sbp??96)} r="4" fill="#e5edda"/><text x={x(90)} y="258" textAnchor="middle" fill="#c4d2bb" fontSize="10">Now</text><text x={x(105)} y="258" textAnchor="middle" fill="#9db396" fontSize="10">+15 min</text><text x={x(120)} y="258" textAnchor="end" fill="#9db396" fontSize="10">+30 min</text></svg>}</div><div className="hero-hypotheses" aria-label="Choose an explanation">{(['volume','vascular','cardiac'] as Hypothesis[]).map(id=><button key={id} aria-pressed={focus===id} onClick={()=>setFocus(id)} style={{'--hypothesis-color':palette[id]} as React.CSSProperties}><i/>{names[id]}</button>)}</div><div className="hero-model-note"><span>Same available pressure.<br/><strong>Different modeled response.</strong></span><span>{family?.alternative_end_sbp!==null&&family?.alternative_end_sbp!==undefined?<><strong>{family.alternative_end_sbp.toFixed(1)}</strong> mmHg<small>Modeled BP at +30 min</small></>:<small>Experiments depend on released evidence.</small>}</span></div><p className="hero-chart-caption">Three views from the four-hypothesis bank. Alternative profile: 650 mL/h. Computed from the research model; these are unvalidated simulated responses.</p></div>;
}
