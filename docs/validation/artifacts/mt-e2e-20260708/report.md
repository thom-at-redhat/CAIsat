# MT-E2E Workflow Report (template)

<!-- Assisted by: cursor, claude -->

| Field        | Value                             |
| ------------ | --------------------------------- |
| Date         | YYYY-MM-DD                        |
| Frontend URL | _(set via `CAISAT_FRONTEND_URL`)_ |
| Verdict      | _(pass / fail)_                   |

## Scenarios

### enhance-256 — pending

- Crop: 256×256
- Enhanced naturalWidth: _(must be > 0)_
- Screenshot: `enhance-256-enhanced.png`

### enhance-768 — pending

- Crop: 768×768 (requires `max_crop >= 768`, e.g. l40s profile)
- Enhanced naturalWidth: _(must be > 0)_
- Screenshot: `enhance-768-enhanced.png`

### detect-progress-stages — pending

- Stages seen: `Activating detection model on GPU…` → `Running object detection…`
- Screenshot: `detect-progress-complete.png`

### health-idle-header — pending

- Header: `Detection: idle` (gpu_exclusive cluster with YOLO scaled down)
- Screenshot: `health-idle-header.png`

## Run

```bash
export CAISAT_FRONTEND_URL=https://caisat-caisat.apps.<cluster-domain>
node scripts/mt-e2e-workflow.mjs
```

Artifacts written to this directory; `report.md` updated on completion.
