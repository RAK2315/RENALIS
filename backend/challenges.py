"""Reproducible observation-policy stress tests, not clinical validation.

Independent challenge futures use an additive response curve, not the twin's
two-compartment pressure projection. Sensor means and noise are authored here,
not obtained from the model's particles. Policies see only the released history.
"""
from functools import lru_cache
import json
from pathlib import Path
import numpy as np
from . import mechanisms as m

RATES = [350,500,650,800,950,1100,1250,1400]
POLICIES = ('bp_only','information_gain','decision_value')


def fixture(seed, family):
    rng=np.random.default_rng(45000+seed)
    cutoff=90
    end_bp=float(rng.uniform(96,106))
    slope=float(rng.uniform(.35,.57))
    # All three possible mechanisms share this available BP history.
    history=tuple({'minute':t,'sbp':round(end_bp+slope*(cutoff-t)+.5*np.sin(t/8),2) if t%5==0 else None,
                   'quality':'valid' if t%5==0 else 'missing','uf_ml_h':1400,'removed_ml':round(1400*t/60)} for t in range(cutoff+1))
    prior={'initial_plasma':3.2,'target_l':2.6,'refill_l_h':.78,'baseline_sbp':end_bp+slope*cutoff}
    # Additive saturation response deliberately differs from the fitted twin.
    sensitivity=[.046,.004,.019][family]*float(rng.uniform(.8,1.2))
    steps=np.arange(1,31)
    future=np.column_stack([end_bp-slope*steps+sensitivity*(1400-rate)*steps/60-
                           .0007*steps**2 for rate in RATES])
    minimum=future.min(axis=0)
    removed=1400*cutoff/60
    residual=np.maximum(0,2600-removed-np.array(RATES)*.5)
    losses=2*(minimum<=90)+.2*np.maximum(0,90-minimum)/20+.8*residual/max(2600-removed,500)
    truth={
        'repeat_bp':end_bp+float(rng.normal(0,3.8)),
        'relative_blood_volume':[85.2,93.8,89.8][family]+float(rng.normal(0,1.3)),
        'cardiac_output':[3.95,5.1,3.65][family]+float(rng.normal(0,.38)),
    }
    return history,prior,losses,truth


