import { Activity, Clock3, ShieldCheck } from 'lucide-react';
import type { Twin } from './types';

export default function ForecastAlert({ twin }: { twin: Twin }) {
  const { status, crossing_fraction, lead_minutes } = twin.alert;
  const reason = {
    monitor: 'In most of the simulated futures, blood pressure stays above 90.',
    review: 'In many of the simulated futures, blood pressure falls below 90 within 30 minutes. A nurse or doctor should take a look.',
    insufficient: 'The last blood pressure reading is more than 15 minutes old, so the twin will not raise a warning until it gets a new one.',
    current_event: 'Blood pressure is already at or below 90, so this is happening now rather than an early warning.',
    complete: 'The dialysis session is over.',
  }[status];
  const forecast = status === 'monitor' || status === 'review';
  const title = status === 'current_event' ? 'Blood pressure is already low' : status === 'insufficient' ? 'Needs a fresh reading' : status === 'complete' ? 'Session finished' : status === 'review' ? 'A drop is likely soon' : 'Looks stable';
  return <section className={`forecast-alert ${status}`} aria-label="Patient observation and forecast status">
    <div className="eyebrow">{forecast ? `RISK IN THE NEXT ${twin.horizon} MINUTES` : status === 'current_event' ? 'RIGHT NOW' : status === 'complete' ? 'SESSION SUMMARY' : 'MISSING DATA'}</div>
    <div className="alert-title"><Activity size={19} /><span>{title}</span></div>
    {forecast && crossing_fraction !== null ? <div className="alert-number">{Math.round(crossing_fraction * 100)}%<span>chance blood pressure falls below 90</span></div> : status === 'current_event' ? <div className="alert-number">{twin.latest.sbp}<span>mmHg · latest blood pressure</span></div> : status === 'insufficient' ? <div className="alert-number">{twin.bp_age_minutes}<span>minutes since the last blood pressure reading</span></div> : <div className="completed-mark"><ShieldCheck size={30} /><span>Nothing left to forecast</span></div>}
    <p>{reason}</p>
    <div className="alert-meta"><span>{status === 'current_event' ? 'Already happening, so not an early warning' : status === 'insufficient' ? 'Warnings paused until a new reading' : status === 'complete' ? `${twin.cutoff} minutes played` : lead_minutes ? `If it drops, most likely in about ${lead_minutes} min` : 'Personal to this patient · not yet clinically checked'}</span><Clock3 size={14} /></div>
  </section>;
}
