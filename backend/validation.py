"""Predeclared independent synthetic policy evaluation, not a clinical study."""
from pathlib import Path
import json,hashlib
import numpy as np
from . import mechanisms as m

PROTOCOL={'version':'policy-holdout/0.4','seeds':list(range(24)),'seed_base':720041,
 'regimes':['volume','vascular','cardiac','mixed','omitted','noisy','basic_unit','late_failure'],
 'policies':['no_observation','fixed_cuff','information_gain','decision_value'],'horizon':30,
 'rates':[350,500,650,800,950,1100,1250,1400],'budget':'At most one acquisition; failure incurs burden and waiting',
 'bootstrap':'Shared-history seed blocks; 500 paired resamples','development_note':'Written before first evaluation; do not tune against this report and call it untouched.'}


def run():
    rows=[];rates=PROTOCOL['rates'];steps=np.arange(1,31);rngb=np.random.default_rng(27104)
    for seed in PROTOCOL['seeds']:
        for ri,regime in enumerate(PROTOCOL['regimes']):
            rng=np.random.default_rng(PROTOCOL['seed_base']+seed*101+ri)
            end=float(rng.uniform(96,109));slope=float(rng.uniform(.28,.52));delay=5 if regime=='late_failure' else 0
            history=tuple({'minute':t,'sbp':round(end+slope*(90-t)+.4*np.sin(t/11),2) if t%5==0 else None,
                'quality':'valid' if t%5==0 else 'missing','uf_ml_h':1400,'removed_ml':round(1400*t/60)} for t in range(91))
            prior={'initial_plasma':3.2,'target_l':2.8,'refill_l_h':.80,'baseline_sbp':end+slope*90}
            cloud=m.infer(history,prior);weights=m.normalize(cloud.log_weights)
            immediate=np.column_stack([m.decision_losses(m.project(cloud,r),2100,2800) for r in rates])
            delayed=np.column_stack([m.decision_losses(m.project(cloud,r,delay_minutes=delay),2100,2800) for r in rates])
            channels=['repeat_bp'] if regime=='basic_unit' else list(m.CHANNELS)
            failure=.4 if regime=='late_failure' else .1;noise_mult=2.5 if regime=='noisy' else 1.
            candidates=[m.measurement_value(cloud,weights,delayed,c,delay,immediate_losses=immediate,
                failure_probability=failure,noise_multiplier=noise_mult) for c in channels]
            by_channel={c['channel']:c for c in candidates}
            info=max(candidates,key=lambda c:c['information_gain_bits']);decision=max(candidates,key=lambda c:c['net_value'])
            alpha=[.043,.004,.018,.026,-.008,.02,.035,.03][ri]*float(rng.uniform(.8,1.2))
            curve=-slope*steps-.0008*steps**2
            if regime=='mixed':curve-=1.5*np.sin(steps/8)
            if regime=='omitted':curve-=6*(steps>=17)
            def score(rate,wait):
                bp=end+curve+alpha*(1400-rate)*np.maximum(0,steps-wait)/60
                minimum=bp.min();remaining=max(0,2800-2100-(1400*wait+rate*(30-wait))/60)
                return float(2*(minimum<=90)+.2*max(0,90-minimum)/20+.8*remaining/700)
            oracle=min(score(r,wait) for wait in sorted(set([0,delay])) for r in rates)
            means={'repeat_bp':end-slope*delay,'relative_blood_volume':[85,94,90,88,97,89,86,87][ri],
                   'cardiac_output':[3.9,5.1,3.6,4.2,5.8,4.0,3.9,4.1][ri]}
            observations={c:means[c]+rng.normal(0,m.CHANNELS[c]['noise']*noise_mult*1.15) for c in channels}
            failed={c:bool(rng.random()<failure) for c in channels}
            selections={'no_observation':None,'fixed_cuff':by_channel['repeat_bp'],
                'information_gain':info,'decision_value':decision if decision['net_value']>.001 else None}
            for policy,candidate in selections.items():
                w=weights;wait=delay if candidate else 0;losses=delayed if candidate else immediate
                channel=candidate['channel'] if candidate else None
                if candidate and not failed[channel]:
                    value=observations[channel];mean=m.sensor_prediction(cloud,channel,90+delay)
                    ll=-.5*((mean-value)/(m.CHANNELS[channel]['noise']*noise_mult))**2
                    w=m.normalize(np.log(np.maximum(weights,1e-300))+ll)
                choice=int(np.argmin(w@losses));burden=m.CHANNELS[channel]['cost']*.5 if channel else 0
                rows.append({'seed':seed,'case':f'{seed:02}-{regime}','regime':regime,'policy':policy,'channel':channel,
                    'failed':failed[channel] if channel else False,'wait_minutes':wait,'burden':burden,
                    'rate_ml_h':rates[choice],'total_policy_regret':round(max(0,score(rates[choice],wait)-oracle)+burden+wait*.002,6),'score':round(score(rates[choice],wait),6),'oracle_score':round(oracle,6),
                    'maximum_family_support':round(float(m.family_mass(w).max()),6),
                    'confident_wrong':bool(m.family_mass(w).max()>=.8 and score(rates[choice],wait)-oracle>.05),'regret':round(max(0,score(rates[choice],wait)-oracle),6)})
    summaries=[]
    for policy in PROTOCOL['policies']:
        subset=[r for r in rows if r['policy']==policy];v=np.array([r['regret'] for r in subset])
        reference={r['case']:r['regret'] for r in rows if r['policy']=='fixed_cuff'}
        deltas={s:np.mean([r['regret']-reference[r['case']] for r in subset if r['seed']==s]) for s in PROTOCOL['seeds']}
        a=np.array(list(deltas.values()));draw=rngb.integers(0,len(a),(500,len(a)))
        summaries.append({'policy':policy,'cases':len(subset),'mean_regret':round(float(v.mean()),5),
            'mean_total_policy_regret':round(float(np.mean([r['total_policy_regret'] for r in subset])),5),
            'p95_regret':round(float(np.quantile(v,.95)),5),'worst_regret':round(float(v.max()),5),
            'acquisitions':sum(r['channel'] is not None for r in subset),'failures':sum(r['failed'] for r in subset),
            'confident_wrong_cases':sum(r['confident_wrong'] for r in subset),
            'mean_burden':round(float(np.mean([r['burden'] for r in subset])),5),
            'cases_worse_than_cuff':sum(r['regret']>reference[r['case']]+1e-6 for r in subset),
            'paired_delta_vs_cuff':round(float(a.mean()),5),'seed_block_95_interval':np.quantile(a[draw].mean(axis=1),[.025,.975]).round(5).tolist(),
            'by_regime':{g:round(float(np.mean([r['regret'] for r in subset if r['regime']==g])),5) for g in PROTOCOL['regimes']}})
    cloud=m.infer(history,prior);w=m.normalize(cloud.log_weights)
    reference=m.measurement_value(cloud,w,immediate,'cardiac_output',0,quadrature_nodes=41)
    numerical=[{'nodes':n,'decision_value':(v:=m.measurement_value(cloud,w,immediate,'cardiac_output',0,quadrature_nodes=n))['decision_value'],
        'absolute_error_vs_41':round(abs(v['decision_value']-reference['decision_value']),5)} for n in [3,9,21]]
    return {'status':'evaluated','version':'policy-holdout/0.4','protocol':PROTOCOL,
        'protocol_sha256':hashlib.sha256(json.dumps(PROTOCOL,sort_keys=True).encode()).hexdigest(),
        'analysis_amendment':{'version':'metric-audit/0.4.1','policy_unchanged':True,'reason':'Oracle now includes the allowed waiting-prefix profiles, preventing negative regret being clipped against an incomplete immediate-only grid. Initial report retained separately. Total-policy regret additionally reports acquisition burden and the declared waiting penalty, separately from physiological regret. Confident-wrong uses descriptive support >=0.8 and regret >0.05; this metric was added after first evaluation, not predeclared.'},
        'model_version':m.VERSION,'cases':len(rows)//4,'summaries':summaries,'numerical_check':numerical,'records':rows,
        'limitations':['Independent authored additive futures and sensor distributions; not clinical efficacy.',
            'Held-out score is a frozen research task, not global generalization.','Mixed/omitted regimes are stress cases, not verified clinical mechanisms.',
            'One-acquisition policy; no multi-step or patient benefit claim.','Numerical check is a diagnostic case, not an exhaustive integration-accuracy bound.']}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    (root/'docs/evaluation-protocol-v04.json').write_text(json.dumps(PROTOCOL,indent=2))
    report=run();(root/'docs/policy-validation-v04.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'cases':report['cases'],'summaries':report['summaries'],'numerical_check':report['numerical_check']},indent=2))
