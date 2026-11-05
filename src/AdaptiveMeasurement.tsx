import { ArrowRight, FlaskConical, GitBranch } from 'lucide-react';
import type { Candidate, Evidence, Family } from './mechanismTypes';
import { channelName, familyName } from './plain';

type Experiment = Candidate & {
  pair_information_bits:number; full_information_bits:number;
  pair_error_before:number; pair_error_after:number; pair_confidence_80_fraction:number;
  observation_minute:number; ranges:{id:string;label:string;range:number[]}[];
  examples:{value:number;family_weights:number[];leading_family:string}[];
};
export type DiscriminationPlan = {
  version:string;status:string;objective:'pair'|'whole_bank';
  pair:{id:string;label:string;weight:number}[];pair_mass:number;other_mass:number;
  recommended:Experiment|null;candidates:Experiment[];latest_evidence:Evidence|null;
  reason:string;method:string;limitations:string;
};
const colors:Record<string,string>={volume:'#307961',cardiac:'#786398',vascular:'#ac7346',mixed:'#487b95'};
const short=familyName;
const pct=(n:number)=>(n*100).toFixed(0);

export default function AdaptiveMeasurement({plan,families,ready,onAcquire}:{plan:DiscriminationPlan;families:Family[];ready:boolean;onAcquire:(c:Candidate)=>void}){
  const r=plan.recommended;
  const lo=r?Math.min(...r.ranges.map(f=>f.range[0])):0;
  const hi=r?Math.max(...r.ranges.map(f=>f.range[2])):1;
  const pos=(v:number)=>100*(v-lo)/Math.max(.001,hi-lo);
  const rName=r?(channelName[r.channel]??r.label):'';
  const nameOf=(id:string,label:string)=>short[id]??label;
  return <section className="adaptive-plan" aria-label="Next measurement planner" data-status={plan.status}>
    <div className="adaptive-heading"><span className="eyebrow"><GitBranch size={14}/> SUGGESTED NEXT CHECK</span><span className="adaptive-badge">{plan.objective==='pair'?'Top two causes':'All four causes'}</span></div>
    <h3>{r?rName:plan.status==='supported'?'One cause now clearly fits best':'No check would help much right now'}</h3>
    {plan.latest_evidence&&<p className="adaptive-observed">Updated after the last reading: <b>{plan.latest_evidence.value} {plan.latest_evidence.unit}</b> at minute {plan.latest_evidence.observed_minute??plan.latest_evidence.available_minute}.</p>}
    {r&&<>
      <p className="adaptive-lede">This check best tells apart <b style={{color:colors[r.ranges[0].id]}}>{nameOf(r.ranges[0].id,r.ranges[0].label).toLowerCase()}</b> and <b style={{color:colors[r.ranges[1].id]}}>{nameOf(r.ranges[1].id,r.ranges[1].label).toLowerCase()}</b>, because they expect different results:</p>
      <div className="adaptive-ranges" aria-label="What each cause expects">{r.ranges.map(f=><div key={f.id}><span style={{color:colors[f.id]}}>{nameOf(f.id,f.label)}</span><div className="measurement-range-track"><i style={{left:`${pos(f.range[0])}%`,width:`${pos(f.range[2])-pos(f.range[0])}%`,background:colors[f.id]}}/><b style={{left:`${pos(f.range[1])}%`,background:colors[f.id]}}/></div><strong>about {f.range[1].toFixed(1)} <small>{r.unit}</small></strong></div>)}</div>
      <p className="adaptive-payoff">Chance of backing the wrong cause: <b>{pct(r.pair_error_before)}%</b> <ArrowRight size={13}/> <b>{pct(r.pair_error_after)}%</b> after this check.</p>
      <div className="adaptive-action"><p>The simulated device gives the real value. Then the cause bar above updates.</p><button className="button primary" disabled={!ready} onClick={()=>onAcquire(r)}><FlaskConical size={15}/>Take this measurement</button></div>
    </>}
    {!r&&<p>{plan.status==='supported'?'The readings so far point clearly to one cause, so another check would add little.':'None of the available checks would separate the causes enough to be worth it.'}</p>}
    <details className="adaptive-more"><summary>More detail</summary>
      {plan.latest_evidence?.channel==='cardiac_output'&&plan.objective==='pair'&&plan.pair.some(f=>f.id==='volume')&&plan.pair.some(f=>f.id==='cardiac')&&<p><b>Why are two causes still left?</b> A weak heart reading fits both “not enough blood volume” and “heart not pumping harder”. Measuring blood volume directly will tell them apart.</p>}
      <div className="adaptive-beliefs">{plan.pair.map(f=><div key={f.id} style={{borderColor:colors[f.id]}}><span>{nameOf(f.id,f.label)}</span><strong style={{color:colors[f.id]}}>{pct(f.weight)}%</strong><small>fit right now</small></div>)}<p>{plan.objective==='pair'?<>These two make up <b>{pct(plan.pair_mass)}%</b>; the other two {pct(plan.other_mass)}%.</>:<>All four causes are being compared. The top two are shown.</>}</p></div>
      {r&&<>
        <p>Bars show the range of results each cause expects; the dot is the most likely value. There’s a <b>{pct(r.pair_confidence_80_fraction)}%</b> chance the result makes one cause at least 80% likely.</p>
        <div className="adaptive-outcomes"><h4>What different results would mean (preview)</h4><div>{r.examples.map((e,i)=><article key={i}><small>{['If low','If in the middle','If high'][i]}</small><strong>{e.value.toFixed(1)} {r.unit}</strong><span>{nameOf(e.leading_family,e.leading_family)} would lead</span>{plan.pair.map(f=><p key={f.id}><span>{nameOf(f.id,f.label)}</span><b style={{color:colors[f.id]}}>{pct(e.family_weights[families.findIndex(x=>x.id===f.id)])}%</b></p>)}</article>)}</div></div>
      </>}
      <p className="adaptive-distinction-note"><b>Informative is not the same as worth it.</b> This box picks the check that best separates the causes. The next box asks whether any check is worth its cost and wait. Neither one recommends a treatment.</p>
    </details>
  </section>;
}
