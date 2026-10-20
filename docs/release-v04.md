# RENALIS 0.4: implementation and evidence ledger

18 October 2026. This release implements the software program from the research dossier. Clinical studies, external publication and team identity remain separate work that software cannot establish.

## What changed

- **History is an input to a learner.** Six preceding synthetic sessions contain raw BP trajectories and machine settings. A grid likelihood fits refill conditional on the declared physiology, then shrinks toward a population reference. The current session is excluded. The learner exposes source records, fit errors, uncertainty and a digest. A four-session/two-later-session ablation is computed separately. Shared simulator structure remains a limitation.
- **Four hypotheses.** Volume/refill, vascular, cardiac and an explicit mixed response family retain 48 particles each. The mixed family does not guarantee that real physiology is in the bank. Existing contradiction/current-event/stale/completed safeguards remain.
- **Whole-policy observation value.** Nine-node Gaussian quadrature compares the best immediate action against acquisition followed by a possibly delayed action. Failed acquisition retains burden and uses the no-result posterior. Negative value is preserved. Information gain remains separate. Numerical reference checks and an isolated waiting-loss regression cover the change.
- **A real acquisition ledger.** Equipment, latency, failure probability and noise are server-validated research settings. Failed requests and artifacts remain visible. Observed time and availability time differ explicitly. Corrections append a new record and retain the old value for earlier cutoffs. Resets archive evidence; saved comparisons stay immutable. Concurrent schema migration is serialized.
- **Evidence journey.** `/workspace?view=investigation` connects learned history, a clickable model graph, rival futures, predicted observation ranges, possible outcomes, acquisition, review notes, corrections, immutable saving and release evaluations under one patient/cutoff.
- **Conditional longitudinal transport.** A separate experiment carries fluid compartments through authored intake/output intervals and future sessions with a conservation check. It produces no future BP or prescribed target.
- **Synthetic FHIR export.** Patient, Device and measured BP Observation resources form a FHIR R4 collection example. No ABDM certification, profile conformance or live integration is claimed.

## Observed-data audit and new evaluation

`scripts/evaluate_observed_v04.py` verifies all deposit checksums, joins session records, reconciles repeated packets, canonicalizes UF from published L/h to mL/h, excludes current-session end values, and derives historical features from preceding completed sessions. Training, calibration and test patients are disjoint. A held-out logistic calibration model, threshold selection, empirical residual-range coverage, patient-cluster intervals, recurrence context and 30-minute refractory alarm consolidation are reported.

The audit found an approximately **eight-hour cross-table clock offset**. The pipeline declares this as an empirical alignment assumption and excludes machine packets with an elapsed-time discrepancy greater than 20 minutes. Independent confirmation of source clock semantics is still needed. This is an explicit limitation, not a silently fixed timezone claim. Of 4,366,298 packets, 2,516,989 match these interval/elapsed rules. The substantial exclusions can introduce selection bias.

The new cohort has 61,947 test windows. MAE is 12.194 mmHg for persistence, 11.356 dynamic-only, 11.328 demographics plus dynamics, and 11.161 preceding-session history plus dynamics. The paired history increment is -0.1665 mmHg with a patient-block interval [-0.2298, -0.1099]. This demonstrates incremental retrospective predictive information under this protocol, not physiological identification or clinical usefulness. The old v0.3 cohort differs and should not be ranked directly against these values.

The endpoint remains the **next distinct measured SBP <=90, gap 5-35 minutes, current BP >90**. It is explicitly distinct from the twin's nominal 30-minute modeled trajectory and from continuous hypotension. Test event sensitivity is 0.6125 and PPV 0.1351; do not hide the missed events or workload. Exact aggregate outputs, calibration bins, counts and limitations are in `observed-v04.json`.

## Independent policy evaluation

`backend/validation.py` evaluates 192 newly specified synthetic cases across volume, vascular, cardiac, mixed, omitted-mechanism, noisy, basic-equipment and failed/delayed regimes. Four policies share draws, availability and timing rules: no observation, fixed cuff, information gain and decision value. Reports retain every case, mean/tail regret, acquisitions, failures, per-regime results and seed-block paired intervals. No acceptance test requires our preferred policy to win.

The current results **do not establish overall decision-value superiority**. The original 108-case negative report remains unchanged at `originality-challenges.json`; the original endpoint serves that frozen report. Running the older diagnostic suite writes a separately named replay and does not replace history.

## Work-package mapping

