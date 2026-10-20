import { ArrowRight, FlaskConical, GitBranch } from 'lucide-react';
import type { Candidate, Evidence, Family } from './mechanismTypes';

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
const short:Record<string,string>={volume:'Volume / refill',cardiac:'Cardiac response',vascular:'Vascular compensation',mixed:'Mixed response'};
const pct=(n:number)=>(n*100).toFixed(1);

export default function AdaptiveMeasurement({plan,families,ready,onAcquire}:{plan:DiscriminationPlan;families:Family[];ready:boolean;onAcquire:(c:Candidate)=>void}){
  const r=plan.recommended;
  const metric=(c:Experiment)=>plan.objective==='pair'?c.pair_information_bits:c.full_information_bits;
  const lo=r?Math.min(...r.ranges.map(f=>f.range[0])):0;
  const hi=r?Math.max(...r.ranges.map(f=>f.range[2])):1;
  const pos=(v:number)=>100*(v-lo)/Math.max(.001,hi-lo);
  return <section className="adaptive-plan" aria-label="Adaptive measurement planner" data-status={plan.status}>
    <div className="adaptive-heading"><span className="eyebrow"><GitBranch size={14}/> ADAPTIVE EVIDENCE PLANNER</span><span className="adaptive-badge">{plan.objective==='pair'?'Separate the remaining pair':'Compare the whole model bank'}</span></div>
    <h3>{r?`Next discriminator: ${r.label}`:plan.status==='supported'?'Model support has concentrated':'Uncertainty remains — no useful feasible discriminator'}</h3>
    {plan.latest_evidence?<p className="adaptive-observed"><b>Observed: {plan.latest_evidence.value} {plan.latest_evidence.unit}</b> at minute {plan.latest_evidence.observed_minute??plan.latest_evidence.available_minute}. The planner has recomputed from this result and all earlier released evidence.</p>:<p>No additional result is known yet. The planner compares noisy possible outcomes before selecting an experiment.</p>}
    {plan.latest_evidence?.channel==='cardiac_output'&&plan.objective==='pair'&&plan.pair.some(f=>f.id==='volume')&&plan.pair.some(f=>f.id==='cardiac')&&<p><b>Why did cardiac output leave two explanations?</b> In these equations, output can fall because circulating volume is depleted or because the modeled cardiac response is limited. This reading fits both; measuring circulating volume tests what they disagree about.</p>}
    <div className="adaptive-beliefs">{plan.pair.map(f=><div key={f.id} style={{borderColor:colors[f.id]}}><span>{short[f.id]}</span><strong style={{color:colors[f.id]}}>{pct(f.weight)}%</strong><small>current relative support</small></div>)}<p>{plan.objective==='pair'?<>Both explanations retain at least 10% support. Together they carry <b>{pct(plan.pair_mass)}%</b>; the other families retain {pct(plan.other_mass)}%. This result has not identified a unique cause.</>:<>Selection considers <b>all four families</b>; the two leading families are shown here for context.</>}</p></div>
    {r&&<>
      <div className="adaptive-reason"><span>WHY THIS MEASUREMENT?</span><p>Under the current evidence, {short[r.ranges[0].id].toLowerCase()} predicts a median of <b>{r.ranges[0].range[1].toFixed(2)} {r.unit}</b>, while {short[r.ranges[1].id].toLowerCase()} predicts <b>{r.ranges[1].range[1].toFixed(2)} {r.unit}</b>. The full noisy distributions give this channel the largest expected {plan.objective==='pair'?'separation of the remaining pair':'reduction in whole-bank uncertainty'} among the feasible channels.</p></div>
      <div className="adaptive-ranges" aria-label="Next measurement predictive ranges">{r.ranges.map(f=><div key={f.id}><span style={{color:colors[f.id]}}>{short[f.id]}</span><div className="measurement-range-track"><i style={{left:`${pos(f.range[0])}%`,width:`${pos(f.range[2])-pos(f.range[0])}%`,background:colors[f.id]}}/><b style={{left:`${pos(f.range[1])}%`,background:colors[f.id]}}/></div><strong>{f.range[0].toFixed(2)}–{f.range[2].toFixed(2)} <small>{r.unit}</small></strong></div>)}</div>
      <p className="journey-footnote">Conditional 10th–90th predictive ranges, including SD {r.noise_sd.toFixed(2)} {r.unit}. Overlap means some results will leave both explanations plausible. Observation at minute {r.observation_minute}; future removal stays at the current setting until acquisition.</p>
      <div className="adaptive-metrics"><div><strong>{metric(r).toFixed(3)} bits</strong><span>expected {plan.objective==='pair'?'pair':'whole-bank'} information</span></div><div><strong>{pct(r.pair_error_before)}% <ArrowRight size={13}/> {pct(r.pair_error_after)}%</strong><span>expected pair classification error</span></div><div><strong>{pct(r.pair_confidence_80_fraction)}%</strong><span>modeled chance of ≥80% pair support</span></div></div>
      <p className="journey-footnote">The last two metrics assume the cause is one of the displayed pair. They average possible results and failure; they are not patient outcome or diagnostic accuracy estimates.</p>
      <div className="adaptive-outcomes"><h4>How to interpret the next result</h4><p>These are possible readings, not values to enter. All four family weights are recomputed for each preview.</p><div>{r.examples.map((e,i)=><article key={i}><small>{['Lower possible reading','Middle possible reading','Higher possible reading'][i]}</small><strong>{e.value.toFixed(2)} {r.unit}</strong><span>{short[e.leading_family]} leads</span>{plan.pair.map(f=><p key={f.id}><span>{short[f.id]}</span><b style={{color:colors[f.id]}}>{pct(e.family_weights[families.findIndex(x=>x.id===f.id)])}%</b></p>)}<small>Other families: {pct(1-plan.pair.reduce((s,f)=>s+e.family_weights[families.findIndex(x=>x.id===f.id)],0))}%</small></article>)}</div></div>
      <div className="adaptive-action"><div><b>Acquire the result, then reassess.</b><p>The synthetic device supplies its own reading. No resolving number is chosen in advance. Timing, equipment and prior acquisitions constrain this choice.</p></div><button className="button primary" disabled={!ready} onClick={()=>onAcquire(r)}><FlaskConical size={15}/>Acquire next discriminator</button></div>
    </>}
    {!r&&<p>{plan.reason}</p>}
    {plan.candidates.length>0&&<details className="adaptive-ranking"><summary>Why this channel rather than the alternatives?</summary><div className="table-wrap"><table><thead><tr><th>Earliest feasible experiment</th><th>{plan.objective==='pair'?'Pair':'Whole-bank'} information</th><th>Decision value</th><th>Burden cost</th></tr></thead><tbody>{plan.candidates.map(c=><tr key={c.channel}><td>{c.label}<small>+{c.offset_minutes} minutes</small></td><td>{metric(c).toFixed(5)} bits</td><td>{c.decision_value.toFixed(4)}</td><td>{c.burden_cost.toFixed(4)}</td></tr>)}</tbody></table></div><p>{plan.method}</p></details>}
    <div className="adaptive-distinction"><b>Separating explanations and improving a decision are different questions.</b><p>This panel ranks information. The whole-policy selector below ranks action-loss value after waiting, failure and cost. A measurement can separate models while failing that value threshold. Neither panel prescribes clinical care.</p></div>
    <p className="journey-footnote">{plan.limitations} Repeated observations assume conditionally independent noise. The 80% display threshold, 10% support floor and 0.005-bit selection floor are declared research conventions. This experimental selector has not been evaluated by the frozen policy holdout. {plan.version}.</p>
  </section>;
}
