# CAIsat Helm Chart

<!-- Assisted by: cursor, claude -->

Deploys frontend, enhancement/detection backends, SwinIR/YOLO/Sentinel2 InferenceServices, S4 storage, and optional pipelines.

## Key values

| Value | Default | Description |
| ----- | ------- | ----------- |
| `computeProfile.name` | `cpu` | `cpu`, `t4`, `l40s`, or `hopper` |
| `computeProfile.gpuAvailable` | `false` | Set `true` when GPU nodes are scheduled |
| `networkPolicy.enabled` | `false` | Enable backend NetworkPolicy (Phase 19) |
| `model.deploy` | `true` | SwinIR InferenceService |
| `detection.deploy` | `true` | YOLOv8-OBB InferenceService |

## Install

```bash
helm template test ./chart
helm upgrade --install caisat ./chart -n <namespace>
```

GPU profile example:

```bash
helm upgrade --install caisat ./chart -n <namespace> \
  --set computeProfile.name=t4 \
  --set computeProfile.gpuAvailable=true
```

See root [`README.md`](../README.md) for full deployment guide.
