# Four-chapter RENALIS submission film

Source: 40 scenes, 30 seconds each, four exact five-minute chapters. Team Sigmoid; Rehaan; JSS University, Noida. The final 20:00 film uses a continuous music/voice encode across chapter joins. No public upload is performed.

## Resume without starting over

```powershell
# Start the application; filming uses its production preview on5174.
python video/submission_v05/story_source.py
.venv-video/Scripts/python.exe -m video.submission_v05.audio
# Alternatively generate just one chapter: add --chapter 1 (or2,3,4).
node video/submission_v05/capture.cjs
.venv-video/Scripts/python.exe -m video.submission_v05.audio --assemble
node video/submission_v05/render.cjs --preview
node video/submission_v05/render.cjs
# Or render a single five-minute chapter: add --chapter 1.
```

The filming application is served from the compiled production build on5174. Serve the workspace's graphics/assets with `python video/submission_v05/serve_assets.py` on5176. This loopback-only server supports HTTP byte ranges, which the final player's chapter seeking requires; Python3.10's plain `http.server` does not. Install the video dependencies from `video/voice-requirements.txt` and `video/requirements.txt`; provide the locally downloaded Kokoro files under `artifacts/video/models`. See `video/narrate.py` for their upstream source and notices. Do not upload the model files to the project repository.

Narration WAVs have text/voice/rate signatures. Filming clips have source signatures and isolated synthetic evidence. Rendered 30-second scenes have content hashes, dimensions,720-frame receipts and file-size checks. `artifacts/submission-v05/progress.json` records completed scenes and chapters. Rendering resumes from matching receipts; a changed scene invalidates its own cache and affected transitions. Keep all receipts with the local work.

Each chapter is separately downloadable. The joined master copies the picture tracks and encodes the continuous soundtrack once, avoiding repeated AAC padding at joins. Captions are burned in and provided as SRT/VTT and a selectable MP4 text track. Cue timing is proportional within the measured synthetic utterance, not forced-aligned human transcription.

The new sequential selector is described as implemented and software-tested. Its independent policy evaluation, matched physiological calibration, external validation and real integration remain planned work. Historical frozen policy results are preserved accurately.
