> Historical snapshot of the earlier release. Current implementation, artifacts, evaluations and unresolved gates are in [release 0.4](release-v04.md) and [README](../README.md). Earlier counts and results remain for provenance.

# RENALIS execution and validation plan

Audit date: 16 October 2026. This document records the implementation inspected on that date and the remaining research and submission work. It is a plan and evidence ledger, not a claim that the prototype is clinically validated or that a hackathon entry has been submitted.

## The project in one paragraph

RENALIS is a local research prototype for one event during maintenance hemodialysis: a new measured systolic BP at or below 90 mmHg within a nominal 30-minute horizon. A synthetic historical EHR supplies patient-specific priors; available synthetic BP and dialysis-machine observations update a fluid-state model. A separate Mechanism lab preserves three authored explanations that may fit the same BP history while predicting different responses to fluid-removal profiles. It estimates which available observation could improve that comparison under an explicit research loss. The strongest implemented contribution is this inspectable uncertainty workflow. Better clinical decisions, diagnosis of the actual mechanism, causal treatment effects, global novelty, and prospective benefit have not been established.

## Source of the hackathon requirements

The requirements below come from the user-supplied organizer brief, saved as `C:/Users/rehtr/.codex/attachments/f5eabe85-9683-4cbb-8078-93ad873803f2/Pasted text.txt`. This is the supplied text, not a separately verified current organizer webpage. Eligibility, submission dates, and organizer instructions should be checked against the official submission portal before publishing the final entry.

The brief contains inconsistent shortlisting language: one passage describes five shortlisted teams after Phase 1, while Phase 2 says ten teams present virtually. Do not invent a resolution. Confirm the current sequence with the organizer and retain the answer with submission records. The supplied summit date is 20 November 2026 in Bengaluru; it does not supply a Phase 1 deadline.

## Exact requirement-to-implementation mapping

