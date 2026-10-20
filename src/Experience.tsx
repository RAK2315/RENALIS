import { lazy, Suspense, useEffect, useState } from 'react';
import { LoaderCircle } from 'lucide-react';
import Landing from './Landing';
import './experience.css';

const Workspace=lazy(()=>import('./App'));
const Research=lazy(()=>import('./Research'));
export type Navigate=(path:string)=>void;
export type WorkspacePage='cockpit'|'mechanisms'|'unit'|'history'|'evidence'|'investigation';
const views:WorkspacePage[]=['cockpit','mechanisms','unit','history','evidence','investigation'];
export default function Experience(){
  const [location,setLocation]=useState(()=>window.location.pathname+window.location.search);
  useEffect(()=>{const change=()=>setLocation(window.location.pathname+window.location.search);window.addEventListener('popstate',change);return()=>window.removeEventListener('popstate',change);},[]);
  function navigate(path:string){window.history.pushState(null,'',path);setLocation(path);window.scrollTo(0,0);}
  const url=new URL(location,window.location.origin);
  useEffect(()=>{if(url.hash){const timer=setTimeout(()=>document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView(),150);return()=>clearTimeout(timer);}},[location]);
  useEffect(()=>{document.title=url.pathname==='/research'?'RENALIS · Research & evidence':url.pathname==='/workspace'?'RENALIS · Patient workspace':'RENALIS · A clearer next question in dialysis';},[location]);
  if(url.pathname==='/workspace'){
    const view=url.searchParams.get('view') as WorkspacePage;
    const rawMinute=Number(url.searchParams.get('minute')??(url.searchParams.get('tour')==='1'?80:90));
    const minute=Number.isFinite(rawMinute)?Math.max(0,Math.min(240,Math.round(rawMinute))):90;
    const rawPatient=url.searchParams.get('patient')??'RNL-014';
    const patient=['RNL-014','RNL-027','RNL-032','RNL-041'].includes(rawPatient)?rawPatient:'RNL-014';
    const rawStep=Number(url.searchParams.get('step')??0);
    const step=Number.isFinite(rawStep)?Math.max(0,Math.min(5,Math.round(rawStep))):0;
    return <Suspense fallback={<div className="experience-loading"><LoaderCircle className="spin"/><p>Opening the research workspace…</p></div>}><Workspace initialPage={views.includes(view)?view:'cockpit'} initialPatient={patient} initialMinute={minute} startTour={url.searchParams.get('tour')==='1'} initialTourStep={step} onHome={()=>navigate('/')} onResearch={()=>navigate('/research')}/></Suspense>;
  }
  if(url.pathname==='/research')return <Suspense fallback={<div className="experience-loading"><LoaderCircle className="spin"/><p>Opening the research guide…</p></div>}><Research navigate={navigate}/></Suspense>;
  if(url.pathname!=='/')return <div className="route-not-found"><span className="eyebrow">RENALIS / 404</span><h1>This page is not in the workspace.</h1><p>Return to the introduction or open the patient twin.</p><button className="site-button dark" onClick={()=>navigate('/')}>Return home</button><button className="site-button outline" onClick={()=>navigate('/workspace')}>Open workspace</button></div>;
  return <Landing navigate={navigate}/>;
}
