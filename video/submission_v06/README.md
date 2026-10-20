# RENALIS visual submission materials

Design revision v06 updates the architecture document and project presentation. The application and scientific model remain release 0.4. The 20-minute YouTube film remains the published demonstration.

The architecture has six native editable views: local system containers, inference components, acquisition sequence, adaptive planning, evidence persistence, and evaluation boundaries. The 20-slide presentation uses the same navy, cyan, jade, coral and lavender palette with Segoe UI and Consolas. Both fonts are system fonts and are not redistributed.

Four native charts preserve literal evidence values in embedded workbook snapshots. These are the released synthetic BP trace, the full-bank evidence progression, observed-data MAE and the independent policy holdout. The PDF copies use reviewed 3200×1800 slide renders with a searchable text layer and public-source links. The corresponding PPTX files retain editable labels, connectors, shapes and charts. Per-slide notes cite source modules and reports.

## Sources and assets

- `public/presentation-assets/evidence.json` is a small fictional replay snapshot, reduced from the isolated film capture. It contains no real patient records.
- `public/presentation-assets/interface-*.png` are actual synthetic workspace captures.
- `public/presentation-assets/renal-twin-cover.png` is conceptual artwork generated with the built-in image tool. Its complete prompt is in `provenance.json` in that directory.
- Lucide library icons retain their original geometry. Their ISC notice is included as `LUCIDE-LICENSE.txt`.
- Observed and policy chart values come directly from `docs/observed-v04.json` and `docs/policy-validation-v04.json`.

## Production

The authoring scripts use the Codex bundled `@oai/artifact-tool` runtime, its finalizer, Sharp, the installed project Lucide/React packages, and the bundled PDF dependencies. The application itself does not depend on the presentation runtime. In the production environment, set `RUNTIME_NODE_MODULES` to the bundled Node modules path and use its Node executable. The local runtime junction inside this directory is ignored by Git.

```powershell
node video/submission_v06/build.mjs --hires
node video/submission_v06/finalize.mjs
python video/submission_v06/build_pdfs.py
```

Private renders and validation receipts stay in `tmp/design-v06`. The finalizer requires new output and receipt paths for each revision and does not overwrite finals. Change the revision filenames before producing another release. PDF conversion requires the ReportLab/pypdf runtime and Segoe UI font available on the production Windows host.

Current public outputs are `output/pdf/RENALIS_Architecture_v06.pdf`, `output/pdf/RENALIS_Project_Presentation_v06.pdf`, `output/presentations/RENALIS_Architecture_v06_Professional_Final.pptx` and `output/presentations/RENALIS_Project_Presentation_v06_Design_Final.pptx`.
