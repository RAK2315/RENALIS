"""Synthetic health records: labs, diagnoses and medicines for the built-in patients.

Only some fields change the model, and each effect is an authored research
assumption, not a fitted clinical coefficient:
- Albumin sets the starting refill estimate before past sessions refine it.
  Low albumin means weaker pull of water back into the blood.
- Heart failure or a beta-blocker makes "heart not pumping harder" more likely
  at the start of the cause comparison.
Everything else is recorded and shown, but marked as not used.
"""

POPULATION_REFILL_L_H = .88
REFERENCE_ALBUMIN_G_DL = 3.8
ALBUMIN_REFILL_SLOPE = .10   # fractional change in refill per g/dL of albumin
HEART_FAILURE_CARDIAC_PRIOR = 1.5
BETA_BLOCKER_CARDIAC_PRIOR = 1.3
FAMILY_ORDER = ('volume', 'vascular', 'cardiac', 'mixed')

GENETIC_NOTE = 'Not used: no genetic marker is proven to predict low blood pressure during dialysis.'

RECORDS = {
    'RNL-014': {'labs': {'albumin_g_dl': 3.1, 'haemoglobin_g_dl': 9.8, 'sodium_mmol_l': 136},
                'diagnoses': ['Kidney failure on dialysis', 'Type 2 diabetes', 'High blood pressure'],
                'medicines': [{'name': 'Amlodipine', 'kind': 'blood pressure medicine', 'beta_blocker': False}],
                'heart_failure': False},
    'RNL-027': {'labs': {'albumin_g_dl': 4.1, 'haemoglobin_g_dl': 11.6, 'sodium_mmol_l': 139},
                'diagnoses': ['Kidney failure on dialysis', 'High blood pressure'],
                'medicines': [{'name': 'Losartan', 'kind': 'blood pressure medicine', 'beta_blocker': False}],
                'heart_failure': False},
    'RNL-032': {'labs': {'albumin_g_dl': 3.4, 'haemoglobin_g_dl': 10.2, 'sodium_mmol_l': 134},
                'diagnoses': ['Kidney failure on dialysis', 'Type 2 diabetes', 'Heart failure'],
                'medicines': [{'name': 'Metoprolol', 'kind': 'beta-blocker', 'beta_blocker': True},
                              {'name': 'Furosemide', 'kind': 'water tablet', 'beta_blocker': False}],
                'heart_failure': True},
    'RNL-041': {'labs': {'albumin_g_dl': 3.9, 'haemoglobin_g_dl': 11.0, 'sodium_mmol_l': 138},
                'diagnoses': ['Kidney failure on dialysis', 'Coronary artery disease'],
                'medicines': [{'name': 'Metoprolol', 'kind': 'beta-blocker', 'beta_blocker': True}],
                'heart_failure': False},
}


def lab_refill_prior(patient_id: str) -> float:
    """Population refill shifted by albumin. Unknown patients keep the population value."""
    record = RECORDS.get(patient_id)
    if not record:
        return POPULATION_REFILL_L_H
    albumin = record['labs']['albumin_g_dl']
    factor = 1 + ALBUMIN_REFILL_SLOPE * (albumin - REFERENCE_ALBUMIN_G_DL)
    return round(POPULATION_REFILL_L_H * min(1.15, max(.8, factor)), 4)


def family_prior(patient_id: str) -> list[float]:
    """Starting weight for each cause family, normalised to sum to one."""
    record = RECORDS.get(patient_id)
    weights = [1., 1., 1., 1.]
    if record:
        cardiac = FAMILY_ORDER.index('cardiac')
        if record['heart_failure']:
            weights[cardiac] *= HEART_FAILURE_CARDIAC_PRIOR
        if any(m['beta_blocker'] for m in record['medicines']):
            weights[cardiac] *= BETA_BLOCKER_CARDIAC_PRIOR
    total = sum(weights)
    return [round(w / total, 4) for w in weights]


def record_summary(patient_id: str) -> dict | None:
    record = RECORDS.get(patient_id)
    if not record:
        return None
    albumin = record['labs']['albumin_g_dl']
    effects = [{'field': 'Albumin', 'used': True, 'status': 'used',
                'effect': f'Albumin {albumin} g/dL sets her starting refill speed to {lab_refill_prior(patient_id):.2f} L/h '
                          f'(average patient {POPULATION_REFILL_L_H:.2f}). Past sessions then refine it.'}]
    prior = family_prior(patient_id)
    reasons = [r for r, on in (('heart failure', record['heart_failure']),
                               ('a beta-blocker', any(m['beta_blocker'] for m in record['medicines']))) if on]
    effects.append({'field': 'Diagnoses and medicines', 'used': bool(reasons),
                    'status': 'used' if reasons else 'no_change',
                    'effect': (f'Because of {" and ".join(reasons)}, “heart not pumping harder” starts at '
                               f'{prior[2] * 100:.0f}% instead of 25%.') if reasons else
                              'No heart failure or beta-blocker, so all four causes start equal.'})
    beta_blocker = any(m['beta_blocker'] for m in record['medicines'])
    effects.append({'field': 'Smartwatch heart rate', 'used': True, 'status': 'used',
                    'effect': 'Her beta-blocker blunts the heart-rate rise, so the twin expects a smaller one.' if beta_blocker else
                              'A rising heart rate means the body is fighting falling blood volume. The twin reads it every 5 minutes.'})
    effects.append({'field': 'Haemoglobin and sodium', 'used': False, 'status': 'not_used',
                    'effect': 'Recorded and shown. Not used by the model yet.'})
    effects.append({'field': 'Genetic markers', 'used': False, 'status': 'not_used', 'effect': GENETIC_NOTE})
    return {**record, 'lab_refill_prior_l_h': lab_refill_prior(patient_id),
            'population_refill_l_h': POPULATION_REFILL_L_H, 'family_prior': prior,
            'effects': effects, 'genetic_markers': None, 'genetic_note': GENETIC_NOTE,
            'provenance': 'synthetic health record'}