| Requirement from supplied brief | Implemented evidence | Status and remaining work |
|---|---|---|
| Foundational proof-of-concept digital twin, not a whole-body model | `backend/model.py` evolves circulating/tissue fluid state and updates particle weights from available BP; clinician UI exposes the state and forecast. | Implemented as a research simulation. It is a localized physiological model, not a complete virtual patient. |
| Select one specific chronic/lifestyle condition prevalent in India | Maintenance-hemodialysis patients with end-stage chronic kidney disease; localized intradialytic low-BP event. | Scope is specific. Final presentation must support Indian clinical relevance with appropriate primary Indian evidence and explain that event prediction is within CKD care, rather than claim Indian validation. |
| Fuse static/historical EHR and dynamic sensor/IoT streams | Authored synthetic baseline, initial volume, refill prior, and session target enter `_filter`; available cuff BP and actual-to-cutoff machine settings drive updates and transitions. `tests/test_model.py` verifies historical-prior influence and future-reading isolation. | Implemented algorithmic fusion. Demographic display alone is not the evidence of fusion. The separately displayed historical summaries are generated from an authored prior; the estimator does not learn that prior from the displayed summaries. |
| Dynamic data may be simulated or open-source | Synthetic medical-device replay includes cuff BP, HR and machine fields. Only modeled channels are described as model inputs. Separate HEMOBP pipeline uses anonymized observed machine/patient tables. | Implemented. Do not describe replay as a live connected wearable, and do not imply that every displayed field is used in prediction. |
| Working algorithm predicts an adverse localized future outcome | Patient twin forecasts a model-particle crossing fraction and BP trajectory; distinguishes existing low BP, stale readings, artifact and session completion. | Working forecast pipeline. Predictive clinical performance is unvalidated; a crossing fraction is not a calibrated clinical probability. |
| Conceptual doctor-facing dashboard | Patient twin, Mechanism lab, unit overview, history, review notes, scenario branches, evidence and exports. | Implemented locally. Usability with clinicians remains unevaluated. Landing, guided workspace, source library, research results, and resources now form a complete visitor-to-demo journey covered by browser regression checks. |
| Use anonymized, open-source or synthetic training/model data | Fictional EHR/device fixtures; separate HEMOBP v3 retrospective baseline, CC BY 4.0. | Meets the stated sandbox data-source restriction for the current prototype. No real patient upload workflow is implemented. Data-use attribution and limits must remain visible. |
| Project title and problem/use case in README | `README.md` identifies RENALIS, dialysis context and endpoint. | Implemented. Keep public-facing language aligned with the model card. |
| Technical stack and AI/ML details | README, model card and source describe React/TypeScript/Vite, FastAPI, NumPy, SQLite, particle model and separate scikit-learn baselines. | Implemented. Record release commit and dependency lockfiles for submission reproducibility. |
| Team details and college/incubator information | No verified team identity supplied in the inspected repository. | **Not done. Human-supplied administrative details required.** Do not fabricate names, college affiliation, eligibility or registration status. |
| Team of 1–4 full-time students; details verified; team fixed after registration | User mentioned 2–3 builders, but building capacity does not establish eligibility or registration. | **Not verified.** Team leader must verify each member, student status and final registered roster. |
| Required folder name `Team Name_College Name` | Current local folder is `24. ai healthcare project`. | **Not done.** Use the exact verified team/college names in the submission package. A cosmetic placeholder is not compliance. |
| Public GitHub repository and accessible files/links | Working local repository/source exists; no public URL established in this audit. | **Not done/verified.** Publish a reviewed release only with user authorization, then test access in a signed-out browser. |
| Open-source license details | `LICENSE` and README identify MIT for authored code; HEMOBP retains CC BY 4.0. | Implemented locally. Preserve notices and dataset attribution in the public release. MIT does not relicense dependencies or data. |
| Architecture diagram in PDF/PPT | README contains an architecture Mermaid diagram. | **Required file artifact not established.** A Mermaid block alone does not satisfy PDF/PPT format. Export and inspect a readable architecture PDF/PPT, including separate synthetic and observed-data paths. |
| Project presentation in PDF/PPT | Documentation describes implementation and outcomes. | **Required deck artifact not established.** Build the deck, render every page and verify graphs, citations, text and claimed metrics against the release. |
| Minimum 20-minute explanation/demo video | A demonstration walkthrough exists in `docs/demo-walkthrough.md`; no recorded video verified. | **Not done.** Record at least 20 minutes, verify actual duration/audio/legibility, and test the final accessible link or file. Storyboard below totals 20:00; allow recording margin. |
| Submit only leader name, phone, email and public repository URL on platform | No platform submission demonstrated. | **Not done.** Leader performs/authorizes the external submission using verified contact details. Do not place private contact information into product UI. |
| Finalist presentations, travel for two members, summit showcase | No finalist status or organizer invitation established. | **Conditional future organizer process.** Do not imply selection, sponsored travel confirmation or awards. |

This mapping supports a strong PoC, but it does not support saying “100% of submission requirements completed.” Administrative verification, required media/file artifacts, public release and platform submission remain separate deliverables until verified.

## Evidence already obtained

### Functional and model evidence

The existing model and mechanism test files currently contain 23 test cases covering conservation/nonnegative fluid compartments, cutoff isolation, historical-prior influence, same-state scenario starts, stale/current-event/session-end states, mechanism disagreement, observation value versus information gain, noise/burden sensitivity, delayed acquisition, idempotency, contradiction downgrade, patient isolation, immutable reports and revision checks. The audit reran `python -m unittest discover -s tests -v`: all 23 passed, including the newly added between-cuff pressure-origin and original-workspace current-event regressions. These tests establish selected software properties under authored fixtures. They do not validate equations, clinical utility or model calibration.

Browser scripts separately cover the workspace, low-BP alert states and mechanism workflow. Each release should record the exact command result and commit; a count of passing tests without an executable report is not clinical evidence. Rebuild and rerun the affected scripts after the landing-page/UI changes. Check keyboard access, mobile layouts, loading/error states, and the first-time visitor's path to a meaningful example.

### Observed-data baseline, distinct from the physiological twin

`docs/observed-baseline.json` records HEMOBP v3, a Taiwan retrospective dataset: 4,366,298 input machine packets, 1,506,275 distinct BP rows, 462,000 eligible windows and 77,138 test windows from 211 held-out patients. Recorded patient overlap between train and test is zero. Training regressors use a sampled 100,000-row training set from 815 patients. Event-classifier threshold selection uses a separate patient-disjoint validation subset (163 patients versus 652 classifier-fit patients).

