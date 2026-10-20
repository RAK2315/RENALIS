# Release 0.4: implementation decisions and reasons

18 October 2026. These decisions implement the research dossier while retaining its evidence boundaries.

## One connected investigation

The preferred entry is the Evidence journey. A shared patient, cutoff and resource configuration controls history, model state, hypotheses, predicted observations, acquisition and review. The request key guards asynchronous responses against patient/clock/configuration changes. Loading and network errors disable mutations. The detailed patient twin and mechanism views remain available for deeper inspection.

This addresses the earlier fragmented demonstration: a viewer can now follow what the model knows, what it assumes, what could change its mind and what actually changed. The guided tour follows the same workflow at minute80. It does not mutate evidence by navigation.

## Learning consumes raw preceding sessions

An authored per-patient refill value cannot demonstrate historical learning. The learner instead fits raw BP trajectories from completed preceding sessions using machine settings and declared physiology, then shrinks the fitted estimate toward a population reference. A history digest and session fit errors expose provenance. An uncertainty floor limits false precision from six synthetic sessions. A four-session/two-later-session ablation provides a forward check.

This verifies a genuine software learning path, not identifiable physiology. Generator and learner share structure. Paired clinical measurements and stronger independent response models remain necessary. `backend/history.py`, `history_fixtures.py` and leakage/mutation tests make that distinction reproducible.

## Four hypotheses, with an explicit failure state

A fourth mixed-response family reduces the forced choice among three single-axis explanations. Each family retains48 particles so comparison resolution remains consistent. Compatibility weights describe the declared bank. They cannot establish a clinical diagnosis, and a mixed hypothesis does not guarantee model completeness.

Unknown physiology is handled through unresolved support and contradiction downgrade rather than an invented universal unknown-model likelihood. The residual threshold is an authored heuristic requiring validation. The UI retains model uncertainty and withholds scenario authority when observations contradict the whole bank.

## Observation value compares complete policies

Let `L(a, theta)` be the declared research loss for a profile. The immediate baseline is `min_a E[L(a, theta)]`. A successful acquisition chooses a later profile conditional on its result. A failed acquisition uses the waiting posterior without new information. Expected acquisition loss is the success-weighted expected minimum posterior loss plus failure-weighted best waiting loss. Decision value subtracts that acquisition loss from the best immediate loss. Net value then subtracts declared burden and a separate delay penalty.

This prevents waiting from being treated as free and preserves negative value. Current removal continues before the result arrives. Information gain remains a separate objective because discriminating models may fail to improve the actual comparison. Nine-node Gaussian quadrature replaces the earlier coarse default; a finer reference diagnostic and isolated waiting/failure regressions check the arithmetic. No claimed global numerical bound follows from one diagnostic case.

The declared loss and acquisition costs are research utilities. They need clinical elicitation and sensitivity analysis before any real decision claim. A lack of positive net value is an allowed abstention.

## Measurement previews use the same assumptions

Ranges integrate particle variation and the selected sensor noise. The observation equation uses the selected measurement time, and hypothetical result updates start from the already assimilated posterior. Three possible values show how support and preferred profiles could change before acquiring anything. Previews never write observations or access the hidden acquisition fixture.

Overlap is useful evidence: it shows why a channel may remain inconclusive. The displayed10th-90th ranges are conditional authored predictive distributions, not clinical device intervals. The server enforces equipment availability even if a caller bypasses frontend controls.

## Observation time, availability time and correction time

A delayed release must not move the measurement itself into the future. Assimilation evaluates its observation equation at `observed_minute` and gates access by `available_minute`. Requests have separate success/failure, burden and activity records. Artifact observations remain auditable but excluded from inference.

Corrections append a new value with a reason and `supersedes` link. Earlier cutoffs retain the earlier value until the correction is available. Archive removes evidence from the active experiment without rewriting saved reports. Revision checks bind current evidence and acquisition lineage to immutable comparisons. Schema initialization is serialized because concurrent first-load requests exposed a migration race.

## The observed cohort is a new protocol

The earlier inferred-session cohort remains historical. The new pipeline uses session records, reconciles time-only fields, checks elapsed consistency, canonicalizes published UF units and derives features from preceding completed sessions. Current-session end summaries remain excluded. Patient-separated fit/calibration/test sets limit patient leakage.

