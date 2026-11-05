"""How many false alarms can be removed, and what does it cost in missed drops?

Rebuilds the v0.4 warning model exactly (same cohort, split, seeds and features),
then compares warning rules. Every threshold is chosen on calibration patients;
test patients are only used to report the result.

Writes docs/alarm-tradeoff.json (aggregate metrics only).
"""
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
from scripts.evaluate_observed_v04 import audit_cohort

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [.75, .60, .50, .40, .30]


def main():
    cohort, history, _ = audit_cohort()
    train_i, test_i = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(cohort, groups=cohort.pid))
    development, test = cohort.iloc[train_i].copy(), cohort.iloc[test_i].copy()
    fit_i, cal_i = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=43).split(development, groups=development.pid))
    fit, cal = development.iloc[fit_i].copy(), development.iloc[cal_i].copy()
    if len(fit) > 100000:
        fit = fit.sample(100000, random_state=42)
    dyn = ['sbp', 'dbp', 'rate_ml_h', 'blood_flow', 'time', 'dia_temp_value', 'conductivity', 'trend_mm_hg_min', 'previous_minutes']
    fused = dyn + ['age', 'diabetes', 'female'] + history
    clf = HistGradientBoostingClassifier(max_iter=90, max_leaf_nodes=16, l2_regularization=12, random_state=42)
    clf.fit(fit[fused], fit.next_sbp.le(90).astype(int))

    def logits(f):
        p = np.clip(clf.predict_proba(f[fused])[:, 1], 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p)).reshape(-1, 1)
    calibrator = LogisticRegression(C=1., random_state=42).fit(logits(cal), cal.next_sbp.le(90).astype(int))
    for f in (cal, test):
        f['risk'] = calibrator.predict_proba(logits(f))[:, 1]
        f['event'] = f.next_sbp.le(90)
        f.sort_values(['session_id', 'timestamp'], inplace=True)
        f['prev_risk'] = f.groupby('session_id').risk.shift().fillna(0)

    precision, recall, thresholds = precision_recall_curve(cal.event.astype(int), cal.risk)
    base_rate = float(test.event.mean())

    def score(f, alert):
        tp = int((alert & f.event).sum()); positives = int(f.event.sum()); alerts = int(alert.sum())
        return {'caught': round(tp / positives, 4), 'right': round(tp / alerts, 4) if alerts else None,
                'false_alarms': int((alert & ~f.event).sum()), 'alerts': alerts}

    rules = []
    for target in TARGETS:
        ids = np.where(recall[:-1] >= target)[0]
        t = float(thresholds[ids[-1]]) if len(ids) else .5
        rules.append({'rule': f'Single reading, tuned to catch {int(target * 100)}% (calibration)', 'threshold': round(t, 5),
                      **score(test, test.risk >= t)})
    # Two risky readings in a row: threshold chosen on calibration for 50% catch under this rule.
    best = None
    for t in np.unique(np.round(cal.risk, 4))[::-1]:
        both = (cal.risk >= t) & (cal.prev_risk >= t)
        caught = (both & cal.event).sum() / cal.event.sum()
        if caught >= .5:
            best = float(t); break
    if best is not None:
        rules.append({'rule': 'Two risky readings in a row, tuned to catch 50% (calibration)', 'threshold': round(best, 5),
                      **score(test, (test.risk >= best) & (test.prev_risk >= best))})
    result = {'status': 'evaluated', 'model': 'Same v0.4 warning model; only the warning rule changes',
              'test_windows': len(test), 'base_rate': round(base_rate, 4),
              'base_rate_note': f'Only {base_rate * 100:.1f} of every 100 moments are followed by a drop, so even a good warning is often false.',
              'rules': rules}
    (ROOT / 'docs/alarm-tradeoff.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
