# Baseline and Smoke Validation

<!-- Assisted by: cursor, claude -->

Repeatable checks before and after functional changes. Automated gate: `make smoke` (default **health** profile only).

**Baseline SHA:** record the commit under test when running manual cluster validation.

Phase numbers match [`docs/project/PLAN.md`](../project/PLAN.md) (0–23).

---

## Smoke profiles

| Profile      | Phases                 | Assertions                                                                                      |
| ------------ | ---------------------- | ----------------------------------------------------------------------------------------------- |
| **health**   | 7 (minimum merge gate) | `GET /health` → 200 on enhancement and detection backends                                       |
| **baseline** | 12+ prep, 13+ required | health + `POST /api/enhance` 200 + non-empty PNG + `POST /api/detect` 200 + `detections` array  |
| **post-p0**  | 13+                    | baseline + manual capture/zoom sign-off at 1×, 2×, 4× (see [Capture/zoom](#capturezoom-manual)) |
| **binary**   | 14+                    | baseline + binary `content-type` + decode on enhance and detect                                 |
| **crop**     | 16+                    | baseline/binary + enhance at profile default crop size when >256                                |

Set profile: `SMOKE_PROFILE=health make smoke` (default `health`). Only **health** is implemented in `scripts/smoke-local.sh`; other profiles use manual checklists below until extended.

---

## Health profile (local)

**Prerequisite:** Python deps for both backends (`pip install -r backend/requirements.txt` and `backend-detection/requirements.txt`).

**Command:**

```bash
make smoke
```

**What it does:** Starts both backends on `127.0.0.1:8000` and `127.0.0.1:8001` with a dummy `MODEL_ENDPOINT` (health only; no model infer), then curls `/health`.

**Override** (backends already running):

```bash
ENHANCE_BACKEND_URL=http://127.0.0.1:8080 \
DETECTION_BACKEND_URL=http://127.0.0.1:8081 \
make smoke
```

**Expected:**

- HTTP 200 from each `/health`
- JSON body containing `"status"` (e.g. `{"status":"healthy"}`)

---

## Cluster sign-off (optional for Phase 7)

Phase 7 merge gate is **health** via `make smoke` only.

Full **baseline** cluster validation is required from Phase 13. Run the checklist below when a stack is deployed and record sign-off before that merge.

---

## Baseline profile (cluster checklist)

Run on a deployed stack before Phase 13 merge. Record branch SHA and namespace.

1. `oc get pods -n <namespace>` — five pods Running (frontend, both backends, both predictors)
2. `oc get inferenceservice -n <namespace>` — both Ready
3. Port-forward or Route: `curl -sf https://<backend-route>/health`
4. Port-forward or Route: `curl -sf https://<detection-backend-route>/health`
5. Full UI workflow: capture 256×256, enhance, detect — non-empty result and `detections` in API response
6. React 19 / three.js 0.185 / react-leaflet 5: globe loads, map tiles render, no console errors on navigation

Document SHA, cluster, and date in this file when baseline is signed off.

| Field         | Value                          |
| ------------- | ------------------------------ |
| Branch SHA    | _(pending — cluster not run)_  |
| Deploy target | _(cluster / local full stack)_ |
| Date          | _(pending)_                    |
| Signed off    | _(pending)_                    |

### Local pre-check (no cluster)

When a cluster is unavailable, run before opening the Phase 13 PR:

1. `make check` and `make smoke` (health) — must pass
2. `cd frontend && npm start` — open app, activate satellite view, capture map
3. Confirm crop UI loads with centered 256×256 box; scroll-wheel and 2×/4× buttons change zoom without shifting box relative to image
4. Optional: compare cropped preview to red box at 1×/2×/4× (see [Capture/zoom](#capturezoom-manual))

---

## Capture/zoom manual

Upstream [#5](https://github.com/rh-ai-quickstart/CAIsat/issues/5): captured PNG region must match visible selection box at zoom 1×, 2×, 4×.

**Fix (Phase 13):** crop coordinates use natural image pixels; image displays 1:1 inside a CSS `transform: scale(zoom)` layer with a scroll spacer sized to `width×zoom` / `height×zoom`.
Wheel and button zoom adjust scroll to keep the focal point stable.

Not automated in `make smoke`; record pass/fail here after manual verification.

### Procedure

1. Deploy stack (or `npm start` + local backends for crop-only check).
2. **Map → Capture & Enhance** on a distinctive area (coastline, road intersection, building).
3. At each zoom level (**1×** Reset, **2×**, **4×**), drag the red box over a recognizable feature.
4. Click **Enhance Selected Area** (or inspect the cropped preview before enhance).
5. **Pass:** cropped/enhanced image shows the same geography as inside the red box (no horizontal/vertical offset).
6. **Fail:** visible offset, wrong region, or box drifts relative to image when zooming.

| Zoom | Cluster result | Local result | Notes                               |
| ---- | -------------- | ------------ | ----------------------------------- |
| 1×   | _(pending)_    | _(pending)_  | Reset zoom; box centered on capture |
| 2×   | _(pending)_    | _(pending)_  | Use 2× button or scroll wheel       |
| 4×   | _(pending)_    | _(pending)_  | Use 4× button or scroll wheel       |

| Field      | Value       |
| ---------- | ----------- |
| Branch SHA | _(pending)_ |
| Date       | _(pending)_ |
| Signed off | _(pending)_ |

---

## Crop profile (Phase 16+)

Manual checklist when `max_crop` > 256 or tiling is enabled:

1. `GET /api/capabilities` returns expected `max_crop`, `max_tile`, `tiling_enabled`
2. Frontend crop box matches capabilities `max_crop`
3. Enhance returns native 4× output (256→1024 on CPU profile; no forced 512 resize)
4. Tiled path: all tiles succeed or request aborts with 502 (no partial stitch)

| Field      | Value       |
| ---------- | ----------- |
| Branch SHA | _(pending)_ |
| Date       | _(pending)_ |
| Signed off | _(pending)_ |

---

## Per-phase re-run rule

Re-run **health** via `make smoke` after backend/chart changes. For baseline/binary/crop profiles, follow the manual checklist at the phase’s merge gate until `smoke-local.sh` implements them.