| Recorded observed baseline | Result | Defensible interpretation |
|---|---:|---|
| Last observed BP regression MAE | 11.336 mmHg | A persistence comparison for the next distinct reading. |
| Dynamic-only regression MAE | 10.697 mmHg | Lower point-estimate error on this split than persistence. |
| Historical/demographic + dynamic regression MAE | 10.679 mmHg | Only 0.018 mmHg lower than dynamic-only; incremental value is not established without patient-level uncertainty and further cohorts. |
| Event sensitivity / PPV | 0.753 / 0.127 | High false-alert burden remains a material limitation; not a clinical performance endorsement. |
| Event PR-AUC | 0.197 | Must be interpreted against event prevalence and alternative baselines. |
| False-positive / positive test windows | 11,497 / 2,212 | Windows are not independent adverse events or consolidated notifications. |

The observed target is **next distinct measured SBP ≤90 mmHg with current SBP >90 and a 5–35-minute next-reading gap**. Its median test gap is 19.97 minutes. This is not the exact same endpoint as detecting any new low BP in a continuous 30-minute horizon. It is also not the synthetic twin's five-minute cuff schedule. A single “accuracy” number must not combine these tasks.

The script excludes post-session weight and later machine changes from predictor inputs, validates downloaded checksums, and uses the first packet in which a repeated BP measurement appears. Episode boundaries are inferred from timestamp gaps and elapsed-time resets; `d1.csv` is downloaded but not yet used to independently audit these boundaries. Source ultrafiltration values remain in source units and must be reconciled before use in the physiological equations. Measurement frequency may depend on clinical concern. No Indian-population transportability, prospective calibration or clinical alert workload has been demonstrated. The trained observed baseline is not driving the synthetic physiological interface.

### Independent synthetic policy challenge: retain the negative result

`backend/challenges.py` and `docs/originality-challenges.json` retain 108 additive-response cases: 36 shared-past histories × three hidden response types, scored over eight constant-rate profiles. The scoring future is not generated with the twin's two-compartment pressure equation. All three policies see the same history, have at most one immediate observation, and receive the same pre-generated channel value when selecting that channel. There are 324 retained policy records.

| Policy | Mean independent decision regret, lower is better | Exact best-profile match | Acquisitions | Cases worse than cuff |
|---|---:|---:|---:|---:|
| Fixed cuff BP | 0.2655 | 0.009 | 108/108 | 0 |
| Family information gain | 0.2290 | 0.250 | 108/108 | 8 |
| Decision value minus burden | 0.2656 | 0.250 | 96/108 | 8 |

**Decision-value selection does not improve mean decision regret over the cuff baseline in this suite.** The near-equal rounded result is not evidence of equivalence. More exact best-profile matches coexist with worse errors on other cases, so exact-match accuracy alone would be misleading. Information gain has a better point estimate in this suite, at higher mean acquisition burden; that is a synthetic result under authored distributions, not proof of clinical superiority.

The challenge sensor assumptions differ from the model: RBV fixture noise is 1.3 percentage points versus model SD 1.0; cardiac-output fixture noise is 0.38 L/min versus model SD 0.30. The response curves, sensor-family mapping, loss and distributions are authored. These shifts are useful stressors but require explicit reporting. The suite evaluates immediate acquisition only. It is not a benchmark of delayed observation, adaptive multistep monitoring, drift recovery or long-term outcomes. Do not tune on these 108 cases and then rename them held-out validation.

## Priority research and execution gaps

