# Spike: RHOAI GPU ServingRuntime

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------- |
| Date            | 2026-07-01 (Wave 8 cloud GPU cluster re-test)                                               |
| Verdict         | **partial** — T4 tier pass (sequential); L40S/Hopper N/A; single-GPU contention documented  |
| Cluster/profile | cloud GPU cluster `computeProfile.name=t4`, `gpuAvailable=true`; helm rev **6** deployed    |
| Follow-up       | Chart: GPU tolerations + T4 CPU request tuning; multi-GPU or time-slicing for concurrent UX |

For per-tier commands and deferral caps, see the GPU tier table in [`README.md`](README.md).

## Command

```bash
# Helm GPU profile (requires GPU node + GPU_AVAILABLE=true)
helm upgrade caisat ./chart -n caisat --reuse-values \
  --set computeProfile.name=t4 \
  --set computeProfile.gpuAvailable=true \
  --set kserve.preferBinary=false

# Capabilities API (cluster route)
curl -sk "https://<backend-route>/api/capabilities"

# Cluster Ready + infer (when GPU available)
oc get inferenceservice -n <namespace>
oc exec -n <namespace> deploy/swinir-predictor -c kserve-container -- \
  curl -sf http://localhost:8080/v2/models/swinir/ready
```

## Output (snippet)

```text
# helm template (t4 profile, gpuAvailable=true)
          nvidia.com/gpu: "1"

# capabilities with GPU active (helm rev 6)
{"gpu_tier":"t4","max_crop":512,"max_tile":512,"tiling_enabled":true,"scale_factor":4,
 "infer_timeout_seconds":300,"profile":"t4","gpu_deferred":false,"kserve_prefer_binary":false}

# swinir JSON infer on T4 (256→1024)
JSON OK 42.18 s HTTP 200 out [1, 3, 1024, 1024]

# yolov8m-satelite JSON infer on T4
JSON OK 1.53 s HTTP 200 out [1, 20, 8400]

# enhance route (256→1024 PNG)
enhance HTTP 200 time 59.4s size 289915 — PNG 1024 x 1024

# detect route
detect HTTP 200 time 1.8s — {"detections":[],"count":0,...}
```

## Notes

| Tier   | Ready | Infer 200 | MT-4b caps API | Status   | Notes                                                                                                                       |
| ------ | ----- | --------- | -------------- | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| CPU    | pass  | pass      | pass           | **pass** | psi-21: swinir `/ready` HTTP 200; JSON infer 52.6 s → `[1,3,1024,1024]`; max_crop=256                                       |
| T4     | pass  | pass      | pass           | **pass** | cloud GPU cluster: 1× Tesla T4 (`g4dn.xlarge`); swinir + yolo Ready+infer **sequentially** on GPU node; caps `max_crop=512` |
| L40S   | —     | —         | —              | **N/A**  | no L40S nodes on test cluster                                                                                               |
| Hopper | —     | —         | —              | **N/A**  | no Hopper nodes on test cluster                                                                                             |

Chart ships `computeProfile.name` and `computeProfile.gpuAvailable` values. Backends expose `GET /api/capabilities` with deferral caps per plan.
Set `GPU_AVAILABLE=true` only after Ready + infer 200.

### Wave 8 cloud GPU cluster (2026-07-01)

**Pre-flight:** 1 GPU worker (`nvidia.com/gpu.product=Tesla-T4`, allocatable `nvidia.com/gpu=1`). `oc get nodes -l nvidia.com/gpu` returns empty (node labeled `node-role.kubernetes.io/gpu-worker` instead).

**Ops workarounds (not in chart):**

1. **sentinel2 scaled to 0** — frees cluster for enhance/detect UX (same pattern as psi-21); left at 0 for stability.
2. **GPU taint** — node has `nvidia.com/gpu=true:NoSchedule`; patched IS tolerations on swinir + yolo (chart does not set tolerations).
3. **CPU requests** — chart swinir requests 4 CPU; `g4dn.xlarge` allocatable 3500m; patched swinir IS to 2 CPU / yolo to 1 CPU for scheduling.
4. **Single GPU contention** — each predictor requests `nvidia.com/gpu: 1`; only one runs on GPU at a time. Stable: swinir on GPU (enhance UX); yolo at 0 until detect or second GPU.

**Blockers for chart hardening:** GPU tolerations, T4-sized CPU requests, optional sentinel2 `deploy` toggle / minReplicas override.

MT-R4 (512+ crop Playwright) not run — optional follow-up with swinir on GPU.

**Prior:** psi-21 CPU pass (2026-07-01); GPU tiers deferred on psi-21 (no GPU nodes).
