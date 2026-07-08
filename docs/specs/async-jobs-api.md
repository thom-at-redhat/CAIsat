# Async Jobs API (`POST/GET /api/*/jobs`)

<!-- Assisted by: cursor, claude -->

| Field      | Value                                                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Status     | accepted                                                                                                                       |
| Spec ID    | ENH-001                                                                                                                        |
| Tests      | `tests/test_enhance_jobs.py`, `tests/test_detect_jobs.py`, `tests/test_async_enhance_api.py`, `tests/test_async_detect_api.py` |
| Validation | `baseline-smoke.md` — async 768 enhance / gpu_exclusive detect                                                                 |
| Modules    | `backend/enhance_jobs.py`, `backend-detection/detect_jobs.py`                                                                  |
| Routes     | `backend/app.py` L170–204, `backend-detection/app.py` L225–259                                                                 |

## Overview

Long-running enhance and detect requests use in-memory async jobs so the UI can return immediately with HTTP 202 and poll for completion.
This avoids route/LB idle timeouts (~60 s) on large crops, multi-tile enhancement, and gpu_exclusive predictor activation.

Enhancement and detection backends mirror the same job module structure (`create_job`, `get_job`, `_run_job`).

## Requirements

### ENH-001-R1: Create enhance job

- **Route:** `POST /api/enhance/jobs` (`backend/app.py`)
- **Request:** `multipart/form-data` with field `image` (same as sync `POST /api/enhance`)
- **Success:** HTTP **202 Accepted**
- **Body:** `{"job_id": "<hex uuid>", "status": "pending"}`
- **Errors:** Same validation as sync enhance (`413` upload/crop limits, `500` queue failure, `503` service not ready) may occur before job creation

### ENH-001-R2: Poll enhance job

- **Route:** `GET /api/enhance/jobs/{job_id}`
- **Success:** HTTP 200, JSON body always includes `job_id` and `status`
- **Unknown job:** HTTP **404**, detail `"Enhance job not found"`
- **Status `complete`:** Body merges job result fields from `_enhance_upload`:
  - `preview` (base64 JPEG), `media_type`, `width`, `height`, `preview_width`, `preview_height`
- **Status `error`:** Body includes `error` string (from caught `HTTPException` detail or `"Image enhancement failed"`)

### ENH-001-R3: Create detect job

- **Route:** `POST /api/detect/jobs` (`backend-detection/app.py`)
- **Request:** `multipart/form-data` with field `image` (same as sync `POST /api/detect`)
- **Success:** HTTP **202 Accepted**
- **Body:** `{"job_id": "<hex uuid>", "status": "pending"}`
- **Errors:** Same validation as sync detect may occur before job creation

### ENH-001-R4: Poll detect job

- **Route:** `GET /api/detect/jobs/{job_id}`
- **Success:** HTTP 200, JSON body always includes `job_id` and `status`
- **Unknown job:** HTTP **404**, detail `"Detect job not found"`
- **Status `complete`:** Body merges job result fields from `_detect_upload`:
  - `detections`, `count`, `image_size`, `sahi_slices`
- **Status `error`:** Body includes `error` string (from caught `HTTPException` detail or `"Object detection failed"`)

### ENH-001-R5: Job status machine

Both `enhance_jobs.py` and `detect_jobs.py` implement identical transitions:

| Status       | When                                                                   |
| ------------ | ---------------------------------------------------------------------- |
| `pending`    | Job created; returned in POST 202 response                             |
| `processing` | Background task started (`_run_job` sets status before `await work()`) |
| `complete`   | Work coroutine returned successfully; `result` populated               |
| `error`      | Work raised any exception; `error` set to `str(exc)`                   |

Poll responses while `pending` or `processing` return only `job_id` and `status` (no result/error fields).

### ENH-001-R6: In-memory store and TTL

- Jobs stored in process memory (`_jobs` dict); not shared across pod replicas
- Stale jobs pruned on create when `created_at` older than `JOB_TTL_SECONDS` (3600 s)
- Job IDs are `uuid.uuid4().hex` (32-char hex, no dashes)

## Acceptance criteria

- [x] `POST /api/enhance/jobs` returns 202 with `job_id` and `status: pending` — `backend/app.py`
- [x] `GET /api/enhance/jobs/{job_id}` returns 404 for unknown id — `backend/app.py`
- [x] `POST /api/detect/jobs` returns 202 with `job_id` and `status: pending` — `backend-detection/app.py`
- [x] `GET /api/detect/jobs/{job_id}` returns 404 for unknown id — `backend-detection/app.py`
- [x] Status transitions `pending` → `processing` → `complete`/`error` — `enhance_jobs.py`, `detect_jobs.py`
- [x] `test_enhance_jobs` importlib load — `tests/test_enhance_jobs.py`
- [x] `test_detect_jobs` mirror for `backend-detection/detect_jobs.py` — `tests/test_detect_jobs.py`
- [x] `TestClient` create → poll complete/error for both backends — `tests/test_async_enhance_api.py`, `tests/test_async_detect_api.py`
