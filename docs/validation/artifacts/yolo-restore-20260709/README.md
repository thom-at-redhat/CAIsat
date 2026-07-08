<!-- Assisted by: cursor, claude -->

# YOLO restore — Gate 0 (2026-07-09)

**Result: PASS (health-based)** — detection backend reports `predictor_ready: true`. Replica count not verified: `oc login` unavailable (Unauthorized) in this environment.

Gate 0 functionally passes; Wave 0 proceeds per operator override.

## Artifacts

| File                    | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| `before-replicas.txt`   | Replica query blocked on `oc`            |
| `after-replicas.txt`    | Scale step skipped (health already good) |
| `detection-health.json` | Full `/health` response                  |

## Evidence

```bash
curl -sS "https://caisat-detection-backend-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com/health"
# {"status":"healthy","gpu_exclusive":true,"predictor_ready":true}
```

## Notes

- MT-E2E @ `mt-e2e-20260709` may have scaled `yolov8m-satelite-predictor` to 0 under `CAISAT_GPU_EXCLUSIVE=1`; predictor was already serving at health-check time.
- When `oc` is available, confirm `spec.replicas == 1` on `deploy/yolov8m-satelite-predictor -n caisat` for full artifact parity.
