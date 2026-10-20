"""Explicit synthetic device acquisition, isolated from inference and policy scoring."""
import numpy as np
from .model import PATIENTS, advance, pressure


def acquire_fixture(patient_id, minute, channel):
    p = PATIENTS[patient_id]
    # Ground truth is confined to this acquisition boundary; the selector never calls it.
    from .model import machine_rate
    plasma, tissue, removed = p.initial_plasma, p.target_ml / 1000, 0.
    for t in range(minute):
        plasma, tissue, removed = advance(plasma,tissue,removed,p.refill_true,p.initial_plasma,p.target_ml/1000,machine_rate(p,t))
    ratio = plasma / p.initial_plasma
    rng = np.random.default_rng(p.seed + minute * 101 + sum(map(ord,channel)))
    if channel == 'relative_blood_volume':
        return round(float(100 * ratio + rng.normal(0,.7)),2)
    if channel == 'cardiac_output':
        return round(float(5.2 * max(.35,ratio)**1.8 + rng.normal(0,.12)),2)
    return round(float(pressure(plasma,p.initial_plasma,p.baseline_sbp,p.compensation)+rng.normal(0,1.4)),1)
