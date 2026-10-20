"""Conditional multi-session fluid transport; no future BP or clinical recommendation."""
import numpy as np
from .model import advance,DURATION
from .mechanisms import base_cloud,assimilate,weighted_quantile


def simulate(patient_id,cutoff,rate,interval_hours=48,intake_ml=2400,residual_ml=800,cycles=3,evidence=()):
    cloud=base_cloud(patient_id,cutoff);w,_=assimilate(cloud,evidence)
    tissue=cloud.tissue_history[-1].copy()
    # Recompute tissue at session end with the same conservative transition.
    p=cloud.plasma_history[-1].copy();removed=np.zeros(len(w))
    for _ in range(DURATION-cutoff):p,tissue,removed=advance(p,tissue,removed,cloud.refill,cloud.reference,cloud.tissue_reference,rate)
    plasma=p;origin=plasma+tissue;entered=np.zeros(len(w));exited=np.zeros(len(w));rows=[]
    for cycle in range(cycles):
        # Spread authored intake/output over the interval, permitting the same refill dynamics.
        for _ in range(interval_hours*60):
            tissue+=intake_ml/1000/(interval_hours*60);entered+=intake_ml/1000/(interval_hours*60)
            out=np.minimum(tissue,residual_ml/1000/(interval_hours*60));tissue-=out;exited+=out
            plasma,tissue,_=advance(plasma,tissue,np.zeros(len(w)),cloud.refill,cloud.reference,cloud.tissue_reference,0)
        before=plasma+tissue
        removal=np.zeros(len(w))
        for _ in range(DURATION):plasma,tissue,removal=advance(plasma,tissue,removal,cloud.refill,cloud.reference,cloud.tissue_reference,rate)
        exited+=removal
        rows.append({'cycle':cycle+1,'start_total_fluid_l':round(float(w@before),3),
            'removed_ml':round(float(w@removal)*1000),'end_plasma_l':round(float(w@plasma),3),
            'end_tissue_l':round(float(w@tissue),3),'total_range_l':[round(weighted_quantile(plasma+tissue,w,q),3) for q in [.1,.9]]})
    error=float(np.max(np.abs(origin+entered-exited-plasma-tissue)))
    return {'status':'experimental','rows':rows,'mass_balance_max_error_l':error,
        'assumptions':{'interval_hours':interval_hours,'intake_ml_per_interval':intake_ml,'residual_output_ml_per_interval':residual_ml,'future_rate_ml_h':rate},
        'scope':'Conditional transport of fluid state across authored intervals and future sessions; no future BP, target recommendation or observed outcome.',
        'limitations':['Shared compartment equations; no paired longitudinal validation.','Intake/output and unchanged future removal settings are user-authored assumptions.','Residual output uses a simplified tissue-compartment exit; no physiological renal-function identification.']}