@lru_cache(maxsize=1)
def run_challenges():
    rows=[]
    for seed in range(36):
        for family in range(3):
            history,prior,true_losses,truth=fixture(seed,family)
            cloud=m.infer(history,prior)
            weights=m.normalize(cloud.log_weights)
            projected=[m.project(cloud,rate) for rate in RATES]
            losses=np.column_stack([m.decision_losses(p,cloud.removed_ml,2600) for p in projected])
            candidates=[m.measurement_value(cloud,weights,losses,channel,0) for channel in m.CHANNELS]
            baseline=int(np.argmin(weights@losses))
            candidates_by_channel={c['channel']:c for c in candidates}
            info=max(candidates,key=lambda c:c['information_gain_bits'])
            decision=max(candidates,key=lambda c:c['net_value'])
            selected={'bp_only':candidates_by_channel['repeat_bp']['channel'],'information_gain':info['channel'],
                      'decision_value':decision['channel'] if decision['net_value']>.001 else None}
            for policy,channel in selected.items():
                choice=baseline
                if channel:
                    posterior,_=m.assimilate(cloud,[{'id':1,'channel':channel,'available_minute':90,'value':truth[channel],'source':'challenge'}])
                    choice=int(np.argmin(posterior@losses))
                rows.append({'case':f'{seed:02d}-{family}','truth_family':m.FAMILIES[family]['id'],'policy':policy,
                             'channel':channel,'rate_ml_h':RATES[choice],'oracle_rate_ml_h':RATES[int(np.argmin(true_losses))],
                             'regret':round(float(true_losses[choice]-true_losses.min()),6),
                             'baseline_regret':round(float(true_losses[baseline]-true_losses.min()),6),
                             'burden':m.CHANNELS[channel]['cost']*.5 if channel else 0.,
                             'oracle_match':choice==int(np.argmin(true_losses))})
    summaries=[]
    for policy in POLICIES:
        subset=[r for r in rows if r['policy']==policy]
        summaries.append({'policy':policy,'cases':len(subset),'mean_regret':round(float(np.mean([r['regret'] for r in subset])),4),
                          'mean_baseline_regret':round(float(np.mean([r['baseline_regret'] for r in subset])),4),
                          'oracle_match_fraction':round(float(np.mean([r['oracle_match'] for r in subset])),3),
                          'mean_burden':round(float(np.mean([r['burden'] for r in subset])),4),
                          'acquisitions':sum(r['channel'] is not None for r in subset),
                          'worse_than_bp_only':sum(r['regret']>next(b['regret'] for b in rows if b['case']==r['case'] and b['policy']=='bp_only')+1e-6 for r in subset)})
    # Explicit failure/abstention challenges use the app engine, separately from
    # the independent policy benchmark; report provenance rather than pooling them.
    base=dict(patient_id='RNL-014',cutoff=90,rate=650,profile='constant',channels=list(m.CHANNELS),evidence=[])
    normal=m.analyze(**base)
    none=m.analyze(**{**base,'channels':[]})
    bp=m.analyze(**{**base,'channels':['repeat_bp']})
    contradiction=m.analyze(**{**base,'evidence':[{'id':1,'channel':'relative_blood_volume','available_minute':90,'value':120.,'source':'challenge'}]})
    low=m.analyze(**{**base,'cutoff':120})
    checks=[
        {'case':'Ambiguous BP','passed':normal['comparison_unresolved'] and all(f['fit_rmse_mm_hg']<3 for f in normal['families']),'observed':'Three close factual fits; different scenario preferences.'},
        {'case':'Uninformative immediate cuff','passed':bp['recommended_measurement'] is None,'observed':'A repeat pressure reading does not resolve mechanism ambiguity at this cutoff.'},
        {'case':'No device available','passed':none['recommended_measurement'] is None and none['comparison_unresolved'],'observed':'No substitute measurement is invented; unresolved state retained.'},
        {'case':'All-family contradiction','passed':contradiction['authority']=='contradicted' and not contradiction['measurement_candidates'],'observed':'Authority downgraded instead of forcing a winning explanation.'},
        {'case':'Already-low BP','passed':low['authority']=='current_event' and not low['measurement_candidates'],'observed':'No advance warning or research waiting schedule.'},
    ]
    return {'version':'observation-challenges/0.2','seed_base':45000,'cases':108,'observation_budget':1,
            'budget_definition':'At most one immediate observation from the same three channels; all channel costs fit a 0.055 raw-burden budget. Decision-value policy may abstain.',
            'method':'108 independently authored additive-response cases: 36 BP histories × three hidden response types. Every policy sees identical history and receives the same pre-generated channel value if it selects that channel. No twin projection generates scored future BP.',
            'metric':'Regret = selected profile loss minus minimum loss among the eight declared constant-rate profiles, scored on the independent synthetic future.',
            'summaries':summaries,'safeguards':checks,'records':rows,
            'limitations':['In-silico challenge performance is not clinical efficacy or validation.',
                          'The author chose the response families, sensor distributions, noise, and loss weights; findings depend on these assumptions.',
                          'Independent equations reduce self-scoring circularity but remain synthetic and share the same declared loss.',
                          'Decision value is an expectation under the twin: any acquired observation can worsen a particular comparison.',
                          'This suite does not evaluate delayed acquisition or longitudinal clinical outcomes.']}


if __name__=='__main__':
    report=run_challenges()
    destination=Path(__file__).resolve().parents[1]/'docs'/'diagnostic-replay-v04.json'
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'cases':report['cases'],'summaries':report['summaries'],'report':str(destination)},indent=2))
