# Proposed clinical and human-factors protocol

Status: design only, 17 October 2026. No participants enrolled and no expert endorsement obtained.

## Intended workflow and discovery

Interview intended clinical/research users about what they need to compare, where uncertainty changes their review, what observations are actually available, who acquires them, and how long acquisition takes. Record disagreements and cases where the feature would not be useful. Obtain permission before outreach. Do not recruit through automated messages without explicit authorization.

## Human-factors walkthrough

Present deterministic synthetic scenarios in varied order: same current BP with different prior sessions; close past fits and diverging scenarios; unavailable auxiliary hardware; failed or late acquisition; a current low-BP event; symptoms above the numeric research threshold; contradictory evidence; a stable session. Ask the participant to identify measured versus estimated versus hypothetical values, the cutoff and freshness, why a result is unresolved, and what changed after a measurement.

Predeclare success criteria and analysis before collecting responses. Capture task completion time, correct interpretation, errors, confidence and qualitative feedback. Compare versions only with a defined study design. Do not label an internal browser test as a clinical usability study. No fabricated participants, quotes or scores.

## Silent paired physiology study

Clinical collaborators and an institutional governance process must define eligible patients, consent/privacy processes, permitted devices and reference measurements, the numeric and symptomatic endpoints, scheduling, signal quality and adjudication. The experimental output remains hidden from care decisions in silent evaluation. Follow routine care and record actual actions; this is not a protocol to manipulate dialysis for information gain.

Capture patient/session pseudonyms; demographic and preceding-history availability; BP observed and available times; channel/device/method; readings and quality flags; machine settings with action time; symptoms; recorded clinician actions; measurement requests and failures; acquisition/operator time; amendments; and outcome ascertainment. Use the accompanying schema as an initial engineering contract, subject to clinical and information-governance review.

## Evaluation and progression

Design sample size around desired precision, event rates and repeated-session clustering. Separate first events from recurrence and distinguish sparse measured endpoints from continuous absence of an event. Freeze training, calibration and final test sets. Evaluate transport across sites/devices and prespecified patient groups, including missingness and acquisition failures. Calibrate observation maps against matched reference data rather than inheriting sandbox noise.

An impact study requires a new clinician-led design for the full workflow, agreed outcomes, bias/confounding handling and oversight. Factual prediction accuracy does not validate the alternate treatment response. Specify causal estimands, intervention versions, time-varying confounders and positivity where applicable. If assumptions are unsupported, retain scenario effects as research simulations.

Sources: TRIPOD+AI https://www.bmj.com/content/385/bmj-2023-078378 ; DECIDE-AI https://www.nature.com/articles/s41591-022-01772-9 ; KDIGO dialysis report https://kdigo.org/wp-content/uploads/2017/05/KDIGO-BP-Volume-in-Dialysis-FINAL.pdf . These sources guide planning; none validates RENALIS.
