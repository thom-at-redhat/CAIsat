# MT-E2E Workflow Report

<!-- Assisted by: cursor, claude -->

| Field                     | Value                                                                  |
| ------------------------- | ---------------------------------------------------------------------- |
| Date                      | 2026-07-08                                                             |
| Branch                    | `feature/test-sdd-hardening`                                           |
| Frontend URL              | `https://caisat-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com` |
| **Final verdict (run 4)** | **pass** (strict — health-idle passes, no waiver)                      |

## Cluster capabilities (`max_crop`)

`GET https://caisat-backend-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com/api/capabilities`

| Key             | Value   |
| --------------- | ------- |
| `max_crop`      | **768** |
| `gpu_exclusive` | true    |
| `gpu_tier`      | l40s    |
| `default_crop`  | 256     |

## Run comparison

| Scenario               | Run 3 (~16:03 UTC)                                              | Run 4 (~16:35 UTC)                           |
| ---------------------- | --------------------------------------------------------------- | -------------------------------------------- |
| health-idle-header     | **waiver** — `Detection: up` after 180s poll (ran after detect) | **pass** — `Detection: idle` at script start |
| enhance-256            | pass (1024px)                                                   | pass (1024px)                                |
| enhance-768            | pass (2048px)                                                   | pass (2048px)                                |
| detect-progress-stages | pass                                                            | pass                                         |

Logs: `results-run3.txt` (run 3), `results-run4.txt` (run 4). Machine-readable: `mt-e2e-summary.json`.

## Run 4 fixes

1. **Scenario order** — `health-idle-header` runs first (before Capture & Enhance) so prior GPU work cannot warm YOLO before the assertion.
2. **Strict assertion** — removed waiver path; `Detection: idle` is required for pass.
3. **Prerequisite** — when `CAISAT_GPU_EXCLUSIVE=1`, script scales `yolov8m-satelite-predictor` to 0 via `oc` and polls detection `/health` until `predictor_ready === false` (TLS-aware probe).
   YOLO does not auto-scale-down after detect; a warm predictor from earlier runs caused run 3 waiver.

## Run 4 scenario detail

### health-idle-header — pass

- Header: `LIVEDetection: idle`
- Screenshot: `health-idle-header.png`
- Prerequisite: `oc scale deploy/yolov8m-satelite-predictor --replicas=0 -n caisat`

### enhance-256 — pass

- Crop: 256×256
- Enhanced naturalWidth: 1024
- Screenshot: `enhance-256-enhanced.png`

### enhance-768 — pass

- Crop: 768×768
- Enhanced naturalWidth: 2048
- Screenshot: `enhance-768-enhanced.png`

### detect-progress-stages — pass

- Stages seen: activating → detecting
- Screenshot: `detect-progress-complete.png`

## Operator notes

- Set `CAISAT_GPU_EXCLUSIVE=1` on gpuExclusive clusters; script requires `oc` access to namespace `caisat`.
- Override scale target: `YOLO_DEPLOYMENT`, `CAISAT_NAMESPACE`.
- E2E not in CI — GPU cluster + ~4–7 min runtime (plan Track D).