| Priority | Gap | Next concrete experiment or deliverable | Completion evidence |
|---|---|---|---|
| Resolved during audit | Timestamp semantics between cuff readings | `infer()` previously advanced volume to the replay cutoff while anchoring pressure to an older cuff as though current. The implementation now propagates the pressure anchor using fitted volume/drift changes over the observation age. | Source inspected; `test_pressure_origin_advances_between_cuff_readings` passes. This is a timestamp consistency correction, not validation of the drift equation. |
| Resolved and browser-verified | Different current-low-BP behavior across views | Patient twin `/scenario` and `/branches` reject `current_event`, matching Mechanism lab. Frontend controls and comparison output agree with that contract. | `test_original_workspace_withholds_current_event_scenarios` passes. The browser regression at Meera minute120 confirms disabled controls and absent alternative comparison output. |
| Resolved in UI and guide | Historical-memory provenance wording | Displayed session summaries illustrate an authored EHR prior; they do not estimate it. The UI and research guide describe this direction explicitly. | EHR schema and explanation agree with the actual dataflow; no claim of learned memory from illustrative summaries. |
| P0 | Submission artifact and identity gaps | Verify roster; produce architecture/deck/video; review public release; signed-out link check; leader submits. | Actual files, measured video duration, repository URL and submission receipt. |
| P1 | HEMOBP episode and unit audit | Reconcile representative and edge-case machine episodes with `d1.csv`/source documentation. Audit midnight sessions, resets, measurement IDs, timestamps, units and joins. | Reproducible audit table with mismatch counts, adjudication rules and unresolved records. |
| P1 | Informative sampling and endpoint mismatch | Define a scheduled-reading cohort and all-reading cohort; compare results. Report exact horizon/gap distributions and missing follow-up. | Cohort flowchart, counts and sensitivity analysis. No claim of continuous-event detection from sparse cuffs. |
| P1 | Incremental EHR value and uncertainty | Freeze patient splits; repeat with patient-level bootstrapped confidence intervals for paired MAE and event metrics. Compare demographics/history additions against dynamic-only and persistence using identical rows. | Patient-clustered intervals, subgroup counts and raw split manifests; no significance from treating overlapping windows as independent. |
| P1 | False alerts and score calibration | Consolidate windows into predeclared event episodes/refractory periods; evaluate alerts per patient-hour/session, lead time, sensitivity/PPV and calibration on a separate split. | Reliability plot, Brier/log loss where appropriate, event-level workload, threshold locked before test. |
| P1 | Negative decision-value result | Preserve current challenge suite as a diagnostic set. Analyze per-case excess regret, model misspecification, sensor noise, discretization and burden effects. Create fresh development and untouched evaluation families/seeds. | Paired regret deltas with cluster intervals, tail/harm counts, acquisition costs and all abstentions; no selective best-case demo used as aggregate evidence. |
| P1 | Authored sensor/physiology proxies | Test identifiable versus nonidentifiable parameter regions; expand to omitted mechanisms and contradictory observations. Obtain matched BP/RBV/output observations before fitting these observation maps to actual physiology. | Parameter/forecast coverage, residuals, family calibration within a known simulator and explicit unidentifiable cases. Clinical family labels remain hypotheses. |
| P2 | Three-node quadrature approximation | Compare expected loss reduction against high-node quadrature or a seeded large Monte Carlo reference; examine threshold discontinuities and ranking stability. | Absolute numerical error and candidate-rank stability across noise, cutoff and loss settings. |
| P2 | Measurement waiting and multistep value | Use separate simulator seeds with actual current-rate evolution during delay, event occurrence before result, missing/late results and repeated monitoring. Compare the full policy, not only posterior entropy. | Decision regret including delay consequences, missed-event counts, burden and time-to-resolution at matched budgets. |
| P2 | Contradiction and recovery | Evaluate the four-SD/all-family residual and RMSE rules under drift, artifact, valid extreme readings and omitted families. A downgrade is implemented; adaptive refitting/recovery is not. | False-downgrade rate, detection delay, unresolved duration, audit retention and explicit recovery procedure. |
| P2 | Support landscape and causal credibility | Evaluate the ±100 mL/h session-proximity heuristic as a heuristic, separately from model disagreement. Specify what actual treatment-response data and confounding controls would be needed for causal evaluation. | Distinct factual, support and causal statements. Input-range proximity never becomes a “safe” region. |
| P2 | Longitudinal carry-over | Keep current unfinished-target plus net-gain accounting. If extending to a true longitudinal twin, explicitly model interval, intake/output and intersession state uncertainty. | Conservation, independently scored multi-session outcomes and documented inputs; accounting alone is not longitudinal physiological validation. |
| P2 | End-to-end usability | Run scripted first-time visitor and clinician/expert walkthroughs: identify data provenance, uncertainty, current event, proposed measurement, assumptions and saved evidence. Record task success and misunderstandings. | Anonymized task outcomes and changes tied to failures; expert usability review does not become clinical validation. |

