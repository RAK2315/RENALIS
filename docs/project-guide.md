> Historical snapshot of the earlier release. Current implementation, artifacts, evaluations and unresolved gates are in [release 0.4](release-v04.md) and [README](../README.md). Earlier counts and results remain for provenance.

# RENALIS — project guide

Updated 16 October 2026. Local research prototype. This guide explains the product, the evidence, the implementation, and the remaining work from first visit through validation.

## 1. The project in one sentence

RENALIS is a focused dialysis digital twin that forecasts a localized low-BP outcome, preserves competing physiological explanations, and calculates which available research measurement could improve a scenario comparison.

The intended demonstration user is a clinician or researcher inspecting evidence. The project does not diagnose a patient's true mechanism, prescribe removal settings, connect to a live dialysis machine, or establish clinical benefit.

## 2. Why this problem

For patients with chronic kidney disease requiring maintenance hemodialysis, pressure and fluid management involve competing considerations. A BP trajectory alone can leave several explanations compatible with the observations. The clinical rationale and the limitations of that inference are documented in the [primary-source review](research-review-2026-10.md).

The precise research question is: **when plausible explanations disagree about a hypothetical removal profile, which feasible observation could improve that comparison?** Information gain, decision quality, and patient benefit are separate outcomes.

## 3. The complete visitor journey

1. **Landing page (`/`).** Understand the condition, localized outcome, two data streams, and uncertainty question. The interactive graph is a read-only computed synthetic example, independent of acquired workspace evidence.
2. **Guided workspace (`/workspace?tour=1`).** Follow six steps: patient state, competing explanations, useful measurements, assumption contradiction, independent challenges, and evidence review. The guide highlights the relevant area and explains what to observe. It does not acquire measurements or erase experiments automatically.
3. **Patient twin.** Inspect available data, estimated fluid compartments, current-event versus future-warning status, hypothetical profiles, outcome reveal, and review records.
4. **Mechanism lab.** Compare three compatible response families, inspect measurement values and timing, acquire a labeled synthetic or manual research observation, and inspect how support changes. Unresolved or contradicted results remain valid outputs.
5. **Research guide (`/research`).** Read the architecture, actual retrospective and synthetic results, originality boundary, next validation gates, searchable sources, and downloadable resources.
6. **Audit and reproducibility.** Export live evidence or an immutable saved report. Reset archives observations; it does not modify existing reports. Source, dependency locks, tests, and evaluation JSON remain in the repository.

## 4. Historical + dynamic fusion

The historical synthetic EHR supplies baseline pressure, reference volume, target fluid, and an authored refill prior. The visible previous-session summaries illustrate this authored history; the estimator does not learn that prior from the displayed summaries.

Valid BP observations update the model. Available machine settings drive one-minute conservative fluid transitions. Future BP, later setting changes, and session-end information cannot be used at an earlier cutoff. Demographics and auxiliary machine fields may be displayed without being claimed as model inputs.

The original Patient twin uses 192 parameter particles in a fluid model. The separate Mechanism lab uses 48 compatibility particles per family. Between cuff readings, modeled pressure propagates from the actual measurement timestamp to the cutoff; a replay tick is not a fresh measurement.

## 5. Rival explanations and evidence value

- **Volume/refill limitation:** pressure is sensitive to circulating-volume loss under the modeled refill constraints.
- **Vascular compensation limitation:** a fitted pressure factor allows a resistance-related explanation despite more preserved modeled volume.
- **Cardiac response limitation:** a fitted output/response factor can explain pressure decline under different volume sensitivity.

These families use authored proxy equations. They can coexist in real physiology and may omit the actual cause. Their weights are relative compatibility within the chosen model set, not diagnosis probabilities.

Candidate channels are repeat cuff BP, relative blood volume, and noninvasive cardiac output. At permissible now/+5/+10-minute times, the engine integrates possible observations and estimates reduction in the best expected scenario loss. It separately reports family information gain. Net value subtracts declared burden and waiting cost. A delayed action retains current removal until its observation arrives. Selection cannot access the synthetic device's hidden value.

