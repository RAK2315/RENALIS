"""Sequential experiment design from released evidence, never acquisition fixtures.

Information is conditional on this authored model bank. This objective is separate
from action-loss value and does not establish a clinical cause or patient benefit.
"""
import numpy as np
from . import mechanisms as m

VERSION = 'sequential-discrimination/0.1'
SUPPORT_FLOOR = .10
INFORMATION_FLOOR = .005


def score(cloud, weights, candidate, pair, failure_probability=0., quadrature_nodes=21):
    mean = m.sensor_prediction(cloud, candidate['channel'], cloud.cutoff + candidate['offset_minutes'])
    noise = candidate['noise_sd']
    nodes, nw = np.polynomial.hermite.hermgauss(quadrature_nodes)
    nw = nw / np.sqrt(np.pi)
    pair_mask = np.isin(cloud.family, pair)
    pair_mass = weights[pair_mask].sum()
    pw = np.where(pair_mask, weights / pair_mass, 0.)
    outcomes = (mean[:, None] + np.sqrt(2) * nodes * noise).ravel()
    pair_qw = (pw[:, None] * nw).ravel()
    full_qw = (weights[:, None] * nw).ravel()
    likelihood = -.5 * ((outcomes[:, None] - mean[None, :]) / noise) ** 2
    likelihood = np.exp(likelihood - likelihood.max(axis=1, keepdims=True))
    posterior = likelihood * weights
    posterior /= np.maximum(posterior.sum(axis=1, keepdims=True), 1e-300)
    fm = np.column_stack([posterior[:, i*m.N:(i+1)*m.N].sum(axis=1) for i in range(len(m.FAMILIES))])
    # Conditional pair posterior must be computed independently: full-bank mass
    # can underflow when outcomes overwhelmingly favor a third explanation.
    pair_likelihood = -.5 * ((outcomes[:, None] - mean[pair_mask][None, :]) / noise) ** 2
    pair_likelihood = np.exp(pair_likelihood - pair_likelihood.max(axis=1, keepdims=True)) * pw[pair_mask]
    pair_likelihood /= np.maximum(pair_likelihood.sum(axis=1, keepdims=True), 1e-300)
    pair_families = cloud.family[pair_mask]
    pf = np.column_stack([pair_likelihood[:, pair_families == i].sum(axis=1) for i in pair])
    prior = m.family_mass(weights)
    prior_pair = prior[pair] / pair_mass
    success = 1 - failure_probability
    pair_info = success * max(0., float(m.entropy(prior_pair) - pair_qw @ m.entropy(pf)))
    full_info = success * max(0., float(m.entropy(prior) - full_qw @ m.entropy(fm)))
    error_before = float(1 - prior_pair.max())
    error_after = float(success * (pair_qw @ (1-pf.max(axis=1))) + failure_probability*error_before)
    confidence = float(success * (pair_qw @ (pf.max(axis=1) >= .80)) + failure_probability*(prior_pair.max() >= .80))
    ranges = []
    for i in pair:
        sl = cloud.family == i
        fw = weights[sl] / weights[sl].sum()
        vals = (mean[sl, None] + np.sqrt(2)*nodes*noise).ravel()
        ow = (fw[:, None]*nw).ravel()
        ranges.append({'id': m.FAMILIES[i]['id'], 'label': m.FAMILIES[i]['label'],
                       'range': [round(m.weighted_quantile(vals, ow, q), 3) for q in [.1,.5,.9]]})
    examples = []
    for q in [.15,.5,.85]:
        value = round(m.weighted_quantile(outcomes, pair_qw, q), 3)
        post = m.normalize(np.log(np.maximum(weights, 1e-300)) - .5*((value-mean)/noise)**2)
        mass = m.family_mass(post)
        examples.append({'value': value, 'family_weights': mass.round(4).tolist(),
                         'leading_family': m.FAMILIES[int(mass.argmax())]['id']})
    return {**candidate, 'pair_information_bits': round(pair_info, 6),
            'full_information_bits': round(full_info, 6),
            'pair_error_before': round(error_before, 6), 'pair_error_after': round(error_after, 6),
            'pair_confidence_80_fraction': round(confidence, 6), 'ranges': ranges, 'examples': examples,
            'observation_minute': cloud.cutoff + candidate['offset_minutes']}


def plan(cloud, weights, analysis, failure_probability=0., quadrature_nodes=21):
    mass = m.family_mass(weights)
    pair = np.argsort(-mass)[:2]
    credible = [i for i, w in enumerate(mass) if w >= SUPPORT_FLOOR]
    objective = 'pair' if len(credible) == 2 else 'whole_bank'
    result = {'version': VERSION, 'status': 'withheld', 'objective': objective,
              'pair': [{'id': m.FAMILIES[i]['id'], 'label': m.FAMILIES[i]['label'], 'weight': round(float(mass[i]), 4)} for i in pair],
              'pair_mass': round(float(mass[pair].sum()), 4),
              'other_mass': round(float(1-mass[pair].sum()), 4),
              'candidates': [], 'recommended': None, 'latest_evidence': analysis['evidence'][-1] if analysis['evidence'] else None,
              'support_floor': SUPPORT_FLOOR, 'information_floor_bits': INFORMATION_FLOOR,
              'method': 'Expected entropy reduction integrated over noisy possible results; earliest feasible slot per channel. Failure returns the current beliefs. Pair scores condition on the two leading families; whole-bank scores retain every family. Costs and action-loss value are shown separately, not converted into bits.',
              'limitations': 'Experimental model-bank discrimination, not a diagnostic probability, clinical recommendation, or validated policy. The true cause may be absent. An informative measurement can still return an ambiguous result.'}
    if analysis['authority'] != 'inspect':
        result['reason'] = 'Measurement planning is withheld for the current authority state.'
        return result
    if len(credible) < 2:
        result.update(status='supported', reason='Fewer than two families retain 10% support. This is model-bank concentration, not confirmation of a cause.')
        return result
    # A failed request is idempotent. Do not suggest clicking the same failed
    # device request again; a later feasible slot may still be considered.
    blocked = {(r['channel'], r['available_minute']) for r in analysis.get('acquisition_log', [])
               if r['active'] and (r['status'] == 'pending' or
                                  (r['status'] == 'failed' and r['request_cutoff'] == cloud.cutoff))}
    earliest = {}
    for c in sorted(analysis['measurement_candidates'], key=lambda c: c['offset_minutes']):
        if (c['channel'], cloud.cutoff+c['offset_minutes']) not in blocked:
            earliest.setdefault(c['channel'], c)
    scores = [score(cloud, weights, c, pair, failure_probability, quadrature_nodes) for c in earliest.values()]
    metric = 'pair_information_bits' if objective == 'pair' else 'full_information_bits'
    scores.sort(key=lambda c: (-c[metric], c['offset_minutes'], c['burden_cost'], c['channel']))
    result['candidates'] = scores
    if scores and scores[0][metric] > INFORMATION_FLOOR:
        result.update(status='available', recommended=scores[0], reason='Best available discriminator under the current predictive distributions and equipment; no observed result is consulted during selection.')
    else:
        result.update(status='no_discriminator', reason='No feasible unacquired measurement exceeds 0.005 expected bits. Available channels may be exhausted, too noisy, failed, or unsafe to wait for. Uncertainty remains; do not invent a resolving result.')
    return result
