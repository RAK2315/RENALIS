import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import { familyName } from './plain';

const causeColor:Record<string,string>={volume:'#307961',vascular:'#ac7346',cardiac:'#786398',mixed:'#487b95'};
const clamp=(v:number,lo=0,hi=1)=>Math.min(hi,Math.max(lo,v));

/* 1 · Landing: what happens during a dialysis session (illustration, not data). */
export function DialysisStory(){
  // Illustrative 4-hour session: BP holds, then falls below 90 late in the session.
  const pts:[number,number][]=[[0,132],[30,131],[60,128],[90,126],[120,121],[150,114],[170,106],[185,97],[200,88],[215,84],[240,86]];
  const x=(m:number)=>470+m/240*500, y=(bp:number)=>330-(bp-70)/80*230;
  const line=pts.map(([m,b],i)=>`${i?'L':'M'}${x(m).toFixed(1)} ${y(b).toFixed(1)}`).join(' ');
  return <figure className="fig-dialysis" aria-labelledby="fig-dialysis-cap">
    <div className="fd-panels"><svg className="fd-left" viewBox="-12 76 432 300" role="img" aria-label="A patient connected by two tubes to a dialysis machine that pulls out extra water.">
      {/* patient */}
      <g className="fd-patient">
        <circle cx="92" cy="118" r="30"/>
        <path d="M44 290 C44 200 60 165 92 165 C124 165 140 200 140 290 Z"/>
        <path className="fd-arm" d="M128 200 C160 214 182 226 205 232"/>
      </g>
      <text x="92" y="320" className="fd-label" textAnchor="middle">Patient</text>
      <text x="92" y="342" className="fd-sub" textAnchor="middle">kidneys no longer work</text>
      {/* tubes */}
      <path className="fd-tube" d="M205 232 C240 232 250 180 280 180"/>
      <path className="fd-tube back" d="M205 244 C245 244 255 262 280 262"/>
      <path className="fd-flow" d="M205 232 C240 232 250 180 280 180"/>
      <path className="fd-flow back" d="M280 262 C255 262 245 244 205 244"/>
      {/* machine */}
      <rect className="fd-machine" x="280" y="140" width="110" height="170" rx="12"/>
      <rect className="fd-screen" x="296" y="156" width="78" height="40" rx="5"/>
      <path className="fd-screen-line" d="M302 184 L318 176 L332 180 L346 170 L366 174"/>
      <rect className="fd-bag" x="304" y="222" width="62" height="70" rx="8"/>
      <rect className="fd-bag-water" x="304" y="252" width="62" height="40" rx="8"/>
      <text x="335" y="128" className="fd-label" textAnchor="middle">Dialysis machine</text>
      <text x="335" y="342" className="fd-sub" textAnchor="middle">pulls out 2–3 litres</text>
      <text x="335" y="362" className="fd-sub" textAnchor="middle">of extra water</text>
    </svg><svg className="fd-right" viewBox="440 60 550 310" role="img" aria-label="A four-hour timeline where blood pressure falls below 90 near the end. RENALIS warns about 30 minutes before.">
      {/* timeline */}
      <rect className="fd-danger" x="470" y={y(90)} width="500" height={330-y(90)}/>
      <line className="fd-threshold" x1="470" x2="970" y1={y(90)} y2={y(90)}/>
      <text x="478" y={y(90)+22} className="fd-danger-label">Too low (below 90)</text>
      {[0,60,120,180,240].map(m=><g key={m}><line className="fd-grid" x1={x(m)} x2={x(m)} y1="100" y2="330"/><text x={x(m)} y="352" className="fd-axis" textAnchor="middle">{m/60}h</text></g>)}
      <text x="470" y="80" className="fd-label">Blood pressure during one 4-hour session</text>
      <path className="fd-bp" d={line}/>
      <g className="fd-warn"><line x1={x(170)} x2={x(170)} y1="100" y2="330"/><circle cx={x(170)} cy={y(106)} r="7"/><text x={x(170)-10} y="120" textAnchor="end">RENALIS warns here</text><text x={x(170)-10} y="140" textAnchor="end" className="fd-sub">≈30 min before the drop</text></g>
      <g className="fd-crash"><circle cx={x(205)} cy={y(86)} r="9"/><text x="984" y={y(86)+36} textAnchor="end">Dizzy, can faint</text></g>
      <line className="fd-playhead" x1={x(0)} x2={x(0)} y1="96" y2="334"/>
    </svg></div>
    <figcaption id="fig-dialysis-cap"><b>What a bad session looks like.</b> Water comes out faster than the body can cope, and blood pressure slides below 90 late in the session. Today, staff usually notice only after it happens. <span>Illustration, not patient data.</span></figcaption>
  </figure>;
}

