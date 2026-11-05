import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, Check, Compass, X } from 'lucide-react';
import type { WorkspacePage } from './Experience';

type TourStep={page:WorkspacePage;minute:number;title:string;seeing:string;meaning:string;tryThis:string;selector:string};

// The tour follows one kidney doctor through one alert, from the warning to the written decision.
export const tourSteps:TourStep[]=[
  {page:'cockpit',minute:70,selector:'.forecast-alert',
    title:'1. An alert comes in',
    seeing:'You are the kidney doctor on shift, looking after several dialysis chairs. Seventy minutes into Meera’s session, her twin raises an alert: a drop is likely soon.',
    meaning:'Her latest blood pressure, 111, still looks normal. But in 82 of every 100 simulated futures, it falls below 90 within the next 30 minutes. The twin gives you about half an hour to act, instead of finding out after she feels faint.',
    tryThis:'Drag the Session time slider back to minute 50, where the risk is 0%, then forward to 70 again to watch the alert appear.'},
  {page:'cockpit',minute:70,selector:'.health-record',
    title:'2. Check who she is',
    seeing:'Before deciding anything, you look at her record: blood tests, diagnoses, medicines, and her heart rate from a smartwatch.',
    meaning:'Her albumin is low, so the twin expects her body to refill the blood more slowly than average. Her heart rate is rising, which means her body is working to hold the pressure up. The twin shows which parts of the record change the forecast, and which it does not use.',
    tryThis:'Open “How her record changes the forecast” to see what each field does.'},
  {page:'cockpit',minute:70,selector:'.scenario-panel',
    title:'3. Try a gentler setting, safely',
    seeing:'The machine is removing 1,150 millilitres of water an hour. You wonder what would happen if it went slower.',
    meaning:'The twin runs the same 192 copies of Meera forward with the new setting. It shows the new risk and the cost: how much more water would stay in her body for later. Nothing here changes a real machine.',
    tryThis:'Drag Water removal speed down to 1,000. The risk falls from 82% to almost zero, for about 75 millilitres more water left for later. Press “Save this scenario” to keep it for your note.'},
  {page:'investigation',minute:70,selector:'#journey-physiology',
    title:'4. Ask why her pressure is falling',
    seeing:'You open the step-by-step story to see the reason. The two water tanks show where her water is right now.',
    meaning:'The machine takes water out of her blood faster than her body can refill it from the tissues. So the blood tank slowly empties, and that is what makes her pressure fall. Step 1, just above, shows why: she refills more slowly than an average patient.',
    tryThis:'Compare the green refill speed with the red removal speed. Then tap a label under the picture, such as “Heart pumping”, to read what it means.'},
  {page:'investigation',minute:70,selector:'#journey-compare',
    title:'5. Four possible reasons',
    seeing:'The twin does not give you a single answer. It shows four reasons that could explain the same falling readings.',
    meaning:'Not enough blood volume, blood vessels not tightening, the heart not pumping harder, or a mix. Right now all four fit equally well, but they predict different futures and call for different responses. Guessing is not good enough.',
    tryThis:'Look at “BP in 30 min” on each card. Then drag the “what if” slider and see how each reason predicts something different.'},
  {page:'investigation',minute:70,selector:'#journey-measure',
    title:'6. Order the one check that settles it',
    seeing:'The twin suggests one extra test, and shows the result each reason would expect from it.',
    meaning:'A test is useful when the reasons expect very different results, because then the real result clearly points one way. The twin also shows what the test is worth: how much it lowers the chance of backing the wrong reason.',
    tryThis:'Press “Take this measurement”. The simulated device returns a value. Scroll up to the coloured bar: the reasons that predicted it grow, and the others shrink.'},
  {page:'investigation',minute:70,selector:'#journey-audit',
    title:'7. Write your decision',
    seeing:'Everything you saw is in the log: each reading, how it moved the four reasons, and any correction.',
    meaning:'You make the decision, not the twin. Your note is stored next to the evidence, and nothing is ever deleted, so a colleague can see later exactly what you saw and why you acted.',
    tryThis:'Type a short note, for example “Slowed removal to 1,000 at minute 70; heart-pumping test ordered”, and press Save note. You can also download the record in the standard hospital format (FHIR).'},
  {page:'investigation',minute:70,selector:'#journey-verify',
    title:'8. How far to trust it',
    seeing:'As a doctor, you will ask how well this works on real patients. Step 6 answers that.',
    meaning:'On real records from 176 patients it had never seen, it warned in time for 60% of drops, and 15% of its warnings were right. That is in the same range as published research systems. It is a research prototype, not ready for patients yet.',
    tryThis:'Look at the two dot grids. Left: of 100 real drops, how many it warned about. Right: of 100 warnings, how many were real.'},
];

