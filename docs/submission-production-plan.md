# Submission production checkpoint

Started 19 October 2026, Asia/Calcutta. Team Sigmoid; Rehaan, solo entrant; JSS University, Noida. GitHub account verified locally: RAK2315. Prepare publication files locally; user will download and upload the video. No YouTube upload or hackathon submission is authorized/performed here.

## Deliverables

- Updated 20:00 film in four independently reproducible 5:00 chapters, joined continuously.
- Warm, upbeat local Kokoro narration in complete sentences; original quiet music; readable captions; real UI footage and motion graphics.
- Current adaptive CO3.74 → selected RBV → actual85.0 example, including honest residual uncertainty.
- Updated presentation and architecture PDF/PPTX, submission README and clean GitHub source bundle.
- Validation manifest, transcript, chapter timestamps, thumbnail and upload description.

## Timeline

1. 00:00–05:00: problem, product, architecture, learned history and competing explanations.
2. 05:00–10:00: actual sequential investigation, predictions, next observation, acquired result and safeguards.
3. 10:00–15:00: auditable evidence, data evaluation, negative policy result and limitations.
4. 15:00–20:00: failure states, longitudinal/FHIR experiments, reproducibility, submission package and next steps.

Each chapter has ten 30-second scenes. Scene narration, captions, graphics, footage and encoded video are individually cached by content hash. A render checkpoint is valid only when its hash, media dimensions, frame count and duration agree. Chapter joins use a common 24fps H.264 profile and a single continuous final audio encode. No chapter-boundary fades or restarted music.

## Restart commands

See `video/submission_v05/README.md` for exact production commands. Progress is persisted in `artifacts/submission-v05/progress.json`; source story is `video/submission_v05/story.json`. Never discard valid completed scenes to resume a render.

## Claims

Do not present planned validation as completed. The sequential selector is software-tested, not independently policy-validated. Frozen holdout results remain negative overall for decision-value selection. All built-in patient/device streams are synthetic. Public observed-data evaluation is separate. Team facts above are user-provided.

## Completed production checks — 20 October 2026

The final master is 1,200 seconds, 1920×1080, 24fps, with 28,800 video packets. All four five-minute chapters and the master passed metadata and packet-count checks. The master passed full-file audio/video decoding without errors. Its single continuous soundtrack was checked at 300,600,900 seconds; the measured waveform jumps were below the declared0.03 threshold. There are40 scenes and243 caption cues.

The final browser player was checked for chapter seeking, advancing playback, working download links, a real source-ZIP download and horizontal overflow at1440,768,390px. Python3.10's basic static server ignored MP4 range requests; `video/submission_v05/serve_assets.py` fixes that delivery issue. Its HTTP regression check exercises bounded, open-ended, suffix and invalid byte ranges plus full-file download. This is a video-serving fix, separate from the physiological model.

The prepared source folder passed50 backend tests and the existing768-record release contract check before packaging. These are local checks; the prepared GitHub Actions workflow has not been run remotely. The final deck contains19 editable slides and the architecture deck4 editable diagrams, each with a PDF copy and checked source references.

Media receipts remain in `artifacts/submission-v05/verification.json`, `capture-checks.json`, `audio-provenance.json`, `player-checks.json`, and `progress.json`. Public source hashes are listed in `artifacts/release/source-manifest.json`. No public repository, YouTube upload, anonymous-access verification or organizer submission has been completed by this production run. Follow `docs/UPLOAD_NEXT.md` after downloading the files.
