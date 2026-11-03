# Ambitious digital twin concepts and build blueprints

14 October 2026. This supersedes the builder-count and deadline-based product sizing in the earlier plan. The user's priorities are ambitious ideas, visually compelling experiences, real healthcare importance, and complete fit to the hackathon brief. Team size and build speed are not used to rank or trim the concepts.

The breadth constraint comes from the challenge itself: choose one chronic/lifestyle condition and predict one localized adverse outcome. Make the model, simulation, evidence and experience deep; do not combine unrelated diseases to make the app appear bigger. These are proposed products, not validated clinical systems. Brand names are working titles, not checked trademarks.

## My revised recommendation

**RENALIS** is my strongest candidate for a distinctive, technically substantive clinical showcase. A patient-and-dialysis twin predicts hypotension and lets a clinician explore fluid-removal scenarios while seeing the tradeoff between circulatory stability and treatment completion. New research found a published, accessible matched dataset, so this is more than an attractive synthetic-data idea.

**PRANA** is the strongest candidate for a broadly understandable, emotionally engaging product: a metabolic future studio for Type 2 diabetes. **AERIS** is the strongest environment-and-India narrative: a personalized asthma twin that joins physiology and exposure. **CardioHarbor** has the most powerful continuity-of-care story but a larger longitudinal outcome-data gap.

This is my product judgment, not an official scoring rubric. No first-of-its-kind claim is made: related metabolic, dialysis and cardiac digital-twin research already exists. The distinction should be demonstrated through the actual individualized model, transparent scenario assumptions, excellent interface, and honest observed-outcome evaluation.

## RENALIS originality: the twin that knows when more evidence is needed

Added 14 October 2026 after an explicit originality review. The detailed related-work comparison, proposed algorithms, visual moments, acceptance criteria and current-versus-planned status are in [the originality plan](docs/originality.md).

The flagship contribution to investigate is **recognizing when different physiological explanations fit the same patient observations but disagree about scenario responses, then estimating which additional measurement could resolve that disagreement**.

The clinician's question becomes: “Do we have enough evidence to compare these futures—and what observation would help?” This gives the visuals an important purpose beyond displaying another risk score.

1. **Competing physiological explanations.** Retain plausible volume/refill, vascular-compensation and cardiac-response models. Show where they agree about a BP forecast but disagree about the effect of a proposed removal profile. Known mechanisms are hypotheses to distinguish, not newly discovered biology or diagnosed causes.
2. **Decision-relevant measurement selection.** Evaluate available channels and permissible times by how their possible observations could change a scenario comparison. Another BP reading may add little value when rival mechanisms predict the same BP. If a useful channel is absent, retain an unresolved comparison. Measurement selection and optimal experimental design already exist; their application to this specific imminent-hypotension workflow is the research direction.
3. **A scenario support landscape.** Plot fluid removed against projected minimum BP and identify comparisons that change across mechanisms, extrapolate beyond observed support, or lack adequate intervention evidence. Keep factual prediction support separate from causal credibility. Display reasons rather than an invented universal trust score.
4. **A model that can downgrade itself.** Incoming observations can contradict previous forecasts and reduce scenario authority. Preserve the contradiction and lineage. This supports the originality story but drift detection itself is established.
5. **Session-to-session consequences.** As a stretch feature, carry residual fluid and uncertain state into a later synthetic session so an apparently attractive current profile exposes its longer-term cost. This remains the same CKD/hypotension use case, with explicit additional assumptions.

**Signature demo:** rival mechanisms fit the same history; a scenario comparison remains unresolved; the twin identifies an informative available synthetic measurement; that observation updates the models and changes the comparison. Repeat with an uninformative or unavailable channel, where the correct result stays unresolved. Unchosen treatment outcomes remain simulated.

