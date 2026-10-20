> Historical snapshot of the earlier release. Current implementation, artifacts, evaluations and unresolved gates are in [release 0.4](release-v04.md) and [README](../README.md). Earlier counts and results remain for provenance.

# RENALIS evidence and validation review

Reviewed 16 October 2026. This is a focused primary-source review and a proposed validation protocol, not a systematic review, a clinical guideline, or proof of global novelty. The searchable in-app source records live in `src/researchSources.ts`.

## The research question

**When plausible physiological explanations fit the same available BP history but disagree about fluid-removal scenarios, can a model identify an additional feasible observation that improves the comparison?**

RENALIS currently demonstrates this calculation in a synthetic workspace. A separate retrospective HEMOBP baseline establishes that the project can ingest observed dialysis data and run a patient-separated predictive evaluation. These are distinct experiments. Neither validates the clinical effects of an alternate removal profile.

The proposed contribution is the combined workflow: retain rival explanations, expose their decision disagreement, estimate the value of another observation, update with its recorded result, and preserve unresolved or contradicted states. Each component has prior work. We should present this as an integration and research hypothesis, never as the first dialysis digital twin or a proven improvement in patient outcomes.

## Why the problem matters

Blood-pressure instability and fluid excess create competing dialysis-management problems. The [KDIGO dialysis conference report](https://kdigo.org/wp-content/uploads/2017/05/KDIGO-BP-Volume-in-Dialysis-FINAL.pdf) explicitly cautions against avoiding hypotension at the expense of euvolemia and adequate treatment time. This supports showing unfinished fluid removal alongside BP scenarios. It does not support an automatically recommended “safe” profile.

For India, a [2024 private-network survival study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11004392/) demonstrates care variation in a large Indian cohort. It includes 23,601 patients and excludes the first 90 days after joining a centre. It supports local relevance, not a national count of dialysis need, a national IDH prevalence, or attribution of mortality differences to hypotension. Avoid unsourced national CKD/dialysis burden numbers on the landing page.

## Endpoint and current-event semantics

Our authored endpoint is **a future measured or modelled systolic BP ≤90 mmHg**, with a specified horizon and availability cutoff. This is a low-BP research endpoint, not a complete diagnosis of symptomatic intradialytic hypotension. [Flythe et al.](https://pubmed.ncbi.nlm.nih.gov/25270068/) studied a nadir **<90** threshold and found that associations varied with predialysis BP. The distinction between `<` and `≤` must be explicit.

If the latest available valid observation is already at or below our threshold, the correct interface state is **current low BP**, with no advance-warning percentage. A stale reading, session end, and model contradiction also require separate states. Do not call particle crossing fractions calibrated patient risks, and do not translate mortality associations into claims that a lower forecast prevents mortality.

The [UK Kidney Association’s January 2025 dialysis BP guideline](https://ukkidney.org/sites/default/files/documents/FINAL%20VERSION%20-%20UKKA%20Management%20of%20blood%20pressure%20guideline-Jan%202025.pdf) is a more recent clinical-reference checkpoint for eventual clinician review. The general KDIGO 2021 BP guideline concerns CKD not receiving dialysis and must not be substituted for dialysis-specific guidance.

## Mechanisms: supported rationale, authored equations

[Levin et al. (2018)](https://academic.oup.com/ndt/article/33/9/1643/4970569) observed distinct cardiac-power, peripheral-resistance, and combined patterns using noninvasive hemodynamic measurements in 54 patients. This is relevant evidence that similar pressure changes can accompany different hemodynamic responses. Measurements were intermittent and important covariates were not collected.

Our volume/refill, vascular-compensation, and cardiac-response families are deliberately simplified research models. They are not a validated mapping to that paper’s clinical groups. Mechanisms may coexist, other causes may be absent from the family set, and a well-fitting BP curve does not establish the true cause. Label weights **relative compatibility within these models**, not diagnostic probabilities. Auxiliary volume/output equations and assumed noise are inspectable assumptions, not measured device accuracy.

## Prior work and the originality boundary

| Verified source | Evidence type | Consequence for RENALIS |
|---|---|---|
| [Zhang et al., real-time IDH prediction, 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10310501/) | Original retrospective prediction study | EHR/device fusion and advance prediction already exist. Reported AUROC 0.89 has a different split, endpoint, and horizon; it cannot rank our benchmark. |
| [Hsieh et al., IoMT and EMR complications model, 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10332468/) | Original integration/prediction study | The paper already uses human digital-twin language for dialysis. Our differentiator must be demonstrated behavior beyond that label. |
| [SICATA survival digital twin, 2024](https://academic.oup.com/ndt/article/39/Supplement_1/gfae069-1568-460/7677830) | Conference abstract | Relevant priority boundary, weaker evidence than a full bedside evaluation. |
| [Shotwell et al., optimal pharmacokinetic design, 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4744591/) | Original methods and simulation study | Informative sampling in dialysis-related systems is established; our specific objective is scenario decision value. |
| [Optimal β2-microglobulin sampling, 2015](https://www.sciencedirect.com/science/article/abs/pii/S0009250915002274) | Original model-based experiment-design study | Another direct counterexample to claiming that optimal dialysis sampling is new. |
| [Keogh and van Geloven, counterfactual evaluation, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11332371/) | Original causal evaluation methods | Ordinary factual prediction metrics do not validate hypothetical intervention predictions. |

A newly checked adjacent proposal is [Patel et al., Physiologically-Guided Ultrafiltration, September 2026](https://onlinelibrary.wiley.com/doi/full/10.1111/nep.70272). This review proposes combining ultrasound congestion and preload assessments to individualize removal. The authors explicitly state that the integrated framework lacks prospective validation. It strengthens the boundary around novelty: bedside physiological reasoning and measurement-guided removal frameworks already exist. It is a proposed framework, not evidence that RENALIS’s measurement policy works.

The focused search did not establish priority for RENALIS’s complete workflow. A defensible description is **an inspectable implementation exploring decision-relevant physiological uncertainty**. A patent, product, and broader database search would be required for a stronger novelty assessment.

## More information is not automatically better care

The [randomized intradialytic blood-volume-monitoring trial](https://pubmed.ncbi.nlm.nih.gov/15930095/) assigned 443 patients to monitoring or conventional care. It did not show benefit and observed higher hospitalization and mortality in the monitoring arm; authors caution about unusually low control-group event rates. This does not condemn every sensor. It shows why discrimination, information gain, decision quality, and patient outcomes must be tested separately.

RENALIS therefore estimates a measurement’s **expected reduction in an authored research loss**. A measurement may reduce family entropy without improving the scenario choice. Device availability, acquisition failure, staff time, noise, and delay belong in the evaluation. A low-value result is meaningful and should remain visible.

## HEMOBP: what our observed benchmark can establish

The [original HEMOBP descriptor](https://www.nature.com/articles/s41597-019-0319-8) describes Taiwan outpatient data from 2013–2018. The 4,366,298 records must not be described as independent cuff readings. BP was routinely measured around 30-minute intervals, with additional measurements and setting changes related to clinical need. This makes observation timing informative. Source tables include session-end weight, which cannot be an input to an earlier forecast. The publication reports UF in L/h; our source-unit reconciliation remains an explicit audit item. It does not supply our synthetic relative-volume/output observations.

Our checked-in `docs/observed-baseline.json` reports a patient-disjoint test set with 77,138 windows and 211 patients, no patient overlap. The fused regression MAE is 10.679 mmHg versus 10.697 dynamic-only and 11.336 last-BP persistence. The historical increment over dynamic-only is small. The event classifier has sensitivity 0.753, PPV 0.127, PR AUC 0.197, and 11,497 false-positive windows. These are **our retrospective benchmark results**, not published HEMOBP study results, and are window-level rather than consolidated alarm burden.

Do not describe the baseline as a calibrated clinical warning system, Indian validation, symptomatic-IDH validation, a learned causal treatment model, or the engine powering the synthetic twin.

## What the current challenge result says

The checked-in 108-case independent simulator challenge is valuable because it exposes a negative result. Decision-value selection has mean regret 0.2656 versus 0.2655 for fixed cuff; it does **not** demonstrate average superiority. Information-only selection has mean regret 0.2290. These authored in-silico outcomes are model-mismatch diagnostics, not clinical effect estimates.

Keep this suite frozen. Any changes motivated by its results must be reported as development work and evaluated on a newly specified holdout suite. Do not tune the simulator until the desired policy wins.

## Predeclared next validation design

1. **Specify the intended use and estimands.** The immediate user is a clinician/researcher inspecting evidence sufficiency during dialysis. Separate factual future low-BP prediction, scenario response, mechanism compatibility, and measurement value. Define time zero, permissible action times, event inequalities, observation delay, and maximum measurement budget before evaluating.
2. **Audit observed data first.** Independently verify inferred session boundaries, repeated BP identifiers, units, time zones, missingness, symptom-triggered sampling, treatment changes, and patient separation. Build a data dictionary and retain counts through every exclusion. Exclude future readings, future settings, and session-end values from each cutoff.
3. **Freeze development and held-out simulations.** Generate distinct mixed-mechanism, unknown-mechanism, nonlinear, drug-effect, artifact, unavailable-device, delayed-reading, and low-information cases with independent code. Seal seeds and parameter ranges before policy changes. Include impossible identification cases whose desired state is unresolved.
4. **Compare fair baselines.** Evaluate no additional measurement, fixed cuff, a fixed auxiliary channel, entropy-only selection, and decision-value selection with identical channels, timing rules, maximum budgets, and missing-device draws. Charge requested failed acquisitions and waiting costs. Compare single-family and multi-family models separately from measurement policy.
5. **Predeclare metrics and uncertainty.** Report independent decision regret, clinically authored profile acceptability once available, unresolved comparisons, false certainty, contradiction detection delay/false alarms, acquisitions, delays, and threshold misses. For factual forecasts report MAE, calibration, interval coverage, discrimination, PPV, event-level sensitivity, lead time, and alarms per session/hour. Use patient/session-block bootstrap confidence intervals and subgroup reporting; never bootstrap correlated windows as independent patients.
6. **Run robustness and ablations.** Vary noise, loss weights, family priors, support cutoffs, time discretization, and missingness. Remove auxiliary channels, model disagreement, and burden terms in turn. Report whether rankings change and why. Test numerical quadrature accuracy and out-of-family contradiction behavior.
7. **Collect paired physiology prospectively in silent mode.** With institutional/ethics approval and clinical collaborators, obtain synchronized BP, valid hemodynamic/volume observations where available, machine settings, symptoms, treatment actions, acquisition failures, and staff time across multiple centres. Follow ordinary care; hide experimental recommendations. Plan sample size from desired precision and clustering, rather than picking a convenient number of windows.
8. **Validate scenario effects separately.** A factual response after a clinician changes treatment is not an observed alternate world. Specify a target trial or appropriate longitudinal causal analysis, confounders, positivity, intervention versions, and sensitivity analyses before using observational treatment logs. If these assumptions are not supportable, keep scenario responses experimental. An eventual clinician-led prospective study is required for outcome-benefit claims.
9. **Evaluate the interface with users.** Use realistic low-BP, stale, unresolved, contradiction, and no-device tasks. Measure correct interpretation of compatibility versus diagnosis, current event versus advance warning, factual versus hypothetical outcomes, task time, and over-reliance. Audit keyboard navigation, screen-reader names, contrast, mobile reflow, and chart units.

Progression gates should be signed off by domain collaborators: trustworthy ingestion before observed forecasting, demonstrated calibration before clinical probability language, evidence of decision benefit before superiority claims, and appropriate prospective validation before any treatment recommendation.

## Reference hygiene and wording corrections

- The existing 2018 hemodynamic reference is relevant; do not imply its three groups validate our three equations or that pure mechanisms are mutually exclusive.
- The existing 2024 SICATA citation is a survival-model conference abstract. Pair it with the full 2023 IoMT/EMR paper when discussing digital-twin prior art.
- The 2016 optimal-design paper appeared online in 2015; 2016 is its journal-volume year. The 2015 β2-microglobulin paper is independently verified and correctly described as adjacent sampling work.
- The 2024 counterfactual-methods citation is relevant, but its time-to-event validation is not directly implemented by our short-horizon sandbox.
- Retrospective association, modelled information value, clinical utility, and prospective patient benefit require different evidence. Use those exact distinctions in the landing page, explanation view, model card, and pitch.
- The original plan’s early future-tense paragraphs coexist with its later implemented-status table. Prefer the implemented section and repository tests when describing current functionality; do not present planned prospective validation as completed.

Search scope: focused combinations of intradialytic hypotension, hemodynamics, cardiac output, blood-volume monitoring randomized trial, India haemodialysis cohort, dialysis digital twin, optimal sampling/design, HEMOBP, and prediction under interventions. Publisher articles, original methods papers, official guidance, and original dataset descriptions were prioritized; aggregator pages were used only to locate primary records. No product/patent comprehensiveness or global-priority claim is made.
