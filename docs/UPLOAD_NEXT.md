# Final publication steps for Team Sigmoid

1. Download `RENALIS_Team_Sigmoid_20min.mp4` from the local video player. Upload the joined master to YouTube and select **Unlisted**. Upload the supplied English captions and thumbnail if desired.
2. Copy its real watch URL into the **Demo video** section of the repository README and `docs/team.json`. No placeholder URL is a valid submission link.
3. The public repository is [RAK2315/RENALIS](https://github.com/RAK2315/RENALIS). Commit and push the README and metadata after adding the actual video link. The source ZIP is a local snapshot; refresh it if further changes are made.
4. Check README links in an anonymous browser: video, architecture PDF, presentation PDF, source, license and model card. No login or extra permission should be required.
5. Paste the public repository URL into the submission form and select every mandatory item only after verifying it. Save the submission receipt.

Optional shortcut after both real links exist: run `python scripts/finalize-links.py --youtube YOUR_ACTUAL_WATCH_URL --repository YOUR_ACTUAL_REPOSITORY_URL`, then commit the updated README and metadata. This inserts the supplied URLs; it does not publish files or verify anonymous access.

Prepared entrant details: Team **Sigmoid**; **Rehaan**, solo; **JSS University, Noida**. The source package excludes raw observed data, local databases, model weights, credentials, temporary renders and the large MP4. The architecture and presentation have downloadable PDFs and editable PPTX copies.

The four individual five-minute videos are recovery/sharing assets. Upload the joined 20-minute master as the main demo. The captured interface uses fictional patients and an isolated database. Do not replace planned validation with a claim of completed studies.

Local player: `http://127.0.0.1:5176/artifacts/submission-v05/player.html`. If it is asleep, run `python video/submission_v05/serve_assets.py` from the original workspace containing the rendered artifacts. The player offers the complete MP4, individual chapters, captions, transcript, thumbnail, source ZIP and complete kit. The source-only ZIP deliberately excludes rendered media.
