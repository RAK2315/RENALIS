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
  return <section className="adaptive-plan" aria-label="Next measurement planner" data-status={plan.status}>
    <div className="adaptive-heading"><span className="eyebrow"><GitBranch size={14}/> SUGGESTED NEXT CHECK</span><span className="adaptive-badge">{plan.objective==='pair'?'Telling the top two causes apart':'Comparing all four causes'}</span></div>
    <h3>{r?`Suggested: ${rName}`:plan.status==='supported'?'One cause now clearly fits best':'No measurement would help much right now'}</h3>
    {plan.latest_evidence?<p className="adaptive-observed"><b>Latest reading: {plan.latest_evidence.value} {plan.latest_evidence.unit}</b> at minute {plan.latest_evidence.observed_minute??plan.latest_evidence.available_minute}. The suggestion below has been updated using it.</p>:<p>No extra readings yet. The twin is choosing the first one.</p>}
    {plan.latest_evidence?.channel==='cardiac_output'&&plan.objective==='pair'&&plan.pair.some(f=>f.id==='volume')&&plan.pair.some(f=>f.id==='cardiac')&&<p><b>Why are two causes still left?</b> A weak heart reading fits both “not enough blood volume” and “heart not pumping harder”. Measuring blood volume directly will tell them apart.</p>}
    <div className="adaptive-beliefs">{plan.pair.map(f=><div key={f.id} style={{borderColor:colors[f.id]}}><span>{short[f.id]??f.label}</span><strong style={{color:colors[f.id]}}>{pct(f.weight)}%</strong><small>fit right now</small></div>)}<p>{plan.objective==='pair'?<>These two causes are still in the running. Together they make up <b>{pct(plan.pair_mass)}%</b>; the other two make up {pct(plan.other_mass)}%. The cause is not settled yet.</>:<>All four causes are being compared. The top two are shown here.</>}</p></div>
    {r&&<>
      <div className="adaptive-reason"><span>WHY THIS ONE?</span><p>If the cause is <b>{(short[r.ranges[0].id]??r.ranges[0].label).toLowerCase()}</b>, this reading should be about <b>{r.ranges[0].range[1].toFixed(1)} {r.unit}</b>. If it is <b>{(short[r.ranges[1].id]??r.ranges[1].label).toLowerCase()}</b>, about <b>{r.ranges[1].range[1].toFixed(1)} {r.unit}</b>. Of all the checks available, this one best separates them.</p></div>
      <div className="adaptive-ranges" aria-label="What each cause expects">{r.ranges.map(f=><div key={f.id}><span style={{color:colors[f.id]}}>{short[f.id]??f.label}</span><div className="measurement-range-track"><i style={{left:`${pos(f.range[0])}%`,width:`${pos(f.range[2])-pos(f.range[0])}%`,background:colors[f.id]}}/><b style={{left:`${pos(f.range[1])}%`,background:colors[f.id]}}/></div><strong>{f.range[0].toFixed(1)}–{f.range[2].toFixed(1)} <small>{r.unit}</small></strong></div>)}</div>
      <p className="journey-footnote">Each bar is the range of results that cause expects; the dot is the most likely value. Less overlap means a more useful check.</p>
      <div className="adaptive-metrics"><div><strong>{pct(r.pair_error_before)}% <ArrowRight size={13}/> {pct(r.pair_error_after)}%</strong><span>chance of backing the wrong cause, before → after</span></div><div><strong>{pct(r.pair_confidence_80_fraction)}%</strong><span>chance the result makes one cause at least 80% likely</span></div></div>
      <div className="adaptive-outcomes"><h4>What different results would mean</h4><p>Previews only. The real reading comes from the simulated device when you press the button.</p><div>{r.examples.map((e,i)=><article key={i}><small>{['If it comes back low','If it is in the middle','If it comes back high'][i]}</small><strong>{e.value.toFixed(1)} {r.unit}</strong><span>{short[e.leading_family]??e.leading_family} would lead</span>{plan.pair.map(f=><p key={f.id}><span>{short[f.id]??f.label}</span><b style={{color:colors[f.id]}}>{pct(e.family_weights[families.findIndex(x=>x.id===f.id)])}%</b></p>)}</article>)}</div></div>
      <div className="adaptive-action"><div><b>Take the reading, then look again.</b><p>The simulated device produces its own value. The twin updates the percentages and suggests the next check.</p></div><button className="button primary" disabled={!ready} onClick={()=>onAcquire(r)}><FlaskConical size={15}/>Take this measurement</button></div>
    </>}
    {!r&&<p>{plan.status==='supported'?'The readings so far point clearly to one cause, so another check would add little.':'None of the available checks would separate the causes enough to be worth it.'}</p>}
    <div className="adaptive-distinction"><b>Telling causes apart is not the same as making a better decision.</b><p>This box picks the most informative check. The box below asks a different question: is any check worth its cost and wait? Sometimes a check is informative but not worth it. Neither box tells a doctor what treatment to give.</p></div>
  </section>;
}
