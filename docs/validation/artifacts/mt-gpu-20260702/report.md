# MT-GPU validation — cloudtest2 (2026-07-02)

<!-- Assisted by: cursor, claude -->

| Field         | Value                                                                                            |
| ------------- | ------------------------------------------------------------------------------------------------ |
| Date          | 2026-07-02                                                                                       |
| Cluster       | cloudtest2 (`default/api-cloudtest2-pool-44ltq-aws-rh-ods-com:6443/htpasswd-cluster-admin-user`) |
| RHOAI         | 3.5.0-ea.2 (CSV Succeeded)                                                                       |
| GPU node      | `ip-10-0-23-248.us-east-2.compute.internal` — allocatable `nvidia.com/gpu=1` (Tesla T4)          |
| Chart merge   | PR #94 @ `032cefa`                                                                               |
| Helm baseline | rev **6** (pre-validation)                                                                       |
| Helm final    | rev **14** (deployed)                                                                            |
| Verdict       | **pass** (MT-3A/3B/4b with documented operator mitigations)                                      |

## Preflight

| Check              | Result                                                                     |
| ------------------ | -------------------------------------------------------------------------- |
| `oc whoami`        | `htpasswd-cluster-admin-user`                                              |
| RHOAI CSV          | 3.5.0-ea.2                                                                 |
| Allocatable GPU    | 1× T4                                                                      |
| `quay-pull-secret` | present in `caisat`                                                        |
| TLS pattern        | `curl -sk` for OpenShift routes (self-signed); in-cluster tests on `:8080` |

## Helm sequence

**Pre-revision:** `PRE_REV=6`

**Step 1 (T4 deploy)** — required `--server-side=false` (SSA conflicts with prior `kubectl-patch`) and explicit `computeProfile.gpuTolerations` (`--reuse-values` drops chart-default tolerations):

```bash
helm upgrade caisat ./chart -n caisat --reuse-values --server-side=false \
  --set computeProfile.name=t4 \
  --set computeProfile.gpuAvailable=true \
  --set 'computeProfile.gpuTolerations[0].key=nvidia.com/gpu' \
  --set 'computeProfile.gpuTolerations[0].operator=Exists' \
  --set 'computeProfile.gpuTolerations[0].effect=NoSchedule' \
  --set model.resources.requests.cpu=2 \
  --set model.resources.limits.cpu=4 \
  --set model.minReplicas=1 \
  --set detection.minReplicas=0 \
  --set sentinel2Model.minReplicas=0 \
  --set pipelines.runAnalysis=false \
  --set pipelines.enabled=false \
  --set kserve.preferBinary=false
```

Deployed @ helm rev **11** (after failed revs 7–9 from SSA/tolerations-null).

## MT-3A — swinir on GPU

| Test                      | Result                                                         |
| ------------------------- | -------------------------------------------------------------- |
| IS Ready                  | pass (after deleting stale pre-chart pod blocking GPU rollout) |
| `/v2/models/swinir/ready` | HTTP 200                                                       |
| JSON infer 256→1024       | **pass** — 44.20 s, output `[1, 3, 1024, 1024]`                |

## MT-3B — yolo sequential

| Test                           | Result                                                                                         |
| ------------------------------ | ---------------------------------------------------------------------------------------------- |
| swinir scaled to 0 / yolo to 1 | helm rev **12**; `oc patch` cleared stale `maxReplicas=0` on yolo IS from prior manual patches |
| yolo IS Ready + JSON infer     | **pass** — 1.41 s, output `[1, 20, 8400]`                                                      |
| Operator note                  | KServe controller lag on minReplicas; brief `oc scale deploy` needed to free GPU               |

## MT-4b — UX restore

| Test                                | Result                                                                                                                  |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `/api/capabilities` (both backends) | **pass** — `gpu_tier=t4`, `max_crop=512`                                                                                |
| Enhance 256→1024                    | **pass** — in-cluster HTTP 200, 61.3 s, PNG 1024×1024 (route times out ~59 s; use in-cluster or increase Route timeout) |
| Detect route                        | **pass** — HTTP 200, 1.76 s (requires yolo on GPU; scale swinir to 0 first on single-GPU node)                          |
| Helm restore                        | rev **14** — `model.minReplicas=1`, `detection.minReplicas=0`                                                           |

## Blockers / follow-ups

1. **`--reuse-values` + `gpuTolerations`:** chart defaults not merged; document explicit `--set` or `--reset-values` in `chart/README.md`.
2. **SSA vs prior patches:** use `--server-side=false` on clusters with manual IS patches until drift cleared.
3. **KServe replica lag:** minReplicas changes may need `oc scale deploy` on single-GPU clusters.
4. **Route timeout:** enhance ~61 s exceeds default Route idle timeout (~59 s); backend succeeds in-cluster.

## Rollback reference

```bash
helm rollback caisat 6 -n caisat --server-side=false
oc delete job -n caisat -l app.kubernetes.io/component=pipeline --ignore-not-found
```
