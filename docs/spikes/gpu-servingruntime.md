# Spike: RHOAI GPU ServingRuntime

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------- |
| Date            | 2026-07-02 (MT-GPU validate post PR #94 chart hardening)                                     |
| Verdict         | **pass** — T4 tier MT-3A/3B/4b on cloudtest2; L40S/Hopper N/A; single-GPU sequential pattern |
| Cluster/profile | cloudtest2 `computeProfile.name=t4`, `gpuAvailable=true`; helm rev **14** deployed           |
| Follow-up       | Document `--reuse-values` + `gpuTolerations`; Route timeout for enhance >60 s; KServe lag    |

Artifact: [`docs/validation/artifacts/mt-gpu-20260702/report.md`](../validation/artifacts/mt-gpu-20260702/report.md)

For per-tier commands and deferral caps, see the GPU tier table in [`README.md`](README.md).

## Command

```bash
# Helm GPU profile (chart @ 032cefa — tolerations + hybrid resources + minReplicas)
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

# Capabilities API (OpenShift route — self-signed TLS: curl -sk)
curl -sk "https://<backend-route>/api/capabilities"

# Cluster Ready + infer (when GPU available)
oc get inferenceservice -n caisat
oc exec -n caisat deploy/swinir-predictor -c kserve-container -- \
  curl -sf http://localhost:8080/v2/models/swinir/ready
```

## Output (snippet)

```text
# helm template (t4 profile, gpuAvailable=true) @ 032cefa
          nvidia.com/gpu: "1"
    tolerations:
      - effect: NoSchedule
        key: nvidia.com/gpu
        operator: Exists

# capabilities with GPU active (helm rev 14)
{"gpu_tier":"t4","max_crop":512,"max_tile":512,"tiling_enabled":true,"scale_factor":4,
 "infer_timeout_seconds":300,"profile":"t4","gpu_deferred":false,"kserve_prefer_binary":false}

# swinir JSON infer on T4 (256→1024) — MT-3A 2026-07-02
JSON OK 44.20 s HTTP 200 out [1, 3, 1024, 1024]

# yolov8m-satelite JSON infer on T4 — MT-3B 2026-07-02
JSON OK 1.41 s HTTP 200 out [1, 20, 8400]

# enhance (256→1024 PNG) — in-cluster MT-4b 2026-07-02
enhance HTTP 200 time 61.3s size 289915 — PNG 1024 x 1024

# detect route — MT-4b 2026-07-02 (yolo on GPU; swinir scaled to 0)
detect HTTP 200 time 1.76s — {"detections":[],"count":0,...}
```

## Notes

| Tier   | Ready | Infer 200 | MT-4b caps API | Status   | Notes                                                                                                        |
| ------ | ----- | --------- | -------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| CPU    | pass  | pass      | pass           | **pass** | psi-21: swinir `/ready` HTTP 200; JSON infer 52.6 s → `[1,3,1024,1024]`; max_crop=256                        |
| T4     | pass  | pass      | pass           | **pass** | cloudtest2: 1× Tesla T4; chart tolerations + 2 CPU swinir; sequential GPU; caps `max_crop=512` @ helm rev 14 |
| L40S   | —     | —         | —              | **N/A**  | MT-R4-L40S defer @ 2026-07-02 — no L40S nodes; cap `max_crop=768` per `capabilities.py`                      |
| Hopper | —     | —         | —              | **N/A**  | MT-R4-HOPPER defer @ 2026-07-02 — no Hopper nodes; cap `max_crop=1024` per `capabilities.py`                 |

Chart ships `computeProfile.gpuTolerations`, hybrid `*.resources`, and per-IS `minReplicas`. Backends expose `GET /api/capabilities` with deferral caps per plan.
Set `gpuAvailable=true` only after Ready + infer 200.

### cloudtest2 GPU validation (2026-07-02, chart hardening)

**Pre-flight:** 1 GPU worker (`nvidia.com/gpu.product=Tesla-T4`, allocatable `nvidia.com/gpu=1`). RHOAI **3.5.0-ea.2**.

**Chart hardening (PR #94 @ `032cefa`):** GPU tolerations, hybrid resources, `minReplicas` on all three InferenceServices — no manual IS toleration/CPU patches required on greenfield deploy.

**Operator notes (clusters with prior manual patches):**

1. **`--reuse-values`** omits chart-default `gpuTolerations` — pass explicit `--set computeProfile.gpuTolerations[...]` or use `-f` values file.
2. **SSA conflicts** with legacy `kubectl-patch` field managers — use `--server-side=false` until drift cleared.
3. **Stale `maxReplicas=0`** on yolo from old patches — verify IS spec after upgrade.
4. **KServe controller lag** on minReplicas — may need `oc scale deploy` on single-GPU nodes during MT-3B/4b transitions.
5. **Route timeout** — enhance ~61 s exceeds default Route idle timeout; in-cluster `:8080` succeeds; increase Route timeout for external UX tests.
6. **Single GPU contention** — swinir on GPU (enhance UX); yolo at `minReplicas=0` until detect; scale swinir to 0 before yolo infer on one T4.

**sentinel2** at `minReplicas=0` via Helm (no manual patch).

MT-R4 (512+ crop Playwright) not run — optional follow-up with swinir on GPU.

**Prior:** Wave 8 pass @ helm rev 6 (2026-07-01, manual patches); psi-21 CPU pass.

---

## MT-R4 — L40S / Hopper tier deferral (2026-07-02)

**MT-IDs:** MT-R4-L40S, MT-R4-HOPPER | **Operator:** hardware-gated | **Clusters:** psi-21, cloudtest2

### Hardware survey

| Cluster    | GPU workers | Products observed | L40S | Hopper |
| ---------- | ----------- | ----------------- | ---- | ------ |
| psi-21     | 0           | —                 | N/A  | N/A    |
| cloudtest2 | 1           | `Tesla-T4` only   | N/A  | N/A    |

No L40S or Hopper nodes available on current test clusters. Operator validation requires hardware access not scheduled for this wave.

### Expected caps (`backend/capabilities.py`)

| Tier   | `max_crop` | `max_tile` | `tiling_enabled` | Status  |
| ------ | ---------- | ---------- | ---------------- | ------- |
| l40s   | 768        | 512        | true             | **N/A** |
| hopper | 1024       | 512        | true             | **N/A** |

Caps are implemented in chart/backends; cluster infer + MT-4b Playwright at 512+ crop deferred until hardware available.

### Verdict

| MT-ID        | Verdict | Rationale                                         |
| ------------ | ------- | ------------------------------------------------- |
| MT-R4-L40S   | **N/A** | No L40S nodes; deferral counts as pass per plan   |
| MT-R4-HOPPER | **N/A** | No Hopper nodes; deferral counts as pass per plan |

**Follow-up:** Re-run when L40S/Hopper workers are provisioned; use `computeProfile.name=l40s|hopper` + `gpuAvailable=true` Helm pattern from T4 section above.
