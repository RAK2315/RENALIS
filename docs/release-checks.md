# RENALIS v0.3 verification record

Checked locally on 16 October 2026. This is an engineering verification record, not a clinical validation or public-deployment claim.

| Check | Result |
|---|---|
| Production TypeScript/Vite build | Passed; landing and workspace/research/chart code split into separate bundles. |
| Python unit/integration suite | 25 tests passed. |
| Original workspace browser regression | Passed: scenario/review persistence, outcome reveal, patient switching, evidence rendering, session completion, and responsive layouts. |
| Low-BP card regression | Passed: current observation instead of future-warning heading, measured BP instead of null percentage, disabled alternative controls, absent alternative comparison during an existing event. |
| Mechanism-lab browser regression | Passed: availability, acquisition, delayed release, evidence export, immutable reports, reset, contradiction downgrade, independent challenge rendering, and guard states. |
| Complete-experience browser regression | Passed: computed interactive hero, landing/research navigation, source search/filter, every document resource, guided journey without evidence mutation, step-preserving reload, browser back, deep links, and missing-route recovery. |
| Simulated backend failure | Passed: hero failure/retry and source-library availability when computed research endpoints fail. |
| Reflow | Landing, research, workspace, and lab checked at 1440, 1024, 768, 390, and 320 pixels; guided panel additionally checked at 390/320. No document-level horizontal overflow. Scrollable data tables retain their own overflow. |
| Visual inspection | Desktop landing and research, mobile landing/research, guided workspace, and lab screenshots inspected during implementation. |

## Commands

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
npm run build
npm run test:browser
npm run test:browser:alerts
npm run test:browser:mechanisms
npm run test:browser:experience
```

Browser checks require Playwright and both local servers. This workstation used the bundled Playwright module via `NODE_PATH`; README documents the configurable `RENALIS_PLAYWRIGHT_PATH`. Screenshots and test downloads are in ignored `artifacts/qa/`. Browser checks add labeled synthetic review/branch records; tests of the guide explicitly verify that guidance itself acquires no measurements.

## Material corrections verified

- Mechanism pressure now propagates from the cuff's actual timestamp to the current cutoff. A tick without a new cuff does not become a new measured pressure.
- The original workspace and mechanism lab both withhold profile comparisons during an existing low-BP event.
- Historical-summary wording correctly describes the authored EHR prior rather than implying a prior learned from the displayed summaries.
- Live example page views are read-only and independent of acquired workspace evidence.
- New pressure-origin semantics are versioned `competing-mechanisms/0.3`; immutable old reports retain their old version and result.

## Verification limits

These checks do not establish WCAG conformance, clinician usability, physiology identifiability, calibrated real-world event probabilities, causal scenario effects, treatment benefit, or superior measurement selection. Source review is focused, not systematic. Public hosting and hackathon submission have not been verified. Required team identity, eligibility, PDF/PPT deliverables, recorded video, and submission steps remain tracked in the execution plan.
