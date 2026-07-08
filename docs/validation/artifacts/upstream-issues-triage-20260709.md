# Upstream issue triage — rh-ai-quickstart/CAIsat (2026-07-09)

<!-- Assisted by: cursor, claude -->

Contributor fork has **issues disabled** (`has_issues: false`). Triage is read-only against upstream; no outbound comments unless maintainer access confirmed.

## #4 — Make places searchable by coordinates

| Field         | Value                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------- |
| Link          | [rh-ai-quickstart/CAIsat#4](https://github.com/rh-ai-quickstart/CAIsat/issues/4)         |
| Fork evidence | No lat/lng search or geocode UI in [`frontend/src/App.js`](../../../frontend/src/App.js) |
| Disposition   | **defer** — enhancement; upstream-only unless product prioritizes                        |

## #5 — Screen capture for image resolution is off

| Field         | Value                                                                                                             |
| ------------- | ----------------------------------------------------------------------------------------------------------------- |
| Link          | [rh-ai-quickstart/CAIsat#5](https://github.com/rh-ai-quickstart/CAIsat/issues/5)                                  |
| Fork evidence | Phase 13 fix in [`baseline-smoke.md` L121–142](../baseline-smoke.md); `pointerToImageCoords` in `App.js` L158–174 |
| Disposition   | **fixed (fork)** — MT-R3a + `mt-e2e-20260709` pass; upstream still open                                           |

## #6 — Image resolution takes long time

| Field         | Value                                                                                  |
| ------------- | -------------------------------------------------------------------------------------- |
| Link          | [rh-ai-quickstart/CAIsat#6](https://github.com/rh-ai-quickstart/CAIsat/issues/6)       |
| Fork evidence | Async jobs + GPU orchestrator (PRs #148–#153); MT-E2E 768→2048 ≤3m @ `mt-e2e-20260709` |
| Disposition   | **partial (fork)** — GPU + async mitigate; ONNX/MLServer latency remains               |

## #7 — Add change detection functionality

| Field         | Value                                                                              |
| ------------- | ---------------------------------------------------------------------------------- |
| Link          | [rh-ai-quickstart/CAIsat#7](https://github.com/rh-ai-quickstart/CAIsat/issues/7)   |
| Fork evidence | **CLOSED** upstream 2026-06-30; fork ships change-detection + SeaweedFS (Phase 25) |
| Disposition   | **fixed (fork)** — closed upstream; fork has full stack                            |

## #8 — Record an arcade of the demo

| Field         | Value                                                                            |
| ------------- | -------------------------------------------------------------------------------- |
| Link          | [rh-ai-quickstart/CAIsat#8](https://github.com/rh-ai-quickstart/CAIsat/issues/8) |
| Fork evidence | No guided demo recording; MT-E2E Playwright captures screenshots only            |
| Disposition   | **defer** — documentation/marketing; upstream-only                               |

## Evidence notes

### #5 — crop/zoom offset

Upstream report: captured region offset left vs visible box. Fork fix uses natural image pixels inside CSS `transform: scale(zoom)` with scroll spacer; baseline-smoke capture/zoom table **pass** at 1×/2×/4×.

### #6 — enhancement latency

Upstream: 15–30 s per image on ONNX/MLServer CPU. Fork additions:

- `backend/enhance_jobs.py` — async job polling from frontend
- `backend/predictor_orchestrator.py` — GPU exclusive mode + L40S tier
- MT-E2E @ qualitycustomer: 768 crop async with stage labels; 256 sync path sub-minute

Remaining gap vs upstream ask: OpenVINO CPU path not implemented; binary KServe still **fail** (separate blocker).

## Summary

| Disposition    | Count | Issues |
| -------------- | ----- | ------ |
| fixed (fork)   | 2     | #5, #7 |
| partial (fork) | 1     | #6     |
| defer          | 2     | #4, #8 |

**Outbound PR:** still deferred per PLAN — ~175 commits vs upstream; user decision required before closing upstream issues from fork.
