"""Competing physiological hypotheses and decision-relevant observation design.

Research equations, not identified clinical causes. Inference accepts ONLY the
history slice and released observations. Synthetic acquisition lives elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from functools import lru_cache
import numpy as np
from .model import PATIENTS, observations, DURATION, advance

VERSION = 'evidence-aware-mechanisms/0.4'
FAMILIES = (
    {'id': 'volume', 'label': 'Volume / refill limitation', 'gamma': 2.65, 'refill_scale': 1.,
     'description': 'Pressure is sensitive to circulating volume when tissue refill cannot match removal.'},
    {'id': 'vascular', 'label': 'Vascular compensation limitation', 'gamma': .45, 'refill_scale': 1.40,
     'description': 'A changing resistance factor can explain falling pressure despite a better-preserved volume.'},
    {'id': 'cardiac', 'label': 'Cardiac response limitation', 'gamma': 1.15, 'refill_scale': 1.20,
     'description': 'A changing output factor can explain pressure loss without the same refill limitation.'},
    {'id': 'mixed', 'label': 'Mixed response hypothesis', 'gamma': 1.85, 'refill_scale': 1.10,
     'description': 'An authored combination of volume sensitivity and changing compensation; it is not an identified clinical mixture.'},
)
CHANNELS = {
    'repeat_bp': {'label': 'Repeat cuff BP', 'unit': 'mmHg', 'noise': 3.5, 'cost': .012, 'range': (30., 220.),
                  'description': 'May reduce pressure uncertainty without separating mechanisms.'},
    'relative_blood_volume': {'label': 'Relative blood volume', 'unit': '% of start', 'noise': 1.0, 'cost': .035, 'range': (40., 125.),
                             'description': 'Tests whether circulating volume has fallen as much as the refill hypothesis assumes.'},
    'cardiac_output': {'label': 'Noninvasive cardiac output', 'unit': 'L/min', 'noise': .30, 'cost': .055, 'range': (1., 12.),
                       'description': 'May distinguish lower output from a predominantly resistance-related pressure change.'},
}
N = 48  # particles per distinct family; 192 across the four authored families


def normalize(log_weights):
    weights = np.exp(log_weights - np.max(log_weights))
    return weights / weights.sum()


def weighted_quantile(values, weights, q):
    order = np.argsort(values)
    return float(np.interp(q, np.cumsum(weights[order]), values[order]))


@dataclass
class Cloud:
    family: np.ndarray
    gamma: np.ndarray
    refill: np.ndarray
    reference: np.ndarray
    tissue_reference: np.ndarray
    plasma_history: np.ndarray
    tissue_history: np.ndarray
    baseline: np.ndarray
    drift: np.ndarray
    log_weights: np.ndarray
    fit_errors: np.ndarray
    anchor: np.ndarray
    cutoff: int
    current_rate: int
    removed_ml: int
    history: tuple
    prior: dict


def infer(history: tuple, prior: dict) -> Cloud:
    """No patient key, hidden mechanism, future row, or acquisition fixture enters here."""
    cutoff = int(history[-1]['minute'])
    valid = [r for r in history if r.get('sbp') is not None and r.get('quality') == 'valid']
    recent = [r for r in valid if r['minute'] >= max(0, valid[-1]['minute'] - 35)]
    if len(recent) < 3:
        recent = valid[-4:]
    rng = np.random.default_rng(7201)
    count=N*len(FAMILIES)
    family = np.repeat(np.arange(len(FAMILIES)), N)
    gamma = np.array([FAMILIES[i]['gamma'] for i in family])
    reference = np.clip(rng.normal(prior['initial_plasma'], .10, count), 2., 5.)
    tissue_reference = np.clip(rng.normal(prior['target_l'], .12, count), .8, 6.)
    refill = np.clip(rng.normal(prior['refill_l_h'], .09, count) *
                     np.array([FAMILIES[i]['refill_scale'] for i in family]), .30, 1.65)
    plasma, tissue, removed = reference.copy(), tissue_reference.copy(), np.zeros(count)
    ph, th = [plasma.copy()], [tissue.copy()]
    for row in history[:-1]:
        plasma, tissue, removed = advance(plasma, tissue, removed, refill, reference,
                                         tissue_reference, row['uf_ml_h'])
        ph.append(plasma.copy()); th.append(tissue.copy())
    ph, th = np.array(ph), np.array(th)
    ts = np.array([r['minute'] for r in recent], dtype=int)
    observed = np.array([r['sbp'] for r in recent])
    # Each family fits a regularized local pressure factor to available observations.
    # A local nuisance trend allows genuine BP ambiguity; its interpretation differs
    # across families. These compatibility weights are NOT diagnostic probabilities.
    x = (ts - cutoff) / 60
    geometric = gamma[None, :] * np.log(np.maximum(ph[ts] / reference, .35))
    residual = np.log(observed[:, None] / prior['baseline_sbp']) - geometric
    denom = float(np.sum((x - x.mean()) ** 2))
    slope = np.sum((x[:, None] - x.mean()) * (residual - residual.mean(axis=0)), axis=0) / max(denom, .001)
    # Conservative regularization: volume family's unmodeled factor stays near zero.
    slope = np.where(family == 0, np.clip(slope, -.08, .08), np.clip(slope, -.75, .30))
    intercept = (residual - x[:, None] * slope).mean(axis=0)
    predicted = prior['baseline_sbp'] * np.exp(geometric + intercept + x[:, None] * slope)
    errors = np.sqrt(np.mean((predicted - observed[:, None]) ** 2, axis=0))
    logw = -.5 * errors ** 2 / 6.0 ** 2 - np.log(count)
    # Anchor all hypotheses to the latest available pressure with observation noise.
    anchor = valid[-1]['sbp'] + rng.normal(0, 1.3, count)
    drift = slope + rng.normal(0, .018, count)
    # The cuff value belongs to its observation minute. Propagate from that
    # minute to the current state; a replay tick is not a new pressure reading.
    age = cutoff - valid[-1]['minute']
    anchor *= np.maximum(ph[-1] / ph[valid[-1]['minute']], .35) ** gamma * np.exp(drift * age / 60)
    return Cloud(family, gamma, refill, reference, tissue_reference, ph, th,
                 np.full(count, prior['baseline_sbp']), drift, logw, errors,
                 anchor, cutoff, history[-1]['uf_ml_h'], history[-1]['removed_ml'], history,dict(prior))


@lru_cache(maxsize=128)
def base_cloud(patient_id: str, cutoff: int):
    p = PATIENTS[patient_id]
    # Explicit slicing is the boundary that prevents any future observation leakage.
    known = observations(patient_id)[:cutoff + 1]
    from .history import patient_history
    memory=patient_history(patient_id)
    return infer(known, {'initial_plasma': p.initial_plasma, 'target_l': p.target_ml / 1000,
                         'refill_l_h': memory['refill_l_h'], 'baseline_sbp': p.baseline_sbp,
                         'history_digest':memory['history_digest'],'sessions_used':memory['sessions_used']})


def project(cloud: Cloud, rate: int, profile='constant', horizon=None, delay_minutes=0):
    horizon = min(30, DURATION - cloud.cutoff) if horizon is None else horizon
    plasma, tissue = cloud.plasma_history[-1].copy(), cloud.tissue_history[-1].copy()
    start = plasma.copy()
    removed = np.full(len(cloud.family), cloud.removed_ml / 1000)
    rows, volumes, flows = [], [], []
    for step in range(horizon + 1):
        # Volume, resistance, and output factors respond differently to the same UF.
        values = cloud.anchor * np.maximum(plasma / start, .35) ** cloud.gamma * np.exp(cloud.drift * step / 60)
        rows.append(values); volumes.append(plasma.copy()); flows.append(removed.copy())
        effective = cloud.current_rate if step < delay_minutes else max(300, rate - 200) if profile == 'step_down' and step - delay_minutes >= 15 else rate
        if step < horizon:
            plasma, tissue, removed = advance(plasma, tissue, removed, cloud.refill, cloud.reference,
                                             cloud.tissue_reference, effective)
    return {'bp': np.array(rows), 'plasma': np.array(volumes), 'removed': np.array(flows)}


def sensor_prediction(cloud: Cloud, channel: str, minute: int):
    offset = minute - cloud.cutoff
    if offset >= 0:
        projected = project(cloud, cloud.current_rate, horizon=offset)
        plasma = projected['plasma'][-1]
        bp = projected['bp'][-1]
    else:
        plasma = cloud.plasma_history[minute]
        # Reconstruct a past pressure factor using current fitted family hypotheses.
        ratio = np.maximum(plasma / cloud.plasma_history[-1], .35)
        bp = cloud.anchor * ratio ** cloud.gamma * np.exp(cloud.drift * offset / 60)
    ratio = np.maximum(plasma / cloud.reference, .35)
    if channel == 'relative_blood_volume':
        return 100 * ratio
    if channel == 'cardiac_output':
        # Vascular family preserves output more strongly; cardiac family carries its
        # fitted pressure-factor decline in output. Proxy equation is a sandbox choice.
        base_output = 5.2 * ratio ** np.where(cloud.family == 0, 1.8, .35)
        cardiac_factor = np.clip((cloud.anchor / cloud.baseline) / ratio ** cloud.gamma, .4, 1.2)
        response=cardiac_factor * np.exp(cloud.drift * offset / 60)
        return base_output * np.where(cloud.family == 2,response,np.where(cloud.family==3,np.sqrt(response),1.))
    return bp


def family_mass(weights):
    return np.array([weights[i*N:(i+1)*N].sum() for i in range(len(FAMILIES))])


def entropy(probabilities):
    return -np.sum(probabilities * np.log2(np.maximum(probabilities, 1e-15)), axis=-1)


def assimilate(cloud: Cloud, evidence: list[dict]):
    logw = cloud.log_weights.copy()
    audit = []
    for item in sorted(evidence, key=lambda r: (r['available_minute'], r.get('id', 0))):
        if item['available_minute'] > cloud.cutoff:
            continue
        if item.get('quality','valid')!='valid' or item.get('status','success')!='success':continue
        predicted = sensor_prediction(cloud, item['channel'], item.get('observed_minute',item['available_minute']))
        noise = item.get('noise_sd') or CHANNELS[item['channel']]['noise']
        before = normalize(logw)
        gap = float(np.min(np.abs(predicted - item['value'])) / noise)
        logw += -.5 * ((predicted - item['value']) / noise) ** 2
        after = normalize(logw)
        audit.append({'id': item.get('id'), 'channel': item['channel'], 'value': item['value'],
                      'unit': CHANNELS[item['channel']]['unit'], 'available_minute': item['available_minute'],
                      'source': item['source'], 'contradiction': gap > 4.,
                      'observed_minute':item.get('observed_minute',item['available_minute']), 'quality':item.get('quality','valid'),
                      'noise_sd':noise,'supersedes':item.get('supersedes'),'correction_reason':item.get('correction_reason'),
                      'nearest_model_residual_sd': round(gap, 2),
                      'before': family_mass(before).round(4).tolist(),
                      'after': family_mass(after).round(4).tolist()})
    return normalize(logw), audit


def decision_losses(projected, current_removed_ml, target_ml):
    minimum = projected['bp'][1:].min(axis=0) if len(projected['bp']) > 1 else projected['bp'][0]
    additional = (projected['removed'][-1] * 1000 - current_removed_ml)
    left = np.maximum(0, target_ml - current_removed_ml - additional)
    # Declared research loss: threshold crossing + severity + unfinished fluid target.
    return 2. * (minimum <= 90) + .2 * np.maximum(0, 90-minimum) / 20 + .8 * left / max(target_ml-current_removed_ml, 500)


def measurement_value(cloud, weights, losses, channel, offset, burden_weight=.5,
                      immediate_losses=None,failure_probability=0.,noise_multiplier=1.,quadrature_nodes=9):
    """Deterministic Gaussian quadrature over possible observations, not hidden truth."""
    spec = CHANNELS[channel]
    mean = sensor_prediction(cloud, channel, cloud.cutoff + offset)
    nodes,node_weights=np.polynomial.hermite.hermgauss(quadrature_nodes)
    nodes=nodes*np.sqrt(2);node_weights=node_weights/np.sqrt(np.pi)
    noise=spec['noise']*noise_multiplier
    outcomes = (mean[:, None] + nodes * noise).ravel()
    quadrature_weights = (weights[:, None] * node_weights).ravel()
    loglik = -.5 * ((outcomes[:, None] - mean[None, :]) / noise) ** 2
    posterior = np.exp(loglik - loglik.max(axis=1, keepdims=True)) * weights
    posterior /= np.maximum(posterior.sum(axis=1, keepdims=True),1e-300)
    prior_risk = float(np.min(weights @ (immediate_losses if immediate_losses is not None else losses)))
    waiting_risk=float(np.min(weights@losses))
    posterior_losses = posterior @ losses
    expected_risk = (1-failure_probability)*float(quadrature_weights @ posterior_losses.min(axis=1))+failure_probability*waiting_risk
    family_probs = np.column_stack([posterior[:, i*N:(i+1)*N].sum(axis=1) for i in range(len(FAMILIES))])
    info_gain = (1-failure_probability)*max(0., float(entropy(family_mass(weights)) - quadrature_weights @ entropy(family_probs)))
    value = prior_risk - expected_risk
    current_choice = int(np.argmin(weights @ losses))
    change_fraction = float(quadrature_weights @ (posterior_losses.argmin(axis=1) != current_choice))
    return {'channel': channel, 'label': spec['label'], 'unit': spec['unit'], 'noise_sd':noise, 'offset_minutes': offset,
            'immediate_loss':round(prior_risk,5),'waiting_loss':round(waiting_risk-prior_risk,5),
            'expected_loss_after_acquisition':round(expected_risk,5),'failure_probability':failure_probability,
            'quadrature_nodes':quadrature_nodes,
            'decision_value': round(value, 4), 'information_gain_bits': round(info_gain, 4),
            'modeled_choice_change_fraction': round((1-failure_probability)*change_fraction, 4),
            'burden_cost': round(spec['cost']*burden_weight,4), 'net_value': round(value - spec['cost']*burden_weight - offset * .002, 4),
            'description': spec['description']}


def analyze(patient_id: str, cutoff: int, rate: int, profile: str, channels: list[str], evidence: list[dict], net_gain_ml=1200, burden_weight=.5, cloud_override=None, patient_override=None,noise_multiplier=1.,failure_probability=0.,latency_minutes=0):
    cloud = cloud_override if cloud_override is not None else base_cloud(patient_id, cutoff)
    p = patient_override if patient_override is not None else PATIENTS[patient_id]
    weights, audit = assimilate(cloud, evidence)
    family_weights = family_mass(weights)
    known = cloud.history
    latest = [r for r in known if r['sbp'] is not None and r['quality'] == 'valid'][-1]
    stale = cutoff - latest['minute'] > 15
    current_event = latest['sbp'] <= 90
    contradiction = any(r['contradiction'] for r in audit)
    bad_fit = float(np.min(cloud.fit_errors)) > 8.
    authority = 'complete' if cutoff >= DURATION else 'stale' if stale else 'current_event' if current_event else 'contradicted' if contradiction or bad_fit else 'inspect'
    rates = sorted(set([350, 500, 650, 800, 950, 1100, 1250, 1400, rate, cloud.current_rate]))
    actions = [(value, 'constant') for value in rates]
    if profile != 'constant':
        actions.append((rate, profile))
    projections = [project(cloud, value, shape) for value, shape in actions]
    losses = np.column_stack([decision_losses(pred, cloud.removed_ml, p.target_ml) for pred in projections])
    chosen = actions.index((rate, profile))
    factual = actions.index((cloud.current_rate, 'constant'))
    rows, family_results = [], []
    family_choices = []
    for i, spec in enumerate(FAMILIES):
        indices = np.arange(i*N, (i+1)*N)
        fw = weights[indices]
        fw = fw / fw.sum() if fw.sum()>1e-250 else np.full(N,1/N)
        alt, current = projections[chosen]['bp'], projections[factual]['bp']
        family_losses = fw @ losses[indices]
        family_choices.append(int(np.argmin(family_losses)))
        delta = float(fw @ (alt[-1, indices] - current[-1, indices]))
        minimum = alt[1:, indices].min(axis=0) if len(alt)>1 else alt[0, indices]
        family_results.append({'id': spec['id'], 'label': spec['label'], 'description': spec['description'],
                               'weight': round(float(family_weights[i]), 4),
                               'response_exponent':round(float(fw @ cloud.gamma[indices]),2),
                               'fit_rmse_mm_hg': round(float(np.average(cloud.fit_errors[indices], weights=fw)), 2),
                               'alternative_end_sbp': round(float(fw @ alt[-1, indices]), 1),
                               'current_end_sbp': round(float(fw @ current[-1, indices]), 1),
                               'alternative_crossing_fraction': round(float(fw @ (minimum<=90)), 3),
                               'alternative_effect_mm_hg': round(delta, 1),
                               'preferred_rate_ml_h': actions[family_choices[-1]][0],
                               'preferred_profile': actions[family_choices[-1]][1],
                               'relative_blood_volume_pct': round(float(fw @ sensor_prediction(cloud,'relative_blood_volume',cutoff)[indices]),1),
                               'cardiac_output_l_min': round(float(fw @ sensor_prediction(cloud,'cardiac_output',cutoff)[indices]),2)})
    for step in range(len(projections[chosen]['bp'])):
        row = {'minute': cutoff + step}
        for i, spec in enumerate(FAMILIES):
            ids = np.arange(i*N,(i+1)*N)
            fw = weights[ids] / weights[ids].sum() if weights[ids].sum()>1e-250 else np.full(N,1/N)
            row[spec['id']] = round(float(fw @ projections[chosen]['bp'][step,ids]),1)
            row[spec['id']+'_range'] = [round(weighted_quantile(projections[chosen]['bp'][step,ids],fw,q),1) for q in (.1,.9)]
        rows.append(row)
    credible = [i for i in range(len(FAMILIES)) if family_weights[i] >= .10]
    disagreement = len({family_choices[i] for i in credible}) > 1
    support_state = 'unresolved' if disagreement else 'model_agreement'
    if authority != 'inspect': support_state = authority
    candidates=[]
    if authority == 'inspect':
        for channel in channels:
            for offset in sorted(set([latency_minutes,latency_minutes+5,latency_minutes+10])):
                if offset>min(30,DURATION-cutoff):continue
                if cutoff + offset > DURATION: continue
                # Never propose waiting past a modeled imminent low-pressure crossing.
                current_bp = projections[factual]['bp']
                if offset and float(weights @ (current_bp[1:min(offset,len(current_bp)-1)+1].min(axis=0)<=90)) >= .25:
                    continue
                if any(e['channel']==channel and e['available_minute']==cutoff+offset for e in evidence):
                    continue
                # A delayed observation cannot retroactively change the removal profile.
                delayed_losses = losses if offset == 0 else np.column_stack([
                    decision_losses(project(cloud,value,shape,delay_minutes=offset),cloud.removed_ml,p.target_ml)
                    for value,shape in actions])
                candidates.append(measurement_value(cloud,weights,delayed_losses,channel,offset,burden_weight,
                    immediate_losses=losses,failure_probability=failure_probability,noise_multiplier=noise_multiplier))
    candidates.sort(key=lambda c:c['net_value'],reverse=True)
    best = candidates[0] if candidates and candidates[0]['net_value'] > .001 else None
    # Model support regions are empirical sandbox settings only, never clinical safety.
    seen_rates = np.array([r['uf_ml_h'] for r in known])
    landscape=[]
    for j,(value,shape) in enumerate(actions):
        pred=projections[j]; minbp=pred['bp'][1:].min(axis=0) if len(pred['bp'])>1 else pred['bp'][0]
        lower,median,upper=[weighted_quantile(minbp,weights,q) for q in (.1,.5,.9)]
        supported = int(seen_rates.min())-100 <= value <= int(seen_rates.max())+100
        landscape.append({'rate_ml_h':value,'profile':shape,'minimum_sbp':round(median,1),'lower':round(lower,1),'upper':round(upper,1),
                          'fluid_removed_ml':round(float(weights @ (pred['removed'][-1]-pred['removed'][0]))*1000),
                          'expected_loss':round(float(weights @ losses[:,j]),3),
                          'input_support':'near_observed_settings' if supported else 'outside_session_settings',
                          'mechanism_dependence':round(float(np.std([np.mean(minbp[i*N:(i+1)*N]) for i in credible])),2) if credible else None})
    reasons=[]
    if stale: reasons.append('Latest valid BP is stale. Measurements and comparison ranking are withheld.')
    if current_event: reasons.append('BP is already low. This research comparison is not an advance warning or an emergency-care scheduler.')
    if contradiction or bad_fit: reasons.append('Available evidence is inconsistent with the model families. Comparison authority is downgraded.')
    if disagreement: reasons.append('Plausible mechanisms prefer different profiles under the declared research loss.')
    if not channels: reasons.append('No additional measurement channel is available. The comparison can remain unresolved.')
    if candidates and best is None: reasons.append('No available measurement has enough modeled decision value after burden costs.')
    selected_landscape=landscape[chosen]
    if selected_landscape['input_support']=='outside_session_settings': reasons.append('The selected rate extrapolates beyond this session’s observed settings.')
    # Carry-over is an explicit accounting scenario, not a predicted future observation.
    projected_end=project(cloud,rate,profile,horizon=DURATION-cutoff)
    left=np.maximum(0,p.target_ml-projected_end['removed'][-1]*1000)
    carry={ 'remaining_at_session_end_ml':round(float(weights@left)), 'assumed_net_gain_ml':net_gain_ml,
           'next_session_excess_ml':round(float(weights@left))+net_gain_ml,
           'range_ml':[round(weighted_quantile(left,weights,.1))+net_gain_ml,round(weighted_quantile(left,weights,.9))+net_gain_ml],
           'provenance':'Hypothetical end-of-session removal plus a user-authored net interdialytic gain; not a clinical prediction'}
    revision=hashlib.sha256(json.dumps({'v':VERSION,'patient':patient_id,'cutoff':cutoff,'rate':rate,'profile':profile,
                    'channels':sorted(channels),'evidence':evidence,'net_gain_ml':net_gain_ml,'burden_weight':burden_weight,
                    'noise_multiplier':noise_multiplier,'failure_probability':failure_probability,'latency_minutes':latency_minutes,
                    'prior':cloud.prior},sort_keys=True).encode()).hexdigest()[:16]
    if authority != 'inspect':
        # Retain factual fit and the evidence audit, but actually withhold forecasts
        # and ranked preferences in the API as well as in the interface.
        for family_result in family_results:
            for key in ('alternative_end_sbp','current_end_sbp','alternative_crossing_fraction','alternative_effect_mm_hg','preferred_rate_ml_h','preferred_profile'):
                family_result[key]=None
        rows=[]
        landscape=[]
    return {'patient_id':patient_id,'cutoff':cutoff,'rate_ml_h':rate,'profile':profile,'horizon':min(30,DURATION-cutoff),
            'version':VERSION,'revision':revision,'authority':authority,'support_state':support_state,
            'families':family_results,'trajectories':rows,'observations':list(known),'historical_priors':cloud.prior,
            'available_channels':sorted(channels),'current_rate_ml_h':cloud.current_rate,
            'measurement_assumptions':{key:{'noise_sd':spec['noise']*noise_multiplier,'base_noise_sd':spec['noise'],'unit':spec['unit'],'raw_burden':spec['cost']} for key,spec in CHANNELS.items()},
            'agreement_rule':'Agreement compares profile preferences among families with at least 10% relative compatibility support; this cutoff is an authored research choice.',
            'interval_definition':'Selected family band is its conditional 10th–90th weighted particle range; not a calibrated clinical interval.',
            'landscape':landscape,'selected_rate_index':chosen if authority=='inspect' else None,'comparison_unresolved':disagreement,
            'measurement_candidates':candidates,'recommended_measurement':best,'reasons':reasons,'evidence':audit,
            'prior_family_weights':family_mass(normalize(cloud.log_weights)).round(4).tolist(),
            'mixed_model_notice':'A fourth authored mixed hypothesis is retained; the model bank can still omit the true physiology.',
            'carry_over':carry if authority=='inspect' else None,'settings_support':selected_landscape['input_support'],
            'loss_definition':{'threshold_crossing':2.,'below_threshold_severity':.2,'unfinished_target':.8,
                'measurement_burden_weight':burden_weight,
                'interpretation':'Research preference under declared loss weights, not a treatment recommendation'},
            'provenance':'Synthetic competing-model experiment; no diagnostic probabilities or validated counterfactual treatment effects',
            'measurement_method':'Gaussian quadrature over possible observations; expected reduction in scenario-decision loss minus stated burden and delay costs'}
