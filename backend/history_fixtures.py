"""Synthetic completed sessions. Hidden truth is confined to fixture generation."""
from functools import lru_cache
import numpy as np


@lru_cache(maxsize=8)
def completed_sessions(patient_id):
    from .model import PATIENTS,advance,pressure
    p=PATIENTS[patient_id];rng=np.random.default_rng(p.seed+8100);sessions=[]
    for index in range(6):
        rate=int(np.clip(p.uf_ml_h+rng.normal(0,90),350,1400))
        target=int(p.target_ml+rng.normal(0,140));baseline=float(p.baseline_sbp+rng.normal(0,3))
        refill=float(np.clip(p.refill_true+rng.normal(0,.04),.35,1.45))
        plasma=p.initial_plasma;tissue=target/1000;removed=0.;readings=[]
        for minute in range(181):
            if minute%15==0:
                readings.append({'minute':minute,'sbp':round(float(pressure(plasma,p.initial_plasma,baseline,p.compensation)+rng.normal(0,1.2)),1),'quality':'valid'})
            plasma,tissue,removed=advance(plasma,tissue,removed,refill,p.initial_plasma,target/1000,rate)
        sessions.append({'session':f'S-{p.prior_sessions-5+index:03}', 'label':f'{(6-index)*2} days earlier',
            'available_minute':-(6-index)*2880,'duration':180,'mean_uf_ml_h':rate,'target_ml':target,
            'reference_plasma_l':p.initial_plasma,'removed_ml':round(removed*1000),'quality':'valid',
            'source':'Synthetic completed session: raw preceding BP and machine record','readings':readings})
    return tuple(sessions)
