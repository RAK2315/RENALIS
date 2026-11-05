# Fixing the four open problems: research notes

Reviewed 5 November 2026, eight days before the jury (13 November). This is a focused primary-source review, not a systematic review. It covers the four weaknesses listed in the README and the [October review](research-review-2026-10.md). Every number about RENALIS comes from files in this repo. Every outside claim links to the paper, dataset page or official docs that owns it. Where the evidence is weak, this note says so.

**Rule used throughout:** test patients are only for reporting. Model settings, priors, thresholds and feature choices are picked on the 563 fit patients or the 141 calibration patients.

## One-screen summary

| Problem | Best fix before 13 Nov | Effort | Confidence it helps |
|---|---|---|---|
| 1. Twin loses to "repeat last BP" (MAE 12.8 vs 12.1) | **Shrink the twin's predicted change.** Fit `next = last BP + k × twin change + b` on fit patients. With k = 0 this *is* persistence, so the twin cannot do worse on fit data. Then feed the twin's outputs into the existing tree model as extra features | 0.5 day + 1–2 days | High that it stops losing; low–medium that it beats the 11.2 ML model |
| 2. Warnings: 61% caught, 14% right | **Report it the way the field does, then add cheap features.** Our lift over chance (5.3×) matches the best comparable paper (5.4×). Add per-episode and per-session scoring, alarms per session-hour, first vs repeat drops, and a decision curve. Then add interdialytic weight gain, planned removal per kg, pre-dialysis BP, last-10-session drop rate, dialysis vintage | 0.5 day + 1 day | High for honest framing; medium for a small PPV gain |
| 3. Labs and heart rate untested on real data | **Say so plainly, and fix the priors to match the evidence.** No open dataset has dialysis-session BP, machine settings, heart rate and labs together. HEMOBP *measured* pulse but did not publish it. MIMIC-IV needs 1–2 weeks of credentialing and is ICU data. Fix the beta-blocker prior (it also lowers refill) and treat a falling heart rate as a danger sign | 0.5 day | High that the claims become defensible; the inputs stay unvalidated |
| 4. Smart test choice does not beat repeat BP (0.241/0.245 vs 0.222) | **Make the planner less sure of its own sensor models, then re-test on new seeds.** Widen non-BP sensor noise (tempered likelihood). Choose a non-BP test only if it beats a repeat cuff by a margin. Keep the old 24 seeds frozen and report v0.5 on fresh seeds | 1 day | Medium that "confidently wrong" cases drop; low that it beats repeat BP on average |

The short version for the jury: the ML warning performs like published systems. The twin's value is its explanation, not a lower error than persistence. Smart test choice fails because it trusts sensor models that do not match the test world. The literature predicts exactly that.

---

## Problem 1. The twin loses to "repeat the last reading"

### What the code does now