## A rigorous evaluation sequence

1. **Freeze definitions before fitting.** Publish exact event definitions, timestamp/availability conventions, eligible population, prediction times, exclusions, loss weights and permitted channels. Keep “new measured low BP,” “existing event,” and “unobserved continuous hypotension” distinct.
2. **Audit data before scoring.** Reconcile session identities and units. Keep patient-disjoint splits, record unique patient/episode counts and retain a split manifest. Protect against future treatment, post-session outcome and carried-forward reading leakage.
3. **Establish factual prediction comparisons.** Persistence, simple trend, dynamic-only, EHR-plus-dynamic, and the physiological model should use identical tasks and windows when compared. Do not compare their metrics directly when endpoints differ. Repeat ablations with intervals clustered by patient.
4. **Measure whether uncertainty is honest.** Assess forecast-range coverage/width and calibration separately from error. Include missingness, artifacts, omitted mechanisms and shifted priors. Check false certainty: a confident wrong scenario ranking is different from an unresolved result.
5. **Assess observation policies on untouched synthetic futures.** Predeclare the action grid, observation budgets, allowed wait times, burdens and loss. Include BP-only, fixed schedule where delayed evaluation exists, information gain, decision value, no-observation, and oracle references. Score mean/tail regret, harm relative to baseline, burden, unresolved fraction and delay. Retain all acquisitions, failures and unavailable channels.
6. **Validate the clinician-facing explanation.** A person should understand what is measured, estimated, assumed and unavailable. Ask them to trace one saved result back to its cutoff, priors, model version and observations without investigator assistance.
7. **Gate stronger claims.** Only an independently validated factual predictor supports a factual accuracy claim. Paired or causally justified treatment-response evidence is needed for scenario-effect claims. Prospective clinical benefit requires a separate reviewed clinical study. No amount of polished UI or synthetic challenge performance bypasses these gates.

Useful next research outputs are an endpoint/data dictionary, reproducible cohort audit, frozen evaluation protocol, complete result tables with uncertainty, a failure analysis and a release evidence bundle. The strongest near-term narrative is transparent progress with testable limits, rather than an unsupported promise to outperform every existing dialysis system.

## Twenty-minute explanation and demo storyboard

The timed content below totals exactly **20:00**. Record a little longer so editing does not put the submitted video below the minimum. Use the release build, readable browser zoom and a clean synthetic workspace. Maintain an offline screenshot backup for each live scene. State the current limitations in the spoken narrative, not only tiny slide footnotes.

