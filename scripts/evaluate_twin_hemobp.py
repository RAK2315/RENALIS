"""Run the RENALIS particle twin itself on real HEMOBP sessions.

Same audited cohort, same patient split and same prediction moments as
evaluate_observed_v04.py, so the numbers line up with the four baselines.
The twin gets only what is known at each moment: readings so far, the machine
rate so far, start weight and dry weight. No current-session end fields.

Writes docs/twin-hemobp.json (aggregate metrics only).
"""
from pathlib import Path
import sys, json, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, average_precision_score
from scripts.evaluate_observed_v04 import audit_cohort
from backend.model import advance


def pressure(plasma, reference, baseline, compensation, gamma):
    # Same form as the twin, but each particle carries its own volume sensitivity (gamma),
    # because real patients' pressure reacts to volume loss far less uniformly than our demo patients.
    ratio = np.maximum(.35, plasma / reference)
    return baseline * ratio ** gamma + compensation * np.maximum(0, 1 - ratio)

ROOT = Path(__file__).resolve().parents[1]
N = 192
SEED = 2026
PROTOCOL = {
    'version': 'twin-on-hemobp/0.1',
    'cohort': 'observed-evaluation/0.4 audited cohort and patient split (seeds 42, 43)',
    'particles': N,
    'priors': 'Population only: refill 0.88 L/h (sd 0.24), compensation 18 (sd 4), plasma 4.5% of start weight; '
              'baseline = first reading of the session',
    'excess_water': 'start weight minus dry weight, floored at 0.5 L',
    'likelihood_sd_mm_hg': 9.0,
    'volume_sensitivity': 'Learned per session: gamma ~ lognormal around 1.0 (demo patients use 2.65)',
    'endpoint': 'Same as v0.4: next distinct reading, 5-35 minutes ahead; event = next reading <= 90',
    'threshold': 'Chosen on calibration patients for 61% sensitivity, matching the v0.4 classifier',
    'not_used': 'Smartwatch heart rate and lab results (HEMOBP has neither)',
}


def replay(session, readings, rng):
    """Particle filter over one real session. Returns predictions at each eligible moment."""
    weight = float(session.weightstart) if pd.notna(session.weightstart) else 60.
    excess = max(.5, (weight - float(session.dryweight)) if pd.notna(session.dryweight) else 2.)
    plasma0 = .045 * weight
    reference = np.maximum(1.8, rng.normal(plasma0, .2, N))
    reference_tissue = np.maximum(.5, rng.normal(excess, .25, N))
    baseline = rng.normal(float(readings.sbp.iloc[0]), 6., N)
    refill = np.clip(rng.normal(.88, .24, N), .35, 1.4)
    compensation = rng.normal(18, 4, N)
    gamma = np.exp(rng.normal(0, .7, N))
    plasma, tissue, removed = reference.copy(), reference_tissue.copy(), np.zeros(N)
    weights = np.ones(N) / N
    minutes = readings.minute.to_numpy()
    sbp = readings.sbp.to_numpy()
    rate = readings.rate_ml_h.fillna(0).clip(0, 3000).to_numpy()
    out = []
    t = 0
    for i in range(len(readings)):
        # Advance to this reading's minute using the machine rate known so far.
        while t < minutes[i]:
            current = rate[i - 1] if i else rate[0]
            plasma, tissue, removed = advance(plasma, tissue, removed, refill, reference, reference_tissue, current)
            t += 1
        expected = pressure(plasma, reference, baseline, compensation, gamma)
        weights *= np.exp(-.5 * ((expected - sbp[i]) / PROTOCOL['likelihood_sd_mm_hg']) ** 2) + 1e-300
        if weights.sum() <= 0 or not np.isfinite(weights.sum()):
            weights = np.ones(N) / N
        weights /= weights.sum()
        if 1 / np.sum(weights ** 2) < N * .55:
            idx = rng.choice(N, size=N, p=weights)
            plasma, tissue, removed = plasma[idx], tissue[idx], removed[idx]
            reference, reference_tissue = reference[idx], reference_tissue[idx]
            baseline, compensation, gamma = baseline[idx], compensation[idx], gamma[idx]
            refill = np.clip(refill[idx] + rng.normal(0, .01, N), .3, 1.5)
            weights = np.ones(N) / N
        # Anchor to the measured value, then project to the next reading at the current rate.
        if i + 1 < len(readings) and readings.eligible.iloc[i]:
            gap = int(minutes[i + 1] - minutes[i])
            p2, t2, r2 = plasma.copy(), tissue.copy(), removed.copy()
            for _ in range(gap):
                p2, t2, r2 = advance(p2, t2, r2, refill, reference, reference_tissue, rate[i])
            now = pressure(plasma, reference, baseline, compensation, gamma)
            later = pressure(p2, reference, baseline, compensation, gamma)
            forecast = sbp[i] + (later - now)  # change predicted by the twin, from today's reading
            out.append({'prediction': float(np.average(forecast, weights=weights)),
                        'risk': float(np.average(forecast <= 90, weights=weights))})
    return out