/* 2 · Step 2: two water tanks driven by the twin's real numbers. */
export function WaterTanks({tissueL,plasmaL,refillLh,removalMlH,removedMl,sbp}:{tissueL:number;plasmaL:number;refillLh:number;removalMlH:number;removedMl:number;sbp?:number}){
  const refillMl=Math.round(refillLh*1000), gap=removalMlH-refillMl;
  const tank=(fill:number)=>{const h=180*clamp(fill);return {y:250-h,h};};
  const t=tank(tissueL/3.6), p=tank(plasmaL/3.5), bag=tank(removedMl/4000);
  const speed=(mlh:number)=>({animationDuration:`${(1400/Math.max(mlh,100)).toFixed(2)}s`} as CSSProperties);
  const bpTone=sbp===undefined?'':sbp<90?'low':sbp<105?'near':'';
  return <figure className="fig-tanks">
    <svg viewBox="0 0 760 300" role="img" aria-label={`Water in the tissues ${tissueL.toFixed(2)} litres refills the blood at ${refillMl} millilitres per hour. The machine removes ${removalMlH} millilitres per hour from ${plasmaL.toFixed(2)} litres of blood water.`}>
      <defs><clipPath id="ft-tissue"><rect x="40" y="70" width="150" height="180" rx="14"/></clipPath><clipPath id="ft-blood"><rect x="300" y="70" width="150" height="180" rx="14"/></clipPath><clipPath id="ft-bag"><rect x="580" y="110" width="120" height="140" rx="14"/></clipPath></defs>
      <text x="115" y="40" className="ft-title" textAnchor="middle">Tissues</text><text x="115" y="60" className="ft-sub" textAnchor="middle">water stored in the body</text>
      <text x="375" y="40" className="ft-title" textAnchor="middle">Blood</text><text x="375" y="60" className="ft-sub" textAnchor="middle">water in the blood vessels</text>
      <text x="640" y="80" className="ft-title" textAnchor="middle">Machine</text><text x="640" y="100" className="ft-sub" textAnchor="middle">water removed so far</text>
      <g clipPath="url(#ft-tissue)"><rect className="ft-water tissue" x="40" y={t.y} width="150" height={t.h+20}/></g>
      <g clipPath="url(#ft-blood)"><rect className="ft-water blood" x="300" y={p.y} width="150" height={p.h+20}/></g>
      <g clipPath="url(#ft-bag)"><rect className="ft-water removed" x="580" y={bag.y} width="120" height={bag.h+20}/></g>
      <rect className="ft-tank" x="40" y="70" width="150" height="180" rx="14"/><rect className="ft-tank" x="300" y="70" width="150" height="180" rx="14"/><rect className="ft-tank" x="580" y="110" width="120" height="140" rx="14"/>
      <text x="115" y="235" className="ft-value" textAnchor="middle">{tissueL.toFixed(2)} L</text>
      <text x="375" y="235" className="ft-value" textAnchor="middle">{plasmaL.toFixed(2)} L</text>
      <text x="640" y="235" className="ft-value" textAnchor="middle">{(removedMl/1000).toFixed(2)} L</text>
      <path className="ft-pipe" d="M190 210 H300"/><path className="ft-flow" style={speed(refillMl)} d="M190 210 H300"/>
      <path className="ft-pipe" d="M450 210 H580"/><path className="ft-flow out" style={speed(removalMlH)} d="M450 210 H580"/>
      <text x="245" y="194" className="ft-rate" textAnchor="middle">refill</text><text x="245" y="240" className="ft-rate-num" textAnchor="middle">{refillMl} mL/h</text>
      <text x="515" y="194" className="ft-rate" textAnchor="middle">removal</text><text x="515" y="240" className="ft-rate-num out" textAnchor="middle">{removalMlH} mL/h</text>
      {sbp!==undefined&&<g className={`ft-bp ${bpTone}`}><rect x="318" y="84" width="114" height="34" rx="17"/><text x="375" y="106" textAnchor="middle">BP {Math.round(sbp)} mmHg</text></g>}
    </svg>
    <figcaption className={gap>0?'draining':'holding'}>{gap>0
      ?<><b>The machine takes water out {gap} mL/h faster than her body refills the blood.</b> So the blood tank slowly empties, and that is what makes blood pressure fall.</>
      :<><b>Her body is refilling the blood as fast as the machine removes water.</b> The blood tank holds steady, so pressure should hold too.</>}</figcaption>
  </figure>;
}