- `scripts/evaluate_twin_hemobp.py` runs a 192-particle filter per session, with population priors only. It uses refill 0.88 ± 0.24 L/h, compensation 18 ± 4, plasma = 4.5% of start weight, a per-particle volume sensitivity `gamma ~ lognormal(0, 0.7)` and a BP likelihood sd of **9** mmHg (see `docs/twin-hemobp.json`). The task brief said ~5; the file says 9.
- The forecast is `last measured BP + (twin BP later − twin BP now)`. So the twin's error is persistence's error plus the error in its predicted change. If the predicted change is biased or noisy, the twin must lose. The measured bias is −1.93 mmHg: the twin expects drops that do not come.
- Only `refill` gets jitter after resampling. `gamma`, `compensation` and `baseline` get none, so their particle sets collapse after a few resamples. This is the standard degeneracy problem for static parameters in particle filters ([Kantas et al. 2015, *Statistical Science*](https://doi.org/10.1214/14-STS511)).
- **The twin's alarm result is degenerate.** In `docs/twin-hemobp.json` the calibration threshold collapsed to 0.0. Every window raised an alarm (sensitivity 1.0, PPV 0.0252, which is the base rate). PR-AUC 0.059 is only about 2.3× chance. Do not present the twin's own risk score as a warning.

### Why a body model can lose to persistence

1. **Persistence is a strong baseline when readings are sparse and noisy.** In HEMOBP, BP and pulse were taken every 30 minutes, plus extra readings when clinically needed ([Lin et al. 2019, *Scientific Data*](https://doi.org/10.1038/s41597-019-0319-8)). Over one 30-minute gap, most change is noise or events the model cannot see. Forecasting research uses the naive "last value" forecast as the reference scale for this reason ([Hyndman & Koehler 2006](https://doi.org/10.1016/j.ijforecast.2006.03.001)).
2. **The twin's main mechanism may be the wrong one.** It explains drops mostly through refill failing to keep up. In 24 patients with absolute blood volume measured, refill was a near-constant fraction of fluid removed (about 70–74%). It was **not lower** in sessions with symptomatic events. Those events instead went with an absolute blood volume below about 65 mL/kg ([Kron et al. 2017, *Blood Purification*](https://doi.org/10.1159/000453441)). An earlier study by the same group found refill volume tracked removal volume (r² = 0.82), not pre-dialysis overload ([Kron et al. 2016, *Hemodialysis International*](https://doi.org/10.1111/hdi.12417)). So starting blood volume, not refill speed, may be the parameter that matters. The twin guesses that volume from body weight.
3. **Many drops are sudden reflex events, not smooth volume loss.** In patients prone to hypotension, the sharp drop came with *falling* sympathetic activity, vessel tone and heart rate ([Converse et al. 1992, *J Clin Invest*](https://doi.org/10.1172/JCI116037)). Beat-to-beat data showed the same: heart rate rose during ordinary ultrafiltration (77 → 89 bpm), but the sudden symptomatic fall came with bradycardia ([Barnas et al. 1999, *JASN*](https://doi.org/10.1681/ASN.V10122577)). A smooth two-tank model cannot forecast such a step.
4. **Too few readings to learn per-session parameters.** A session gives roughly 8 readings, and the filter tries to learn five unknowns from them. Patients also differ a lot: IDH ran from 0% to 100% of treatments across patients ([Sands et al. 2014, *Hemodialysis International*](https://doi.org/10.1111/hdi.12138)). Population priors with no per-patient memory are a poor match for that spread.

### How published physiological / twin models are validated

I found no peer-reviewed IDH digital twin validated against real intradialytic BP. A recent preprint pairs a mechanistic fluid model with an unscented Kalman filter and an ML residual model. It is validated only on simulated patients ([Research Square preprint, not peer-reviewed](https://www.researchsquare.com/article/rs-11119867/v1)). The ML papers all compare against learned baselines. The field is now asking for a naive baseline as standard ([Kim et al. 2026, *Front Digit Health*](https://doi.org/10.3389/fdgth.2026.1804788)). RENALIS already reports persistence. That is a strength to state, not hide.

### Fixes, ranked

**1a. Shrink the twin's change toward zero, learned on fit patients (MOS-style correction).** *Do this first.*
- What: on fit-patient windows, regress `next_sbp − sbp` on the twin's predicted change: `next = sbp + k·Δtwin + b`. Pick k and b on fit, check on calibration, and report on test once. This is the same idea as weather "model output statistics": you keep the physics model and statistically correct its output ([Gneiting et al. 2005, *Monthly Weather Review*](https://doi.org/10.1175/MWR2904.1)).
- Expected effect: removes the −1.9 bias. With k = 0 it equals persistence (12.13 on the same windows), so it should stop losing. A small gain below persistence is possible if Δtwin carries any signal. The ML model shows about 1 mmHg of predictable change exists (12.19 → 11.16 in `docs/observed-v04.json`). **Honest caveat:** if the fitted k is near 0, the twin has no forecasting value on HEMOBP. That finding is still worth reporting.
- Effort: about half a day. Run the twin on a sample of fit sessions (~1,000 sessions takes ~2 minutes per `twin-hemobp.json`).
- Files: `scripts/evaluate_twin_hemobp.py`, `docs/twin-hemobp.json`, README results section.
- Overfitting risk: low. Two parameters, fit on fit patients only.

**1b. Hybrid: give the twin's outputs to the tree model as features (residual learning).**
- What: add twin features (predicted change, crossing fraction, posterior plasma ratio, posterior refill, posterior gamma) to the existing `HistGradientBoostingRegressor`. Or train it on the residual `next_sbp − twin forecast`. Physics-plus-learned-correction designs fit the physics part first and let the learned part explain only what physics cannot. This helps both interpretation and generalization ([Yin et al. 2021, APHYNITY, arXiv](https://arxiv.org/abs/2010.04456)). The statistical basis is an explicit "model discrepancy" term ([Kennedy & O'Hagan 2001, *JRSS B*](https://doi.org/10.1111/1467-9868.00294)).
- Expected effect: uncertain. If the twin features add nothing beyond `trend_mm_hg_min` and `rate_ml_h`, MAE stays near 11.16. A paired, patient-clustered comparison (the existing `cluster_interval` function) shows whether the gain is real. Either result is honest. "The twin adds X mmHg to ML" is a stronger pitch than "the twin alone".
- Effort: 1–2 days, mostly runtime. Twin features are needed for fit, calibration and test windows. Subsample fit sessions.
- Files: new or extended script next to `scripts/evaluate_observed_v04.py`; a new results JSON.
- Overfitting risk: low if feature choices are fixed before looking at test.

**1c. Empirical-Bayes priors and per-patient memory on HEMOBP.**
- What: (i) fit the prior hyperparameters (gamma mean/sd, compensation, plasma fraction, likelihood sd) on fit patients only. Use a coarse grid scored by one-step-ahead log-likelihood or MAE. A particle filter gives a likelihood estimate per session, which is the standard basis for this ([Kantas et al. 2015](https://doi.org/10.1214/14-STS511)). (ii) For each patient, run `backend/history.py`'s `learn()` on that patient's **earlier sessions only**, so each session starts from a patient-specific prior. Patient-to-patient spread is large ([Sands et al. 2014](https://doi.org/10.1111/hdi.12138)). (iii) Add small jitter to every static parameter, or use the Liu–West kernel-shrinkage move reviewed by [Kantas et al. 2015](https://doi.org/10.1214/14-STS511), so the particles do not collapse.
- Expected effect: likely reduces bias and some error. Unlikely on its own to beat the ML model, because problems 2 and 3 above are structural.
- Effort: 2–3 days. Probably too much before 13 Nov if 1a and 1b are done. Mark it as next.
- Files: `scripts/evaluate_twin_hemobp.py`, `backend/history.py` (would need to accept HEMOBP sessions), `docs/twin-hemobp.json`.
- Overfitting risk: medium. A grid search over many hyperparameters can overfit calibration. Use fit for the search, calibration for one confirmation, and test once. Using a test patient's *own earlier sessions* is allowed, because that is information available at prediction time. It is not tuning.

**1d. Longer-term: change the structure.** Add starting absolute blood volume as the key unknown ([Kron et al. 2017](https://doi.org/10.1159/000453441)). Add a "sudden reflex drop" component that a smooth model lacks ([Converse et al. 1992](https://doi.org/10.1172/JCI116037)). Both need data HEMOBP lacks (blood volume, beat-to-beat BP). Do not attempt before the jury.

---

## Problem 2. Warnings catch 61% of drops, but only 14% of warnings are right

### Where RENALIS stands against published work

The endpoint here is strict and rare. It is the next distinct reading ≤ 90, 5–35 minutes ahead, from a current reading above 90. The base rate is 2.57% (`docs/alarm-tradeoff.json`). PPV depends heavily on base rate, so compare **lift** (PPV ÷ base rate) and use precision–recall, not ROC, for rare events ([Saito & Rehmsmeier 2015, *PLOS ONE*](https://doi.org/10.1371/journal.pone.0118432)).

| Study | Endpoint / unit | Base rate | Sensitivity | PPV | Lift |
|---|---|---|---|---|---|
| **RENALIS v0.4** (`observed-v04.json`) | next reading ≤ 90, per window | 2.57% | 0.61 | 0.135 | **5.3×** |
| RENALIS, first drop in session only | same | — | 0.50 | 0.115 | — |
| RENALIS, repeat drops | same | — | 0.84 | 0.173 | — |
| [Zhang et al. 2023, *NDT*](https://doi.org/10.1093/ndt/gfad070) | SBP < 90 within 15–75 min, per BP reading (~30 min) | 4.06% | 0.65 | 0.22 | **5.4×** |
| Zhang et al. 2023 | same, **per session** | 16.2% of sessions | 0.73 | 0.39 | 2.4× |
| [Kim et al. 2026, *Front Digit Health*](https://doi.org/10.3389/fdgth.2026.1804788) | Nadir90, first event only, at best-F1 threshold | 0.7–10.4% before first event (range across definitions) | not reported | 0.129 | — |
| [Kim et al. 2022, *Front Med*](https://doi.org/10.3389/fmed.2022.878858) | Nadir90 within 10 min | 2.2% (external) | not reported | not reported | AUPRC 0.118 (external) |
| [Lee et al. 2021, *CJASN*](https://doi.org/10.2215/CJN.09280620) | nadir < 90 within 1 h, per timestamp | 8% | not in main text | not in main text | AUPRC 0.62 |

What this shows:
- **14% PPV is normal for this task, not a failure.** At the same unit of analysis, the best comparable system ([Zhang et al. 2023](https://doi.org/10.1093/ndt/gfad070)) has the same lift. Its features included pulse, labs and 10-session history. Its threshold came from clinicians accepting a 10% false-positive rate, not from a cost analysis.
- **Papers above 14% PPV either use a looser endpoint or a different unit.** Per-session scoring gives 0.39–0.54 in Zhang's table (thresholds 0.09–0.20). A 1-hour "any time" horizon gives Lee's AUPRC of 0.62. Pooling repeat drops inflates results. In Kim 2026, PPV on repeat drops exceeded 0.81 for one definition "mostly reflect[ing] higher prevalence" ([Kim et al. 2026](https://doi.org/10.3389/fdgth.2026.1804788)). The same paper found that a naive baseline reached AUROC 0.798 on all fall-based events with no training.
- **Definitions matter.** Nadir90 (SBP < 90) and Fall20 (a fall of ≥ 20 mmHg) give very different base rates. Fall20 was 35–41% of windows in [Kim et al. 2022](https://doi.org/10.3389/fmed.2022.878858), against 2–4% for Nadir90. That is why Fall20 PPVs look high. A nadir below 90 had the strongest link with mortality ([Flythe et al. 2015, *JASN*](https://doi.org/10.1681/ASN.2014020222)). Keep Nadir90. Note that RENALIS uses **≤ 90**, while Flythe and most papers use **< 90**. Say so on the slide.
- **Selection bias can make warnings look better than they are.** The hypotension prediction index's apparent accuracy may be inflated by how non-event samples were picked ([Enevoldsen & Vistisen 2022, *Anesthesiology*](https://doi.org/10.1097/ALN.0000000000004320)). RENALIS already excludes windows that start at or below 90 and uses every eligible window. That is the stricter design. Say so.

### Fixes, ranked

**2a. Score per episode and per session, add alarm burden, split first vs repeat drops. Pre-declare the definitions.** *Do this first.*
- What: keep window PPV, and add:
  - **episode-level recall:** share of drops with any alarm 5–35 min before;
  - **alarm-level precision** with the existing 30-minute refractory period (`consolidated_ppv` = 0.1406 already exists);
  - **alarms per session and per session-hour** (0.28 alarms per session already computed);
  - **first-drop vs repeat-drop results** (already computed as `by_event_context`).

  This is the evaluation design used by a well-known ICU early-warning system: event-based recall, alarm-based precision, a 30-minute silencing period, and alarms per patient-hour ([Hyland et al. 2020, *Nature Medicine*](https://doi.org/10.1038/s41591-020-0789-4); details in the [arXiv full text](https://arxiv.org/abs/1904.07990)). Kim 2026 recommends separating first and repeat events and reporting a naive baseline ([Kim et al. 2026](https://doi.org/10.3389/fdgth.2026.1804788)).
- Expected effect: the model does not change. The story does: about one alarm every 3.5 sessions, 14% right, ~5× better than chance, same as the best published comparator. **Caution:** these extra metrics must be reported side by side with window PPV, not swapped in because they look better. Write the definitions into `docs/evaluation-protocol-v04.json` (or a v0.5) before running.
- Effort: half a day.
- Files: `scripts/alarm_tradeoff.py` or `scripts/evaluate_observed_v04.py`, `docs/alarm-tradeoff.json`, README.
- Overfitting risk: none. No tuning.

**2b. Add known-predictive features HEMOBP already has.**
- What: the current fused model uses only the *previous* session (`prior_nadir`, `prior_mean_sbp`, `prior_rate`, `prior_end_weight`, `prior_session_count`). Add:
  - **interdialytic weight gain** = this session's `weightstart` − previous `weightend` (known at session start);
  - **planned removal per kg** = (`weightstart` − `dryweight`) / `weightstart`;
  - **pre-dialysis SBP** (first reading of the session);
  - **drop rate and mean nadir over the last 10 sessions**;
  - **dialysis vintage** from `idp.csv` `first_dialysis` (present, confirmed in the local file header, currently unused);
  - **body temperature** from `d1.csv` `temperature`;
  - **within-session history**: count of earlier readings ≤ 90 (`prior_low` is computed but only used for reporting) and the running minimum SBP.

  Evidence: in Zhang's model the top features were most recent SBP, IDH rate over the last 10 treatments, mean nadir over the last 10 treatments, blood flow, time, UF rate and fluid removed ([Zhang et al. 2023](https://doi.org/10.1093/ndt/gfad070)). In 44,801 treatments, more frequent IDH went with higher UF volume, lower pre-HD SBP, longer vintage, diabetes, age and higher dialysate temperature ([Sands et al. 2014](https://doi.org/10.1111/hdi.12138)). Recurrence-aware inputs raised AUROC by 3.0–5.5 points for repeat events, but **did not** improve first-event nadir prediction ([Kim et al. 2026](https://doi.org/10.3389/fdgth.2026.1804788)).
- Expected effect: modest. A realistic hope is PR-AUC 0.18 → low 0.20s and a few points of PPV at the same recall, mostly on repeat drops. First drops may barely move. **Do not promise a large gain.**
- Effort: about 1 day, including a rerun (~minutes).
- Files: `scripts/evaluate_observed_v04.py` (`audit_cohort` feature list), `scripts/alarm_tradeoff.py`, `docs/observed-v04.json` (write to a new v0.5 file instead, so v0.4 stays as history).
- Overfitting risk: low if the feature list is written down before the run and the threshold comes from calibration. Do not add and drop features by looking at test.

**2c. Choose the threshold from costs, and show a decision curve.**
- What: decision curve analysis plots net benefit = TP/n − FP/n × pt/(1 − pt) across threshold probabilities pt. Each pt states how many false alarms a clinician accepts per caught drop ([Vickers & Elkin 2006, *Med Decis Making*](https://doi.org/10.1177/0272989X06295361)). For example, pt = 0.10 means 9 false alarms are acceptable per true one. Plot RENALIS against "alarm always" and "never alarm" on calibration data, then test. scikit-learn's `TunedThresholdClassifierCV` can tune a threshold to a custom cost scorer. Its docs warn never to tune the threshold on the data used to train the classifier ([scikit-learn docs](https://scikit-learn.org/stable/modules/classification_threshold.html)). Its default CV is stratified, not grouped, so pass a patient-grouped splitter or use `cv="prefit"` on the calibration patients.
- Expected effect: no PPV gain. `alarm_tradeoff.py` already shows there is no free lunch. But it turns "14% right" into "useful for anyone who accepts ≤ N false alarms per caught drop". Pair it with tiered alerts: "watch" at the current threshold, "act" at a stricter one (≈27% PPV at 19% recall in `alarm-tradeoff.json`).
- Effort: half a day.
- Files: `scripts/alarm_tradeoff.py`, `docs/alarm-tradeoff.json`, one chart in the UI or slides.
- Overfitting risk: low. Thresholds come from calibration.

**2d. Will not work before 13 Nov:** continuous BP, heart rate or blood-volume monitoring. No such data is available (see Problem 3). More model capacity is also unlikely to help much: in [Kim et al. 2022](https://doi.org/10.3389/fmed.2022.878858) logistic regression matched the deep model on internal Nadir90 AUPRC (0.298 vs 0.287).

---

## Problem 3. Lab results and heart rate are untested on real data

### Datasets checked

| Dataset | Access | Intradialytic BP | Heart rate | Labs (albumin) | Session start/stop + UF | Usable before 13 Nov? |
|---|---|---|---|---|---|---|
| **HEMOBP** ([figshare v3](https://doi.org/10.6084/m9.figshare.6260654.v3), CC BY 4.0; [paper](https://doi.org/10.1038/s41597-019-0319-8)) | Open | Yes (~30 min) | **Measured but not published.** The paper says BP *and pulse rate* were taken every 30 min. The deposited `vip.csv` has only `sbp, dbp, dia_temp_value, conductivity, uf, blood_flow, time` (local header checked) | **No.** "Laboratory biochemistry test results were not included since these tests were performed only once a month" | Yes | Already used |
| **MIMIC-IV v3.1** ([PhysioNet](https://physionet.org/content/mimiciv/3.1/)) | Credentialed: CITI training + DUA. Approval "typically takes 1–2 weeks" ([PhysioNet FAQ](https://physionet.org/about/faqs/)) | Yes (charted NIBP) | Yes (charted) | Yes (`labevents`) | Intermittent HD as a procedure with times (itemid 225441), separate from CRRT/CVVHD/SCUF, per the official [mimic-code `rrt.sql`](https://github.com/MIT-LCP/mimic-code/blob/main/mimic-iv/concepts/treatment/rrt.sql). No per-minute UF rate found | **No** (access time; ICU patients, often acute kidney injury, not chronic outpatients) |
| **eICU-CRD v2.0** ([PhysioNet](https://physionet.org/content/eicu-crd/2.0/)) | Credentialed, same process | Non-invasive BP at irregular times ([vitalAperiodic](https://eicu.mit.edu/eicutables/vitalaperiodic/)) | Yes, 5-minute medians ([vitalPeriodic](https://eicu.mit.edu/eicutables/vitalperiodic/)) | Yes | **Weak.** The [treatment table](https://eicu.mit.edu/eicutables/treatment/) has only an entry offset, no start/stop, and its docs warn that a missing entry does not prove the treatment was not given | No |
| Other open HD session data | — | — | — | — | — | None found. The large IDH ML cohorts (Zhang, Lee, Kim, Wang) are not public |

The honest jury line: *no public dataset links dialysis-session BP, machine settings, heart rate and lab results.* HEMOBP's authors recorded pulse. Asking them to share it is the cheapest route to a real heart-rate test, but it will not happen in eight days.

### Do the ehr.py priors match the evidence?

| Prior in `backend/ehr.py` / `model.py` | What the evidence says | Verdict |
|---|---|---|
| Albumin shifts refill by 10% per g/dL | In 18 patients, the early blood-volume drop tracked **total protein** (r = −0.531). Albumin showed no significant correlation ([Tanaka et al. 2024, *Blood Purif*](https://doi.org/10.1159/000536073)). Refill was not reduced in sessions with events ([Kron et al. 2017](https://doi.org/10.1159/000453441)). Low albumin is *associated* with more IDH in cohorts, e.g. a 94-patient crossover trial's secondary analysis ([Mokkongphai et al. 2026, *Kidney Dis*](https://doi.org/10.1159/000551997)), but the path may not be refill | **Weak.** Keep it small and labelled as an authored assumption. Widen the prior sd for low albumin instead of shifting the mean |
| Beta-blocker → cardiac cause ×1.3; HR gain 0.4 | In a 20-patient crossover, dialysing under beta-blocker effect raised IDH risk (RR 2.40, 95% CI 1.04–5.55) **and lowered the refill fraction** (63% vs 70%). The effect was strongest with carvedilol ([Nadal et al. 2021, *Cardiorenal Med*](https://doi.org/10.1159/000519661)). In 27,064 patients, carvedilol (poorly dialysed) vs metoprolol (well dialysed) went with more IDH (IRR 1.10) ([Assimon et al. 2018, *AJKD*](https://doi.org/10.1053/j.ajkd.2018.02.350)). The demo patients take metoprolol, the drug *more* removed by dialysis | **Partly supported.** Beta-blockers should also lower the refill prior, and the effect should depend on the drug. No source gives the 0.4 HR gain; label it authored |
| Heart failure → cardiac cause ×1.5 | No direct primary source found in this review | **Unsupported number.** Keep it as an authored assumption |
| HR rises steadily as plasma volume falls | True in uneventful sessions (77 → 89 bpm). But sudden symptomatic drops came with **bradycardia** ([Barnas et al. 1999](https://doi.org/10.1681/ASN.V10122577)) and falling sympathetic drive ([Converse et al. 1992](https://doi.org/10.1172/JCI116037)) | **Incomplete.** A sudden HR *fall* should raise risk, not count as evidence against volume loss |

### Fixes, ranked

**3a. Correct the claims and priors to match the evidence.** *Do this.*
- What: in `ehr.py`, (i) shrink or widen the albumin effect and cite it as weak; (ii) add a refill penalty for beta-blockers, larger for poorly dialysed drugs; (iii) flag the heart-failure and HR-gain numbers as authored. In `model.py` / `mechanisms.py`, treat a sudden HR drop as a warning pattern. Update the record text so it no longer reads as if albumin is known to set refill.
- Expected effect: no accuracy claim, since there is no data to test on. The gain is credibility. A jury nephrologist would likely question the albumin→refill link.
- Effort: half a day.
- Files: `backend/ehr.py`, `backend/model.py` (`hr_gain`, `expected_hr`), `backend/mechanisms.py` (family prior), the model card.
- Overfitting risk: none.

**3b. Run a prior sensitivity analysis instead of a validation.**
- What: show how much risk and cause rankings change when each lab/medication prior is switched off or doubled on the four demo patients. This shows the size of an untested assumption, not whether it is right.
- Effort: half a day. Files: a small script in `scripts/`, one table in the model card.
- Overfitting risk: none.

**3c. Longer-term: get real paired data.** Options: (i) apply now for PhysioNet credentialing and build an ICU intermittent-HD cohort in MIMIC-IV (HR, NIBP, albumin, procedure times); (ii) ask the HEMOBP authors for the pulse column; (iii) silent-mode prospective capture using `docs/data-capture-schema.json`, with ethics approval. None of these finishes before 13 Nov.

---

## Problem 4. "Smart next-check selection" does not beat repeating the BP

### What the stress test actually does (from `backend/validation.py`)

- 8 regimes × 24 seeds = 192 cases. All cases share the *same* BP history shape, so history cannot separate causes.
- The "true" relative blood volume and cardiac output values are **fixed per-regime means plus noise**. They are not produced by the planner's sensor equations in `mechanisms.sensor_prediction`. The true BP response depends on a per-regime UF sensitivity `alpha`, not on the planner's four families.
- The real sensor noise is 1.15× what the planner assumes. The `noisy` regime is 2.5× on top.
- Results (`docs/policy-validation-v04.json`): mean regret is 0.222 for repeat cuff, 0.245 for information gain and 0.241 for decision value. Information gain was "confidently wrong" in **49** cases, decision value in **68**, repeat cuff in **0**. Information gain did much worse in the vascular (0.376 vs 0.269) and cardiac (0.412 vs 0.143) regimes. The paired difference against cuff has a 95% interval of [−0.016, 0.070] for information gain, so it is not clearly worse either. "Does not beat" is the correct claim.

### Why information-gain selection loses (literature)

1. **It learns about the wrong thing.** Expected information gain here targets the *cause family* (entropy of four labels). Information about parameters is not information about the outcome you care about. Choosing samples to maximise parameter information can hurt prediction. Targeting information about predictions does better ([Bickford Smith et al. 2023, EPIG, arXiv](https://arxiv.org/abs/2304.08151)).
2. **Misspecification causes "active learning bias".** When the model is wrong, adaptive Bayesian designs can pick unrepresentative data and become confidently wrong. Worse misspecification makes it worse. Models that assume **more** observation noise suffer less ([Sloman et al. 2022, arXiv](https://arxiv.org/abs/2205.13698)). That matches the 49/68 confident-wrong cases.
3. **Standard EIG assumes the model is true.** Recent work adds model-discrepancy terms to the design criterion ([Catanach & Das 2023, arXiv](https://arxiv.org/abs/2304.07949)). It also makes EIG robust to prior error by minimising over nearby priors, which in practice is a log-sum-exp stabilisation ([Go & Isaac 2022, arXiv](https://arxiv.org/abs/2205.09914)). The review by [Rainforth et al. 2024, *Statistical Science*](https://doi.org/10.1214/23-STS915) lists robustness to misspecification as an open problem.
4. **Bayesian updating under a wrong model is overconfident.** Raising the likelihood to a power below 1 ("tempered" or "generalized" Bayes) is a principled fix ([Grünwald & van Ommen 2017, *Bayesian Analysis*](https://doi.org/10.1214/17-BA1085); [Bissiri et al. 2016, *JRSS B*](https://doi.org/10.1111/rssb.12158)).

### Fixes, ranked

**Important process rule:** the October review already said to keep the v0.4 suite frozen and test changes on a new holdout ([research-review-2026-10.md](research-review-2026-10.md)). Any fix below must be reported as **policy-holdout/0.5 on new seeds**, with the protocol written and hashed before the first run. Tuning on the 24 old seeds and calling it a win would be overfitting.

**4a. Temper the non-BP sensor likelihoods.** *Do this first.*
- What: in `mechanisms.assimilate` and `measurement_value`, multiply the assumed noise for relative blood volume and cardiac output by a factor (e.g. 2), or use a power likelihood with η ≈ 0.5. Choose the factor from a **development** suite with its own seeds, not from v0.4. Also reduce the cap on how much one observation can move family support.
- Expected effect: fewer confident-wrong cases, which [Sloman et al. 2022](https://arxiv.org/abs/2205.13698) directly predicts. Average regret should move toward the cuff's. It may not beat it.
- Effort: half a day plus a rerun.
- Files: `backend/mechanisms.py` (`CHANNELS` noise, `assimilate`, `measurement_value`), `backend/validation.py` (new protocol version and seeds), new `docs/policy-validation-v05.json`.
- Overfitting risk: medium unless the factor is fixed on separate development seeds first.

**4b. Default to a repeat cuff. Choose another test only if it wins by a clear margin.**
- What: select a non-BP channel only if its decision value beats repeat cuff's by more than its burden plus a robustness margin. Compute that value as the worst case over a few perturbed sensor models, as a cheap version of robust EIG ([Go & Isaac 2022](https://arxiv.org/abs/2205.09914)).
- Expected effect: the policy should be no worse than cuff in most cases. Gains appear only where the sensor is truly informative. This is the cleanest jury story: "the planner only asks for an extra test when it can prove it helps, and says so when it cannot."
- Effort: half a day.
- Files: `backend/mechanisms.py` (`analyze` selection), `backend/validation.py`.
- Overfitting risk: low–medium. Same new-seed rule.

**4c. Target the decision, not the cause label.** Replace family-entropy gain with information about the 30-minute minimum BP or the rate choice, in the spirit of EPIG ([Bickford Smith et al. 2023](https://arxiv.org/abs/2304.08151)). **Evidence that this alone helps here is weak.** The existing `decision_value` policy already targets the decision and still lost (0.241, 68 confident-wrong). Do 4a first. 4c probably only helps once the sensor models are less overconfident.

**4d. Longer-term: make the test world fair.** In v0.4 the true sensor values are fixed regime means unrelated to the planner's equations. No planner can then use them well except by chance. A v0.5 suite should generate sensor values from an *independent but related* model with a real, partial link to the outcome, plus deliberate misspecification. That tests robustness without making the task impossible. It needs careful pre-registration and is too large to do properly before 13 Nov.

---

## Suggested order for the next eight days

1. Problem 2a (half a day): reframe warnings with lift, per-episode and per-session scoring, burden, and first vs repeat drops. Add the comparison table to the README.
2. Problem 1a (half a day): shrunk-change twin. Report k and b honestly.
3. Problem 3a (half a day): correct the priors and claims in `ehr.py` and the model card.
4. Problem 4a + 4b (1 day): tempered sensors and cuff-by-default, on a new pre-registered seed set.
5. If time remains: 2b (features) and 1b (hybrid). Leave 1c, 1d, 3c and 4d as stated future work.

## Search scope and limits

Searches covered IDH prediction (PPV, AUPRC, Nadir90/Fall20, recurrence), alarm evaluation (event-based, silencing, decision curves), physiological refill and autonomic studies, beta-blockers and albumin in IDH, PhysioNet dataset documentation, particle-filter parameter learning, hybrid physics–ML modelling, and Bayesian experimental design under misspecification. PubMed/PMC pages were partly blocked during this session, so some abstracts were read through Europe PMC or Crossref records of the same papers. Supplementary tables (e.g. Lee 2021 thresholds) were not accessible. Preprints are marked as not peer-reviewed. No claim of completeness is made.
