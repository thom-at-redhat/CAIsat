# MT-E2E Workflow Report

<!-- Assisted by: cursor, claude -->

| Field         | Value                                              |
| ------------- | -------------------------------------------------- |
| Date          | 2026-07-08                                         |
| Frontend URL  | `<CAISAT_FRONTEND_URL>` (qualitycustomer `caisat`) |
| Git SHA       | `07daa16`                                          |
| Helm revision | 10                                                 |
| Verdict       | **pass**                                           |

## Deploy metadata

- Frontend image digest: `sha256:e29be76aa370d97b57985ee8cf3ac2fddb03b89e48bfe4e19274a801da163582`
- Backend image digest: `sha256:f2afce8f51918e785543e6c316b8171d62039a921b5c15114905f59d91a961b3`
- Capabilities: `max_crop=768`, `gpu_exclusive=true`, `gpu_tier=l40s`, `default_crop=256`, `scale_factor=4`

## Scenarios

### health-idle-header — pass

- Header: `LIVEDetection: idle`
- Screenshot: `health-idle-header.png`

### enhance-256 — pass

- Crop: 256×256
- Enhanced naturalWidth: 1024
- Screenshot: `enhance-256-enhanced.png`

### enhance-768 — pass

- Crop: 768×768
- Enhanced naturalWidth: 2048
- Stages seen: Preparing crop…
- Screenshot: omitted from git (>500KB); assertion recorded in summary JSON

### detect-progress-stages — pass

- Stages seen: activating → detecting
- Screenshot: omitted from git (>500KB); assertion recorded in summary JSON

## Operator notes

- Restore YOLO after gpu_exclusive run: `oc scale deploy/yolov8m-satelite-predictor --replicas=1 -n caisat`
- Script scales YOLO to 0 for idle check but does not restore; operators must scale back up.