Noise SD and loss weights are inspectable authored assumptions. If no channel is available or sufficiently valuable, the lab can retain an unresolved result without requesting a measurement. A strongly incompatible observation downgrades all model families rather than forcing a diagnosis.

## 6. The research endpoint and guards

The nominal endpoint is a new systolic BP **≤90 mmHg** in the next 30 minutes, shortened at session end. This differs from studies using `<90` and does not define every symptomatic intradialytic hypotension event.

Already-low BP is a current event, not an advance warning. Original workspace comparisons and lab experiments are withheld during an existing low-BP event. Stale observations and session completion also withhold comparisons. The lab additionally checks model contradiction. Particle fractions and bands are conditional model quantities, not calibrated clinical probabilities or intervals.

## 7. Three distinct evidence lanes

| Experiment | Actual result and interpretation |
|---|---|
| Four-patient synthetic twin | Demonstrates the working pipeline and guards. Shared generator/estimator structure limits accuracy claims. |
| Separate observed HEMOBP baseline | 77,138 held-out windows from 211 patients, zero patient overlap. MAE: persistence 11.336, dynamic 10.697, fused 10.679 mmHg. The incremental historical benefit is small; no significance interval is reported. Event sensitivity 75.3%, PPV 12.7%, and 11,497 false-positive windows reveal substantial burden. |
| Independent observation-policy challenges | 108 authored cases using additive future equations separate from the twin. Mean regret: cuff 0.2655; information gain 0.2290; decision value minus burden 0.2656. Both adaptive policies worsen eight cases relative to cuff. Decision-value superiority is not established. |

HEMOBP records are not independent cuff readings. Measurement timing can reflect clinical concern. The source dataset does not validate the lab's relative-volume/output equations or alternative treatments. Neither retrospective next-reading metrics nor synthetic decision regret establish patient benefit.

## 8. What is original—and what is established

Dialysis prediction, digital-twin integration, hemodynamic mechanism distinctions, optimal sampling, and measurement-guided removal frameworks already exist. RENALIS investigates their connection in an inspectable workflow: retain rival explanations, expose scenario disagreement, estimate useful next evidence, update support, and preserve unresolved or contradicted states.

A focused review supports an integration research question; it does not prove global priority or patentability. The September 2026 physiological ultrasound proposal and earlier full digital-twin integration papers further constrain any “first” claim. Read the source library and [originality report](originality.md).

## 9. Implementation and reproduction

Frontend: React, TypeScript, Vite, Lucide, and Recharts. Backend: FastAPI, NumPy, SQLite. Separate observed-data processing: pandas and scikit-learn. The product entry and research guide load separately from the workspace; the introduction's computed example is read-only.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
npm run build
& .\.venv\Scripts\python.exe -m backend.challenges
```

Playwright browser checks cover the original workspace, the low-BP regression, mechanism acquisition/audit flows, and the complete landing/research/guided journey. See README for the runtime/module-path setup. Dependency locks are retained; data and local SQLite records stay outside Git.

## 10. Next research and release gates

First reconcile observed units, episode boundaries, repeated measurements, and temporal availability independently. Freeze new out-of-family simulator holdouts before adjusting the policy. Add patient/session uncertainty, calibration, event-level alarm accounting, and sensitivity to noise, priors, and loss assumptions. Evaluate physiological identifiability with paired measurements and test whether users interpret uncertainty correctly. Clinical treatment-effect and outcome claims require separate appropriate prospective and causal study designs.

The [execution plan](execution-and-validation-plan.md) maps every supplied hackathon requirement to actual evidence and includes a timed 20-minute storyboard. Team/college identity and eligibility, the required folder name, public repository, required PDF/PPT artifacts, recorded video, and platform submission are separate deliverables until verified. This guide does not assert their completion.

## 11. Licensing and data scope

Authored code is MIT. The HEMOBP v3 source retains CC BY 4.0 and its attribution. Dependencies retain their own licenses. Built-in patient and device examples are synthetic. No real patient upload or clinical deployment is part of this release.
