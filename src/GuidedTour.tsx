import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, Check, Compass, X } from 'lucide-react';
import type { WorkspacePage } from './Experience';

type TourStep={page:WorkspacePage;title:string;seeing:string;meaning:string;tryThis:string;selector:string};

export const tourSteps:TourStep[]=[
  {page:'investigation',selector:'#journey-memory',
    title:'Learning from the past',
    seeing:'Meera is 80 minutes into a four-hour dialysis session. Before predicting anything, the twin studies her earlier sessions.',
    meaning:'The left number is how fast an average patient’s body moves water back into the blood. The right number is Meera’s own rate, learned from her history. A personal number makes the forecast fit her rather than an average person.',
    tryThis:'Open “See the past sessions it learned from” to see each earlier session and how low her blood pressure went.'},
  {page:'investigation',selector:'#journey-physiology',
    title:'What is happening inside her body',
    seeing:'A simple map of the patient: water in the tissues, water in the blood, the machine taking water out, the heart, and blood pressure.',
    meaning:'The machine pulls water out of the blood. The body tops the blood back up from the tissues. If the blood runs low, pressure falls. These numbers are the model’s estimates, not scans.',
    tryThis:'Click any box to read what it means and where its number comes from.'},
  {page:'investigation',selector:'#journey-compare',
    title:'Four possible causes',
    seeing:'Four cards, one for each reason her blood pressure could fall.',
    meaning:'All four explain her readings so far, but they predict different futures. The percentage shows how well each one fits. A high percentage means “fits best so far”, not “this is the diagnosis”.',
    tryThis:'Drag the “what if” water removal speed slider and watch each cause predict a different blood pressure 30 minutes from now.'},
  {page:'investigation',selector:'#journey-measure',
    title:'Which check would settle it?',
    seeing:'The planner compares three possible checks: re-checking blood pressure, a blood volume sensor, and a heart pumping measurement.',
    meaning:'It picks the check whose result would best tell the leading causes apart. The coloured bars show the result each cause expects. Where the bars do not overlap, the check is useful.',
    tryThis:'Press “Take this measurement”. A simulated reading arrives, the percentages update, and the planner suggests the next check.'},
  {page:'investigation',selector:'#journey-audit',
    title:'Nothing gets erased',
    seeing:'A log of every reading taken, including the failed ones.',
    meaning:'Each reading shows how it moved the percentages, for example 40% → 70%. Corrections are added on top and the original is never deleted, so a doctor could check the twin’s reasoning later.',
    tryThis:'Look at the before → after numbers on the reading you just took. You can also add a review note.'},
  {page:'investigation',selector:'#journey-verify',
    title:'How well does it actually work?',
    seeing:'Results from two separate tests: real hospital data, and a 192-case stress test.',
    meaning:'On real data it predicts the next blood pressure reading reasonably well, but raises too many false alarms. In the stress test, picking the smartest check did not beat simply re-checking blood pressure. We show that openly.',
    tryThis:'“Average miss” is how far off the forecast was, in mmHg. Lower is better.'},
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
      <span><Compass size={16}/>Guided demo · step {step+1} of {tourSteps.length}</span>
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
      <div className="tour-meaning"><span>What it means</span><p>{meaning}</p></div>
      <div className="tour-observe"><span>Try this</span><p>{tryThis}</p></div>
    </div>
  </section>;
}