def run_split(cohort_rows, readings, sessions, rng, limit=None):
    keys = cohort_rows.session_id.unique()
    if limit and len(keys) > limit:
        keys = rng.choice(keys, size=limit, replace=False)
    rows = []
    eligible = set(zip(cohort_rows.session_id, cohort_rows.timestamp))
    wanted = set(keys)
    by_session = {sid: g for sid, g in readings[readings.session_id.isin(wanted)].groupby('session_id')}
    cohort_by_session = {sid: g for sid, g in cohort_rows[cohort_rows.session_id.isin(wanted)].groupby('session_id')}
    for n, sid in enumerate(keys):
        r = by_session[sid].sort_values('timestamp').copy()
        r['minute'] = r['time'].round().astype(int)
        r = r.drop_duplicates('minute')
        if len(r) < 2:
            continue
        r['eligible'] = [(sid, ts) in eligible for ts in r.timestamp]
        preds = replay(sessions.loc[sid], r, rng)
        targets = r[r.eligible & r.index.isin(r.index[:-1])]
        c = cohort_by_session[sid].set_index('timestamp')
        for (ts, row), pred in zip(targets.iterrows(), preds):
            if row.timestamp in c.index:
                hit = c.loc[[row.timestamp]].iloc[0]
                rows.append({'pid': hit.pid, 'sbp': hit.sbp, 'next_sbp': hit.next_sbp, **pred})
        if n % 250 == 0:
            print(f'  {n}/{len(keys)} sessions', flush=True)
    return pd.DataFrame(rows)


def main(limit=None):
    started = time.time()
    cohort, _, audit, readings, sessions = audit_cohort(return_readings=True)
    sessions = sessions.set_index('session_id')
    train_i, test_i = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(cohort, groups=cohort.pid))
    development, test = cohort.iloc[train_i], cohort.iloc[test_i]
    _, cal_i = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=43).split(development, groups=development.pid))
    cal = development.iloc[cal_i]
    rng = np.random.default_rng(SEED)
    print('calibration sessions...', flush=True)
    cal_rows = run_split(cal, readings, sessions, rng, limit=800)
    print('test sessions...', flush=True)
    test_rows = run_split(test, readings, sessions, rng, limit=limit)
    # Threshold from calibration patients only, aiming at the classifier's 61% sensitivity.
    cal_event = cal_rows.next_sbp.le(90)
    candidates = np.unique(np.round(cal_rows.risk, 3))
    sens = np.array([((cal_rows.risk >= c) & cal_event).sum() / max(1, cal_event.sum()) for c in candidates])
    threshold = float(candidates[np.where(sens >= .61)[0][-1]]) if (sens >= .61).any() else .5
    event = test_rows.next_sbp.le(90)
    alert = test_rows.risk >= threshold
    tp = int((alert & event).sum())
    result = {
        'status': 'evaluated', 'protocol': PROTOCOL,
        'test_patients': int(test_rows.pid.nunique()), 'test_windows': len(test_rows),
        'sessions_limit': limit,
        'bias_mm_hg': round(float((test_rows.prediction - test_rows.next_sbp).mean()), 3),
        'mae_mm_hg': {'Last observed BP': round(float(mean_absolute_error(test_rows.next_sbp, test_rows.sbp)), 3),
                      'RENALIS twin': round(float(mean_absolute_error(test_rows.next_sbp, test_rows.prediction)), 3)},
        'event': {'threshold': threshold, 'positive_windows': int(event.sum()),
                  'sensitivity': round(tp / max(1, int(event.sum())), 4),
                  'ppv': round(tp / max(1, int(alert.sum())), 4),
                  'pr_auc': round(float(average_precision_score(event, test_rows.risk)), 4)},
        'runtime_seconds': round(time.time() - started),
        'limitations': ['Population priors only; per-patient history learning was not run on HEMOBP.',
                        'HEMOBP has no heart rate or lab results, so those inputs are untested on real data.',
                        'Plasma volume is assumed from body weight, not measured.',
                        'Same clock-alignment assumption as the v0.4 audit.'],
    }
    out = ROOT / 'docs/twin-hemobp.json'
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