The approximately eight-hour cross-table shift is an empirical alignment assumption. It is deliberately visible because source clock semantics have not been independently confirmed. Substantial exclusions can alter the population. The new cohort must not be compared directly with the older MAE as though only the model changed.

## Calibration, recurrence and workload stay distinct

The event task predicts the next distinct measured SBP<=90 after a currently non-low reading with a5-35-minute gap. It does not observe every continuous low-pressure episode. Calibration patients select thresholds and residual ranges. Test patients assess error, range coverage, PPV and sensitivity. Patient-block uncertainty accounts for within-patient clustering. Recurrence context and a30-minute refractory alarm consolidation expose additional workload structure.

The observed history increment is small and its statistical interval does not establish clinical importance. Low PPV, missed events and undercoverage remain visible. Prospective measurement schedules and external populations need separate evaluation.

## Independent policy failures remain published

The192-case authored holdout uses scoring futures independent of the twin pressure equation and includes mixed/omitted mechanisms, noise, equipment limits and failed/delayed acquisitions. Four policies share draws and a one-acquisition budget. All768 records are retained. Decision value does not beat fixed cuff overall, so no acceptance test demands that the preferred policy win.

A metric audit extended the oracle grid to permitted waiting-prefix profiles. The initial output remains available and no policy changed. Physiological regret and regret including burden/delay are reported separately. Confident-wrong counts are descriptive additions after first evaluation, not predeclared endpoints. The study is now a frozen diagnostic task. Future tuning requires a separately declared evaluation.

## Longitudinal transport remains conditional

The transport experiment starts from current evidence-weighted compartments, carries them through authored intake/output intervals and future sessions, and reports mass-balance error. Changing inputs or evidence invalidates previous results. Shared compartment equations and simplified residual-output mapping limit interpretation. It supplies no future BP, renal-function identification or prescribed target.

## Interoperability has a bounded claim

The FHIR R4 collection exports fictional Patient, Device and measured BP Observation resources. Reference integrity and UCUM/LOINC fields are tested. This demonstrates a concrete mapping that reviewers can inspect. It does not establish ABDM profile validation, certification, real EHR integration, authentication or deployment readiness.

## Submission completeness and clinical completeness

The local package contains the software, diagrams, presentation, model card, reproducible evaluations, study protocol, capture schema and a current demonstration. Actual entrant details, public links, anonymous access, eligibility verification and platform submission are external administrative steps. Clinical collaborators, governance, paired measurements, silent external validation and impact studies are external evidence steps. Inventing any of them would weaken the project and cannot complete the plan.

The strongest next scientific work is therefore specific: confirm source timing, reproduce the cohort independently, test users' interpretation, calibrate matched physiology and evaluate external workload before making treatment or patient-benefit claims.

## Sequential discrimination is a distinct objective (18 October)

After a CO observation of 3.74 L/min at Meera minute90, action-loss value can abstain even though volume and cardiac remain plausible. Adding an information objective addresses that gap without changing or relabeling the existing decision-value objective. `backend/discrimination.py` receives only the current particle posterior, feasible candidates and released acquisition ledger. It never reads a synthetic acquisition fixture.

Two families with at least10% support trigger pair-conditional entropy reduction; more than two use whole-bank entropy reduction. Remaining mass outside the leading pair stays visible. Gaussian quadrature integrates noisy future readings; failure retains current beliefs. The earliest feasible unacquired slot per channel competes. Selection requires more than0.005 expected bits; ties favor lower delay and cost. Burden stays in its declared action-loss units and is not subtracted from information bits. A nonzero information score does not justify a clinically burdensome measurement.

The panel displays family-specific noisy predictive ranges, three computed outcome previews with full-bank posterior weights, expected pair classification error and modeled probability of reaching80% pair support. Neither metric is clinical diagnostic accuracy. The actual next result is acquired from the existing device boundary and may remain ambiguous: synthetic RBV85.0 shifts Meera support to66.9% volume and31.8% cardiac. Planning then repeats from that posterior. Repeated readings currently assume conditionally independent noise, without device bias or physiological process-noise validation.

Equipment, timing/event guards, failed idempotent requests and already acquired slots constrain selection. No positive score, insufficient remaining hypotheses or a withheld authority state stops the selector. This experimental selector has its own version and is included in investigation exports and immutable snapshots. The frozen one-acquisition policy holdout is unchanged and supplies no evidence for sequential-policy effectiveness. A future independent multi-acquisition evaluation must predeclare budgets, correlated noise, abstention and calibration endpoints.
