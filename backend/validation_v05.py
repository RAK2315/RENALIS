"""Policy stress test v0.5: does a cautious planner stop being confidently wrong?

The v0.4 suite (validation.py) stays frozen. This file adds one policy, "robust":
- it trusts the blood-volume and heart-output sensors less (their assumed noise is
  multiplied by a temper factor), because the planner's sensor equations may not
  match the world (Sloman et al. 2022, arXiv 2205.13698);
- it repeats the cuff by default and asks for another check only when that check
  beats the cuff by a clear margin.
The temper factor and margin are picked on DEVELOPMENT seeds, then frozen and
reported once on new HOLDOUT seeds. Neither seed set overlaps v0.4.
"""
from pathlib import Path
import json, hashlib
import numpy as np
from . import mechanisms as m
from .validation import PROTOCOL as V04

PROTOCOL = {'version': 'policy-holdout/0.5', 'regimes': V04['regimes'], 'rates': V04['rates'], 'horizon': 30,
            'development_seeds': list(range(100, 124)), 'holdout_seeds': list(range(200, 248)), 'seed_base': V04['seed_base'],
            'policies': ['no_observation', 'fixed_cuff', 'information_gain', 'decision_value', 'robust'],
            'robust_grid': {'temper': [1.5, 2., 3.], 'margin': [0., .005, .01]},
            'selection_rule': 'Lowest mean regret on development seeds; ties go to the larger temper and margin',
            'budget': V04['budget'],
            'note': 'Written before the first run. v0.4 seeds 0-23 are not used.'}
ALPHA = [.043, .004, .018, .026, -.008, .02, .035, .03]
RBV = [85, 94, 90, 88, 97, 89, 86, 87]
CO = [3.9, 5.1, 3.6, 4.2, 5.8, 4.0, 3.9, 4.1]


def case(seed, ri, regime):
    """Same case generator as v0.4, so results are comparable."""
    rates = PROTOCOL['rates']; steps = np.arange(1, 31)
    rng = np.random.default_rng(PROTOCOL['seed_base'] + seed * 101 + ri)
    end = float(rng.uniform(96, 109)); slope = float(rng.uniform(.28, .52)); delay = 5 if regime == 'late_failure' else 0
    history = tuple({'minute': t, 'sbp': round(end + slope * (90 - t) + .4 * np.sin(t / 11), 2) if t % 5 == 0 else None,
                     'quality': 'valid' if t % 5 == 0 else 'missing', 'uf_ml_h': 1400, 'removed_ml': round(1400 * t / 60)} for t in range(91))
    prior = {'initial_plasma': 3.2, 'target_l': 2.8, 'refill_l_h': .80, 'baseline_sbp': end + slope * 90}
    cloud = m.infer(history, prior); weights = m.normalize(cloud.log_weights)
    immediate = np.column_stack([m.decision_losses(m.project(cloud, r), 2100, 2800) for r in rates])
    delayed = np.column_stack([m.decision_losses(m.project(cloud, r, delay_minutes=delay), 2100, 2800) for r in rates])
    channels = ['repeat_bp'] if regime == 'basic_unit' else list(m.CHANNELS)
    failure = .4 if regime == 'late_failure' else .1; noise_mult = 2.5 if regime == 'noisy' else 1.
    alpha = ALPHA[ri] * float(rng.uniform(.8, 1.2))
    curve = -slope * steps - .0008 * steps ** 2
    if regime == 'mixed': curve -= 1.5 * np.sin(steps / 8)
    if regime == 'omitted': curve -= 6 * (steps >= 17)

    def score(rate, wait):
        bp = end + curve + alpha * (1400 - rate) * np.maximum(0, steps - wait) / 60
        minimum = bp.min(); remaining = max(0, 2800 - 2100 - (1400 * wait + rate * (30 - wait)) / 60)
        return float(2 * (minimum <= 90) + .2 * max(0, 90 - minimum) / 20 + .8 * remaining / 700)
    oracle = min(score(r, wait) for wait in sorted({0, delay}) for r in rates)
    means = {'repeat_bp': end - slope * delay, 'relative_blood_volume': RBV[ri], 'cardiac_output': CO[ri]}
    obs = {c: means[c] + rng.normal(0, m.CHANNELS[c]['noise'] * noise_mult * 1.15) for c in channels}
    failed = {c: bool(rng.random() < failure) for c in channels}
    return dict(cloud=cloud, weights=weights, immediate=immediate, delayed=delayed, channels=channels, failure=failure,
                noise_mult=noise_mult, delay=delay, score=score, oracle=oracle, obs=obs, failed=failed)


def candidates(c, temper=1.):
    out = []
    for ch in c['channels']:
        t = 1. if ch == 'repeat_bp' else temper
        out.append(m.measurement_value(c['cloud'], c['weights'], c['delayed'], ch, c['delay'], immediate_losses=c['immediate'],
                                       failure_probability=c['failure'], noise_multiplier=c['noise_mult'] * t))
    return {x['channel']: x for x in out}


