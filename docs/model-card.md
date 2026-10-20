# RENALIS model card 0.4

18 October 2026. Patient twin `history-informed-particle-twin/0.4`; mechanism engine `evidence-aware-mechanisms/0.4`. Local research prototype. The earlier card is retained in `model-card-v 03.md`.

## Scope and data

Maintenance-hemodialysis research review. Built-in patients, prior-session histories, BP streams and device acquisitions are fictional. A separate HEMOBP retrospective pipeline produces observed-data aggregate results. Its trained models do not drive the synthetic physiological workspace. No clinical deployment, diagnosis, causal treatment effect or prospective patient benefit is claimed.

The sandbox predicts a new model SBP <=90 mmHg over up to 30 minutes. Current low BP is an existing event. Stale BP, completed sessions and whole-bank contradiction withhold scenario authority. The observed task is different: next distinct measured SBP <=90 with current BP >90 and a 5-35-minute measurement gap. Symptoms, clinical responses and continuous-event outcomes are not captured by that numeric endpoint.

## History learner

Six preceding raw synthetic sessions supply BP trajectories and available removal settings. A grid likelihood fits refill and compensation using the declared fluid/pressure equations. Estimates shrink toward a population reference, preserve an uncertainty floor and carry a history digest. Current and future-available sessions are excluded. A four-session fit/two-later-session ablation is exposed. Generator and learner share model structure, so apparent synthetic performance can be optimistic. Conditional parameter fitting does not establish physiological identifiability.

## State and competing mechanisms

The patient estimator and mechanism bank remain distinct engines. The Evidence journey consistently uses the mechanism bank for its state, measurement previews and comparison. Four authored volume/refill, vascular, cardiac and mixed-response families retain 48 particles each. Conservative two-compartment fluid transitions consume available machine settings. Local response equations permit comparable factual BP fits with different hypothetical responses.

Family support expresses compatibility within this chosen bank. It is not a clinical diagnostic probability. The mixed family cannot guarantee model completeness. Particle percentiles and threshold-crossing fractions are not calibrated real-world probabilities or confidence intervals. Measured synthetic settings, inferred compartment states and authored sensor proxies are labeled separately.

## Observation value and previews

Cuff BP, relative blood volume and cardiac output use authored observation equations. Base noise SDs are 3.5 mmHg,1 percentage point and 0.30 L/min, multiplied by the selected research setting. These are not verified device specifications. Predictive 10 th-90 th ranges and three hypothetical outcomes use selected observation time and noise. Possible-result previews update the existing posterior hypothetically and never create acquired evidence.

Nine-node Gaussian quadrature integrates candidate observations. Whole-policy value compares the best immediate profile against waiting, acquisition success/failure and a later profile. Waiting trajectories retain current removal until the observation time. Failed acquisition has no information and retains cost. Negative value remains visible. Information gain, expected decision-loss reduction and burden are separate quantities. Declared loss weights, acquisition costs, delay penalty and failure/noise values are research assumptions, not measured clinical utilities. One diagnostic comparison against 41 nodes is reported; it is not an exhaustive numerical error bound.

## Evidence and authority

Server-side validation enforces equipment, channel/value ranges, cutoff, timing and quality. Observation time and release time differ. Only released valid observations enter assimilation. Failed requests and artifacts remain in the ledger. Corrections append a new record at correction release time and retain original evidence for earlier cutoffs. Archive resets active experiments without rewriting saved reports. Saved comparisons retain settings, evidence IDs, acquisition IDs and a revision hash. Concurrent SQLite schema initialization is serialized.

An acquired observation more than four assumed noise SDs from every particle, or a minimum family factual-fit RMSE above 8 mmHg, downgrades authority. This heuristic is not validated drift detection. Comparisons and experiments stop for current low BP, stale observations, completion or contradiction. Review notes and exports document research reasoning without issuing machine commands.

## Observed retrospective evaluation

