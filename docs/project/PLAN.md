# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for operational follow-up, merge gates, and spike outcomes. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `7eb9a76` (2026-07-01). **All planned phases (0–23) complete.** Wave 5 in progress (W5-P0–P4 **done** — MT-R3a pass; chart PR #82 merged).
CI parallelization MT-CP-0→5 **complete** (MT-CP-3 deferred).
Open operational items below; use feature branches for follow-up; never push `main`.

**Archive:** Completed phased work (phases **0–23**) → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary, archived):** Cursor artifact `~/.cursor/plans/caisat_plan_bootstrap_3c3a4d19.plan.md` — archived 2026-06-29; historical OpenSSF detail, parallel execution, smoke profiles;
`~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only.

**Renumbering (2026-06-29):** Removed serial suffixes (`1A`/`1B` → Phases 1–2). OpenSSF supply-chain = Phases **4–6**. Former phases 3–18 → **7–19**.

**Renumbering (2026-06-30):** Inserted Phases **8–11** (OpenSSF score improvement); former **8–19 → 12–23**. Spike tracks `8-onnx`/`8-binary` → **`12-onnx`/`12-binary`**.

---

## Verification artifact

| Claim                   | Path                                                                                         | Evidence                                    | Status                |
| ----------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------- | --------------------- |
| MODEL_ENDPOINT required | [`backend/app.py`](../../backend/app.py) L35–39                                              | `if not MODEL_ENDPOINT: raise`              | ok                    |
| CI harden-runner block  | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | egress block + allowlists; MT-CP-5 PR #62   | ok                    |
| CI binary smoke job     | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | required CI job `smoke-binary`; MT-CP-2 #60 | ok                    |
| CI timing metrics       | [`docs/validation/ci-timing.md`](../validation/ci-timing.md)                                 | MT-CP-1 #59; MT-CP-3 gate p50 ≈ 1.2 min     | ok (MT-CP-3 deferred) |
| CI smoke venv cache     | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | `.venv-smoke` cache; MT-CP-4 PR #61 −14.7%  | ok                    |
| Helm metadata fix       | [`chart/templates/backend.yaml`](../../chart/templates/backend.yaml)                         | single metadata block                       | ok                    |
| `make smoke` health     | [`Makefile`](../../Makefile), [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)       | health in required CI job `pre-commit`      | ok                    |
| Baseline smoke phases   | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md)                       | phases 7/13/14/16                           | ok                    |
| Quay gate               | [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md)                                         | **pass** (fork mirror); upstream **fail**   | ok                    |
| Chart image default     | [`chart/values.yaml`](../../chart/values.yaml)                                               | `thom_at_redhat/caisat` (public)            | ok                    |
| OpenSSF Scorecard       | [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) | **6.9** @ `d15eafe` (MT-W14 post-merge)     | ok                    |
| Scorecard gap plan      | [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md)                               | Phases 8–11 + Wave 5                        | ok                    |
| SAST (CodeQL)           | [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml)       | PR #29; Python + JS; **10/10**              | ok                    |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                                           | PR #24; reporting + supported versions      | ok                    |
| Workflow permissions    | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | PR #24; `permissions: contents: read`       | ok                    |
| README Scorecard badge  | [`README.md`](../../README.md)                                                               | contributor fork slug (see badge URL)       | ok (fork)             |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                                | pre-commit, smoke-binary, Scorecard, CodeQL | ok (fork)             |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #26; `markdown-link-check@3.14.2` pinned | ok                    |
| Pre-commit SHA pins     | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | Phase 11 PR #41; 13 hook repos + exact pins | ok                    |
| Scorecard pre-commit    | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #42; local Scorecard hook + npm vuln fix | ok                    |
| Upstream sync           | fork `main` @ `4abef20`                                                                      | PR #43 inbound sync                         | ok (inbound)          |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                                 | ML spikes documented (PR #45)               | ok                    |
| Phases 12–23 merge      | PR #45 @ `ee3f1b3`                                                                           | phases-12-23 integration                    | ok                    |
| PLAN post-23 archive    | PR #47 @ `4abef20`                                                                           | PLAN archive merged                         | ok                    |
| Local smoke profiles    | [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh) L133–143                            | `health` + `binary` (pytest `tests/`)       | ok                    |
| Pytest suite            | [`tests/`](../../tests/)                                                                     | kserve_v2 + capabilities; both backends     | ok                    |
| `make test`             | [`Makefile`](../../Makefile)                                                                 | pytest via `requirements-dev.txt`           | ok                    |
| Cluster baseline        | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) L101–106              | **pass** @ MT-R3a 2026-07-01                | ok                    |
| Frontend Containerfile  | [`frontend/Containerfile`](../../frontend/Containerfile) L1                                  | `ubi9/nodejs-20`; PR #70 @ `8c44336`        | ok                    |
| SDD specs index         | [`docs/specs/README.md`](../specs/README.md)                                                 | CAP/KSRV/DRL **accepted** (MT-R3a pass)     | ok (W5-P4)            |

**Last verified:** fork `main` @ `7eb9a76` (2026-07-01); W5-P4 MT-R3a **pass**; PR #81/#82 merged; prior MT-R5 @ `e2a7704`; CI parallelization MT-CP-3 deferred;
Scorecard **6.9** @ `d15eafe` (MT-W14a/b); SAST **10/10**

**Revalidate:** `docs/project/PLAN.md`, `docs/specs/`, `docs/validation/baseline-smoke.md`, `docs/validation/ci-timing.md`, `docs/spikes/README.md`,
`docs/spikes/scorecard-gaps.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** MT-4a full crop after redeploy @ `b367b63`; GPU tiers **deferred**; upstream outbound PR; Wave 5 **Full** closure blocked on `12-binary`

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