export default function GuidedTour({step,onStep,onClose,onShow}:{step:number;onStep:(step:number)=>void;onClose:()=>void;onShow:()=>void}){
  const {title,seeing,meaning,tryThis,selector}=tourSteps[step];
  const [targetReady,setTargetReady]=useState(false);
  const [box,setBox]=useState<{left:number;width:number}|null>(null);
  const autoShown=useRef(-1);

  // On wide screens, sit as a strip under the content column instead of covering the middle of it.
  useEffect(()=>{
    const place=()=>{
      const main=document.querySelector('.main-content');
      if(!main||window.innerWidth<=850){setBox(null);return;}
      const r=main.getBoundingClientRect();
      setBox({left:r.left+16,width:r.width-32});
    };
    place();
    window.addEventListener('resize',place);
    return()=>window.removeEventListener('resize',place);
  },[]);

  useEffect(()=>{
    setTargetReady(false);
    autoShown.current=-1;
    const highlight=()=>{
      const target=document.querySelector(selector);
      if(!target)return false;
      target.classList.add('tour-focus');
      setTargetReady(true);
      if(autoShown.current!==step){
        autoShown.current=step;
        target.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
      }
      return true;
    };
    const observer=new MutationObserver(()=>{if(highlight())observer.disconnect();});
    if(!highlight())observer.observe(document.querySelector('.main-content')??document.body,{childList:true,subtree:true});
    return()=>{observer.disconnect();document.querySelectorAll('.tour-focus').forEach(el=>el.classList.remove('tour-focus'));};
  },[step,selector]);

  return <section className={`guided-tour ${box?'strip':''}`} style={box?{left:box.left,width:box.width}:undefined} aria-label="Guided walkthrough" role="dialog" aria-live="polite">
    <div className="tour-heading">
      <span><Compass size={16}/>A doctor’s view · step {step+1} of {tourSteps.length}</span>
      <div className="tour-actions">
        <button className="text-button" disabled={step===0} onClick={()=>onStep(step-1)}><ArrowLeft size={14}/>Back</button>
        <button className="button light" disabled={!targetReady} onClick={onShow}>{targetReady?'Scroll to it':'Loading…'}</button>
        <button className="button primary" onClick={()=>step===tourSteps.length-1?onClose():onStep(step+1)}>{step===tourSteps.length-1?<><Check size={14}/>Finish</>:<>Next<ArrowRight size={14}/></>}</button>
        <button className="icon-button" onClick={onClose} aria-label="Close walkthrough"><X size={16}/></button>
      </div>
    </div>
    <div className="tour-progress" aria-label={`Step ${step+1} of ${tourSteps.length}`}>
      {tourSteps.map((s,i)=><button key={s.title} className={i===step?'current':i<step?'done':''} aria-label={`Walkthrough step ${i+1}: ${s.title}`} aria-current={i===step?'step':undefined} onClick={()=>onStep(i)}/>)}
    </div>
    <div className="tour-body">
      <div className="tour-intro"><h2>{title}</h2><p>{seeing}</p></div>
      <div className="tour-meaning"><span>What it tells you</span><p>{meaning}</p></div>
      <div className="tour-observe"><span>Your move</span><p>{tryThis}</p></div>
    </div>
  </section>;
}
