# Baseline and Smoke Validation

<!-- Assisted by: cursor, claude -->

Repeatable checks before and after functional changes. Automated gate: `make smoke` (default **health** profile).

**Baseline SHA:** record the commit under test when running manual cluster validation.

---

## Smoke profiles

| Profile      | Phases                 | Assertions                                                                                      |
| ------------ | ---------------------- | ----------------------------------------------------------------------------------------------- |
| **health**   | 3 (minimum merge gate) | `GET /health` → 200 on enhancement and detection backends                                       |
| **baseline** | 4+ prep, 5+ required   | health + `POST /api/enhance` 200 + non-empty PNG + `POST /api/detect` 200 + `detections` array  |
| **post-p0**  | 5+                     | baseline + manual capture/zoom sign-off at 1×, 2×, 4× (see [Capture/zoom](#capturezoom-manual)) |
| **binary**   | 6+                     | baseline + binary `content-type` + decode on enhance and detect                                 |
| **crop**     | 8+                     | baseline/binary + enhance at profile default crop size when >256                                |

Set profile: `SMOKE_PROFILE=health make smoke` (default `health`).

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

## Baseline profile (cluster checklist)

Run on a deployed stack before Phase 5 merge. Record branch SHA and namespace.

1. `oc get pods -n <namespace>` — five pods Running (frontend, both backends, both predictors)
2. `oc get inferenceservice -n <namespace>` — both Ready
3. Port-forward or Route: `curl -sf https://<backend-route>/health`
4. Port-forward or Route: `curl -sf https://<detection-backend-route>/health`
5. Full UI workflow: capture 256×256, enhance, detect — non-empty result and `detections` in API response

Document SHA, cluster, and date in this file when baseline is signed off.

| Field         | Value                          |
| ------------- | ------------------------------ |
| Branch SHA    | _(pending)_                    |
| Deploy target | _(cluster / local full stack)_ |
| Date          | _(pending)_                    |
| Signed off    | _(pending)_                    |

---

## Capture/zoom manual

Upstream [#5](https://github.com/rh-ai-quickstart/CAIsat/issues/5): captured PNG region must match visible selection box at zoom 1×, 2×, 4×.

Not automated in `make smoke`; record pass/fail here after Phase 5.

---

## Per-phase re-run rule

Re-run `make smoke` at the **profile required for that phase** after any change to backends, frontend crop/capture, or chart deploy paths.
