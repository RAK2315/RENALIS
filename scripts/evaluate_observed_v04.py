"""Audited HEMOBP evaluation; never overwrites the v0.3 historical result.

Authoritative session intervals and preceding completed sessions are used.
Only aggregate metrics and hashed split identifiers leave ignored data/.
"""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import HistGradientBoostingRegressor,HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error,average_precision_score,brier_score_loss,precision_recall_curve
from scripts.hemo import DATA,validate_file,FILES

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL={'version':'observed-evaluation/0.4','endpoint':'Next distinct measured SBP <=90; current SBP >90; elapsed gap 5-35 minutes',
 'split_seed':42,'calibration_seed':43,'max_fit_rows':100000,'bootstrap_seed':2040,'bootstrap_replicates':300,
 'threshold_target_recall':.75,'alarm_refractory_minutes':30,
 'session_clock_offset_hours':8,'max_elapsed_discrepancy_minutes':20,
 'clock_offset_status':'Empirical cross-table alignment assumption; source timezone semantics need independent confirmation',
 'history':'Only aggregates of sessions completed before the current session begins',
 'uf_conversion':'HEMOBP publication reports L/h; canonical rate_ml_h = uf * 1000',
 'forbidden_inputs':['current session weightend','current session future BP','current session future settings','current session outcome summaries']}


def session_time(d,column):
    s=d[column].astype(str)
    only_time=s.str.match(r'^\d{1,2}:')
    combined=d.keyindate.astype(str).str.slice(0,10)+' '+s
    return pd.to_datetime(s.where(~only_time,combined),format='mixed',errors='coerce')


def audit_cohort():
    for name in FILES:validate_file(DATA/name)
    d=pd.read_csv(DATA/'d1.csv',dtype={'pid':str})
    d['pid']=d.pid.str.replace(r'\.0$','',regex=True)
    d['start']=session_time(d,'dialysisstart');d['end']=session_time(d,'dialysisend')
    d.loc[d.end<d.start,'end']+=pd.Timedelta(days=1)
    d['start']+=pd.Timedelta(hours=PROTOCOL['session_clock_offset_hours'])
    d['end']+=pd.Timedelta(hours=PROTOCOL['session_clock_offset_hours'])
    source_sessions=len(d)
    d=d.dropna(subset=['start','end']).sort_values(['pid','start'])
    d=d[d.end.sub(d.start).dt.total_seconds().between(30*60,10*3600)].copy()
    overlap=d.start<d.groupby('pid').end.shift()
    ambiguous=overlap|overlap.groupby(d.pid).shift(-1,fill_value=False)
    ambiguous_count=int(ambiguous.sum());d=d[~ambiguous].drop_duplicates(['pid','start']).copy()
    d['session_id']=np.arange(len(d))
    v=pd.read_csv(DATA/'vip.csv',dtype={'pid':str},low_memory=False)
    v['pid']=v.pid.str.replace(r'\.0$','',regex=True)
    input_rows=len(v);v['timestamp']=pd.to_datetime(v.datatime,format='mixed',errors='coerce')
    v=v.dropna(subset=['timestamp','measuretime','sbp']);v=v[v.sbp.between(30,220)&v.time.between(0,300)].copy()
    v=pd.merge_asof(v.sort_values('timestamp'),d[['pid','start','end','session_id']].sort_values('start'),
        left_on='timestamp',right_on='start',by='pid',direction='backward',tolerance=pd.Timedelta(hours=10))
    discrepancy=((v.timestamp-v.start).dt.total_seconds()/60-v.time).abs()
    valid=v.session_id.notna()&(v.timestamp<=v.end)&discrepancy.le(PROTOCOL['max_elapsed_discrepancy_minutes'])
    matched_rows=int(valid.sum());v=v[valid].copy();v.session_id=v.session_id.astype(int)
    v['rate_ml_h']=pd.to_numeric(v.uf,errors='coerce')*1000
    # Repeated packets are reduced to their earliest availability within a verified interval.
    v=v.sort_values(['pid','session_id','timestamp']).drop_duplicates(['pid','session_id','measuretime'],keep='first')
    aggregate=v.groupby('session_id').agg(session_nadir=('sbp','min'),session_mean_sbp=('sbp','mean'),session_rate=('rate_ml_h','mean'),reading_count=('sbp','size'))
    d=d.join(aggregate,on='session_id').sort_values(['pid','start'])
    g=d.groupby('pid',sort=False)
    for source,name in [('session_nadir','prior_nadir'),('session_mean_sbp','prior_mean_sbp'),('session_rate','prior_rate'),('weightend','prior_end_weight')]:d[name]=g[source].shift()
    d['prior_session_count']=g.cumcount()
    d['prior_end']=g.end.shift()
    d['history_available']=d.prior_end.isna()|(d.prior_end<d.start)
    assert bool(d.history_available.all()),'Overlapping history cannot be used'
    features=['prior_nadir','prior_mean_sbp','prior_rate','prior_end_weight','prior_session_count']
    v=v.merge(d[['session_id']+features],on='session_id',validate='many_to_one')
    patient=pd.read_csv(DATA/'idp.csv',dtype={'pid':str})
    patient['pid']=patient.pid.str.replace(r'\.0$','',regex=True)
    v=v.merge(patient[['pid','birthday','DM','gender']],on='pid',validate='many_to_one')
    v['age']=v.timestamp.dt.year-pd.to_numeric(v.birthday,errors='coerce');v['diabetes']=pd.to_numeric(v.DM,errors='coerce');v['female']=(v.gender=='F').astype(int)
    v=v[v.age.between(18,100)].sort_values(['pid','session_id','timestamp'])
    g=v.groupby('session_id',sort=False)
    v['previous_sbp']=g.sbp.shift();v['previous_minutes']=(v.timestamp-g.timestamp.shift()).dt.total_seconds()/60
    v['trend_mm_hg_min']=(v.sbp-v.previous_sbp)/v.previous_minutes.replace(0,np.nan)
    v['next_sbp']=g.sbp.shift(-1);v['next_timestamp']=g.timestamp.shift(-1)
    v['next_minutes']=(v.next_timestamp-v.timestamp).dt.total_seconds()/60
    low=v.sbp.le(90);v['prior_low']=low.groupby(v.session_id).cumsum()-low.astype(int)
    v['event_type']=np.where(v.prior_low>0,'recurrence_context','first_event_context')
    cohort=v[v.sbp.gt(90)&v.next_minutes.between(5,35)].copy()
    audit={'input_machine_rows':input_rows,'session_table_rows':source_sessions,'usable_session_intervals':len(d),
        'ambiguous_overlapping_intervals_excluded':ambiguous_count,'matched_machine_rows':matched_rows,
        'unmatched_or_outside_interval_rows':input_rows-matched_rows,'distinct_bp_readings':len(v),
        'eligible_windows':len(cohort),'uf_source_unit':'L/h','uf_canonical_unit':'mL/h','uf_conversion_factor':1000,
        'rate_range_ml_h':[float(v.rate_ml_h.min()),float(v.rate_ml_h.max())],
        'session_clock_offset_hours':PROTOCOL['session_clock_offset_hours'],
        'median_elapsed_discrepancy_minutes':round(float(discrepancy[valid].median()),3),
        'clock_offset_status':PROTOCOL['clock_offset_status'],
        'current_session_end_fields_excluded':True,'history_end_before_current_start':bool(d.history_available.all()),
        'checksums':'All three versioned deposit files verified'}
    return cohort,features,audit