**Originality status:** related work already covers IDH forecasting, personalized control, digital twins, counterfactual prediction and optimal sampling in adjacent dialysis models. The focused review did not identify the exact proposed end-to-end combination. This is an underexplored integration hypothesis, not a verified “never done anywhere” claim. As of 16 October 2026, the Mechanism lab implements the flagship three-family comparison, decision-value observation engine, support landscape, contradiction downgrade, audit, and 108-case independent synthetic challenge suite. The original Patient twin remains a separate single-family view. Decision-value selection has not shown superiority on mean regret in the current challenge suite; clinical and longitudinal validation remain outstanding.

**Build priority:** competing mechanism families → scenario disagreement → measurement-value engine → support landscape → independent simulator challenge suite. Compare against the current single-family twin and fixed measurement schedules under the same observation budgets. Evaluate incorrect scenario comparisons, unresolved cases, measurement burden, missed events and false certainty.

## 1. RENALIS — The patient and machine, modeled together

**Pitch:** “See a dialysis patient's next blood-pressure drop before it happens—and compare the consequences of a different treatment profile inside their twin.”

### The important problem

The project targets end-stage chronic kidney disease treated with maintenance hemodialysis. The adverse event is intradialytic hypotension, not CKD diagnosis and not a generic risk of death. In a primary study involving patients from the US and India, BP drops during dialysis were associated with a greater rate of clinically significant arrhythmia. This supports the importance of investigating earlier warning; it does not prove a twin would prevent those outcomes. [Monitoring in Dialysis study](https://pubmed.ncbi.nlm.nih.gov/32381584/).

The real clinical tension makes the idea unusually strong: fluid must be removed, but removal can exceed the patient's ability to maintain circulating volume and blood pressure. A simulation should show both sides of that tension instead of always declaring less removal “better.”

### Exact core outcome

Forecast a new systolic BP nadir at or below 90 mmHg at the next eligible measurement within a 30-minute horizon. Report predictions only for currently non-hypotensive patients. The label is a BP-based research endpoint; symptomatic hypotension requires symptoms/intervention information. Record horizon, interval censoring and event onset uncertainty. If actual measurement spacing does not support a reliable 30-minute endpoint, use the next-measurement task and show its elapsed time explicitly.

### Data and twin

The [HEMOBP data publication](https://www.nature.com/articles/s41597-019-0319-8) describes linked demographics, session information and machine records. BP was normally measured at 30-minute intervals, with additional clinically prompted observations. Do not market these sparse readings as beat-to-beat blood pressure or a validated ten-minute warning system.

The [versioned data deposit](https://figshare.com/articles/dataset/Hemrec_VIP_csv/6260654/3) lists d1.csv, idp.csv and vip.csv under CC BY 4.0. The files have now been downloaded, checksum-verified and used in a separate retrospective baseline pipeline. Preliminary held-out results are in [the observed baseline report](docs/observed-baseline.json); inferred session boundaries and physiological units still need independent reconciliation. Published study totals should not be assumed to equal the cleaned training cohort. The observed baseline does not yet replace the synthetic physiological twin.

Static/historical stream: demographics, diabetes status, dialysis history, past-session BP response, and pre-session weight/dry-weight information available before the prediction. Do not use post-session weight or session-end information at an earlier forecast cutoff. These records can be mapped into EHR resources. Additional labs and cardiac diagnoses belong only to separately labeled synthetic scenarios unless actually available for the same patient.

Dynamic stream: connected BP readings, elapsed session time and machine settings such as ultrafiltration rate, blood flow and dialysate settings. The medical-device IoT route is explicitly compatible with the brief; a consumer watch is not necessary.

The proposed twin has circulating-volume and interstitial-fluid compartments, vascular compensation and a BP observation model. Initialize it from historical responses and session history; estimate current state from new BP and machine observations. Use a Bayesian filter to maintain multiple plausible parameter/state configurations rather than one falsely precise reconstruction. Fit a data-driven residual/event model alongside the mechanistic simulator.

### Ambitious experience

**The dialysis cockpit:** a selected patient's twin at center, connected-machine observations on one side, upcoming BP trajectory on the other. The centerpiece is a physically interpretable fluid-flow diagram, optionally rendered in 3D. It shows estimated tissue refill into circulation and removal out of the system. Every latent quantity is labeled estimated.

**Session memory:** earlier sessions appear as traceable overlays. The doctor can inspect whether the current trajectory differs from this patient's ordinary tolerance.

**Parallel treatment futures:** compare clinician-authored ultrafiltration profiles while keeping identical patient state and observation cutoff. Plot predicted BP alongside cumulative fluid removal and remaining treatment target. A profile that reduces BP risk but leaves more fluid to remove must visibly show that cost. Profile constraints come from a documented sandbox, not an autonomous prescription engine.

**Evidence on demand:** selecting a forecast point reveals the last BP, machine settings, data age, history used and uncertainty. Model explanations distinguish observed contributors from inferred mechanisms. SHAP values describe model attribution, not causal physiology.

**Uncertainty stress test:** remove a BP reading, widen uncertainty, and show when the twin declines to rank treatment scenarios. This can be a striking, honest demo moment.

**Unit overview:** several synthetic or anonymized replay patients appear in a clinic queue with synchronized session progress. It supports the same single hypotension task; it does not introduce a second clinical objective.

### Signature jury sequence

Replay a held-out session. Show that BP is not yet hypotensive. The twin forecasts a low upcoming measurement. Open the fluid-flow state and previous-session evidence. Fork two removal profiles; one delays instability but leaves more fluid. Reveal the actual recorded BP for the factual path. Keep alternative outcomes labeled simulated because only the recorded treatment path has an observed outcome. Finish with a stable session and an artifact/missing-data session.

### Build and validation

Build ingestion and joins by patient/session/time; an availability-aware event buffer; historical-session features; mechanistic parameter fitting; sequential filtering; a prospective event model; ensemble uncertainty; scenario branching; and a cockpit with a reproducible session recorder. Train/evaluate static-only, machine/vitals-only, fused and personalized models. Measure sensitivity at fixed alert burden, PPV, calibration, next-reading BP MAE and realized lead time.

Split patients and also run a distinct later-session adaptation study. Do not use future prescription changes as features, confuse machine-record frequency with BP-observation frequency, or impute across outcome boundaries. More frequent measurements during symptomatic events introduce observation bias; report scheduled-reading and all-reading evaluations separately where feasible.

The counterfactual simulation needs physiological sensitivity analysis and explicit identification limits. Prediction quality on a recorded treatment path does not validate alternative prescriptions. A reduced-order mechanistic twin is scientifically more useful here than an elaborate uncalibrated full-body mesh.

## 2. PRANA — The metabolic future studio

**Pitch:** “Explore possible glucose futures in a model that learns this patient's response, remembers yesterday, and updates when new readings arrive.”

### Problem and outcome

Focus on Type 2 diabetes and one core adverse event: a new sustained above-range glucose excursion during the next 60 minutes. Forecast the trajectory and event together. Longer horizons may be evaluated separately, but do not assume extra time guarantees useful accuracy. This extends the earlier GlucoTwin concept into a richer physiological and clinical experience.

The intended value is individualized pattern review and informed clinician-patient discussion, rather than generic diet scoring. A compelling Indian patient story can involve meals, work routines and repeated excursions. It must be separated from claims of Indian population validation.

### Physiological model and data

Use [CGMacros](https://physionet.org/content/cgmacros/1.0.0/) for linked observed patient health data, CGM, activity and meals. Preserve its small-cohort limitations and dataset license. The [published paper](https://www.nature.com/articles/s41597-025-05851-7) provides context about the cohort and processing. The earlier plan documents important unit and interpolation-availability checks.

Model the localized metabolic system with meal absorption, circulating glucose, glucose clearance and a parsimonious delayed response. Historical labs initialize priors; each new glucose observation updates state estimates and identifiable patient parameters. A residual ML model corrects systematic forecast error. Do not claim CGM alone identifies pancreatic function, hepatic production or insulin sensitivity uniquely; those may remain uncertain model parameters.

Maintain a separation between observed-data fitting and synthetic meal/activity/sleep experiments. Sleep and hormonal effects need supporting paired data; they cannot be inferred from absent CGMacros channels just because sliders look attractive.

### Ambitious experience

**Future studio:** a patient's actual trajectory flows into a branching set of clinician-selected scenarios. The doctor can compare meal amounts and timing with shared starting state. Show uncertainty and sensitivity, and refuse scenarios outside supported input ranges.

**Physiology view:** a schematic or 3D model visualizes modeled absorption and clearance flows. It acts as a readable representation of the state equations, not fake imaging of the patient's organs.

**Patient memory:** a searchable history of measured meal responses helps explain what the twin has learned. Similar meals need similar quantities/context; arbitrary same-name matches are insufficient.

**Meal workbench:** build Indian meal examples from editable quantities and documented nutritional inputs. Food-photo recognition can assist entry, but portion estimates require confirmation. Do not let an image model silently invent carbohydrate grams and feed them into a precise medical forecast.

**Scenario search:** under clinician-set constraints, explore a bounded set of meal compositions and identify the tradeoff between modeled excursion risk, calories, satiety proxies if supported, and patient preferences. Describe this as scenario exploration until prospective intervention benefit is demonstrated.

**Twin comparison:** show a population model and the personalized model forecasting the same held-out patient. This makes personalization visible and testable instead of a marketing adjective.

**Patient explanation:** a companion view translates the forecast into plain language, local-language text and accessible audio, grounded in structured outputs. It does not infer new diagnoses or change medication.

### Signature jury sequence

Two patients encounter the same authored meal. Their historical data and learned response states produce different predicted trajectories. For one held-out patient, replay the factual path and reveal the observed excursion. Open similar previous measured responses. Fork alternative meal scenarios with uncertain simulated outcomes. Switch to missing-meal context and show the model's confidence degrade.

### Build and evaluation

Implement a versioned metabolic state model, online assimilation, historical response memory, factual replay, bounded branch simulations, uncertainty calibration, and multilingual explanation templates. Build dietary input provenance and a clinician scenario editor. Optional scientific extensions include parameter-identifiability analysis and active measurement suggestions, such as whether an additional reading would materially reduce uncertainty.

Evaluate glucose error, event sensitivity/PPV, calibration, false-alert burden and patient-specific adaptation. Compare mechanistic-only, ML-only and hybrid models. Compare factual forecasts on observed data; evaluate counterfactual simulations separately with published physiological plausibility checks and synthetic stress tests. Do not present a lower simulated curve as a proven health improvement.

## 3. AERIS — The patient's lungs in their daily environment

**Pitch:** “The same environment affects different asthma patients differently. AERIS estimates this person's changing vulnerability and next-day airflow deterioration.”

### Problem and event

Condition: chronic asthma. Core endpoint: a next-day sustained reduction in measured peak expiratory flow relative to an established personal baseline, with an explicitly defined threshold and quality rule. This is an airflow-deterioration endpoint, not automatically a medically adjudicated severe asthma attack. If the data includes sufficient well-defined exacerbations, evaluate that endpoint separately rather than relabeling peak-flow decline as hospitalization.

India has a substantial asthma burden, documented in the [primary Indian respiratory-burden study](https://pubmed.ncbi.nlm.nih.gov/30219316/). The concept is compelling because environment and chronic disease meet in a patient-specific model. Pollution is an additional context stream; it must not replace the required wearable/IoT stream.

### Verified data lead

[AAMOS-00 at Edinburgh DataShare](https://datashare.ed.ac.uk/handle/10283/4761) lists linked patient information, smart peak-flow, smart inhaler, smartwatch, environmental and questionnaire files. It covers 22 UK participants and 2,054 participant-days. The [dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10248342/) describes anonymization and CC BY 4.0 use. Its date fields use relative study days and its patient information is restricted; the exact retained historical fields need a file audit.

The granularity supports a next-day task more defensibly than a speculative minute-by-minute attack countdown. India-specific location, exposure and patient scenarios should be synthetic or based on separately sourced context. Do not relocate actual UK patients to Delhi and treat the resulting data as observed Indian cases.

### Twin model

Historical asthma records and prior peak-flow observations initialize a personal baseline and response priors. Dynamic smart-device observations and exposure summaries update a low-order airway-resistance/inflammation state. A temporal model forecasts the next-day PEF decline. Treat inflammation and regional airway constriction as latent estimates; smartwatch data does not measure them directly. Inputs such as medication class or allergy history must be documented or clearly synthetic.

### Ambitious experience

**Breathing workspace:** a schematic or generalized 3D airway model becomes the spatial view of modeled resistance. Pair it with an actual PEF forecast and an uncertainty band. It is not a patient-specific CT reconstruction unless imaging and its reconstruction are actually present.

**Personal exposure timeline:** activity, measured or authored environmental exposure, inhaler logs, sleep and PEF appear on aligned timescales. The doctor sees the patient's state change as observations arrive.

**Day-plan comparison:** compare two explicitly authored exposure schedules—such as indoor/outdoor timing—with the same physiological starting state. Use a real map only with verified geographic geometry and sourced exposure data; a fictional glowing city would weaken the evidence.

**Personal trigger memory:** inspect earlier temporal associations and their uncertainty. The UI says “associated in recorded data,” not “proven cause of the attack.”

**Missing-device reasoning:** missing inhaler data is distinguished from confirmed nonuse. An absent peak-flow reading is not automatically a normal reading.

### Signature jury sequence

The same hypothetical outdoor exposure schedule is applied to two synthetic patient models with different baselines and response priors. Compare modeled next-day PEF. Then replay an actual held-out AAMOS-00 sequence, show a forecast before the next-day measured decline, and reveal it. Clearly distinguish recorded exposure from a proposed schedule.

### Build and validation

Build multi-file patient/day joins, an EHR representation, personal-baseline estimation, missingness-aware temporal features, a localized airway simulator, next-day forecasting, an exposure editor and a clinician screen. Validate participant-level generalization and later-day adaptation separately. Report PEF error, deterioration sensitivity/PPV, PR-AUC, calibration and false alerts per patient-week. Test exposure shift, device dropout and small-cohort uncertainty.

This has stronger verified multimodal data than initially assumed. Its remaining challenges are retained historical fields, event count, sparse measurements and transfer from a UK sample to Indian scenarios.

## 4. CardioHarbor — A fluid-balance twin across discharge and home

**Pitch:** “A patient's discharge snapshot becomes a living model of their recovery, detecting a worsening trajectory across several home signals.”

### Focus and evidence

Retain chronic heart failure and one adverse endpoint: impending congestion-related deterioration. Use a 48-hour synthetic endpoint unless a paired real longitudinal dataset supports that horizon and outcome. The previous plan covers the Indian registry and wearable-monitoring evidence.

New mechanistic research strengthens the modeling direction: a [2025 cardiac digital-twin study](https://www.nature.com/articles/s41746-025-01501-9) fitted cardiovascular models in 343 HF patients. That supports exploring interpretable personalized physiology; it does not supply validation for our proposed home-wearable 48-hour forecast.

### Ambitious experience

**Recovery corridor:** an interactive timeline from admission to discharge to home follow-up. Historical measurements initialize the model; the evolving sensor stream drives the home state.

**Fluid-flow workspace:** generalized cardiac and fluid compartments visualize estimated volume, circulating state and congestion. Measured scale weight remains visibly distinct from inferred lung fluid. A weight increase is not automatically pulmonary edema.

**Evidence constellation:** aligned weight, resting HR, activity and supported respiratory measurements show how a pattern develops. Drivers are traceable to original observations and timestamps.

**Parallel follow-up scenarios:** explore the information value of an additional measurement or earlier clinician review. Medication-dose scenarios remain sandbox research with explicit assumptions and clinical constraints. No autonomous dosing or external clinical message is part of the PoC.

**Care-team view:** a doctor/nurse queue and a patient/caregiver explanation share the same underlying state and audit log. The clinical output remains the single deterioration forecast.

### Build and validation

Implement a reduced-order volume/cardiovascular model, particle or ensemble state estimation, static EHR priors, synthetic longitudinal trajectories, a multimodal event predictor and replay. Use open observed data only where the data genuinely matches the claimed task. Simulated latent event state must not leak into predictor inputs. Test recovery, deterioration, intercurrent illness, nonadherence to scale use and sensor artifacts.

Validate personal-baseline, weight-only and fused models under fixed false-alert budgets. Report parameter uncertainty and limitations of identifying physiological state from home measurements. This is the richest continuity-of-care experience, with the clearest need for further matched prospective data.

## One ambitious platform architecture, one selected disease module

1. **Patient history and provenance:** EHR-shaped historical records, exact available timestamps, units, documented observations and derived features. Synthetic histories are labeled. A FHIR-compatible adapter is useful; a full FHIR server is optional infrastructure.
2. **Observation event log:** append-only sensor/device data with event time, arrival time, patient/session identifiers and quality flags. Replay uses availability time, not a hindsight view of a finished table.
3. **Physiological state engine:** condition-specific state equations, historical parameter priors, sequential assimilation and posterior uncertainty. Every displayed latent state points to the model/parameter version that produced it.
4. **Data-driven predictor:** a well-benchmarked event and trajectory model using both historical and dynamic inputs. A TCN or another temporal model is a candidate when data supports it; complexity is selected by validation, not visual ambition.
5. **Scenario branches:** snapshot a patient state, apply explicitly proposed inputs, simulate multiple futures and retain lineage. Factual observed replay and simulated alternative outcomes occupy different evidence categories.
6. **Scenario comparison:** show risk/trajectory estimates, clinical or operational constraints, uncertainty and costs. Do not optimize a single risk score while hiding treatment incompleteness or unsupported assumptions.
7. **Clinician experience:** twin, trajectory, comparison, original evidence, history and review audit. Use accessible controls and strong units/labels. Explain only facts the model can support.
8. **Scientific evaluation workspace:** cohorts, patient-level splits, baseline comparisons, uncertainty calibration, event-level alert accounting, robustness and reproducibility. These views report real measured metrics only after evaluation runs.

Suggested implementation: Python with scientific/ML libraries for physiology and forecasting; FastAPI for typed model APIs; PostgreSQL for histories, events, predictions and scenario lineage; a worker queue for batch/ensemble simulations; React/TypeScript for the clinician application; WebGL/React Three Fiber for justified physiology diagrams; a charting layer for responsive uncertainty and time-series views. Select current package versions when implementing. Deploy locally first for reproducibility, then package containerized services if useful. No cloud or paid service is inherently required.

A generative assistant can help a doctor ask “show me the last comparable session” or explain a selected forecast, but its answers must be grounded in the event log and structured model results. It is not the physiological prediction engine. No sending, publishing or clinical-action integration should be inferred from an in-app review click.

## Build by scientific capabilities, not reduced feature count

**Capability A — Factual twin:** audited matched data, live/replayed observations, persistent individualized state, and a defined future event. Acceptance: an available-time replay and reproducible held-out predictions.

**Capability B — Physiological interpretation:** model/state fitting and meaningful visual representation. Acceptance: units and flow balance make sense, parameter uncertainty is visible, and unsupported anatomical precision is absent.

**Capability C — Parallel futures:** shared initial state, authored future inputs, branched simulation, comparison with tradeoffs and support bounds. Acceptance: alternatives are labeled simulated and prediction success is not misrepresented as causal validation.

**Capability D — Clinical workspace:** traceable evidence, session memory, patient explanation, cohort view and review audit. Acceptance: useful interactions operate on model output and data, not canned text or hard-coded risk numbers.

**Capability E — Scientific showcase:** robustness, baselines, calibration, patient-level validation, full reproducibility and a story that reveals an outcome after the forecast. Acceptance: every numerical performance claim points to an evaluation output.

**Capability F — Originality demonstrated in behavior:** competing physiological explanations, decision-relevant measurement selection and explicit scenario support boundaries. Acceptance: the system handles both resolvable and genuinely unresolved cases, and demonstrates benefit against single-family/fixed-measurement baselines in independently generated tests. See [the originality build sequence](docs/originality.md).

The interactive RENALIS concept lab accompanying this document is a small, explicitly synthetic reduced-order illustration. It computes alternative volume/BP trajectories locally to demonstrate the proposed interaction and tradeoff. It is not fitted to HEMOBP, not a clinical recommendation, not a trained event predictor, and not the finished hackathon submission.

## Requirement coverage and submission

| Core brief requirement | RENALIS | PRANA | AERIS | CardioHarbor |
|---|---|---|---|---|
| One chronic condition | End-stage CKD | Type 2 diabetes | Chronic asthma | Chronic HF |
| Static/historical stream | Patient + earlier dialysis records | Labs + prior responses | Patient profile + earlier PEF/history | Discharge history + earlier observations |
| Wearable/IoT dynamic stream | BP + dialysis-machine stream | CGM + activity | Smart PEF/inhaler/watch | Wearable + scale |
| One predicted adverse outcome | New hypotensive BP nadir | New sustained glucose excursion | Next-day PEF deterioration | Congestion-related deterioration |
| Updating patient twin | Volume/refill/compensation state | Absorption/glucose response state | Airway response state | Volume/cardiovascular state |
| Doctor dashboard | Dialysis cockpit | Metabolic future studio | Breathing/exposure workspace | Recovery/volume workspace |
| Allowed training provenance | Open matched data; synthetic scenarios | Open matched data; synthetic scenarios | Open multimodal data; synthetic scenarios | Synthetic matched trajectories; compatible observed data if verified |

All four can be designed to cover every explicit technical requirement. Completion requires a working evaluated model and permitted data, not just the interface. Synthetic data is allowed by the brief; it does not become real clinical evidence because the visuals are sophisticated. Data-access terms, exact fields and endpoint counts must be audited before promising accuracy.

Retain the supplied submission requirements: public GitHub repository, required README/team/college/model/license details, **minimum 20-minute demonstration video**, architecture PDF/PPT, presentation PDF/PPT, accessible files/links and required folder naming. Team eligibility and registration remain administrative requirements. The earlier deadline information is not used to constrain the ambition of this plan.

## Choice based on the user’s actual priorities

- Choose **RENALIS** for a focused medical decision with a visible physical mechanism, meaningful scenario tradeoffs and verified matched data.
- Choose **PRANA** for the most immediately relatable product and the strongest meal/physiology/parallel-future experience.
- Choose **AERIS** for the most compelling environment-and-India story with a verified linked smart-device dataset.
- Choose **CardioHarbor** for the deepest hospital-to-home continuity story, accepting that real outcome validation requires further data.

My pick is **RENALIS** for clinical distinctiveness and mechanistic depth, with **PRANA** close behind for audience appeal. The recommendation changed because the user prioritized ambition and the expanded research found stronger dialysis and asthma data leads—not because bigger features inherently improve healthcare.
