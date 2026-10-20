"""Preceding-session learning. The learner accepts records, never hidden simulator state."""
from functools import lru_cache
import hashlib
import json
import numpy as np


def learn(records, cutoff=0):
    from .model import advance, pressure
    eligible=[s for s in records if s['available_minute']<cutoff and s['quality']=='valid']
    grid=np.linspace(.35,1.45,45)
    compensation=np.linspace(6,34,8)
    refills=np.repeat(grid,len(compensation)); comps=np.tile(compensation,len(grid))
    estimates=[]
    for s in eligible:
        readings=[r for r in s['readings'] if r['quality']=='valid']
        if len(readings)<5:continue
        reference=np.full(len(refills),s['reference_plasma_l'])
        tissue_reference=np.full(len(refills),s['target_ml']/1000)
        plasma,tissue,removed=reference.copy(),tissue_reference.copy(),np.zeros(len(refills))
        by_minute={r['minute']:r['sbp'] for r in readings}
        baseline=readings[0]['sbp'];error=np.zeros(len(refills));count=0
        for minute in range(s['duration']+1):
            if minute in by_minute:
                error+=(pressure(plasma,reference,baseline,comps)-by_minute[minute])**2;count+=1
            if minute<s['duration']:
                plasma,tissue,removed=advance(plasma,tissue,removed,refills,reference,tissue_reference,s['mean_uf_ml_h'])
        mse=error/max(count,1)
        likelihood=np.exp(-.5*(mse-mse.min())/5.)
        likelihood/=likelihood.sum()
        mean=float(likelihood@refills)
        estimates.append({**{k:v for k,v in s.items() if k!='readings'},
            'refill_estimate_l_h':round(mean,3),'fit_rmse_mm_hg':round(float(np.sqrt(likelihood@mse)),2),
            'refill_sd':float(np.sqrt(likelihood@(refills-mean)**2)),
            'min_sbp':min(r['sbp'] for r in readings),'readings_count':len(readings)})
    # Shrink to the declared population reference; limited data never implies certainty.
    n=len(estimates);population=.88
    mean=(2*population+sum(s['refill_estimate_l_h'] for s in estimates))/(2+n)
    sd=max(.055,float(np.std([s['refill_estimate_l_h'] for s in estimates])) if n else .24,
           float(np.mean([s['refill_sd'] for s in estimates])) if n else .24)
    digest=hashlib.sha256(json.dumps(eligible,sort_keys=True).encode()).hexdigest()[:16]
    return {'refill_l_h':round(mean,4),'refill_sd':round(sd,4),'population_refill_l_h':population,
        'sessions_used':n,'history_digest':digest,'sessions':estimates,
        'method':'Grid likelihood on preceding measured synthetic BP trajectories, shrunk toward a population reference',
        'limitations':['Synthetic fixtures share a physiology family; not observed clinical personalization.',
            'Refill is conditional on the declared pressure equation; latent physiology need not be identifiable.',
            'Only completed records available before the cutoff enter learning.']}


@lru_cache(maxsize=8)
def patient_history(patient_id):
    from .history_fixtures import completed_sessions
    return learn(completed_sessions(patient_id))


def ablation(patient_id):
    from .history_fixtures import completed_sessions
    from .model import advance,pressure
    records=completed_sessions(patient_id);training=records[:4];held_out=records[4:]
    learned=learn(training)
    errors={'population':[],'learned_history':[]}
    for s in held_out:
        for label,refill in [('population',.88),('learned_history',learned['refill_l_h'])]:
            plasma=s['reference_plasma_l'];tissue=s['target_ml']/1000;removed=0
            values={r['minute']:r['sbp'] for r in s['readings']};baseline=values[0]
            for t in range(s['duration']+1):
                if t in values:errors[label].append(abs(float(pressure(plasma,s['reference_plasma_l'],baseline,18))-values[t]))
                plasma,tissue,removed=advance(plasma,tissue,removed,refill,s['reference_plasma_l'],s['target_ml']/1000,s['mean_uf_ml_h'])
    return {'patient_id':patient_id,'training_sessions':4,'held_out_sessions':2,
        'rows':[{'model':k,'mae_mm_hg':round(float(np.mean(v)),3),'observations':len(v)} for k,v in errors.items()],
        'scope':'Forward-session synthetic ablation; fixed compensation and shared simulator family; not clinical validation'}