def cluster_interval(frame,delta):
    a=pd.DataFrame({'pid':frame.pid.to_numpy(),'delta':delta}).groupby('pid').delta.agg(['sum','count'])
    rng=np.random.default_rng(PROTOCOL['bootstrap_seed']);draws=rng.integers(0,len(a),size=(PROTOCOL['bootstrap_replicates'],len(a)))
    values=a['sum'].to_numpy()[draws].sum(axis=1)/a['count'].to_numpy()[draws].sum(axis=1)
    return [round(float(x),4) for x in np.quantile(values,[.025,.975])]


def run():
    cohort,history,audit=audit_cohort();print(json.dumps({'audit':audit}),flush=True)
    if len(cohort)<1000 or cohort.pid.nunique()<10:raise ValueError('Insufficient reconciled cohort; do not train on an unmatched subset.')
    train_i,test_i=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(cohort,groups=cohort.pid))
    development,test=cohort.iloc[train_i].copy(),cohort.iloc[test_i].copy()
    fit_i,cal_i=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=43).split(development,groups=development.pid))
    fit,cal=development.iloc[fit_i].copy(),development.iloc[cal_i].copy()
    groups=[set(f.pid) for f in [fit,cal,test]]
    assert not(groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
    manifest={name:sorted(hashlib.sha256(('RENALIS-v04:'+pid).encode()).hexdigest()[:16] for pid in set(f.pid)) for name,f in [('fit',fit),('calibration',cal),('test',test)]}
    split_hash=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    if len(fit)>100000:fit=fit.sample(100000,random_state=42)
    dyn=['sbp','dbp','rate_ml_h','blood_flow','time','dia_temp_value','conductivity','trend_mm_hg_min','previous_minutes']
    demo=dyn+['age','diabetes','female'];fused=demo+history
    predictions={'Last observed BP':test.sbp.to_numpy()};models=[]
    for label,cols in [('Dynamic only',dyn),('Demographics + dynamic',demo),('Preceding sessions + dynamic',fused)]:
        reg=HistGradientBoostingRegressor(max_iter=90,max_leaf_nodes=20,l2_regularization=8,random_state=42)
        reg.fit(fit[cols],fit.next_sbp);predictions[label]=reg.predict(test[cols])
        if cols==fused:
            q=float(np.quantile(abs(cal.next_sbp-reg.predict(cal[cols])),.9,method='higher'))
            coverage=float((abs(test.next_sbp-predictions[label])<=q).mean())
    truth=test.next_sbp.to_numpy()
    for label,pred in predictions.items():models.append({'label':label,'mae_mm_hg':round(float(mean_absolute_error(truth,pred)),3)})
    classifier=HistGradientBoostingClassifier(max_iter=90,max_leaf_nodes=16,l2_regularization=12,random_state=42)
    classifier.fit(fit[fused],fit.next_sbp.le(90).astype(int))
    def logits(f):
        scores=np.clip(classifier.predict_proba(f[fused])[:,1],1e-6,1-1e-6)
        return np.log(scores/(1-scores)).reshape(-1,1)
    calibrator=LogisticRegression(C=1.,random_state=42).fit(logits(cal),cal.next_sbp.le(90).astype(int))
    cv=calibrator.predict_proba(logits(cal))[:,1];prob=calibrator.predict_proba(logits(test))[:,1]
    precision,recall,thresholds=precision_recall_curve(cal.next_sbp.le(90).astype(int),cv)
    ids=np.where(recall[:-1]>=.75)[0];threshold=float(thresholds[ids[-1]]) if len(ids) else .5
    test['probability']=prob;test['alert']=prob>=threshold;test['event']=test.next_sbp.le(90)
    def metrics(f):
        tp=int((f.alert&f.event).sum());positives=int(f.event.sum());alerts=int(f.alert.sum())
        return {'windows':len(f),'positive_windows':positives,'sensitivity':round(tp/positives,4) if positives else None,
            'ppv':round(tp/alerts,4) if alerts else None,'false_positive_windows':int((f.alert&~f.event).sum())}
    # Consolidate alarm windows per authoritative session; report eligibility-specific exposure.
    consolidated=[]
    for _,g in test.groupby('session_id',sort=False):
        until=None
        for row in g.sort_values('timestamp').itertuples():
            if row.alert and (until is None or row.timestamp>=until):
                consolidated.append(bool(row.event));until=row.timestamp+pd.Timedelta(minutes=30)
    bins=[]
    for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
        mask=(prob>=lo)&(prob<hi if hi<1 else prob<=hi)
        bins.append({'lower':round(float(lo),1),'upper':round(float(hi),1),'count':int(mask.sum()),
            'mean_score':round(float(prob[mask].mean()),4) if mask.any() else None,
            'event_frequency':round(float(test.event.to_numpy()[mask].mean()),4) if mask.any() else None})
    delta=abs(truth-predictions['Preceding sessions + dynamic'])-abs(truth-predictions['Demographics + dynamic'])
    result={'status':'evaluated','version':'observed-evaluation/0.4','protocol':PROTOCOL,'audit':audit,
        'split':{'fit_patients':len(groups[0]),'calibration_patients':len(groups[1]),'test_patients':len(groups[2]),'patient_overlap':0,'manifest_sha256':split_hash},
        'test_rows':len(test),'test_sessions':int(test.session_id.nunique()),'models':models,
        'history_increment':{'paired_mae_delta_mm_hg':round(float(delta.mean()),4),'patient_cluster_95_interval':cluster_interval(test,delta),'negative_is_better':True},
        'interval':{'method':'Held-out calibration absolute-residual quantile; marginal empirical range, no conditional guarantee','nominal':.9,'half_width_mm_hg':round(q,3),'test_coverage':round(coverage,4)},
        'event_model':{**metrics(test),'threshold':threshold,'brier_score':round(float(brier_score_loss(test.event,prob)),5),
            'pr_auc':round(float(average_precision_score(test.event,prob)),4),'calibration_bins':bins,
            'by_event_context':{k:metrics(v) for k,v in test.groupby('event_type')},
            'consolidated_alerts':len(consolidated),'consolidated_ppv':round(float(np.mean(consolidated)),4) if consolidated else None,
            'alerts_per_eligible_session':round(len(consolidated)/test.session_id.nunique(),4),
            'alarm_definition':'Earliest positive window per 30-minute refractory interval within an authoritative session; next-distinct-reading PPV, not continuous-event sensitivity'},
        'limitations':['Retrospective Taiwan deposit, not Indian or prospective validation.','Measured next-distinct-reading endpoint differs from anytime-within-30-minute model crossings.',
            'Session table intervals improve identity but unmatched and overlapping records are excluded; temporal availability of source metadata remains a source assumption.',
            'Prior completed-session aggregates are predictive associations, not causal intervention effects.','Marginal calibration and residual coverage need external transport validation.',
            'Old v0.3 results use a different cohort and model protocol; do not directly rank release scores.']}
    out=ROOT/'docs/observed-v04.json';out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    dest=ROOT/'data/models';dest.mkdir(exist_ok=True)
    (dest/'split-manifest-v04.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'report':str(out),'models':models,'history_increment':result['history_increment'],'event_model':metrics(test)},indent=2))


if __name__=='__main__':run()