`scripts/evaluate_observed_v 04.py` verifies deposit checksums, joins session intervals, canonicalizes source UF fromL/h tomL/h, deduplicates first-available BP packets, excludes current-session end fields and derives aggregates only from earlier completed sessions. Fit 563, calibration 141 and test 176 patients are disjoint. Test includes 61,947 windows and 18,420 sessions.

An empirical eight-hour table shift and elapsed-discrepancy filter match 2,516,989 of 4,366,298 packets. Source clock semantics still need independent confirmation. The substantial exclusions and concern-dependent measurement schedule may bias results. MAE is 12.194 persistence,11.356 dynamic,11.328 demographics+dynamic and 11.161 preceding sessions+dynamic. Paired history increment is-0.1665 mmHg, patient-cluster 95% interval[-0.2298,-0.1099]. This is small retrospective information under the protocol, not demonstrated clinical usefulness.

Event sensitivity 0.6125, PPV 0.1351 and empirical nominal 90% range coverage 0.8674 retain workload and undercoverage limitations. Calibration bins, recurrence context and 30-minute refractory alarm consolidation are reported in `observed-v 04.json`. They do not establish prospective workload or continuous-event performance. Earlier v 0.3 results use a different cohort and remain separate.

## Independent policy evaluation

The frozen 192-case study includes eight authored regimes: volume, vascular, cardiac, mixed, omitted mechanism, noise, basic equipment and delayed/failing acquisition. Four policies share observations, availability and an at-most-one-acquisition budget. Independent additive scoring futures differ from the twin's pressure equations. All 768 policy records remain in `policy-validation-v 04.json`.

Mean regret is 0.23078 no observation,0.22170 cuff,0.24472 information and 0.24145 decision value. Decision value minus cuff is+0.01975, paired seed-block interval[-0.00981,0.05996]. Overall superiority is not demonstrated. Decision value is worse than cuff in 51 cases. The oracle-grid metric correction includes allowed waiting-prefix profiles, preserves the initial report and changes no policy. Confident-wrong counts were added descriptively after first evaluation. The original 108-case negative study remains unchanged. Future tuning needs a separately declared evaluation.

## Extensions and next evidence

**Sequential discrimination extension (`sequential-discrimination/0.1`, 18 October).** The Evidence journey now computes the next measurement from the posterior after every released reading. With exactly two families retaining at least10% support, it ranks expected pair-conditional entropy reduction; with more families it ranks whole-bank entropy reduction. It considers the earliest feasible slot per available channel, selected sensor noise and acquisition failure, with a0.005-bit information floor. Full-bank posterior previews and mass outside the pair remain visible. Costs and action-loss value are shown separately. There is no access to future fixture values during selection.

After synthetic CO3.74 at Meera minute90, the selected next discriminator is RBV. Actual synthetic RBV85.0 shifts support to66.9% volume and31.8% cardiac, retaining uncertainty. The displayed pair classification error and80% support probability are model-conditional quantities, not calibrated diagnostic performance. Repeat readings assume independent sensor noise. This extension is covered by sequential acquisition, preview-consistency, quadrature, noise/failure/equipment, feasibility, immutable-export and browser tests; it has no independent policy or clinical validation. The frozen holdout above evaluated different, one-acquisition policies.

Conditional longitudinal transport propagates current evidence-weighted fluid compartments through authored intake/output intervals and future removal sessions, checking conservation. It predicts neither future BP nor a prescribed target. Shared equations and simplified tissue-compartment residual output are unvalidated.

The FHIR R 4 collection contains fictional Patient, Device and measured BP Observation resources with internal references, LOINC 8480-6 and UCUMmm[Hg]. It is an example, not ABDM profile validation or certification. No real clinical integration or authentication is claimed.

Next gates are independent clock/cohort confirmation, expert task study, paired physiological calibration, approved silent external validation, workload assessment and later prospective impact evaluation. Study protocol and schema are prepared. No recruited experts, approved institution, Indian-population validation or measured patient outcomes are implied.