All phased work archived in [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Operational follow-up only:

| ID        | Track                | Status       | Next action                                                                                            |
| --------- | -------------------- | ------------ | ------------------------------------------------------------------------------------------------------ |
| tests     | Pytest scaffold      | **pass**     | W5-P1a merged — `tests/` + `make test` in `make check`; CI `smoke-binary` runs standalone pytest       |
| baseline  | Phase 13 sign-off    | **pass**     | MT-R3a **pass** — 100%/150% layout + box overlay — `baseline-smoke.md` L157+; DRL-001 **accepted**     |
| binary    | 12-binary / Phase 14 | **fail**     | ea.1 JSON pass / binary HTTP 500; RHOAI ticket required for waiver — `binary-kserve-v2.md`             |
| crop      | Phase 16 sign-off    | **pass**     | CPU **pass** @ `e2a7704`; JSON 256→1024; `KSERVE_PREFER_BINARY=false` — `baseline-smoke.md`            |
| gpu       | Phase 15 deferral    | **waiver**   | MT-3 skipped; T4/L40S/Hopper deferred; re-test 2026-07-31 or GPU clusters — `gpu-servingruntime.md`    |
| scorecard | Optional             | **triaged**  | **6.9** @ `d15eafe`; pin 10/10 (W14a); OSV triage done (W14b) — `scorecard-gaps.md`                    |
| upstream  | Outbound PR          | **deferred** | PR back to `rh-ai-quickstart/CAIsat` deferred; gate MT-1b + MT-2 outcomes recorded (user decision)     |
| ci-split  | MT-CP-3 job split    | **deferred** | p50 `pre-commit` ≈ 1.2 min; gate > ~12 min — `ci-timing.md`; revisit if CI grows or hooks add weight   |
| phase-25  | S4 → SeaweedFS       | **planned**  | Author `seaweedfs.yaml`, update values/seed/dspa/change-detection; `helm template` gate — see Phase 25 |

---

## Spike outcomes (archived)

Detail in [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md#phases-1223-integration-pr-45) and spike docs. Summary:

| Spike             | Verdict                                    | Artifact                                                   |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------- |
| SwinIR ONNX       | **pass** — dynamic H/W; 256→1024 native 4× | [`swinir-onnx.md`](../spikes/swinir-onnx.md)               |
| Binary KServe v2  | **fail** — JSON OK; binary HTTP 500        | [`binary-kserve-v2.md`](../spikes/binary-kserve-v2.md)     |
| RHOAI GPU runtime | **blocked** — CPU pass; GPU tiers deferred | [`gpu-servingruntime.md`](../spikes/gpu-servingruntime.md) |
| YOLO11-OBB eval   | **skipped** — Phase 17 QA sufficient       | [`yolo11-obb-eval.md`](../spikes/yolo11-obb-eval.md)       |

---

## Decisions

| Topic       | Decision                                                                                                               |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| Priority    | Larger context (512+ crop, tiled SR) — shipped Phase 16                                                                |
| GPU         | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override; tiers **deferred**                              |
| Detection   | Demo quality OK; YOLO11 eval **skipped**; OBB + SAHI shipped Phase 17                                                  |
| Git         | Push-as-you-go on feature branches; CI before push (`make push`)                                                       |
| PLAN source | This file after Phase 3 merge; phased work archived post-23                                                            |
| Quay        | Phase 0 **pass** on fork (`thom_at_redhat/caisat` public mirror); upstream `rh-ai-quickstart` **fail**                 |
| OpenSSF     | Phases 4–6 on fork first; badge uses fork slug                                                                         |
| Upstream    | Fork synced from upstream @ `0e4281e` (PR #43); PR back to `rh-ai-quickstart/CAIsat` still deferred                    |
| Scorecard   | **6.0** @ `acb9a79`; gap plan Phases 9–11 done; see `scorecard-gaps.md`                                                |
| 12-binary   | **fail** @ RHOAI 3.4.0 (2026-07-01); JSON pass / binary HTTP 500; RHOAI ticket required; Phase 14 JSON-fallback active |
| Spike docs  | Cluster names **never** in spike docs — use `<namespace>` placeholders                                                 |

---

## Open items

Follow-up after Phases **0–23** merge (PR #45 @ `ee3f1b3`; PLAN archive PR #47 @ `4abef20`). Code merged; cluster validation and spike gaps remain.

| Item              | Detail                                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| Binary spike fail | `12-binary` **fail** @ ea.1 (2026-07-01); JSON pass / binary HTTP 500; RHOAI ticket — `binary-kserve-v2.md`     |
| Phase 13 baseline | Cluster **pass** @ `b367b63` (PR #65); MT-R3a **pass** 2026-07-01 — `baseline-smoke.md` L157+                   |
| Crop sign-off     | **pass (CPU)** @ `e2a7704`; JSON 256→1024; `KSERVE_PREFER_BINARY=false` — `baseline-smoke.md`                   |
| GPU deferral      | MT-3 **skipped**; T4/L40S/Hopper deferred — `gpu-servingruntime.md`                                             |
| Cluster redeploy  | **pass** W5-P3 frontend + helm rev **3** (PR #82 chart); route **200** — `baseline-smoke.md`                    |
| MT-R3a layout     | **pass** — Playwright 100%/150%; DRL-001 **accepted** — `baseline-smoke.md` L157+; artifacts `mt-r3a-20260701/` |

### Wave 5 detection layout sign-off (W5-P4 / MT-R3a)

| Field       | Value                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------- |
| Git SHA     | `7eb9a76` (fork `main` post PR #81/#82)                                                           |
| Chart fix   | PR #82 @ `6459038` — `KSERVE_PREFER_BINARY=false` on SR + detection backends                      |
| Helm rev    | **3** (cluster)                                                                                   |
| DRL-001     | **accepted** — `detection-results-layout.md`                                                      |
| Verdict     | **pass** — enhance + detect 200; 100% row + 150% stack; 1 detection with OBB overlay              |
| Artifacts   | `docs/validation/artifacts/mt-r3a-20260701/` (`01-100pct-*.png`, `02-150pct-*.png`, `report.md`)  |
| Wave 5 Full | **blocked** — Phase 14 / `12-binary` infer HTTP 500; JSON fallback active — `binary-kserve-v2.md` |

### Wave 5 frontend Quay (W5-P2 / MT-W1b)

| Field                         | Value                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Git SHA                       | `2dd097b` (`2dd097bac0a3a220cba2ee91dd11fce4704be685`)                                                                   |
| Containerfile                 | `ubi9/nodejs-20` in-container build (post-PR #70)                                                                        |
| Tags pushed                   | `frontend`, `frontend-2dd097b`, retention `frontend-pre-20260701`                                                        |
| Pre-push digest (`:frontend`) | `sha256:158ea4995c01ca394f9b07ad5e34e8bd0b6006c0ead1a716ad632d57f36a8136`                                                |
| Post-push manifest digest     | `sha256:01ffd7825c5f71d35f84613822157380471dec4d70274aae69223632ee961a7e`                                                |
| Image config                  | `sha256:107bbf18263f1f8b4b463bf7e817df5eb0c1f3ebbe38d0524b19d4bd095ace0d`                                                |
| Anonymous pull                | **fail** — Quay returns unauthorized without credentials (cluster uses `quay-pull-secret`)                               |
| Rollback                      | `podman tag quay.io/thom_at_redhat/caisat:frontend-pre-20260701 quay.io/thom_at_redhat/caisat:frontend && podman push …` |

### Wave 5 frontend cluster rollout (W5-P3 / MT-W2b)

| Field                | Value                                                                                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| Git SHA              | `2dd097b`                                                                                                |
| Method               | `oc rollout restart deployment/caisat-frontend` (`pullPolicy: Always`, tag `:frontend`)                  |
| Helm                 | `--reuse-values` upgrade **blocked** (chart drift); rolled back; release rev **2** (verified 2026-07-01) |
| Pre-rollout imageID  | `sha256:158ea4995c01ca394f9b07ad5e34e8bd0b6006c0ead1a716ad632d57f36a8136`                                |
| Post-rollout imageID | `sha256:01ffd7825c5f71d35f84613822157380471dec4d70274aae69223632ee961a7e`                                |
| Pod (post)           | `caisat-frontend-6bf8f9754d-xnw7j`                                                                       |
| Route smoke          | HTTP **200** (edge TLS)                                                                                  |
| MT-R3a               | **pass** — detect 200 after `KSERVE_PREFER_BINARY=false` (PR #82); 100%/150% layout Playwright           |

---

## Open blockers

| Blocker               | Detail                                                                                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MLServer binary       | **fail** @ 3.4.0 (2026-07-01): MLServer `1.7.1+rhaiv.8`; JSON pass / binary HTTP 500 both predictors; RHOAI ticket required for waiver                              |
| RHOAI ea.2            | **deferred** — ea.2 bundle manifest unknown on `registry.redhat.io`; cluster on **3.4.0** fallback; does not gate MT-R3a                                            |
| Pull secrets          | `quay-pull-secret` chart default merged (PR #79 @ `2090e98`); `rhoai-quay-pull` **not created** — see [`chart/README.md`](../../chart/README.md) two-secret pattern |
| KSERVE binary default | Chart sets `KSERVE_PREFER_BINARY=false` on both backends (PR #82 @ `6459038`); cluster helm rev **3** verified MT-R3a                                               |
| Phase 14 binary-only  | JSON fallback active until binary round-trip passes on cluster                                                                                                      |

---

## Smoke profiles

| Profile      | Phases | Assertions                                                               | Automation                                                                                       |
| ------------ | ------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| **health**   | 7+     | `/health` 200 on both backends                                           | Required CI job `pre-commit` (`make smoke`)                                                      |
| **baseline** | 13+    | health + enhance/detect 200 + valid payloads                             | Manual — `baseline-smoke.md`                                                                     |
| **post-p0**  | 13+    | baseline + capture/zoom 1×/2×/4×                                         | Manual                                                                                           |
| **binary**   | 14+    | Local: `pytest tests/` (kserve encode/decode). Cluster: infer round-trip | Required CI job `smoke-binary` (standalone pytest + `SMOKE_SKIP_HEALTH=1` smoke); cluster manual |
| **crop**     | 16+    | baseline/binary + profile default crop size                              | Manual                                                                                           |

See [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md).

---

## Git rules

Feature branches only; never push `main`; no `--no-verify`. Run `make check` before push (`make push`).

---

## Phase 25 — Replace S4 with SeaweedFS

| Field        | Value                                                                                  |
| ------------ | -------------------------------------------------------------------------------------- |
| Goal         | Swap S4 for SeaweedFS S3 gateway; keep bucket `satellite-images` and boto3 unchanged   |
| Status       | **planned**                                                                            |
| Branch       | `feature/seaweedfs-phase`                                                              |
| Dependencies | Storage class (`standard-csi`); DSPA S3 compat; SeaweedFS OCI image cluster-accessible |

### Background

S4 (`quay.io/rh-aiservices-bu/s4`) is a demo-only S3 service that bundles a Ceph RGW wrapper with no upstream release cadence or production support path.
SeaweedFS provides an S3-compatible gateway with an active release cycle and a single-process `weed server` mode suitable for demo and small-cluster deployments.
The boto3 call surface and bucket name are unchanged; only the pod/service/values keys change.

### Scope

**In scope:**

- `chart/templates/s4.yaml` → replace with `chart/templates/seaweedfs.yaml` (Deployment, PVC, ConfigMap, Secret, Service; drop S4 web-UI Route)
- `chart/values.yaml` — rename `s4` key to `seaweedfs`; keep `credentials`, `seed.bucketName`, `storageClassName` sub-keys
- `chart/templates/pipeline-dspa.yaml` — update `externalStorage.host` to SeaweedFS service FQDN
- `chart/templates/s4-seed-job.yaml` → update init-container wait target to `seaweedfs` Deployment; rename file to `storage-seed-job.yaml`
- `chart/templates/s4-seed-serviceaccount.yaml` → update component labels; rename file to `storage-seed-serviceaccount.yaml`
- `chart/templates/pipeline-secret.yaml` — reference SeaweedFS credentials Secret
- `chart/templates/backend-changedetection.yaml` — update S3 endpoint env var to SeaweedFS service
- `chart/README.md` — update storage section; replace S4 references

**Out of scope:**

- `backend/` and `backend-detection/` — no direct S3 dependency; enhance/detect UX unaffected
- `frontend/` — no S3 dependency
- DSPA pipeline DAG logic — only the storage endpoint changes

### Tasks

- [ ] Pin SeaweedFS image: mirror `docker.io/chrislusf/seaweedfs:<tag>` to Quay or use a public OCI mirror; record digest in `values.yaml`
- [ ] Author `chart/templates/seaweedfs.yaml` — Deployment (`weed server -s3 -s3.port=7480 -dir=/data`), PVC (`/data`), ConfigMap (region, endpoint), Secret (accessKey/secretKey), Service (port 7480)
- [ ] Remove `chart/templates/s4.yaml`
- [ ] Rename and update `chart/templates/s4-seed-job.yaml` → `storage-seed-job.yaml`; init-container waits on SeaweedFS Deployment; S3 endpoint env `http://<release>-seaweedfs.<ns>.svc.cluster.local:7480`
- [ ] Rename `chart/templates/s4-seed-serviceaccount.yaml` → `storage-seed-serviceaccount.yaml`; update component labels
- [ ] Update `chart/values.yaml`: rename all `s4` keys to `seaweedfs`; update image repository/tag; keep `seed.bucketName: satellite-images`, credentials keys, `storageClassName`
- [ ] Update `chart/templates/pipeline-dspa.yaml`: `externalStorage.host` → `<release>-seaweedfs.<ns>.svc.cluster.local:7480`
- [ ] Update `chart/templates/pipeline-secret.yaml`: reference `seaweedfs` credentials Secret name
- [ ] Update `chart/templates/backend-changedetection.yaml`: S3 endpoint env vars → SeaweedFS service
- [ ] Update `chart/README.md`: replace S4 references with SeaweedFS; document `weed server` mode and port
- [ ] `helm template test ./chart` passes (`make check`)
- [ ] `pre-commit run --all-files` passes
- [ ] Record Phase 25 outcome row in `PLAN_COMPLETED.md`

### Acceptance criteria

- [ ] `helm template test ./chart` produces no `s4` component references
- [ ] Seed job creates bucket `satellite-images` and uploads ≥1 test image without boto3 changes
- [ ] `DataSciencePipelinesApplication` `externalStorage.host` resolves to SeaweedFS service
- [ ] `backend-changedetection` `/health` returns 200; S3 read/write confirmed against SeaweedFS
- [ ] Pipeline run artifact uploads/downloads succeed (SeaweedFS S3 path)
- [ ] Enhance/detect backends unaffected — `/health` 200 both backends; no S3 path in enhance/detect code

### Notes

- SeaweedFS `weed server` runs master + volume + S3 gateway in a single process; no separate filer needed for demo scale.
- Port 7480 matches the S4 S3 port; all existing service-internal references (`svc.cluster.local:7480`) carry over once the Service name changes from `s4` to `seaweedfs`.
- `KSERVE_PREFER_BINARY` is unrelated to this phase — change-detection uses direct S3, not KServe inference.
- Ties to the optional change-detection path only; core satellite enhance/detect UX is unaffected.
