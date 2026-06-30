# Spike: RHOAI GPU ServingRuntime

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                                                |
| --------------- | ------------------------------------------------------------------------------------ |
| Date            | 2026-06-30                                                                           |
| Verdict         | **blocked** — GPU tiers deferred; CPU profile validated locally                      |
| Cluster/profile | Chart `computeProfile.name=cpu`; GPU nodes not scheduled this pass                   |
| Follow-up       | GPU tiers (512+ crop) **deferred** until scheduled; CPU partial crop (256) validated |

For per-tier commands and deferral caps, see the GPU tier table in [`README.md`](README.md).

## Command

```bash
# Helm GPU profile (requires GPU node + GPU_AVAILABLE=true)
helm template test ./chart --set computeProfile.name=t4 --set computeProfile.gpuAvailable=true \
  | grep -A2 nvidia.com/gpu

# Capabilities API (local smoke)
cd backend && python3 -c "import os; os.environ['COMPUTE_PROFILE']='t4'; os.environ['GPU_AVAILABLE']='false'; from capabilities import get_capabilities; print(get_capabilities())"

# Cluster Ready + infer (when GPU available)
oc get inferenceservice -n <namespace>
oc exec -n <namespace> deploy/swinir-predictor -c kserve-container -- \
  curl -sf http://localhost:8080/v2/models/swinir/ready
```

## Output (snippet)

```text
# helm template (t4 profile, gpuAvailable=true)
          nvidia.com/gpu: "1"

# capabilities with deferred GPU
{'profile': 't4', 'gpu_tier': 't4', 'max_crop': 256, 'max_tile': 256, 'tiling_enabled': False, 'gpu_deferred': True, ...}
```

## Notes

| Tier   | Ready | Infer 200 | Status   | Cap when deferred       |
| ------ | ----- | --------- | -------- | ----------------------- |
| CPU    | pass  | N/A       | **pass** | max_crop=256, no tiling |
| T4     | —     | —         | deferred | capped to CPU limits    |
| L40S   | —     | —         | deferred | capped to CPU limits    |
| Hopper | —     | —         | deferred | capped to CPU limits    |

Chart ships `computeProfile.name` and `computeProfile.gpuAvailable` values. Backends expose `GET /api/capabilities` with deferral caps per plan.
Re-test GPU tiers on T4/L40S/Hopper clusters when scheduled; set `GPU_AVAILABLE=true` only after Ready + infer 200.
