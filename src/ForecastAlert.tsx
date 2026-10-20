import { Activity, Clock3, ShieldCheck } from 'lucide-react';
import type { Twin } from './types';

export default function ForecastAlert({ twin }: { twin: Twin }) {
  const { status, crossing_fraction, lead_minutes, reason } = twin.alert;
  const forecast = status === 'monitor' || status === 'review';
  const title = status === 'current_event' ? 'Current low BP' : status === 'insufficient' ? 'Fresh reading needed' : status === 'complete' ? 'Session complete' : status === 'review' ? 'Review forecast' : 'Monitoring';
  return <section className={`forecast-alert ${status}`} aria-label="Patient observation and forecast status">
    <div className="eyebrow">{forecast ? `NEXT ${twin.horizon} MINUTES` : status === 'current_event' ? 'CURRENT OBSERVATION' : status === 'complete' ? 'SESSION SUMMARY' : 'DATA AVAILABILITY'}</div>
    <div className="alert-title"><Activity size={19} /><span>{title}</span></div>
    {forecast && crossing_fraction !== null ? <div className="alert-number">{Math.round(crossing_fraction * 100)}%<span>of model particles cross 90 mmHg</span></div> : status === 'current_event' ? <div className="alert-number">{twin.latest.sbp}<span>mmHg · latest valid systolic BP</span></div> : status === 'insufficient' ? <div className="alert-number">{twin.bp_age_minutes}<span>minutes since the last valid BP</span></div> : <div className="completed-mark"><ShieldCheck size={30} /><span>No further treatment forecast</span></div>}
    <p>{reason}</p>
    <div className="alert-meta"><span>{status === 'current_event' ? 'Current event · not an advance warning' : status === 'insufficient' ? 'Prospective alert withheld' : status === 'complete' ? `${twin.cutoff} minutes replayed` : lead_minutes ? `Median modeled crossing: +${lead_minutes} min` : 'Patient-specific ensemble · uncalibrated'}</span><Clock3 size={14} /></div>
  </section>;
}