/* 3 · Step 4: one bar split between the four causes; animates when a reading arrives. */
export function CauseShift({families,latest}:{families:{id:string;weight:number}[];latest?:{id:number;channel:string;value:number;unit:string;before:number[];after:number[]}}){
  const now=families.map(f=>f.weight), before=latest?.before;
  const [shown,setShown]=useState<number[]>(before??now);
  useEffect(()=>{setShown(before??now);const t=setTimeout(()=>setShown(now),350);return()=>clearTimeout(t);},[latest?.id,now.join(',')]); // eslint-disable-line react-hooks/exhaustive-deps
  const lead=families.reduce((a,f,i)=>f.weight>families[a].weight?i:a,0);
  const bar=(w:number[],label:string,live=false)=><div className="cs-row"><span>{label}</span><div className={`cs-bar ${live?'live':''}`}>{families.map((f,i)=><i key={f.id} style={{width:`${(w[i]??0)*100}%`,background:causeColor[f.id]}} title={`${familyName[f.id]}: ${Math.round((w[i]??0)*100)}%`}>{(w[i]??0)>=.12&&<b>{Math.round((w[i]??0)*100)}%</b>}</i>)}</div></div>;
  return <div className="cause-shift" aria-live="polite">
    <div className="cs-head"><h3>Where the four causes stand</h3><div className="cs-legend">{families.map(f=><span key={f.id}><i style={{background:causeColor[f.id]}}/>{familyName[f.id]}</span>)}</div></div>
    {before&&bar(before,'Before the last reading')}
    {bar(shown,before?'After it':'Right now',true)}
    <p>{latest&&before
      ?<>The new reading moved <b style={{color:causeColor[families[lead].id]}}>{familyName[families[lead].id].toLowerCase()}</b> from {Math.round(before[lead]*100)}% to {Math.round(now[lead]*100)}%. Each reading shifts the bar towards the causes that expected it.</>
      :<>All four causes still fit equally well. Press <b>Take this measurement</b> below and watch this bar shift towards the cause the reading supports.</>}</p>
  </div>;
}

/* 4 · Test results: 100-dot grids for real-data warnings. */
export function AlarmDots({sensitivity,ppv}:{sensitivity:number;ppv:number}){
  const caught=Math.round(sensitivity*100), right=Math.round(ppv*100);
  const grid=(n:number,hit:string,miss:string)=><div className="ad-grid" aria-hidden="true">{Array.from({length:100},(_,i)=><i key={i} className={i<n?hit:miss} style={{animationDelay:`${i*9}ms`}}/>)}</div>;
  return <div className="alarm-dots">
    <figure><figcaption><b>Of every 100 real drops…</b></figcaption>{grid(caught,'hit','miss')}<div className="ad-key"><span><i className="hit"/>{caught} warned in time</span><span><i className="miss"/>{100-caught} missed</span></div></figure>
    <figure><figcaption><b>Of every 100 warnings…</b></figcaption>{grid(right,'hit','false')}<div className="ad-key"><span><i className="hit"/>{right} were real drops</span><span><i className="false"/>{100-right} false alarms</span></div></figure>
    <p>It catches most drops, but sounds too many false alarms to use on real patients yet. Tested on real hospital records (HEMOBP) from patients the model never saw.</p>
  </div>;
}
