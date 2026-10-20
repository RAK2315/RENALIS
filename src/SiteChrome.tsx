import type { MouseEvent, ReactNode } from 'react';
import { ArrowRight, ArrowUpRight, Droplets } from 'lucide-react';
import type { Navigate } from './Experience';

export function RouteLink({href,navigate,className,children,...props}:{href:string;navigate:Navigate;className?:string;children:ReactNode;'aria-label'?:string}){
  function follow(event:MouseEvent<HTMLAnchorElement>){if(!event.ctrlKey&&!event.metaKey&&!event.shiftKey&&!event.altKey&&event.button===0){event.preventDefault();navigate(href);}}
  return <a href={href} className={className} onClick={follow} {...props}>{children}</a>;
}
export function SiteHeader({navigate,research=false}:{navigate:Navigate;research?:boolean}){
  return <header className="site-header"><div className="site-nav"><RouteLink href="/" navigate={navigate} className="site-brand" aria-label="RENALIS home"><span><Droplets size={23} strokeWidth={1.5}/></span><div>RENALIS<small>A patient, in perspective.</small></div></RouteLink><nav aria-label="Main navigation"><RouteLink href="/#how-it-works" navigate={navigate} className="site-nav-link">How it works</RouteLink><RouteLink href="/research" navigate={navigate} className={`site-nav-link ${research?'selected':''}`}>Research & evidence</RouteLink><RouteLink href="/workspace?view=investigation" navigate={navigate} className="site-button dark small">Open workspace <ArrowUpRight size={15}/></RouteLink></nav></div></header>;
}
export function SiteFooter({navigate}:{navigate:Navigate}){
  return <footer className="site-footer"><div><RouteLink href="/" navigate={navigate} className="footer-wordmark">RENALIS <Droplets size={19}/></RouteLink><p>A focused dialysis digital twin research prototype.<br/>Synthetic patients. Open research. Inspectable assumptions.</p></div><div className="footer-links"><RouteLink href="/workspace?tour=1" navigate={navigate}>Guided demo <ArrowRight size={13}/></RouteLink><RouteLink href="/research#sources" navigate={navigate}>Research library <ArrowRight size={13}/></RouteLink><a href="/api/project-documents/project-guide" target="_blank" rel="noreferrer">Project guide <ArrowUpRight size={13}/></a><a href="/api/project-documents/license" target="_blank" rel="noreferrer">MIT code license <ArrowUpRight size={13}/></a></div><div className="footer-note">Built for the Digital Twin Challenge.<br/>A research demonstration; clinical benefit and readiness have not been established.</div></footer>;
}
