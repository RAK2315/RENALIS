"""A localized dialysis research twin. All built-in observations are synthetic.

Hidden simulator truth is used only to generate observations and score future outcomes.
The particle filter receives historical priors and observations available by the cutoff.
It never receives the hidden state or later observations.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from functools import lru_cache
import math
import numpy as np

MODEL_VERSION = "history-informed-particle-twin/0.4"
N_PARTICLES = 192
HORIZON = 30
DURATION = 240


@dataclass(frozen=True)
class Patient:
    id: str
    name: str
    age: int
    sex: str
    diabetes: bool
    dry_weight: float
    target_ml: int
    initial_plasma: float
    baseline_sbp: float
    refill_prior: float
    refill_true: float
    compensation: float
    uf_ml_h: int
    prior_sessions: int
    phenotype: str
    seed: int
    dropout: bool = False


PATIENTS = {
    "RNL-014": Patient("RNL-014", "Meera Rao", 58, "F", True, 65, 3500, 3.2, 151, .82, .76, 12, 1050, 24, "Lower refill tolerance", 140),
    "RNL-027": Patient("RNL-027", "Arjun Nair", 46, "M", False, 72, 2800, 3.6, 144, 1.04, 1.07, 26, 750, 31, "Stable compensation", 270),
    "RNL-032": Patient("RNL-032", "Leela Shah", 67, "F", True, 59, 3000, 2.95, 148, .72, .69, 10, 950, 18, "Reduced observation coverage", 320, True),
    "RNL-041": Patient("RNL-041", "Kabir Sen", 61, "M", False, 78, 3300, 3.8, 158, .88, .93, 19, 950, 42, "Variable session response", 410),
}


def machine_rate(p: Patient, minute: int) -> int:
    if p.id == "RNL-014" and minute >= 60:
        return 1150
    if p.id == "RNL-032" and minute >= 120:
        return 800
    return p.uf_ml_h


def advance(plasma, tissue, removed, refill, reference_plasma, reference_tissue, rate):
    """One-minute conservative fluid step, L and L/hour. No negative volumes."""
    refill_rate = np.clip(refill * np.maximum(tissue, 0) / reference_tissue *
                          (1 + .65 * np.maximum(reference_plasma - plasma, 0)), 0, 1.8)
    moved = np.minimum(tissue, refill_rate / 60)
    taken = np.minimum(plasma + moved, rate / 60000)
    return plasma + moved - taken, tissue - moved, removed + taken


def pressure(plasma, reference, baseline, compensation):
    ratio = np.maximum(.35, plasma / reference)
    return baseline * ratio ** 2.65 + compensation * np.maximum(0, 1 - ratio)


@lru_cache(maxsize=8)
def observations(patient_id: str) -> tuple[dict, ...]:
    """Generate a deterministic future session; callers must slice by cutoff."""
    p = PATIENTS[patient_id]
    rng = np.random.default_rng(p.seed)
    plasma, tissue, removed = p.initial_plasma, p.target_ml / 1000, 0.
    rows = []
    for minute in range(DURATION + 1):
        sbp = float(pressure(plasma, p.initial_plasma, p.baseline_sbp, p.compensation))
        # Five-minute cuff observations belong to our sandbox, not HEMOBP's cadence.
        cuff = minute % 5 == 0 and not (p.dropout and 65 <= minute <= 105)
        if p.id == "RNL-041" and minute == 80:
            cuff = True
        reading = round(sbp + rng.normal(0, 2.1), 1) if cuff else None
        quality = "valid"
        if p.id == "RNL-041" and minute == 80:
            reading = 42.
            quality = "artifact"
        rows.append({"minute": minute, "sbp": reading, "quality": quality,
                     "uf_ml_h": machine_rate(p, minute),
                     "hr": round(72 + .3 * (p.baseline_sbp - sbp) + rng.normal(0, 1.2)),
                     "dialysate_c": 36.5, "blood_flow_ml_min": 280,
                     "removed_ml": round(removed * 1000),
                     "source": "synthetic medical-device replay"})
        plasma, tissue, removed = advance(plasma, tissue, removed, p.refill_true,
                                         p.initial_plasma, p.target_ml / 1000,
                                         machine_rate(p, minute))
    return tuple(rows)


def historical_sessions(p: Patient) -> list[dict]:
    from .history import patient_history
    return patient_history(p.id)['sessions']


def _filter(p: Patient, cutoff: int, dynamic: bool = True, history: bool = True):
    rng = np.random.default_rng(p.seed + 1000)
    n = N_PARTICLES
    # Static ablation uses a population prior. Patient history determines the fused prior.
    from .history import patient_history
    memory=patient_history(p.id) if history else None
    prior = memory['refill_l_h'] if memory else .88
    reference = np.maximum(2.4, rng.normal(p.initial_plasma if history else 3.3, .15, n))
    reference_tissue = np.maximum(1., rng.normal(p.target_ml / 1000 if history else 3.2, .17, n))
    baseline = rng.normal(p.baseline_sbp if history else 149, 4.5, n)
    refill = np.clip(rng.normal(prior, memory['refill_sd'] if memory else .24, n), .35, 1.4)
    compensation = rng.normal(p.compensation if history else 18, 4., n)
    plasma, tissue, removed = reference.copy(), reference_tissue.copy(), np.zeros(n)
    weights = np.ones(n) / n
    log = []
    known = observations(p.id)[:cutoff + 1]
    for row in known:
        minute = row["minute"]
        if minute:
            previous_rate = known[minute - 1]["uf_ml_h"]
            plasma, tissue, removed = advance(plasma, tissue, removed, refill,
                                             reference, reference_tissue, previous_rate)
        expected = pressure(plasma, reference, baseline, compensation)
        if dynamic and row["sbp"] is not None and row["quality"] == "valid":
            # Robust likelihood guards against a single surprising measurement.
            likelihood = np.exp(-.5 * ((expected - row["sbp"]) / 3.5) ** 2) + 1e-12
            weights *= likelihood
            weights /= weights.sum()
            if 1 / np.sum(weights ** 2) < n * .55:
                indices = rng.choice(n, size=n, p=weights)
                plasma, tissue, removed = plasma[indices], tissue[indices], removed[indices]
                reference, reference_tissue = reference[indices], reference_tissue[indices]
                baseline, refill, compensation = baseline[indices], refill[indices], compensation[indices]
                refill = np.clip(refill + rng.normal(0, .008, n), .3, 1.5)
                weights.fill(1 / n)
        log.append({"minute": minute, "estimated_sbp": round(float(np.average(
            pressure(plasma, reference, baseline, compensation), weights=weights)), 1)})
    # Draw equally weighted posterior particles for forecasting and quantiles.
    indices = rng.choice(n, size=n, p=weights)
    return {"plasma": plasma[indices], "tissue": tissue[indices], "removed": removed[indices],
            "reference": reference[indices], "reference_tissue": reference_tissue[indices],
            "baseline": baseline[indices], "refill": refill[indices],
            "compensation": compensation[indices], "log": log, "known": known}


def _forecast(state: dict, cutoff: int, rate: int, mode: str = "constant"):
    plasma, tissue, removed = (state[k].copy() for k in ("plasma", "tissue", "removed"))
    below = np.zeros(len(plasma), dtype=bool)
    rows, crossings = [], np.full(len(plasma), np.nan)
    horizon = min(HORIZON, DURATION - cutoff)
    for step in range(horizon + 1):
        values = pressure(plasma, state["reference"], state["baseline"], state["compensation"])
        lo, median, hi = np.quantile(values, [.1, .5, .9])
        if step:
            new = (values <= 90) & ~below
            crossings[new] = step
            below |= values <= 90
        rows.append({"minute": cutoff + step, "sbp": round(float(median), 1),
                     "lower": round(float(lo), 1), "upper": round(float(hi), 1),
                     "plasma_l": round(float(np.median(plasma)), 3),
                     "tissue_l": round(float(np.median(tissue)), 3),
                     "removed_ml": round(float(np.median(removed)) * 1000)})
        effective_rate = rate
        if mode == "step_down" and step >= 15:
            effective_rate = max(300, rate - 200)
        if step < horizon:
            plasma, tissue, removed = advance(plasma, tissue, removed, state["refill"],
                                             state["reference"], state["reference_tissue"], effective_rate)
    finite = crossings[np.isfinite(crossings)]
    return {"trajectory": rows, "crossing_fraction": round(float(below.mean()), 3),
            "median_crossing_minutes": round(float(np.median(finite))) if len(finite) else None,
            "fluid_removed_next_ml": rows[-1]["removed_ml"] - rows[0]["removed_ml"],
            "final": rows[-1]}


@lru_cache(maxsize=512)
def snapshot(patient_id: str, cutoff: int):
    p = PATIENTS[patient_id]
    cutoff = max(0, min(DURATION, cutoff))
    state = _filter(p, cutoff)
    known = state["known"]
    valid = [r for r in known if r["sbp"] is not None and r["quality"] == "valid"]
    latest = valid[-1]
    age = cutoff - latest["minute"]
    estimate = _forecast(state, cutoff, known[-1]["uf_ml_h"])
    already_low = latest["sbp"] <= 90
    status = "complete" if cutoff >= DURATION else "insufficient" if age > 15 else "current_event" if already_low else \
             "review" if estimate["crossing_fraction"] >= .35 else "monitor"
    alert = {"status": status,
             "crossing_fraction": None if status in ("insufficient", "current_event", "complete") else estimate["crossing_fraction"],
             "lead_minutes": estimate["median_crossing_minutes"] if status == "review" else None,
             "reason": "Dialysis session complete; no further treatment forecast." if status == "complete" else
                       "Last valid BP is stale; prospective alert withheld." if status == "insufficient" else
                       "Latest valid BP is already at or below 90 mmHg; this is not an advance warning." if already_low else
                       "Posterior simulations cross the BP threshold within the next 30 minutes." if status == "review" else
                       "Most posterior simulations remain above the threshold."}
    return {"patient": {**asdict(p), "refill_true": None, "seed": None,
                        "condition": "End-stage chronic kidney disease",
                        "provenance": "fictional patient / synthetic EHR"},
            "cutoff": cutoff, "duration": DURATION, "horizon": min(HORIZON, DURATION - cutoff),
            "history": [{**r, "estimated_sbp": state["log"][r["minute"]]["estimated_sbp"]} for r in known],
            "latest": latest, "current_machine": known[-1], "bp_age_minutes": age,
            "compartments": {"plasma_l": round(float(np.median(state["plasma"])), 2),
                             "tissue_l": round(float(np.median(state["tissue"])), 2),
                             "removed_ml": known[-1]["removed_ml"],
                             "refill_l_h": round(float(np.median(state["refill"])), 2)},
            "forecast": estimate, "alert": alert, "sessions": historical_sessions(p),
            "historical_learning": __import__('backend.history',fromlist=['patient_history']).patient_history(p.id),
            "model": {"version": MODEL_VERSION, "particles": N_PARTICLES,
                      "interval": "10th–90th percentile of model particles; not clinically calibrated",
                      "endpoint": "New measured systolic BP ≤90 mmHg within 30 minutes",
                      "availability": f"Only observations at or before session minute {cutoff}",
                      "source": "Synthetic observations + synthetic EHR priors",
                      "calibration": "Unvalidated research model; crossing fraction is not calibrated clinical probability"}}


def scenario(patient_id: str, cutoff: int, rate_ml_h: int, profile: str):
    p = PATIENTS[patient_id]
    state = _filter(p, cutoff)
    result = _forecast(state, cutoff, rate_ml_h, profile)
    factual = snapshot(patient_id, cutoff)
    removed_now = factual["current_machine"]["removed_ml"]
    return {**result, "rate_ml_h": rate_ml_h, "profile": profile,
            "remaining_target_ml": max(0, p.target_ml - removed_now - result["fluid_removed_next_ml"]),
            "additional_remaining_ml": factual["forecast"]["fluid_removed_next_ml"] - result["fluid_removed_next_ml"],
            "provenance": "Hypothetical physiological simulation, not an observed treatment outcome",
            "support": "Sandbox rate range 300–1,400 mL/h; not a prescription recommendation"}


def revealed_outcome(patient_id: str, cutoff: int):
    # Explicit separate endpoint; never called by the estimator.
    rows = [r for r in observations(patient_id)[cutoff+1:cutoff+HORIZON+1]
            if r["sbp"] is not None and r["quality"] == "valid"]
    events = [r for r in rows if r["sbp"] <= 90]
    return {"observations": rows, "event": bool(events),
            "first_event_minute": events[0]["minute"] if events else None,
            "provenance": "Revealed future synthetic readings; excluded from all forecast inputs"}


def patient_list(cutoff: int):
    result = []
    for pid, p in PATIENTS.items():
        s = snapshot(pid, cutoff)
        result.append({"id": pid, "name": p.name, "age": p.age, "sex": p.sex,
                       "phenotype": p.phenotype, "status": s["alert"]["status"],
                       "sbp": s["latest"]["sbp"], "bp_age_minutes": s["bp_age_minutes"],
                       "crossing_fraction": s["alert"]["crossing_fraction"],
                       "uf_ml_h": s["current_machine"]["uf_ml_h"], "minute": cutoff})
    return result


def evaluation():
    """Real computations on a fixed synthetic benchmark, never hard-coded scores."""
    rows = []
    for pid in PATIENTS:
        for cutoff in (30, 60, 90, 120, 150, 180):
            s = snapshot(pid, cutoff)
            if s["alert"]["status"] in ("insufficient", "current_event"):
                continue
            outcome = revealed_outcome(pid, cutoff)
            if not outcome["observations"]:
                continue
            future = outcome["observations"][-1]
            index = future["minute"] - cutoff
            p = PATIENTS[pid]
            fused = s["forecast"]["trajectory"][index]["sbp"]
            dynamic_state = _filter(p, cutoff, history=False)
            dynamic = _forecast(dynamic_state, cutoff, s["current_machine"]["uf_ml_h"])["trajectory"][index]["sbp"]
            static_state = _filter(p, cutoff, dynamic=False)
            static = _forecast(static_state, cutoff, s["current_machine"]["uf_ml_h"])["trajectory"][index]["sbp"]
            rows.append({"patient_id": pid, "cutoff": cutoff, "actual": future["sbp"],
                         "fused": fused, "dynamic": dynamic, "static": static,
                         "persistence": s["latest"]["sbp"], "event": outcome["event"],
                         "alert": s["alert"]["status"] == "review"})
    models = []
    for key, label in (("persistence", "Last BP"), ("static", "History + machine"),
                       ("dynamic", "Population prior + observations"), ("fused", "Personalized fused twin")):
        errors = [abs(r[key] - r["actual"]) for r in rows]
        models.append({"key": key, "label": label, "mae_mm_hg": round(float(np.mean(errors)), 2) if errors else None})
    tp = sum(r["alert"] and r["event"] for r in rows)
    fp = sum(r["alert"] and not r["event"] for r in rows)
    positives = sum(r["event"] for r in rows)
    return {"models": models, "rows": rows, "eligible_windows": len(rows),
            "positive_windows": positives, "true_alerts": tp, "false_alerts": fp,
            "sensitivity": round(tp/positives, 3) if positives else None,
            "ppv": round(tp/(tp+fp), 3) if tp+fp else None,
            "provenance": "Fixed four-patient synthetic sandbox benchmark",
            "limitations": ["Not clinical validation or external validation.",
                           "Generator and estimator share a model family; results may be optimistic.",
                           "Overlapping forecast windows are not independent events.",
                           "Synthetic cuff cadence is 5 minutes, unlike HEMOBP's usual 30-minute cadence.",
                           "Particle crossing fractions have not been probability-calibrated."]}
