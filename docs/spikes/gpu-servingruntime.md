# Spike: RHOAI GPU ServingRuntime

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                                             |
| --------------- | --------------------------------------------------------------------------------- |
| Date            | 2026-07-01 (Wave 8 re-test)                                                       |
| Verdict         | **partial** — CPU cluster pass; GPU tiers deferred (no GPU nodes / expired creds) |
| Cluster/profile | psi-21 `computeProfile.name=cpu`; helm rev 19 deployed                            |
| Follow-up       | Re-test T4/L40S/Hopper on GPU clusters when credentials restored                  |

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

| Tier   | Ready | Infer 200 | MT-4b caps API | Status       | Notes                                                                                                              |
| ------ | ----- | --------- | -------------- | ------------ | ------------------------------------------------------------------------------------------------------------------ |
| CPU    | pass  | pass      | pass           | **pass**     | swinir `/ready` HTTP 200; JSON infer 52.6 s → `[1,3,1024,1024]`; enhance + detect `/api/capabilities` max_crop=256 |
| T4     | —     | —         | local defer    | **deferred** | psi-21: no `nvidia.com/gpu` nodes; nvd-srv-18: creds expired; helm template + local caps defer OK                  |
| L40S   | —     | —         | local defer    | **deferred** | same as T4                                                                                                         |
| Hopper | —     | —         | local defer    | **deferred** | same as T4                                                                                                         |

Chart ships `computeProfile.name` and `computeProfile.gpuAvailable` values. Backends expose `GET /api/capabilities` with deferral caps per plan.
Re-test GPU tiers on T4/L40S/Hopper clusters when scheduled; set `GPU_AVAILABLE=true` only after Ready + infer 200.

**Wave 8 (2026-07-01):** psi-21 has zero GPU-labeled nodes (`oc get nodes -l nvidia.com/gpu` empty). Alternate contexts (`nvd-srv-18`, `qualitycustomer`) require re-login.

Local validation: helm template emits `nvidia.com/gpu: "1"` for t4/l40s/hopper with `gpuAvailable=true`; capabilities API returns `max_crop=256`, `gpu_deferred=True` when `GPU_AVAILABLE=false`.

MT-R4 (512+ crop Playwright) not run — requires live GPU tier.

**Prior waiver (2026-06-30):** No CAIsat deploy on accessible GPU cluster; superseded by Wave 8 CPU pass on psi-21.
