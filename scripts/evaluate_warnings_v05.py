"""Warnings v0.5: score the drop warning the way the field does, and test five extra features.

Same audited cohort, patient split and seeds as v0.4. v0.4 results stay untouched.
Rules fixed before the run:
- The extra feature list below is written down first and not changed after looking at results.
- v0.5 is adopted only if it beats v0.4 on CALIBRATION patients (PR-AUC). Test patients only report.
- Thresholds come from calibration patients.

Writes docs/warnings-v05.json (aggregate metrics only).
"""
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve
from scripts.evaluate_observed_v04 import audit_cohort, PROTOCOL as V04
from scripts.hemo import DATA

ROOT = Path(__file__).resolve().parents[1]
DYN = ['sbp', 'dbp', 'rate_ml_h', 'blood_flow', 'time', 'dia_temp_value', 'conductivity', 'trend_mm_hg_min', 'previous_minutes']
EXTRA = {
    'weight_gain_kg': 'Weight gained since the last session ended (start weight minus last end weight)',
    'planned_removal_frac': 'Planned removal per kg: (start weight minus dry weight) / start weight',
    'pre_sbp': 'First blood pressure reading of this session',
    'last10_drop_rate': 'Share of the last 10 sessions with any reading at or below 90',
    'last10_mean_nadir': 'Average lowest reading over the last 10 sessions',
    'vintage_years': 'Years on dialysis (first_dialysis in idp.csv)',
    'body_temp': 'Body temperature at session start (d1.csv)',
    'prior_low': 'Readings at or below 90 earlier in this session',
    'running_min_sbp': 'Lowest reading so far in this session',
}
PROTOCOL = {
    'version': 'warnings/0.5',
    'cohort': 'observed-evaluation/0.4 audited cohort and patient split (seeds 42, 43)',
    'endpoint': V04['endpoint'],
    'threshold_target_recall': V04['threshold_target_recall'],
    'extra_features': EXTRA,
    'adoption_rule': 'Use v0.5 only if its PR-AUC on calibration patients beats v0.4',
    'refractory_minutes': 30,
    'decision_curve_thresholds': [.05, .10, .20],
}


def add_features(cohort, v, d):
    d = d.sort_values(['pid', 'start']).copy()
    d['weightstart'] = pd.to_numeric(d.weightstart, errors='coerce')
    d['dryweight'] = pd.to_numeric(d.dryweight, errors='coerce')
    d['weight_gain_kg'] = d.weightstart - pd.to_numeric(d.prior_end_weight, errors='coerce')
    d.loc[~d.weight_gain_kg.between(-5, 10), 'weight_gain_kg'] = np.nan
    d['planned_removal_frac'] = ((d.weightstart - d.dryweight) / d.weightstart).where(d.weightstart > 20)
    d['had_drop'] = d.session_nadir.le(90).astype(float).where(d.session_nadir.notna())
    g = d.groupby('pid', sort=False)
    d['last10_drop_rate'] = g.had_drop.transform(lambda s: s.shift().rolling(10, min_periods=1).mean())
    d['last10_mean_nadir'] = g.session_nadir.transform(lambda s: s.shift().rolling(10, min_periods=1).mean())
    d['body_temp'] = pd.to_numeric(d.get('temperature'), errors='coerce')
    d.loc[~d.body_temp.between(34, 42), 'body_temp'] = np.nan
    patient = pd.read_csv(DATA / 'idp.csv', dtype={'pid': str})
    patient['pid'] = patient.pid.str.replace(r'\.0$', '', regex=True)
    patient['first_dialysis'] = pd.to_datetime(patient.first_dialysis, errors='coerce', format='mixed')
    d = d.merge(patient[['pid', 'first_dialysis']], on='pid', how='left')
    d['vintage_years'] = ((d.start - d.first_dialysis).dt.days / 365.25).where(lambda x: x.between(0, 50))
    first = v.sort_values(['session_id', 'timestamp']).groupby('session_id').sbp.first().rename('pre_sbp')
    d = d.join(first, on='session_id')
    v = v.sort_values(['session_id', 'timestamp']).copy()
    v['running_min_sbp'] = v.groupby('session_id').sbp.cummin()
    session_cols = ['weight_gain_kg', 'planned_removal_frac', 'pre_sbp', 'last10_drop_rate', 'last10_mean_nadir', 'vintage_years', 'body_temp']
    out = cohort.merge(d[['session_id'] + session_cols], on='session_id', how='left', validate='many_to_one')
    out = out.merge(v[['session_id', 'timestamp', 'running_min_sbp']].drop_duplicates(['session_id', 'timestamp']),
                    on=['session_id', 'timestamp'], how='left', validate='many_to_one')
    out.index = cohort.index
    return out


def fit_model(fit, cal, features):
    clf = HistGradientBoostingClassifier(max_iter=90, max_leaf_nodes=16, l2_regularization=12, random_state=42)
    clf.fit(fit[features], fit.next_sbp.le(90).astype(int))

    def logits(f):
        p = np.clip(clf.predict_proba(f[features])[:, 1], 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p)).reshape(-1, 1)
    calibrator = LogisticRegression(C=1., random_state=42).fit(logits(cal), cal.next_sbp.le(90).astype(int))
    return lambda f: calibrator.predict_proba(logits(f))[:, 1]


def threshold_for(cal, risk, target):
    precision, recall, thresholds = precision_recall_curve(cal.next_sbp.le(90).astype(int), risk)
    ids = np.where(recall[:-1] >= target)[0]
    return float(thresholds[ids[-1]]) if len(ids) else .5