| Time | Duration | Scene / section | What to explain and demonstrate |
|---|---:|---|---|
| 00:00–01:00 | 1:00 | Opening and use case | “One dialysis patient, one localized future event.” Explain proactive observation and the problem of a plausible-looking but underdetermined scenario. Identify RENALIS as a research prototype. |
| 01:00–02:20 | 1:20 | Clinical workflow and Indian relevance | Explain the maintenance-dialysis context, the selected BP endpoint and competing immediate/fluid-removal objectives. Cite verified relevance; do not infer Indian model performance from Taiwan data. |
| 02:20–03:30 | 1:10 | Hackathon scope and data provenance | Show historical EHR and medical-device replay as two streams entering the algorithm. Distinguish fictional demo patients from the separate anonymized HEMOBP benchmark. |
| 03:30–05:00 | 1:30 | Architecture | Show the architecture file: availability checks → estimator → forecast/uncertainty → UI/persistence. Place acquisition and future reveal outside inference; place the observed-data pipeline on its own branch. |
| 05:00–06:40 | 1:40 | What personalization actually does | Show authored historical priors, available BP and current machine input. Explain particle updates and conservative fluid movement in plain language. State which displayed fields are not model inputs. |
| 06:40–08:10 | 1:30 | Live Patient twin | Open Meera at minute90, inspect measured versus estimated data, 30-minute conditional range and threshold-crossing fraction. Explain that a model fraction is not a calibrated clinical probability. |
| 08:10–09:30 | 1:20 | Alternative profiles | Compare a slower profile from the same starting state. Show BP and fluid-removal tradeoff, save a branch. State that an unchosen treatment outcome is simulated, not observed. |
| 09:30–12:10 | 2:40 | Competing explanations | Open Mechanism lab at the same cutoff. Show close factual fits but divergent scenario effects across volume, vascular and cardiac hypotheses. Explain compatibility weights and the unresolved comparison. Do not identify a clinical diagnosis. |
| 12:10–13:40 | 1:30 | Which measurement helps? | Compare decision value with information gain, channel availability, noise, burden and timing. Acquire the explicitly synthetic observation. Show changed weights and whether disagreement actually remains. Do not promise that every measurement resolves it. |
| 13:40–14:40 | 1:00 | Honest failure and abstention | Show unavailable channels or all-family contradiction. Show current low BP and stale-data states. Explain why these do not become advance warnings or invented monitoring recommendations. |
| 14:40–15:40 | 1:00 | Audit and explanation | Open the saved report, evidence lineage, assumptions, revision and export. Explain archived resets versus immutable saved snapshots. Point to the model card. |
| 15:40–17:00 | 1:20 | Observed evidence | Present patient-disjoint HEMOBP counts, MAEs and event metrics. Mention the small 0.018 mmHg EHR addition and substantial false-positive workload; explain next-distinct-reading endpoint and lack of Indian validation. |
| 17:00–18:00 | 1:00 | Independent challenge outcome | Show all three policy regret results. Explicitly say decision-value selection has not beaten cuff-only mean regret. Explain why family identification and better decisions are different questions. |
| 18:00–19:00 | 1:00 | Validation and research plan | Show the prioritized audit, calibration, independent-policy and usability work. Distinguish software safeguards from clinically validated thresholds. Identify what evidence would change the current conclusion. |
| 19:00–20:00 | 1:00 | Contribution and final demonstration | Return to the core workflow: retain plausible explanations → expose divergent futures → ask what observation helps → preserve uncertainty when needed. Give the verified repository/run instructions and bounded originality claim. |

## Release and submission evidence checklist

- Tag a reproducible code release and record model/report versions, dependency locks, run commands and test outputs.
- Review every product and presentation claim against the model card; make synthetic, observed retrospective, authored assumption and future plan visually distinct.
- Include the architecture and presentation in the organizer-required PDF/PPT format, inspect their rendered pages, and verify that all linked evidence is accessible.
- Verify team and college/incubator details, student eligibility and the exact required folder name with the team leader.
- Record and inspect at least 20 minutes of explanation/demo with audible narration and readable screenshots; verify duration and final link access.
- With explicit publication/submission authorization, publish the repository and media, test access signed out, then retain the platform receipt. Local completion is not public submission.

## Artifacts used in this audit

- Supplied organizer brief at the attachment path above.
- `backend/model.py`, `backend/mechanisms.py`, `backend/challenges.py`, `backend/measurement_fixtures.py`, and `backend/app.py`.
- `scripts/hemo.py`, `docs/observed-baseline.json`, `docs/originality-challenges.json`, `tests/test_model.py`, and `tests/test_mechanisms.py`.
- `README.md`, `docs/model-card.md`, `docs/originality.md`, and `docs/demo-walkthrough.md`.

Literature links and novelty context remain in `docs/originality.md`; this audit does not upgrade that focused prior-art search into a systematic review or a claim that the integration does not exist elsewhere.

## Product experience delivered in v0.3

The default landing page, read-only computed hero, six-step walkthrough, reloadable workspace URLs, research guide, 11-source search/filter library, live result reports, architecture SVG, and allowlisted document resources are implemented. Browser checks cover navigation/back/reload, document links, failure and retry states, non-mutating guidance, and reflow at 1440, 1024, 768, 390, and 320 pixels. These product checks do not establish clinical usability or research superiority.
