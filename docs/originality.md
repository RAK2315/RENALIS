> Historical snapshot of the earlier release. Current implementation, artifacts, evaluations and unresolved gates are in [release 0.4](release-v04.md) and [README](../README.md). Earlier counts and results remain for provenance.

# RENALIS originality and research contribution

Updated 16 October 2026. This combines the original research plan with the implemented mechanism lab, now version 0.3 with timestamp-consistent pressure propagation. It is not a claim of priority, patentability, or proven clinical benefit. The implementation table and measured results below distinguish working behavior from remaining research.

## The originality we should aim to demonstrate

**A dialysis twin that recognizes when several physiological explanations fit the same observations, checks whether those explanations disagree about a proposed scenario, and estimates which additional measurement could resolve the disagreement.**

The core question becomes: **“Do we have enough evidence to compare these futures—and, if not, what would help?”** The original contribution we intend to test is that combined decision process, its clinician interface and its evaluation. Predicting hypotension alone, applying a digital-twin label, showing an uncertainty band or adding a scenario slider does not establish originality.

This keeps the original hackathon task: historical EHR plus dynamic medical-device data, an updating patient model, one localized future hypotension outcome, and a doctor-facing dashboard. The new elements deepen that task rather than introduce unrelated diseases.

## What already exists

| Component | Related work identified | Consequence for our claim |
|---|---|---|
| Real-time IDH prediction using history and intradialytic observations | [2023 real-time prediction study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10310501/) | Our factual predictor and EHR/device fusion are foundational, not the novelty claim. |
| Future-session risk and personalized triage | [2023 triage-support algorithms](https://pubmed.ncbi.nlm.nih.gov/37707692/) | Session memory and personalized risk are not new by themselves. |
| Dialysis research using digital-twin terminology | [2024 SICATA registry conference abstract](https://academic.oup.com/ndt/article/39/Supplement_1/gfae069-1568-460/7677830) | We cannot claim to invent the dialysis digital twin. A conference abstract is narrower evidence than a fully evaluated bedside system. |
| Different hemodynamic mechanisms behind hypotension | [2018 cardiac-power/peripheral-resistance study](https://academic.oup.com/ndt/article/33/9/1643/4970569) | Mechanism distinctions are known physiology. Our proposal concerns retaining ambiguity and using it to guide information gathering. |
| UF biofeedback and adaptive control | [2024 closed-loop UF review](https://pmc.ncbi.nlm.nih.gov/articles/PMC11360213/) | Personalized fluid-removal control already has substantial research history; a changing UF profile is not an original invention. |
| Optimal sampling in dialysis-related models | [2015 toxin-kinetics sampling study](https://www.sciencedirect.com/science/article/abs/pii/S0009250915002274), [2016 dialysis pharmacokinetic design study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4744591/) | Information-efficient measurement is established in adjacent dialysis problems. The proposed focus is resolving disagreement about imminent hypotension scenarios. |
| Treatment-response counterfactuals | [2017 treatment-response modeling paper](https://auai.org/uai2017/proceedings/papers/266.pdf), [2024 intervention-prediction evaluation methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11332371/) | Counterfactual prediction itself is established. Factual forecast accuracy cannot validate alternative treatment outcomes. |

The review found adjacent approaches for all the building blocks. It did not identify a matching end-to-end dialysis bedside implementation of the proposed combination. That is a bounded search finding, not proof that no unpublished, commercial or differently described implementation exists.

## Originality direction 1: Competing physiological explanations

### The new product behavior

Instead of collapsing all uncertainty into one fluid-state estimate, retain several plausible model families:

- Volume/refill limitation: removal outpaces modeled refill.
- Vascular compensation limitation: the pressure response involves inadequate modeled resistance compensation.
- Cardiac response limitation: modeled output/compensation contributes to the falling pressure.

Each family must fit only observations available at the cutoff. A model family is a physiological hypothesis, not a diagnosis. The original Patient twin retains one fluid-model family with parameter particles. The implemented Mechanism lab adds three distinct authored response families; identifiability on matched observed physiology remains unestablished.

Families can agree that BP may fall while disagreeing about the expected benefit of slowing removal. That disagreement should remain visible. If the signals cannot distinguish the explanations, the UI must preserve that ambiguity rather than choose an attractive anatomical story.

### Why it matters

A well-fitting BP curve does not uniquely establish what is happening inside the circulation. A scenario can look precise even when its assumed mechanism is uncertain. We should test whether making this uncertainty explicit reduces unsupported scenario rankings.

### Visual experience

A clinician switches between plausible mechanism views sharing the same observed BP trace. The mechanism views show estimated volume, compensation and response flows, with their assumptions. The scenario plot displays where their future estimates diverge. Use “consistent with available data,” not an asserted probability of a clinical diagnosis.

### Acceptance and evaluation

Fit rival model families to deliberately ambiguous synthetic histories. Test on an independent simulator with mechanisms not shared by the fitted family. Compare a single-family twin, an averaged ensemble and the mechanism-disagreement version. Evaluate predictive fit, scenario-ranking disagreement and false certainty, not just curve error. Include a case where the mechanism cannot be identified and the correct output is unresolved.

**Novelty status:** known mechanisms and ensemble methods; proposed distinctive application is clinician-visible, decision-relevant disagreement across plausible dialysis mechanisms.

## Originality direction 2: The next measurement that could change the comparison

### The new product behavior

For each available measurement type and permissible time, simulate possible results and posterior updates. Estimate how often those results would resolve a scenario comparison, change its ranking or materially reduce decision uncertainty. Report expected decision value relative to measurement burden.

Candidate channels may include a repeat cuff reading, relative blood-volume/hematocrit information or an appropriate noninvasive hemodynamic measurement. Availability is explicit. HEMOBP does not provide all these channels, so unobserved-channel experiments begin as synthetic research and cannot be described as measured performance on that dataset.

Do not assume a repeat cuff can resolve every mechanism. When rival families predict the same BP but different responses, another BP measurement might have little discriminating value. The system should be able to say that no available observation is sufficient.

### Proposed algorithm

1. Start with the current posterior over model family and patient state.
2. Evaluate clinician-authored UF scenarios under each plausible model.
3. For each available candidate measurement, draw possible values from its observation model, including noise and missingness.
4. Update the posterior using each hypothetical value, without seeing the actual future.
5. Recompute scenario comparison and estimate the expected reduction in decision ambiguity or regret.
6. Subtract a transparent sandbox measurement cost/burden; apply clinician-set limits.
7. Present the measurement with its modeled value and uncertainty, or state that none is informative enough.

Decision value must be distinct from entropy reduction. A measurement can improve parameter certainty while leaving all scenario comparisons unchanged. This policy must not delay routine monitoring or urgent clinical assessment; it is a research comparison aid, not an emergency-care scheduler.

### Visual experience

The twin displays “What evidence would help?” beside the scenario fork. Each available measurement shows the decision it could clarify. After an explicitly requested synthetic observation arrives, the competing trajectories update and the comparison may become better supported. No fictitious channel appears as a real device reading.

### Acceptance and evaluation

Compare fixed-period measurements, repeat-BP-only, uncertainty-only selection, and decision-value selection under identical measurement budgets. Measure incorrect scenario rankings, unresolved comparisons, measurements consumed, delay and missed events. Count every requested but unavailable measurement. Test a channel that provides no useful information and require the policy to reject it.

**Novelty status:** optimal experimental design is established, including in dialysis-related models. The focused review did not identify this specific scenario-disagreement-driven bedside hypotension workflow. Treat it as an originality hypothesis to test.

## Originality direction 3: A visible boundary around supported scenarios

### The new product behavior

Every scenario has separate assessments for:

- Fit to available factual observations.
- Similarity to observed patient/settings support.
- Sensitivity to uncertain parameters and competing mechanisms.
- Availability of the measurements needed to distinguish those mechanisms.
- Credibility of intervention effects, distinct from factual forecast accuracy.

Do not combine these into an unexplained “trust score.” Show the actual reasons and which evidence is missing. A scenario can be physiologically possible but unsupported by observed treatment data. It can also lie within observed input ranges while still lacking causal identification.

### Visual experience

Create a scenario landscape with fluid removed on one axis and projected minimum BP on the other. Mark regions where comparisons are stable across plausible models, change with the model, or extrapolate beyond observed support. Selecting a point opens its assumptions and evidence lineage. Labels say “supported under current sandbox assumptions,” not “clinically safe.”

The useful moment is a scenario that initially looks attractive but loses its ranking after unsupported assumptions are exposed. After an informative measurement, the model-disagreement region can shrink without implying that causal efficacy has been proven.

### Acceptance and evaluation

Test out-of-support UF inputs, physiological model mismatch, missing channels and small parameter changes. Record unsupported scenarios detected, valid comparisons retained and false declarations of support. Use blinded synthetic cases with known counterfactual outcomes, then a separately justified observational causal-evaluation protocol if the available data meets its assumptions. A “causal certificate” is not claimed.

**Novelty status:** out-of-distribution detection, uncertainty and causal identification are established topics. The proposed contribution is their explicit separation at each simulated dialysis scenario and their coupling to decision-relevant measurement selection.

## Originality direction 4: A twin that can challenge and downgrade itself

### The new product behavior

When a new observation arrives, check whether it was plausible under the previous forecast. Repeated mismatch can reduce the model's scenario authority, broaden its model family or trigger an unresolved state. Preserve both the previous forecast and the later observation in a lineage log.

For observed treatment changes, test the factual response under the actual post-change input; do not treat that as observing the unrealized alternative. Treatment changes are not random and can be confounded by clinician concern. A simple before/after residual cannot establish causality.

### Visual experience and test

An “assumptions no longer fit” state replaces the polished forecast when an independent simulator changes its mechanism. The clinician can inspect which observations contradicted it. Measure detection delay, false resets and recovery after refitting. Compare against a model that keeps producing narrow intervals despite drift.

**Novelty status:** drift detection and online calibration exist. This is a supporting feature; its standalone novelty is weak. Its role is to make the proposed mechanism/measurement workflow auditable.

## Stretch direction: Session-to-session consequences

Carry residual fluid and uncertain response state into the next synthetic session, with explicit assumptions for interdialytic intake, residual kidney function and interval duration. Show the cost of declaring a profile successful merely because it avoided a current-session BP event while leaving fluid behind. Continue predicting the same localized hypotension outcome, not a new suite of diagnoses.

Volume management and longitudinal modeling are established. Treat this as a product-depth extension rather than the primary originality claim. It requires additional data and cannot be validated from the current four-patient sandbox alone.

## A concrete signature demonstration

1. Two plausible mechanism families fit the patient's past BP/device history.
2. Both forecast possible hypotension, but they disagree about the benefit of two proposed UF profiles.
3. The scenario view marks the comparison unresolved and shows why.
4. The measurement engine finds that another BP alone would add little information, while an available synthetic volume/hemodynamic channel could distinguish the hypotheses.
5. Reveal that channel's synthetic measurement; update both families from the same cutoff.
6. Show the revised scenario comparison and its fluid-removal tradeoff.
7. Reveal later factual readings separately. Keep unchosen treatment outcomes simulated.
8. Repeat with unavailable or uninformative channels. The twin remains unresolved instead of manufacturing certainty.

This makes the originality visible in the algorithm's behavior. It also ties the visual experience to a clinically relevant question: whether the available evidence is sufficient for the comparison being shown.

## Build order and measurable research questions

1. **Competing-mechanism engine:** multiple explicit equations, shared observation interface, posterior family weights, and identifiability tests.
2. **Scenario disagreement:** rank clinician-authored alternatives under each family and record which assumptions change the comparison.
3. **Measurement-value engine:** simulate possible observations and assess decision changes under a fixed observation budget.
4. **Scenario support view:** observed support, mechanism dependence and intervention-assumption limits, displayed separately.
5. **Independent challenge suite:** unseen simulator mechanisms, unavailable channels, artifact/missingness and drift.

Research questions: Does decision-value measurement selection reduce incorrect comparisons at an equal measurement budget? Does explicit mechanism disagreement reduce false certainty under model mismatch? Can scenario support checks withhold extrapolative claims without discarding all useful comparisons?

Use predeclared metrics and patient/mechanism-separated evaluation sets. Synthetic results support only in-silico claims. For a clinical claim, identify and collect the required paired measurements, treatment logs and prospective outcomes.

## Current implementation versus proposed originality

| Capability | Current state |
|---|---|
| Single fluid-model family with parameter particles | Implemented |
| Synthetic historical/dynamic fusion and posterior forecast | Implemented |
| Two authored UF profile types, tradeoff display and lineage | Implemented |
| Fixed stale-data abstention | Implemented |
| Separate observed HEMOBP baseline and held-out evaluation | Implemented; retrospective audit limitations remain |
| Competing physiological mechanism families | Implemented: three explicit response families, 48 compatibility particles each, shared available BP history |
| Decision-disagreement-driven measurement selection | Implemented: expected research-loss reduction, separate information gain, noise/burden assumptions, permitted timing, and no-value abstention |
| Per-scenario separation of observed support and intervention assumptions | Implemented: factual fit, within-session input support, mechanism dependence, and causal limits shown separately |
| Independent simulator challenge suite and automatic authority downgrade | Implemented: independent additive-response scoring, one-observation policy comparison, contradiction downgrade, immutable evidence audit |
| Session-to-session carry-over | Implemented as explicit fluid accounting; not a validated longitudinal physiological model |
| Adaptive clinical refitting and prospective superiority | Not established; remains scientific work |

The flagship features are now working algorithms and UI flows, separate from the original single-family Patient twin. The lab is an inspectable research experiment; it does not identify a patient’s true mechanism.

## Implemented algorithm and measured challenge results

`backend/mechanisms.py` accepts an explicitly sliced history and historical priors. It fits volume/refill, vascular-compensation, and cardiac-response families to available BP. The families use different volume sensitivities and fitted local pressure factors; auxiliary relative-volume and cardiac-output equations are research proxies. Compatibility weights express conditional fit within the chosen family set, not probabilities of diagnoses.

For each eligible channel at now, +5, or +10 minutes, Gaussian quadrature integrates over possible measurements. The value is prior minimum expected scenario loss minus expected posterior minimum loss. Family information gain is calculated separately in bits. Research loss is `2 × threshold crossing + 0.2 × scaled below-threshold severity + 0.8 × unfinished target fraction`. Net value subtracts channel burden times the user’s multiplier and `0.002 × delay minutes`. Three quadrature nodes approximate Gaussian measurement noise; this is not a calibrated clinical utility function.

Assumed noise SD: cuff 3.5 mmHg, relative volume 1.0 percentage point, output 0.30 L/min. Raw burden units: 0.012, 0.035, and 0.055 respectively; default multiplier 0.5. These authored values are inspectable, and are not device specifications or measured clinical costs. Channel availability, high burden, redundant observations, and low decision value can all produce no suggested measurement. Delayed measurements cannot retroactively change a profile: removal stays at the current rate until the observation arrives. Waiting past modeled instability is excluded.

Acquisition is isolated in `backend/measurement_fixtures.py`; inference and selection cannot call it. Observations become available at their recorded minute, cannot be counted twice, and are archived rather than deleted on reset. Saved reports retain original evidence, settings, and revision; restoring settings explicitly recomputes against current evidence. Live exports include all available history, historical priors, available channels, noise/burden assumptions, and model revision. Conditional agreement considers families with at least 10% relative support, an authored research cutoff. The selected family's band shows its weighted 10th–90th particle range, not a calibrated clinical interval. A value farther than four assumed noise SD from every particle, or a minimum factual fit RMSE above 8 mmHg, downgrades comparison authority. Current low BP, stale BP, and completed sessions also withhold scenario curves, ranking, measurement scheduling, and carry-over projections.

At Meera’s minute 90, the three families fit recent BP at approximately 1.8–1.9 mmHg RMSE but estimate changes of +20.3, +2.9, and +8.0 mmHg for the selected 650 mL/h profile relative to continuing current removal. The initial best observation is immediate cardiac output (expected loss reduction 0.0521; net 0.0246). The synthetic value 3.74 L/min reduces vascular-family support but does not resolve volume versus cardiac ambiguity. A different compatible output observation can yield conditional model agreement; neither outcome establishes a diagnosis.

`backend/challenges.py` scores 108 independent additive-response cases (36 identical-past histories × three hidden response types) rather than generating scored futures with the twin’s pressure equations. Fixed cuff, family-information, and decision-value policies share the same channels and one-observation budget. The selector cannot inspect any unreleased value. Results are reproducible in `docs/originality-challenges.json`:

| Policy | Mean independent regret ↓ | Exact best-profile match | Acquisitions | Cases worse than cuff |
|---|---:|---:|---:|---:|
| Fixed cuff | 0.2655 | 0.9% | 108/108 | 0 |
| Family information gain | 0.2290 | 25.0% | 108/108 | 8 |
| Decision value minus burden | 0.2656 | 25.0% | 96/108 | 8 |

**The decision-value policy does not beat the cuff baseline on mean regret in this challenge set.** Better model-family discrimination does not ensure a better profile choice under model mismatch. Do not claim superiority, and do not tune against this suite and call it a held-out result. All model equations, loss weights, and challenge distributions are authored synthetic assumptions. The suite does not validate clinical treatment effects or delayed-measurement outcomes.

Regenerate with `python -m backend.challenges`. The dashboard’s “Run challenge suite” computes the same report and exports all 324 scored policy rows. Guard checks cover ambiguous BP, uninformative cuff, no device availability, all-family contradiction, and an already-low event. Unit tests additionally cover future-data isolation, delayed release, duplicate acquisition, immutable saves, measurement-noise sensitivity, and blocked end-of-session forecasts.

## What to say to the jury

**“RENALIS explores whether a dialysis twin can recognize when different physiological explanations imply different scenario responses, then identify which additional observation would make that comparison more informative.”**

The implemented claim is: “In a synthetic workspace, RENALIS preserves rival explanations, shows scenario disagreement, and computes which available observation has the highest expected decision value under declared assumptions.” Do not claim the first dialysis digital twin, the first IDH predictor, the first UF optimizer, the first counterfactual system, or clinically proven scenario effects.

## Search scope and novelty confidence

Focused web review on 14 October 2026 covered dialysis digital twins, IDH prediction, UF biofeedback/control, treatment-response counterfactuals, hemodynamic mechanism identification and optimal measurement/sampling. Representative searches included “hemodialysis digital twin ultrafiltration,” “intradialytic hypotension value of information,” “hemodialysis decision disagreement,” “hemodialysis optimal experimental design,” and “intradialytic hypotension information gain.”

Published papers and original study/repository descriptions were prioritized. Water-treatment ultrafiltration results, unrelated educational active-learning results and unsupported concept pages were excluded from the novelty argument. Adjacent sampling-design papers were retained because they directly weaken any claim that choosing informative measurements is itself new.

This was a focused literature comparison, not a systematic search of every publication, patent, product or unpublished project. The responsible status is **a distinctive, underexplored integration candidate with adjacent prior work and unverified global novelty**. Recheck that status as the implementation and literature review develop.
