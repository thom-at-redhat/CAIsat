# Capabilities API (`GET /api/capabilities`)

<!-- Assisted by: cursor, claude -->

| Field      | Value                                                          |
| ---------- | -------------------------------------------------------------- |
| Status     | accepted                                                       |
| Spec ID    | CAP-001                                                        |
| Tests      | `tests/test_capabilities.py`                                   |
| Validation | `baseline-smoke.md` L188, L203                                 |
| Modules    | `backend/capabilities.py`, `backend-detection/capabilities.py` |
| Routes     | `backend/app.py` L76–78, `backend-detection/app.py` L148–150   |

## Overview

Both FastAPI backends expose `GET /api/capabilities` returning runtime compute limits from Helm env vars (`COMPUTE_PROFILE`, `GPU_AVAILABLE`, `KSERVE_PREFER_BINARY`).
The enhancement backend uses this response to cap crop size and tile settings; the detection backend exposes the same contract for UI consistency.

## Requirements

### CAP-001-R1: HTTP contract

- Method: `GET /api/capabilities`
- Success: HTTP 200, `Content-Type: application/json`
- Body: JSON object from `get_capabilities()` with keys documented in CAP-001-R2–R4

### CAP-001-R2: Response schema

| Field                   | Type    | Source                                                               |
| ----------------------- | ------- | -------------------------------------------------------------------- |
| `profile`               | string  | `COMPUTE_PROFILE` env (default `cpu`, lowercased)                    |
| `gpu_tier`              | string  | Active tier name (`cpu`, `t4`, `l40s`, `hopper`)                     |
| `max_crop`              | integer | Profile limit or deferred cap                                        |
| `max_tile`              | integer | Profile limit or deferred cap                                        |
| `tiling_enabled`        | boolean | Profile limit or deferred cap                                        |
| `scale_factor`          | integer | Always `4` (native SwinIR 4×)                                        |
| `infer_timeout_seconds` | integer | `300` (enhancement) or `60` (detection)                              |
| `gpu_deferred`          | boolean | `true` when GPU profile selected but GPU unavailable                 |
| `kserve_prefer_binary`  | boolean | `KSERVE_PREFER_BINARY` env (default `true`)                          |
| `default_crop`          | integer | Always `256` — safe default for UI crop selector                     |
| `inference_accelerator` | string  | `cpu` (MLServer) or `gpu` (Triton); from `INFERENCE_ACCELERATOR` env |

### CAP-001-R3: Profile tier limits

When `gpu_deferred` is `false`, limits match `PROFILE_LIMITS[profile]`:

| Profile  | `max_crop` | `max_tile` | `tiling_enabled` | `infer_timeout_seconds` (enh / det) |
| -------- | ---------- | ---------- | ---------------- | ----------------------------------- |
| `cpu`    | 256        | 256        | false            | 300 / 60                            |
| `t4`     | 512        | 512        | true             | 300 / 60                            |
| `l40s`   | 768        | 512        | true             | 300 / 60                            |
| `hopper` | 1024       | 512        | true             | 300 / 60                            |

Unknown `COMPUTE_PROFILE` values fall back to `cpu` limits.

When `INFERENCE_ACCELERATOR` is not `gpu` on a non-CPU profile with GPU available, apply `CPU_INFERENCE_GPU_CAP`:
`max_crop=512`, `max_tile=512`, `tiling_enabled=true` (MLServer runs on CPU even when the pod is GPU-scheduled).

### CAP-001-R4: GPU deferral

When `COMPUTE_PROFILE` is not `cpu` and `GPU_AVAILABLE` is not truthy (`1`, `true`, `yes`):

- Apply `DEFERRED_GPU_CAP`: `max_crop=256`, `max_tile=256`, `tiling_enabled=false`
- Set `gpu_deferred=true`
- Preserve requested `gpu_tier` name for UI messaging

### CAP-001-R5: Environment variables

| Variable                | Default | Effect                                                              |
| ----------------------- | ------- | ------------------------------------------------------------------- |
| `COMPUTE_PROFILE`       | `cpu`   | Selects tier from `PROFILE_LIMITS`                                  |
| `GPU_AVAILABLE`         | `false` | When false on non-CPU profile, triggers deferral                    |
| `INFERENCE_ACCELERATOR` | `cpu`   | `gpu` when Triton runtime active; caps apply when `cpu` on GPU tier |
| `KSERVE_PREFER_BINARY`  | `true`  | Exposed as `kserve_prefer_binary` in response                       |

Chart values: [`chart/values.yaml`](../../chart/values.yaml) `computeProfile.name`, `computeProfile.gpuAvailable`.

## Acceptance criteria

- [x] Both `backend/` and `backend-detection/` modules implement identical deferral and env parsing logic (timeout differs per module)
- [x] CPU cluster returns `max_crop=256`, `gpu_tier=cpu`, `tiling_enabled=false`, `gpu_deferred=false` — verified `baseline-smoke.md` L203 @ `e2a7704`
- [ ] `test_cpu_profile_defaults` — enhancement + detection backends (MT-W12)
- [ ] `test_gpu_deferred_caps_to_cpu` — `COMPUTE_PROFILE=t4`, `GPU_AVAILABLE=false` (MT-W12)
- [ ] `test_gpu_available_uses_tier_limits` — hopper profile with GPU available (MT-W12)
- [ ] `test_kserve_prefer_binary_env` — `KSERVE_PREFER_BINARY=false` reflected in response (MT-W12)
