# RENALIS product film — second cut

A 1920 × 1080, 30 fps product explainer with 14 scenes and 31 individually timed spoken concepts. The film is approximately 2 minutes 46 seconds. The original generated ambient score is retained and extended to the new timeline.

## What changed

- Windows Zira narration was replaced with free, locally generated Kokoro-82M speech, using the af_heart voice. Four short voice samples are available in the player.
- Every utterance has its own audio file, visible concept, caption interval, and reading pause. A visual never needs to catch up with a different spoken concept.
- Long page scrolls were replaced with complete element captures fitted without cropping. The old measurement shot could show only about 413 of its 631 CSS-pixel height; the new panel is contained in full.
- Explanatory animation now carries the story: evidence streams and availability gate, fluid compartments, refill/removal, vessel and pump responses, diverging model trajectories, measurement comparison, changing compatibility, and the contradiction safeguard.
- Large labels explain the important points independently of fine print in product screenshots.
- The player has chapter jumps, voice auditions, audio-version switching, and download links. The previous export remains under artifacts/video/previous-v1/.

The film preserves the research boundaries: fictional patients, authored historical priors, conditional model compatibility rather than diagnosis probabilities, hypothetical scenario comparisons, and no demonstrated clinical benefit or measurement-policy superiority.

## Deliverables

Generated media stays under ignored artifacts/video/:

- renalis-explainer.mp4 — neural narration, original music, burned-in captions, optional text subtitle stream.
- renalis-music-only.mp4 — same picture and captions with the score alone.
- player.html — local player, chapter navigation, voice samples, and download links.
- renalis-explainer.srt and transcript.txt — editable text.
- narration.wav, original-score.wav, soundtrack.wav — editing stems.
- narration-v2/ — one speech WAV and synthesis record per visual beat.
- voice-samples/ — Heart, Bella, Emma, and Fenrir.
- timeline.json — exact scene, speech, concept, and caption timing.
- voice-provenance.json — model origin, licenses, runtime, voice, and downloaded-file hashes.
- composition-checks.json, player-checks.json, verification.json — verification results.
- qa/beats/ — a sample from every spoken concept.

The source files in video/ are editable and retained independently of generated artifacts.

## Free local voice

Kokoro-82M v1.0 weights are Apache-2.0 licensed; kokoro-onnx is MIT licensed. Download origin:

- https://huggingface.co/hexgrad/Kokoro-82M
- https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1

The model and voice pack are cached locally. Generation uses CPU inference; no account, API key, metered service, speaker reference recording, or per-character charge is required. Personality comes from the selected voice, questions, phrasing, pacing, and pauses. This model does not provide the full emotional direction controls of some larger speech models.

The optional narration environment is separate from the application's .venv so speech dependencies cannot change clinical-research calculations. narrate.py explicitly supplies float32 speed to the ONNX graph because kokoro-onnx 0.4.9 incorrectly casts it to int32 for this export. Phrase lengths are checked rather than silently truncated.

## Reproduce on Windows

Start the normal frontend at http://127.0.0.1:5173/. The app's regular .venv is used for isolated API capture and audio assembly. Install video/requirements.txt there if not already installed. Set NODE_PATH to a Playwright installation, or set RENALIS_PLAYWRIGHT_PATH. Chromium must be available.

```powershell
& .\.venv\Scripts\python.exe -m venv .venv-video
& .\.venv-video\Scripts\python.exe -m pip install -r video/voice-requirements.txt
node video/capture.cjs
& .\.venv-video\Scripts\python.exe video/narrate.py --samples
& .\.venv-video\Scripts\python.exe video/narrate.py
& .\.venv\Scripts\python.exe video/prepare_audio.py
node video/check-composition.cjs
node video/render.cjs --preview
node video/render.cjs
& .\.venv\Scripts\python.exe video/verify.py
node video/check-player.cjs
```

narrate.py --voice af_bella can change the narrator; rerun timeline assembly, composition checks, rendering, and verification afterward. The earlier narrate.ps1 is retained only for reproducing the Windows speech approach; it does not generate the second cut's phrase assets.

## Verification

check-composition.cjs samples three positions inside every actual utterance. It checks the visible concept, caption ownership, safe text boundaries, complete screenshot containment, screenshot aspect ratio, and runtime errors. It also exports one frame per spoken concept. Those structural checks complement visual inspection; they do not prove artistic or clinical quality.

verify.py completely decodes both finished MP4s, checks dimensions, frame rate, duration and audio levels, and extracts encoded scene samples. check-player.cjs verifies actual browser decoding of picture and audio, chapter seeking, audio-version position retention, all four voice samples, and layout at 320, 390, 768 and 1440 pixels.

An optional independent speech-to-text check can use faster-whisper with tiny.en; its dependencies are in video/qa-requirements.txt. Transcription is a spelling/pronunciation aid, not proof of natural delivery.

## Capture isolation and rendering

capture.cjs starts the production API against a new SQLite file in the ignored output directory. Requests from the filming browser are forwarded to that isolated API. Actual synthetic acquisition, saved reports, reset and contradiction flows run there. The main workspace database is not reset or edited by filming.

composition.html is a deterministic Canvas composition. renderFrame(seconds) sets every animation to an exact time. Captured elements use contain sizing without scrolling, clipping or distortion. Actual API values provide the mechanism curves, fit errors, decision values and compatibility update. Diagrams illustrating refill, vessels and pumping are conceptual, not patient images or calibrated anatomy.

Rendering uses three browser pages feeding JPEG frames to H.264 encoders, then muxes AAC audio and captions. prepare_audio.py produces the original oscillator-based score and smoothly ducks it under speech. No stock song or sampled melody is used.

This short product film is separate from the hackathon's required minimum-20-minute explanation.

## Verified second-cut export

The delivered MP4s are 165.967 seconds, 4,979 frames, 1920 × 1080 at 30 fps. Both passed a complete audio/video decode. The narrated export measured −16.07 LUFS integrated and −1.24 dBTP true peak. All 31 spoken concepts passed 93 alignment/framing samples; encoded scene samples were also inspected. Actual browser playback, 14 chapter links, audio-version switching, all four voice auditions, and responsive player layouts passed. Reports are in the generated files listed above.