def outcome(c, channel, temper=1.):
    rates = PROTOCOL['rates']; w = c['weights']; wait = c['delay'] if channel else 0
    losses = c['delayed'] if channel else c['immediate']
    if channel and not c['failed'][channel]:
        t = 1. if channel == 'repeat_bp' else temper
        mean = m.sensor_prediction(c['cloud'], channel, 90 + c['delay'])
        ll = -.5 * ((mean - c['obs'][channel]) / (m.CHANNELS[channel]['noise'] * c['noise_mult'] * t)) ** 2
        w = m.normalize(np.log(np.maximum(w, 1e-300)) + ll)
    choice = int(np.argmin(w @ losses)); s = c['score'](rates[choice], wait)
    regret = max(0, s - c['oracle'])
    support = float(m.family_mass(w).max())
    return {'channel': channel, 'regret': round(regret, 6), 'confident_wrong': bool(support >= .8 and s - c['oracle'] > .05)}


def policies(c, temper, margin):
    plain = candidates(c)
    robust = candidates(c, temper) if temper != 1. else plain
    cuff = robust['repeat_bp']
    others = [x for k, x in robust.items() if k != 'repeat_bp' and x['net_value'] > cuff['net_value'] + margin]
    decision = max(plain.values(), key=lambda x: x['net_value'])
    pick = {'no_observation': (None, 1.), 'fixed_cuff': ('repeat_bp', 1.),
            'information_gain': (max(plain.values(), key=lambda x: x['information_gain_bits'])['channel'], 1.),
            'decision_value': (decision['channel'] if decision['net_value'] > .001 else None, 1.),
            'robust': ((max(others, key=lambda x: x['net_value'])['channel'] if others else 'repeat_bp'), temper)}
    return {p: outcome(c, ch, t) for p, (ch, t) in pick.items()}


def evaluate(seeds, settings):
    rows = []
    for seed in seeds:
        for ri, regime in enumerate(PROTOCOL['regimes']):
            c = case(seed, ri, regime)
            for name, (temper, margin) in settings.items():
                res = policies(c, temper, margin)
                for p, r in res.items():
                    if name != 'main' and p != 'robust':
                        continue
                    rows.append({'seed': seed, 'regime': regime, 'setting': name, 'policy': p, **r})
    return rows


def summarise(rows):
    out = []
    cuff = {(r['seed'], r['regime']): r['regret'] for r in rows if r['policy'] == 'fixed_cuff'}
    for p in PROTOCOL['policies']:
        sub = [r for r in rows if r['policy'] == p]
        v = np.array([r['regret'] for r in sub])
        # Paired difference against the cuff, resampled by seed block (all regimes of one seed together).
        seeds = sorted({r['seed'] for r in sub})
        block = np.array([np.mean([r['regret'] - cuff[(r['seed'], r['regime'])] for r in sub if r['seed'] == s]) for s in seeds])
        draws = np.random.default_rng(27105).integers(0, len(block), (1000, len(block)))
        out.append({'policy': p, 'cases': len(sub), 'mean_regret': round(float(v.mean()), 5),
                    'paired_delta_vs_cuff': round(float(block.mean()), 5),
                    'seed_block_95_interval': np.quantile(block[draws].mean(axis=1), [.025, .975]).round(5).tolist(),
                    'confident_wrong_cases': sum(r['confident_wrong'] for r in sub),
                    'cases_worse_than_cuff': sum(r['regret'] > cuff[(r['seed'], r['regime'])] + 1e-6 for r in sub),
                    'non_cuff_checks': sum(r['channel'] not in (None, 'repeat_bp') for r in sub),
                    'by_regime': {g: round(float(np.mean([r['regret'] for r in sub if r['regime'] == g])), 5) for g in PROTOCOL['regimes']}})
    return out


def run():
    grid = {f't{t}_m{mg}': (t, mg) for t in PROTOCOL['robust_grid']['temper'] for mg in PROTOCOL['robust_grid']['margin']}
    dev = evaluate(PROTOCOL['development_seeds'], grid)
    scores = {k: float(np.mean([r['regret'] for r in dev if r['setting'] == k])) for k in grid}
    best = min(grid, key=lambda k: (round(scores[k], 6), -grid[k][0], -grid[k][1]))
    temper, margin = grid[best]
    holdout = evaluate(PROTOCOL['holdout_seeds'], {'main': (temper, margin)})
    return {'status': 'evaluated', 'version': PROTOCOL['version'], 'protocol': PROTOCOL,
            'protocol_sha256': hashlib.sha256(json.dumps(PROTOCOL, sort_keys=True).encode()).hexdigest(),
            'chosen_on_development': {'temper': temper, 'margin': margin,
                                      'development_mean_regret': {k: round(v, 5) for k, v in scores.items()}},
            'holdout_cases': len(PROTOCOL['holdout_seeds']) * len(PROTOCOL['regimes']),
            'summaries': summarise(holdout),
            'limitations': ['Same authored stress world as v0.4: sensor values are fixed per regime, not produced by the planner.',
                            'Synthetic research task, not clinical efficacy.']}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    report = run()
    (root / 'docs/policy-validation-v05.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('chosen_on_development', 'summaries')}, indent=2))
