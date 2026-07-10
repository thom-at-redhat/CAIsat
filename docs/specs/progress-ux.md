# Progress UX (Enhance & Detect Workflows)

<!-- Assisted by: cursor, claude -->

| Field      | Value                                                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Status     | accepted                                                                                                                                          |
| Spec ID    | UX-001                                                                                                                                            |
| Tests      | `frontend/src/workflowUtils.test.js`; Playwright `scripts/mt-e2e-workflow.mjs` (cluster); `scripts/mt-r3a-playwright.mjs` (CI stub layout subset) |
| Validation | `baseline-smoke.md` MT-E2E — 768 enhance, detect stages, idle header (cluster); CI stub = R3a layout only via `e2e-playwright`                    |
| Source     | `frontend/src/workflowUtils.js`, `frontend/src/App.js`                                                                                            |

## Overview

The Processing view shows stage labels, upload progress, and elapsed time during enhance and detect.
Routing between sync HTTP and async job polling is decided client-side from capabilities and crop settings.
The header shows detection health including gpu_exclusive idle state from the detection backend `/health` endpoint.

## Requirements

### UX-001-R1: Enhance stage labels

`ENHANCE_STAGE_LABELS` maps internal stage keys to user-visible strings:

| Key          | Label                        |
| ------------ | ---------------------------- |
| `preparing`  | Preparing crop…              |
| `uploading`  | Uploading to server…         |
| `inferring`  | Running AI super-resolution… |
| `finalizing` | Building preview…            |

Stages advance: `preparing` → `uploading` → `inferring` → `finalizing` → cleared on success.
Progress bar `aria-valuetext` uses the label for the current stage.

### UX-001-R2: Detect stage labels

`DETECT_STAGE_LABELS` maps internal stage keys to user-visible strings:

| Key          | Label                              |
| ------------ | ---------------------------------- |
| `preparing`  | Preparing enhanced image…          |
| `uploading`  | Uploading to detection server…     |
| `activating` | Activating detection model on GPU… |
| `detecting`  | Running object detection…          |
| `drawing`    | Drawing bounding boxes…            |

When `gpu_exclusive` is true, upload completion sets `activating` (not `detecting`).
Async poll tick maps job `processing` → `detecting`, other statuses → `activating`.

### UX-001-R3: Enhance async routing (`shouldUseAsyncEnhance`)

Function signature: `shouldUseAsyncEnhance(cropSize, caps, tileCount)`.

Returns `true` (use `POST /api/enhance/jobs` + poll) when **any** of:

1. `tileCount > 1` — multi-tile crop (`getEnhanceTileCount` from `max_tile` and `tiling_enabled`)
2. `caps` is null/undefined **and** `cropSize > defaultCrop` — capabilities-not-loaded race guard (`defaultCrop` defaults to 256)
3. `cropSize > defaultCrop` — crop larger than `caps.default_crop` (always 256)

Otherwise uses sync `POST /api/enhance`.

| Scenario                       | Async?   |
| ------------------------------ | -------- |
| caps=null, crop=768, tiles=1   | yes (#2) |
| caps loaded, crop=256, tiles=1 | no       |
| caps loaded, crop=768, tiles=1 | yes (#3) |
| caps loaded, crop=512, tiles=4 | yes (#1) |

### UX-001-R4: Detect async routing

`useAsyncDetect = Boolean(capabilities?.gpu_exclusive)` — **only** when `gpu_exclusive` is true.

Detection does **not** use crop size or tile count for async routing (intentional asymmetry vs enhance).
When false, uses sync `POST /api/detect`.

### UX-001-R5: Async job polling (`pollAsyncJob`)

- Poll interval: 2 s between `GET /api/{resource}/jobs/{job_id}` requests
- Client timeout: enhance `(infer_timeout_seconds + 60) × 1000` ms; detect `(infer_timeout_seconds + 300) × 1000` ms
- Terminal `complete`: returns merged payload (same shape as sync response)
- Terminal `error`: throws with `payload.error`
- `onTick` callback invoked with current `status` on each non-terminal poll

### UX-001-R6: ETA hints

| Function            | Condition                                  | Hint text                                              |
| ------------------- | ------------------------------------------ | ------------------------------------------------------ |
| `getEnhanceEtaHint` | `tileCount > 1`                            | Processing N tiles sequentially · may take 1–2 minutes |
| `getEnhanceEtaHint` | else                                       | Usually ~10–60 seconds                                 |
| `getDetectEtaHint`  | `gpuExclusive && predictorReady === false` | First run may take 30–90s while the model starts       |
| `getDetectEtaHint`  | `gpuExclusive` (ready or unknown)          | Model swap after enhance · usually ~30–90s             |
| `getDetectEtaHint`  | else                                       | Usually ~10–45 seconds                                 |

### UX-001-R7: Detection health header

Header displays `Detection: {label}` where label comes from `getDetectionStatusLabel(detectionOnline, gpuExclusive, predictorReady)`:

| `detectionOnline` | `gpuExclusive` | `predictorReady` | Label  |
| ----------------- | -------------- | ---------------- | ------ |
| false             | \*             | \*               | `down` |
| true              | true           | `false`          | `idle` |
| true              | \*             | else             | `up`   |

Detection `/health` polled every 30 s (`DETECTION_BASE/health`).
When response includes boolean `predictor_ready`, UI stores it; otherwise `predictorReady` is `null`.

### UX-001-R8: Health endpoint asymmetry

| Backend     | Route     | `predictor_ready` | Notes                                          |
| ----------- | --------- | ----------------- | ---------------------------------------------- |
| Enhancement | `/health` | **not exposed**   | Returns `{"status": "healthy"}` only           |
| Detection   | `/health` | conditional       | Present when `gpu_exclusive` and session ready |

Detection `/health` also includes `gpu_exclusive` from capabilities.
`predictor_ready` is computed via `is_predictor_ready("yolo", ...)` only when `gpu_exclusive` is true.

Enhancement backend does not expose predictor readiness on `/health`; enhance orchestration is opaque to the header.

### UX-001-R9: Preview display (`previewPayloadToObjectUrl`)

On enhance success (sync or async), response payload is converted to a blob object URL for `<img alt="Enhanced">`.
Requires `preview` (base64) and `media_type`; probes load with `Image.onload` before returning URL.
Invalid payload or load failure surfaces user error (768×768 regression vector — unit test planned Track C).

## Acceptance criteria

- [x] Enhance stage labels match `ENHANCE_STAGE_LABELS` in `App.js`
- [x] Detect stage labels match `DETECT_STAGE_LABELS` in `App.js`
- [x] `shouldUseAsyncEnhance` implements tile count, caps-null, and crop>default rules
- [x] Detect async gated solely on `capabilities.gpu_exclusive`
- [x] Header `Detection: idle` when online + gpu_exclusive + `predictor_ready === false`
- [x] Detection `/health` exposes `predictor_ready`; enhancement `/health` does not
- [x] Unit tests in `workflowUtils.test.js` — `frontend/src/workflowUtils.test.js`
- [x] Playwright asserts enhance/detect stage strings and 768 `naturalWidth === 2048` — `scripts/mt-e2e-workflow.mjs` (cluster; `mt-e2e-20260709`)
- [x] `baseline-smoke.md` operator rows — 768 enhance, detect progress, gpu_exclusive idle