def report(test, risk, threshold):
    f = test[['pid', 'session_id', 'timestamp', 'event_type']].copy()
    f['risk'] = risk
    f['event'] = test.next_sbp.le(90).to_numpy()
    f['alert'] = f.risk >= threshold
    tp = int((f.alert & f.event).sum()); pos = int(f.event.sum()); alerts = int(f.alert.sum())
    base = float(f.event.mean())
    ppv = tp / alerts if alerts else 0.
    # Alarms with a 30-minute quiet period after each one.
    f = f.sort_values(['session_id', 'timestamp'])
    kept, last = [], {}
    for sid, ts, a in zip(f.session_id, f.timestamp, f.alert):
        ok = a and (sid not in last or (ts - last[sid]).total_seconds() >= 1800)
        if ok:
            last[sid] = ts
        kept.append(ok)
    f['alarm'] = kept
    alarms = int(f.alarm.sum())
    # Session hours covered by eligible windows.
    span = f.groupby('session_id').timestamp.agg(['min', 'max'])
    hours = float(((span['max'] - span['min']).dt.total_seconds() / 3600 + .5).sum())
    s = f.groupby('session_id').agg(had=('event', 'any'), warned=('alert', 'any'))
    contexts = {}
    for name, g in f.groupby('event_type'):
        t = int((g.alert & g.event).sum())
        contexts[name] = {'caught': round(t / max(1, int(g.event.sum())), 4), 'right': round(t / max(1, int(g.alert.sum())), 4)}
    n = len(f)
    curve = []
    for pt in PROTOCOL['decision_curve_thresholds']:
        a = f.risk >= pt
        tpp, fpp = int((a & f.event).sum()), int((a & ~f.event).sum())
        nb = tpp / n - fpp / n * pt / (1 - pt)
        treat_all = base - (1 - base) * pt / (1 - pt)
        curve.append({'threshold': pt, 'false_alarms_accepted_per_catch': round((1 - pt) / pt, 1),
                      'net_benefit': round(nb, 5), 'alarm_everyone': round(treat_all, 5), 'never_alarm': 0.0})
    return {
        'windows': n, 'base_rate': round(base, 4), 'threshold': round(threshold, 5),
        'caught': round(tp / max(1, pos), 4), 'right': round(ppv, 4), 'lift_over_chance': round(ppv / base, 2),
        'pr_auc': round(float(average_precision_score(f.event, f.risk)), 4),
        'false_alarms': int((f.alert & ~f.event).sum()),
        'alarms_with_30min_quiet': alarms,
        'alarm_right_with_30min_quiet': round(float((f.alarm & f.event).sum()) / max(1, alarms), 4),
        'alarms_per_session': round(alarms / f.session_id.nunique(), 3),
        'alarms_per_session_hour': round(alarms / hours, 3),
        'per_session': {'sessions': len(s), 'sessions_with_drop': int(s.had.sum()),
                        'caught': round(float((s.had & s.warned).sum()) / max(1, int(s.had.sum())), 4),
                        'right': round(float((s.had & s.warned).sum()) / max(1, int(s.warned.sum())), 4)},
        'first_vs_repeat': contexts,
        'decision_curve': curve,
    }


def main():
    cohort, history, _, v, d = audit_cohort(return_readings=True)
    cohort = add_features(cohort, v, d)
    train_i, test_i = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(cohort, groups=cohort.pid))
    development, test = cohort.iloc[train_i].copy(), cohort.iloc[test_i].copy()
    fit_i, cal_i = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=43).split(development, groups=development.pid))
    fit, cal = development.iloc[fit_i].copy(), development.iloc[cal_i].copy()
    if len(fit) > 100000:
        fit = fit.sample(100000, random_state=42)
    v04 = DYN + ['age', 'diabetes', 'female'] + history
    v05 = v04 + list(EXTRA)
    results, cal_prauc = {}, {}
    for name, feats in [('v0.4', v04), ('v0.5', v05)]:
        predict = fit_model(fit, cal, feats)
        cal_risk = predict(cal)
        cal_prauc[name] = round(float(average_precision_score(cal.next_sbp.le(90), cal_risk)), 4)
        t = threshold_for(cal, cal_risk, PROTOCOL['threshold_target_recall'])
        results[name] = report(test, predict(test), t)
        print(name, json.dumps({k: results[name][k] for k in ('caught', 'right', 'pr_auc')}), flush=True)
    adopted = 'v0.5' if cal_prauc['v0.5'] > cal_prauc['v0.4'] else 'v0.4'
    out = {'status': 'evaluated', 'protocol': PROTOCOL, 'test_patients': int(test.pid.nunique()),
           'calibration_pr_auc': cal_prauc, 'adopted': adopted, 'models': results,
           'published_comparison': [
               {'study': 'Zhang et al. 2023, Nephrol Dial Transplant', 'doi': '10.1093/ndt/gfad070',
                'unit': 'per BP reading', 'base_rate': .0406, 'caught': .65, 'right': .22, 'lift_over_chance': 5.4},
               {'study': 'Kim et al. 2026, Front Digit Health', 'doi': '10.3389/fdgth.2026.1804788',
                'unit': 'first drop only', 'right': .129}],
           'notes': ['Lift over chance = share of warnings that are right, divided by the share of moments followed by a drop.',
                     'RENALIS counts a drop as a reading at or below 90; most papers use below 90.']}
    (ROOT / 'docs/warnings-v05.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps({'adopted': adopted, 'calibration_pr_auc': cal_prauc}, indent=2))


if __name__ == '__main__':
    main()