| Packages | Implemented artifacts | Evidence still required |
|---|---|---|
| WP01 | Requirement/claim ledger, source register, README release links | Final team/college information and organizer ambiguities |
| WP02-06 | Observed audit, session/history features, patient-separated calibration/test and ablations | Independent clock confirmation, external/Indian validation, clinical importance |
| WP07-12 | Model graph, mixed hypothesis, acquisition ledger, whole-policy value, numerical checks and new independent suite | Paired physiological calibration, stronger robustness and clinical utility definitions |
| WP13-18 | Evidence journey, counterevidence, corrections, handover/export, accessibility/responsive tests and reproducibility commands | Expert task study and external clean-environment replication |
| WP19-20 | Study protocol and data-capture schema | Clinical collaborators, institutional approvals, actual measurements and staff-time study |
| WP21-23 | Conditional multi-session transport and independent shifted-regime tests | Identifiable longitudinal physiology and actual multi-centre transport evaluation |
| WP24 | Silent/impact study design and progression gates | Conducted approved studies and measured outcomes |
| WP25 | Synthetic FHIR collection with internal reference checks | ABDM profile validator and live authorized integration |
| WP26 | Architecture/presentation PDF and editable PPTX, current demonstration, evidence exports and release checklist | Real team details, public repository/video upload and actual submission receipt |

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
npm run build
.\.venv\Scripts\python.exe scripts/evaluate_observed_v04.py
.\.venv\Scripts\python.exe -m backend.validation
```

The observed pipeline requires the permitted local HEMOBP v3 files. Raw data and model/split files stay under ignored `data/`; public reports contain aggregate results. The new policy report is a frozen task. Any future tuning against it must use a separately declared next evaluation.

## External actions and clinical gates

No publication, registration, message to collaborators, patient data collection, clinical recommendation or machine control is performed by this release. The final package must never invent team identity, affiliation, public links, expert approval or prospective outcomes. A clear, reproducible prototype can be complete while those human and clinical evidence gates remain open.

## Evaluation audit amendment

The initial 192-case report is preserved in `policy-validation-v04-initial.json`. Metric audit 0.4.1 extends the oracle grid to include allowed waiting-prefix profiles, avoiding clipping against an incomplete immediate-only comparison. No policy changed. Current mean regret is 0.23078 no observation, 0.22170 fixed cuff, 0.24472 information and 0.24145 decision value. Decision value is worse than cuff in 51 cases, with paired delta +0.01975 and seed-block interval [-0.00981, 0.05996]. Confident-wrong uses descriptive support >=0.8 and regret >0.05; this metric was added after first evaluation and is not predeclared evidence.

## Release artifacts

The current architecture is available as a dedicated PDF and editable PPTX. The project presentation has 16 editable slides and two native charts with embedded literal-data workbooks. Its PDF has a readable source appendix. Per-slide notes retain source files, external references and material limitations. PDF pages preserve reviewed slide renders; editable objects remain in PPTX.

The current click-through guide is `demo-walkthrough-v04.md`. The main guided tour now follows the new Evidence journey at minute 80. The older detailed mechanism view and historical reports remain accessible. Current-low-BP controls correctly withhold experimentation at minute 95 instead of pretending it is an advance warning.

The minimum 20-minute recording is prepared from the current presentation, complete-sentence local synthetic narration, captions and actual browser recordings against an isolated fictional-patient database. Public YouTube upload, anonymous access and actual team details remain external gates. See `submission-checklist.md`.

## Final local verification

42 backend tests pass in a fresh Python environment installed from the pinned requirements. A separate fresh npm installation and production build also pass. The five browser suites cover the new journey, legacy workspace, mechanism lab, alert states and complete site, including 320/390/768/1024/1440-pixel layouts. The final journey check verifies that immutable investigations retain history learning and measurement previews. No browser JavaScript errors were reported in the successful runs.

The two finalized PPTX files pass package/layout/font/chart-workbook checks and reimport/render for every slide. All PDF pages render and have been checked against the reviewed content. PDFs preserve slide images with a readable source appendix; editable charts/diagrams and source notes remain in PPTX. These checks do not establish clinical validity or native PowerPoint execution.

The full local demo is 1920x1080,24fps,H.264/AAC,20:00 with burned captions and separate SRT/VTT files. Local playback is `http://127.0.0.1:5173/artifacts/submission/player.html`. It is not uploaded to YouTube. Actual entrant details and public access remain open requirements.


## Adaptive evidence planning extension — 18 October

Implemented sequential-discrimination/0.1 in the Evidence journey. After CO3.74 at Meera minute90, the posterior selects RBV by pair-conditional expected information, with predicted ranges, outcome previews and channel comparisons on screen. Actual synthetic RBV85.0 retains uncertainty rather than forcing a resolving result. Equipment, noise, failure, acquisition availability and existing authority guards constrain selection. The selector uses no acquisition fixtures; exported investigations and immutable snapshots include its complete plan.

Verification: 50 backend tests pass, including eight sequential-discrimination tests; production TypeScript/Vite build passes; isolated browser checks cover the actual CO→RBV flow, failure/equipment abstention, export and five responsive widths. The complete Evidence journey regression also passes. Existing policy evaluations are frozen and do not evaluate this new multi-acquisition objective. Existing video and submission decks predate this extension.


## Submission production update — 19 October

Entrant details are now supplied: Team Sigmoid; Rehaan, solo; JSS University, Noida. The prepared public-source bundle excludes raw observed data, local databases, model weights, credentials and production intermediates. A focused README maps every mandatory organizer item, and a GitHub Actions verification workflow is prepared. Local source-folder verification passes50 backend tests and aggregate-release contracts; no remote CI run or public repository is claimed.

The updated presentation includes19 editable slides, including adaptive CO→RBV planning and its limits. The architecture has4 editable diagram slides. Their PDFs include readable source appendices. Latest deliverables use the v05 filenames; the application model remains0.4. Earlier materials remain historical.

The film is built as40 checkpointed30-second scenes, grouped into four5-minute chapters, with complete-sentence local synthetic narration, original continuous music, captions, motion graphics and22 actual website captures from an isolated fictional-patient database. The joined master is the intended20-minute submission video. Final media verification is recorded in the local film folder. The entrant will download/upload the video, add its actual unlisted YouTube URL to README, publish the source and verify public access before submitting. No clinical validation or publication step is silently marked complete.

Development startup now restricts dependency entries to index.html and excludes generated/source-export/large-data folders from file watching. A stalled dev-server request reproduced before this change; bounded HTTP checks and the production build pass afterward.
