# Digital Twin Challenge: researched concept and build plan

> Updated direction: the user explicitly rejected builder-count and deadline-based product sizing. The new [ambitious concept plan](ambitious-twin-concepts.md) supersedes the scope and ranking below. This earlier document retains useful data-quality, evaluation and submission details.

Prepared 14 October 2026 (IST). Context: team of 2–3 students; one builder working through Codex. This document plans ideas and a submission; no prediction model has been trained or clinically validated. Any companion interface numbers are illustrative.

## Recommendation

Build **GlucoTwin — a personalized glucose-excursion twin for Type 2 diabetes**. It has the strongest combination of linked historical/sensor data, a precise event, visible personalization, a compelling doctor workflow, and a scope one builder can finish. PressureTwin is the strongest alternative if you prefer hypertension and accept primarily synthetic validation. CardioHarbor has the strongest acute-care story but the largest evidence gap for this deadline.

These designs cover every explicit product requirement in the supplied brief. That is design compliance, not a guarantee of model success, finalist selection, organizer approval, or team eligibility. The brief does not provide weighted judging criteria, a minimum accuracy, or a required simulation technique.

## Timing and brief interpretation

The live [organizer listing on Unstop](https://unstop.com/hackathons/crp-digital-twin-challenge-2026-happiest-health-1757873/amp), checked 14 October, lists registration ending **18 October 2026, 19:00 IST**, code submission ending **20 October 2026, 19:00 IST**, virtual jury on **30 October**, and the summit showcase on **20 November**. Its stage description says ten teams reach the virtual jury and five reach the summit; another paragraph still says five at initial screening. Treat that discrepancy as unresolved. The displayed one-minute jury time window is likely placeholder metadata and should not be used as the presentation duration.

The supplied brief requires full-time students, 1–4 members, verified member details, and no team changes after registration. Those are administrative conditions the team must satisfy. A strong technical idea cannot compensate for ineligibility.

## What makes the prototype a twin

For this challenge, use the following defensible design: a persistent patient model initialized from historical information, updated as new observations arrive, and used to simulate a localized future trajectory. The patient model contains a baseline, individualized response parameters, a current estimated state, and uncertainty. Explain this clearly in the architecture and demonstration.

An EHR card displayed beside an unrelated prediction does not demonstrate fusion. A static diabetes classifier does not demonstrate a changing twin. A three-dimensional body is optional visual decoration. Put the engineering effort into an individualized model whose forecast visibly changes when new sensor data arrives.

Use three provenance categories everywhere: **open observed data**, **synthetic patient data**, and **scenario estimate**. Keep measured replay and hypothetical scenarios separate. A changed input to a predictive model is not proof that an intervention causes a better outcome.

## Idea A: GlucoTwin

**Pitch:** “Before a meal-related glucose excursion appears, the doctor sees the patient's likely next hour—and how that forecast differs from a generic model.”

### Importance and intended users

The Indian Ministry of Health cited **10.1 crore people with diabetes** from the 2023 ICMR-INDIAB study. This is a dated burden estimate, not a new 2026 count. [Government source](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1944600&lang=2&reg=48).

The intended workflow is an outpatient diabetes clinic reviewing CGM users. The practical benefit to investigate is earlier visibility of repeated excursions and a clearer discussion of meal-related patterns. Do not claim the hackathon prototype prevents complications or that CGM is affordable for every Indian patient. The initial target is CGM-equipped users; a population-scale low-cost version is future work.

### Condition, event, and horizon

- Condition: Type 2 diabetes; restrict the initial claim to the population supported by the chosen data.
- Primary adverse outcome: a **new sustained above-range glucose excursion** in the next 60 minutes. Proposed label: glucose above 180 mg/dL for at least 15 minutes, with glucose not already above that threshold at forecast time.
- Secondary task: predict glucose at +30 and +60 minutes and display an estimated future trajectory. A +120-minute horizon is exploratory, not a promised capability.
- Above 180 mg/dL is a useful glucose-management threshold; it does not automatically imply an acute emergency. The persistence rule is a prototype definition, not a universal clinical guideline. Thresholds should eventually be individualized by a clinician. [ADA 2026 glycemic guidance](https://doi.org/10.2337/dc26-s006).

### Data that can actually be fused

Use [CGMacros on PhysioNet](https://physionet.org/content/cgmacros/1.0.0/), an open-access dataset with 45 participants, including 14 with Type 2 diabetes, monitored for approximately ten days. It contains linked demographic/lab information, CGM, activity, and meal information. Its license is CC BY-NC-SA 4.0. Keep dataset terms distinct from the code license.

Historical stream: participant age, BMI, HbA1c, fasting glucose and selected lipid labs, joined by participant ID and mapped into a compact EHR-shaped JSON record. Enrich the demonstration with explicitly synthetic historical diagnosis entries if needed. Do not randomly attach a Synthea patient to an unrelated real wearable participant and claim real patient fusion. [Historical data dictionary](https://physionet.org/files/cgmacros/1.0.0/DataDictionary_Bio.csv).

Dynamic stream: one CGM device, Fitbit heart rate and activity/METs, and logged meal timing/macronutrients. Meals are contextual inputs in addition to the required sensor stream. Use only documented columns; do not claim the dataset contains sleep stages, steps, or HRV without verifying them. [Sensor and meal data dictionary](https://physionet.org/files/cgmacros/1.0.0/DataDictionary_CGMacros-00X.csv).

The [published CGMacros paper](https://www.nature.com/articles/s41597-025-05851-7) describes US recruitment and a small, restricted cohort. Its T2D eligibility excluded insulin and most non-metformin glucose therapies. It also describes interpolation to one-minute CGM rows. Therefore, the first model cannot support insulin-dose decisions, demonstrate generalization to India, or treat every minute as an independent sensor observation.

Data dictionary inspection also found a possible HbA1c unit inconsistency: values around 4.6–8.5 are described as mmol/mol. Check against the paper and raw files before ingestion; do not silently relabel or trust that field description. Fitbit METs are reported multiplied by ten. Record every unit conversion in a data-quality report.

### Twin and prediction design

1. Initialize each patient with a historical baseline and population-informed response parameters.
2. Estimate current glucose level, recent slope, volatility, time since meal, meal load, and activity state from past observations only.
3. Maintain a patient-specific offset and response scale, updating them from prediction residuals after outcomes become observable.
4. Use a compact autoregressive/state-space glucose model to produce a trajectory. Add a small gradient-boosted model to predict residuals or future exceedance risk from both static and dynamic inputs.
5. Update on each replay tick; store prediction time, input cutoff, model version, horizon, and eventual outcome.
6. Produce an uncertainty estimate from held-out residuals or quantile models. Evaluate coverage before calling it a calibrated interval.

Start with persistence and trend extrapolation baselines. Use scikit-learn HistGradientBoosting or XGBoost only after the baseline pipeline works. Skip transformers, microbiome features, insulin pharmacology, and food-image recognition in the six-day version.

### Visual concept and signature demonstration

Use a clean clinician workspace with restrained teal, a warm amber warning, and a large glucose trajectory. The chart is the main visual: observed history, a vertical “now” marker, dashed forecast, uncertainty band, and a threshold line with units. Beneath it, place aligned meal and activity markers; beside it, a compact historical record and model-state summary.

The memorable interaction is **one patient, two meal scenarios**. A clinician adjusts a proposed meal's macronutrients and sees a second estimated curve. Use Indian meal names only as clearly authored scenario examples with editable quantities. Western meals in the training data do not establish validated prediction for a specific Indian dish. Do not hard-code a walk as reducing glucose by a fixed amount.

The scientifically stronger live demonstration is: replay a held-out patient, issue an alert before a real recorded excursion, reveal the later observation, and compare the personalized twin with a sensor-only baseline. If the personalized model does not improve, show that honestly and explain the limitation.

### Evaluation and acceptance gates

- First inspect usable T2D participants, missingness, meal coverage, positive-event count and clock alignment. Dataset availability alone does not prove the target has enough examples.
- Split by patient for the main generalization experiment; do not randomly divide neighboring time windows. With only 14 T2D participants, use grouped cross-validation and report counts and variability, rather than a single flattering accuracy.
- Run a separate within-patient adaptation experiment: calibrate only on early days and test on later days. Label that setting separately from new-patient generalization.
- Fit scaling, imputation, feature selection, and probability calibration inside training folds. Use chronological validation and purge overlapping windows at temporal boundaries.
- Prevent interpolation leakage. Prefer original native samples with known timestamp alignment; otherwise assign conservative availability delays of at least 5 minutes for the processed Dexcom values and 15 minutes for Libre. Do not feed a minute value into the model before the later endpoint used in its interpolation could have arrived.
- Report glucose MAE in mg/dL at each horizon, event sensitivity, positive predictive value, PR-AUC, false alerts per patient-day, and advance warning time for truly new events. Cluster uncertainty estimates by patient. Do not convert a 60-minute horizon into a claim of 60 minutes of realized warning.
- Compare persistence, trend, static-only, dynamic-only, fused, and personalized fused models. Historical fields must enter the actual algorithm. Fusion improvement is a hypothesis to test.
- Count one excursion as one event and consolidate repeated alerts with a documented refractory rule. Freeze the alert threshold on validation data.
- Stress-test sensor dropout, late packets, missing meals, unit errors and out-of-distribution profiles. Show “insufficient data” instead of a confident forecast where appropriate.

**Go/no-go:** by the end of the first build day, require a linked-data loader, a defensible availability cutoff, sufficient usable events for a small evaluation, and a baseline result. If those fail, switch to a fully disclosed synthetic version of the same concept; do not hide the switch or present simulator metrics as clinical evidence.

### Minimum product and expansion

Minimum: one patient screen, replay controls, EHR initialization, an updating patient state, future trajectory, event alert, evidence drawer, and held-out outcome reveal. Demonstrate three states: upcoming excursion, stable patient, and missing-data abstention. Expansion after submission: uncertainty calibration, a carefully bounded scenario comparison, and better patient-level validation.

## Idea B: PressureTwin

**Pitch:** “A hypertension patient's next morning is forecast from their history and the preceding day's physiological pattern.”

### Importance and narrow scope

Hypertension is a recognized Indian chronic-disease priority; the [WHO India country profile](https://www.who.int/publications/m/item/hypertension-ind-2023-country-profile) provides the population context. Focus on already-diagnosed patients and a concrete uncontrolled-BP episode, rather than announcing a heart attack or stroke from smartwatch data.

Primary output at 22:00: probability that two valid next-morning cuff readings, taken one minute apart during a predefined 06:00–09:00 session, both exceed a configurable systolic threshold. Use 160 mmHg as an explicitly selected sandbox threshold, not a diagnostic or emergency definition. Also forecast the morning systolic level and its uncertainty.

### Data and patient twin

Historical EHR: age, established hypertension, baseline BP distribution, BMI, renal-function category, documented antihypertensive treatment, and previous morning readings. Dynamic data: simulated wearable resting heart rate, HRV when available, activity and sleep summaries, plus a connected upper-arm cuff stream. Medication adherence is an explicitly logged contextual input, not inferred from a wearable.

Use synthetic EHRs and a coherent longitudinal simulator sharing the same patient ID and physiological parameters. [Synthea](https://github.com/synthetichealth/synthea) can supply historical records, but its default population is not automatically India-representative. A smaller custom synthetic record generator is acceptable under the brief and easier for one builder.

Build a circadian BP state with a patient-specific baseline, amplitude, noise, and response parameters. Update the estimated state when cuff observations arrive. Fuse static vulnerability and the past day's sensor summaries using a small regression/classification model. Wearable-only BP inference is an optional future experiment; it is not the core measurement source. [ESC measurement guidance](https://esc365.escardio.org/journal/92043) supports validated upper-arm cuff devices.

### Synthetic-data design that remains credible

Generate varied patient parameters and noisy observed channels, with medication logs and sleep/activity patterns affecting the sandbox's latent dynamics. Derive labels from future cuff values, not from an event flag supplied to the predictor. Include stable hypertensive patients, nonadherence without an excursion, sensor noise, and sleep disruption without an excursion. Use independently sampled held-out patients and an alternative generator with changed coupling strengths to test brittleness.

This validates model and pipeline behavior within a sandbox. It cannot establish real hypertension forecast accuracy, prove sleep causes tomorrow's BP, or substantiate claims of stroke prevention. Do not call a repeated reading a clinically verified crisis.

### Visual concept and demonstration

Create a 24-hour clock-style circadian ribbon paired with a readable Cartesian BP forecast, a compact sleep timeline, and directly labeled cuff readings. A small clinic queue ranks patients by estimated next-morning excursion risk and data completeness. The selected patient's history should visibly set the baseline; the last cuff observation changes the forecast.

Signature demo: replay two synthetic patients with similar wearable patterns but different historical baselines. The fused twin forecasts different morning BP trajectories. Reveal the next-morning cuff measurements and a missing-cuff case that forces uncertainty or abstention. Any medication-timing scenario is descriptive simulation, not a medication recommendation.

### Evaluation, build scope, and value

Compare last-reading and same-time-yesterday baselines with static-only, dynamic-only and fused models. Report next-morning systolic MAE, sensitivity/PPV for repeated excursions, false alerts per patient-week, probability calibration and missing-cuff behavior. Publish synthetic-only metrics separately and test changed simulator parameters.

Minimum build: coherent patient generator, cuff/wearable replay, personalized circadian state, tomorrow's event prediction, and one doctor screen. Skip cuffless BP estimation, stroke prediction, autonomous prescription changes, and continuous photorealistic vascular animation.

The intended clinic value is prioritizing follow-up and obtaining timely confirmed readings. It has strong India relevance and a clean visual story; its central weakness is lack of verified matched longitudinal training/outcome data in the researched shortlist. Feasibility is good for a sandbox prototype, but scientific strength is lower than GlucoTwin.

## Idea C: CardioHarbor

**Pitch:** “After heart-failure discharge, the twin spots a patient's worsening trajectory before the next routine follow-up.”

### Why the problem matters

India's National Heart Failure Registry followed 10,851 admitted patients and reported 14.2% mortality and 8.4% readmission at 90 days. These are observational registry findings, not outcomes this product has improved. [Primary registry study](https://pubmed.ncbi.nlm.nih.gov/36214477/).

The [LINK-HF study](https://pubmed.ncbi.nlm.nih.gov/32093506/) supports investigating personalized wearable deviations before worsening-HF admissions. Its small, predominantly male cohort and observational design limit generalization. An alert is not by itself evidence that care improves.

### Exact event and streams

Condition: chronic heart failure following discharge. Sandbox target: a simulated congestion-related deterioration event within the next 48 hours, defined by the simulator's latent progression and recorded as a synthetic clinical event. The model sees observations only up to the prediction time. Distinguish this label from confirmed hospitalization or a measured biomarker endpoint.

Historical EHR: ejection-fraction category, discharge date, kidney function, prior admissions, baseline weight and heart rate, and documented medication classes. Dynamic stream: wearable resting HR, respiratory-rate estimates if actually supported by the chosen sensor, activity, sleep summaries, and connected-scale weight. Structured symptom reports are an additional context stream. Do not imply every consumer watch produces clinical-quality respiratory rate or directly measures congestion.

### Patient model and data plan

Create synthetic patients with a latent fluid-balance/congestion state and a separate activity/autonomic state. Observed weight, HR, respiratory summaries and activity are noisy, partially missing consequences. EHR parameters set baseline vulnerability; incoming observations update estimates through a simple Bayesian filter or state-space estimator. Predict whether the deterioration threshold will be reached within 48 hours.

Use Synthea or a custom EHR generator for history. Generate 30-day aligned sensor trajectories with varied disease severity, recovery, deterioration and confounders. Hospital EHR tables alone do not provide the matched home-wearable outcomes needed for this forecast. Short physiological recordings from people with HF do not validate 48-hour deterioration predictions either. I have not verified an openly downloadable dataset with the full required paired discharge EHR, home wearable series and deterioration labels for the deadline.

The latent generator state can define synthetic ground truth but must never be a predictor input. Include illness-like HR changes without congestion, stable weight with sensor artifacts, and incomplete scale adherence. Test a second generator with different observation relationships. Publish the generative assumptions and keep all results labeled synthetic.

### Visual concept and doctor workflow

Use a seven-day timeline of deviation from the patient's own baseline. Present weight in kg, resting HR in bpm and activity in its own units on aligned small plots. The main panel shows estimated trajectory and the next 48-hour forecast. If an anatomical motif is used, keep it subordinate and mark estimated fluid state as model output, not imaging.

The important visual moment is a pattern emerging across several individually modest changes. A doctor opens the supporting measurements, checks missing data, and marks the case for review. The UI records an audit note; it does not change a diuretic dose or send an external clinical message.

Signature demo: a synthetic postdischarge patient appears stable in one measurement but deteriorates across several channels; the personalized twin raises an advance alert. Then show a sensor-artifact case where corroboration and data-quality logic prevent a confident alert. Reveal the later synthetic event with clear provenance.

### Evaluation and feasibility

Compare personal-baseline thresholding, weight-only monitoring and fused state estimation. Report sensitivity at a fixed false-alert budget, lead-time distribution, PPV, calibration, and alerts per patient-week. Evaluate subgroup behavior by simulated renal function/severity and performance under dropout. None of these constitute clinical validation.

Minimum: synthetic paired records, longitudinal simulator, updating state estimator, forecast, aligned evidence plots and review workflow. Skip hospital-readmission claims, imaging interpretation, automatic dosing and hardware integration. This is achievable as a focused sandbox demonstration but carries the highest risk of spending the deadline tuning a believable simulator instead of validating a model.

## Requirement coverage

| Requirement in supplied brief | GlucoTwin | PressureTwin | CardioHarbor |
|---|---|---|---|
| One India-relevant chronic/lifestyle condition | Type 2 diabetes | Hypertension | Chronic heart failure |
| Historical/EHR input consumed by model | Linked labs/demographics + EHR representation | Synthetic diagnosis, labs, BP history | Synthetic discharge and cardiac history |
| Dynamic wearable/IoT input consumed by model | CGM + Fitbit replay | Wearable + connected cuff simulation | Wearable + scale simulation |
| One localized future adverse outcome | New sustained glucose excursion | Repeated next-morning BP excursion | Synthetic congestion deterioration |
| Working model with prospective replay | Mandatory build deliverable | Mandatory build deliverable | Mandatory build deliverable |
| Updating individualized patient model | Glucose-response state | Circadian BP state | Congestion/activity state |
| Conceptual doctor dashboard | Trajectory + meal context | Morning forecast + cuff evidence | Baseline-deviation timeline |
| Allowed data provenance | Open anonymized + clearly synthetic history | Synthetic | Synthetic |
| Public code, documentation, license, architecture, slides, video | Required packaging | Required packaging | Required packaging |

All three meet these requirements only when implemented and packaged as specified. Eligibility, timely registration, verified details, and accessible submission links remain separate team obligations. No published weighted scoring rubric was found; the ranking below is my assessment, not jury scoring.

| Decision factor | GlucoTwin | PressureTwin | CardioHarbor |
|---|---|---|---|
| Evidence availability | Best: verified matched open cohort; small | Synthetic evaluation | Synthetic evaluation; outcome-data gap |
| Visual demonstration | Forecast + meal-scenario fork | Circadian forecast + morning reveal | Multi-signal deterioration timeline |
| Practical value to investigate | Personalized diabetes review | Timely hypertension follow-up | Postdischarge triage |
| One-builder deadline risk | Lowest if data passes day-one audit | Moderate | Highest |
| Recommendation | Build first | Best alternative | Choose only with clinical/simulation expertise |

## Common architecture and stack

Historical record loader + timestamped sensor replay → ID/unit/data-quality checks → past-only feature buffer → persistent individualized twin state → forecast/event model → uncertainty and alert policy → doctor UI + audit log.

Suggested stack: Python, pandas, NumPy and scikit-learn; FastAPI; SQLite for patient state/prediction logs; React + TypeScript and a chart library for the clinician interface. Choose versions and package manager at build time. Streamlit is a viable fallback if frontend development starts threatening submission completion. No LLM is needed in the prediction loop. An optional generated explanation must refer only to structured model facts and cannot invent clinical reasoning.

A patient record needs patient_id, condition, history_timestamp, demographics, labs with units, documented diagnoses, and provenance. A sensor observation needs patient_id, event_time, available_time, channel, value, unit, and quality flag. A prediction needs generated_at, input_cutoff, horizon, event_definition, estimated probability, trajectory, uncertainty method, model_version, and provenance. Do not encode diagnosis/outcome labels in patient IDs or demo filenames fed into the model.

The replay clock advances through saved data without exposing later readings. Future values are revealed only after the matching time arrives. Offer stable and failure cases alongside the attractive event case. Require predictions to reproduce under a fixed seed and clean installation. Real streaming hardware and external cloud services are unnecessary for the brief.

## One-builder schedule: 14–20 October

| Date, IST | Builder work | Reviewable output |
|---|---|---|
| 14 Oct | Select concept; inspect data; lock event and provenance; check team registration requirements | Data audit and one-page scope |
| 15 Oct | Build loader, strict clock, baselines and first evaluation | Working forecast on held-out data |
| 16 Oct | Add historical fusion, persistent personalized state and alert policy | Reproducible twin + ablation results |
| 17 Oct | Build polished doctor screen, provenance and uncertainty display | End-to-end replay; stable/event/dropout cases |
| 18 Oct | Finish evaluation, prevent leakage, freeze essential features; ensure registration before 19:00 | Model card and registered, verified team |
| 19 Oct | Record ≥20-minute explanation/demo; prepare actual PDF/PPT architecture and slides; clean repo | Complete accessible submission package |
| 20 Oct | Fresh-install verification; check public links; submit before 19:00, ideally by 15:00 | Submitted repository and all deliverables |

If the data audit consumes more than a day, cut optional meal scenarios, comparison screens, animations, authentication, deployment, FHIR server integration and auxiliary models. Preserve the actual fused algorithm, individualized state, evaluation and submission materials. A two-hour forecast and an elaborate avatar are not required.

Team contribution: the builder owns implementation and reproducibility. A second member owns literature, exact medical wording, model-card review and slide content. A third member, if available, owns the demo narrative, recording, link checks and team details. The builder does not have to do every non-code task alone.

## Submission packaging checklist

Use the required **Team Name_College Name** folder naming convention. Public GitHub repository with a README containing team/college/incubator details, project title, problem/use case, technical stack and model details, open-source license details and every accessible deliverable link.

Include source, exact environment/dependency specification, data download/generation instructions, preprocessing, train/evaluate commands, saved evaluation outputs, a short model card, synthetic demo data, and instructions for launching the replay. Keep third-party dataset terms and attribution in a separate notice; do not relicense data under the code license or upload restricted data. MIT or Apache-2.0 can be considered for independently authored code.

Provide the **minimum 20-minute video**, architecture in **PDF/PPT**, and project presentation in **PDF/PPT**. An image or Mermaid source can help author the architecture, but does not replace the specified format. These artifacts are planned here and still must be created for submission.

Suggested 22-minute recording: 0–2 problem and patient story; 2–4 requirement fit and data provenance; 4–7 architecture and individualization; 7–13 live replay including stable and failure cases; 13–17 evaluation and baselines; 17–20 limitations and intended clinic workflow; 20–22 reproducibility and next validation step. State the actual measured results, including failures, rather than target accuracy.

Submit only the team leader's name, phone, email, and public repository link through the specified platform. Verify the repository, video and document links from a signed-out browser. Finish registration and member verification before the earlier deadline; do not wait for code completion.

## Visual direction that strengthens the science

Every visual must answer a clinical question: what is happening, what might happen next, what evidence supports it, and how reliable is the data? Use typography, spacing, aligned timelines and clear units to create appeal. Reserve warning colors for actual alert states. Show history/forecast with line style and labels, not color alone. Place uncertainty and provenance near the estimate. Use small anatomical artwork only where it adds understandable meaning.

The best final pitch for GlucoTwin is: **“A narrow patient twin that joins past labs with incoming glucose and activity, updates its own baseline, and forecasts a defined excursion before it occurs.”** Its distinction is the end-to-end individualized replay and honest evaluation. A generic chatbot, static risk score, unsupported watch-based diagnosis, or decorative body model would weaken the fit.
