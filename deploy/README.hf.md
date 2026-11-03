---
title: RENALIS API
emoji: 💧
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# RENALIS backend API

FastAPI research API for RENALIS, an evidence-aware dialysis digital twin built for the Happiest Health Digital Twin Challenge 2026.

All patients, device readings and EHR records served by this API are synthetic/fictional. This is a research prototype, not a clinical system.

- Health check (safe for uptime pings): `GET /api/health`
- Interactive API docs: `/docs`
- Consumed by the RENALIS frontend: https://github.com/RAK2315/RENALIS

Source for this container is generated from the `backend/` directory of the main repository by `scripts/deploy-hf-space.sh`; it is not edited directly here.
