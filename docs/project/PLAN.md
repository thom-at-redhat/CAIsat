# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for operational follow-up, merge gates, and spike outcomes. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `b625b56` (2026-07-09). Phases 0–23 **complete**. Wave 5 **Partial** (canonical); **Full** + RHOAI operator cases **deferred** (MT-TICKET, MT-EA2-\*, MT-2-RETEST, MT-W5-FULL).
Phase 25 SeaweedFS chart merged (PR #85); cluster prove-out **pass**; changedetection image + `/health` **pass**; Wave 7 pipeline runAnalysis E2E **pass** (2026-07-01).
Wave 8 T4 GPU validation **pass** (PR #94 chart @ `032cefa`, PR #96 MT-GPU artifact); Wave 9 ea.2 **partial pass** (cloudtest2 PR #92; psi-21 Path A operator upgrade **pass** 2026-07-03).
Wave 10 ecosystem tracks **complete** (PRs #97–#102). OpenSSF Phases **26–29 + 31 complete** @ `31606a8` (PRs #104–107, #108, #114–116); Phase 30 **deferred** @ **2026-09-27** — see tables below.
CI parallelization MT-CP-0→5 **complete** (MT-CP-3 deferred).
Open operational items below; use feature branches for follow-up; never push `main`. MT-2-RETEST @ psi-21 ea.2 **complete** 2026-07-06 — JSON **pass** / binary **fail**;
RHOAI ticket **pending operator filing**.

**Archive:** Completed phased work (phases **0–23**) → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary, archived):** Cursor artifact `~/.cursor/plans/caisat_plan_bootstrap_3c3a4d19.plan.md` — archived 2026-06-29; historical OpenSSF detail, parallel execution, smoke profiles;
`~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only.

**Renumbering (2026-06-29):** Removed serial suffixes (`1A`/`1B` → Phases 1–2). OpenSSF supply-chain = Phases **4–6**. Former phases 3–18 → **7–19**.

**Renumbering (2026-06-30):** Inserted Phases **8–11** (OpenSSF score improvement); former **8–19 → 12–23**. Spike tracks `8-onnx`/`8-binary` → **`12-onnx`/`12-binary`**.

---

## Verification artifact

| Claim                   | Path                                                                             | Evidence                                                        | Status                |
| ----------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------- |
| MODEL_ENDPOINT required | [`backend/app.py`](../../backend/app.py) L35–39                                  | `if not MODEL_ENDPOINT: raise`                                  | ok                    |
| CI harden-runner block  | [pre-commit.yaml](../../.github/workflows/pre-commit.yaml)                       | egress block; MT-CP-5 PR #62                                    | ok                    |
| CI binary smoke job     | [pre-commit.yaml](../../.github/workflows/pre-commit.yaml)                       | required job `smoke-binary`; MT-CP-2 #60                        | ok                    |
| CI timing metrics       | [`ci-timing.md`](../validation/ci-timing.md)                                     | MT-CP-1 #59; MT-CP-3 gate p50 ≈ 1.2 min                         | ok (MT-CP-3 deferred) |
| CI smoke venv cache     | [pre-commit.yaml](../../.github/workflows/pre-commit.yaml)                       | `.venv-smoke` cache; MT-CP-4 PR #61 −14.7%                      | ok                    |
| Helm metadata fix       | [`backend.yaml`](../../chart/templates/backend.yaml)                             | single metadata block                                           | ok                    |
| `make smoke` health     | [`Makefile`](../../Makefile), [`smoke-local.sh`](../../scripts/smoke-local.sh)   | health in CI job `pre-commit`                                   | ok                    |
| Baseline smoke phases   | [`baseline-smoke.md`](../validation/baseline-smoke.md)                           | phases 7/13/14/16                                               | ok                    |
| Quay gate               | [`quay-tags.md`](../spikes/quay-tags.md)                                         | **pass** (fork mirror); upstream **fail**                       | ok                    |
| Chart image default     | [`values.yaml`](../../chart/values.yaml)                                         | `thom_at_redhat/caisat` (public)                                | ok                    |
| OpenSSF Scorecard       | [scorecard-analysis.yml](../../.github/workflows/scorecard-analysis.yml)         | **7.3** @ 2026-07-09; Fuzzing 10; SR **5**; Packaging -1 waiver | ok                    |
| Scorecard gap plan      | [`scorecard-gaps.md`](../spikes/scorecard-gaps.md)                               | Phases 8–11 + Wave 5                                            | ok                    |
| SAST (CodeQL)           | [codeql-analysis.yml](../../.github/workflows/codeql-analysis.yml)               | PR #29; Python + JS; **10/10**                                  | ok                    |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                               | PR #24; reporting + supported versions                          | ok                    |
| Workflow permissions    | [pre-commit.yaml](../../.github/workflows/pre-commit.yaml)                       | PR #24; `permissions: contents: read`                           | ok                    |
| README Scorecard badge  | [`README.md`](../../README.md)                                                   | contributor fork slug                                           | ok (fork)             |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                    | pre-commit, smoke-binary, Scorecard, CodeQL                     | ok (fork)             |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                       | PR #26; `markdown-link-check@3.14.2`                            | ok                    |
| Pre-commit SHA pins     | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                       | Phase 11 PR #41; 13 hook repos + exact pins                     | ok                    |
| Scorecard pre-commit    | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                       | PR #42; local Scorecard hook + npm vuln fix                     | ok                    |
| Upstream sync           | fork `main` @ `4abef20`                                                          | PR #43 inbound sync                                             | ok (inbound)          |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                     | ML spikes documented (PR #45)                                   | ok                    |
| Phases 12–23 merge      | PR #45 @ `ee3f1b3`                                                               | phases-12-23 integration                                        | ok                    |
| PLAN post-23 archive    | PR #47 @ `4abef20`                                                               | PLAN archive merged                                             | ok                    |
| Local smoke profiles    | [`smoke-local.sh`](../../scripts/smoke-local.sh) L133–143                        | `health` + `binary` (pytest `tests/`)                           | ok                    |
| Pytest suite            | [`tests/`](../../tests/)                                                         | kserve_v2 + capabilities; both backends                         | ok                    |
| `make test`             | [`Makefile`](../../Makefile)                                                     | pytest via `requirements-dev.txt`                               | ok                    |
| Cluster baseline        | [`baseline-smoke.md`](../validation/baseline-smoke.md) L101–106                  | **pass** @ MT-R3a 2026-07-01                                    | ok                    |
| Frontend Containerfile  | [`Containerfile`](../../frontend/Containerfile) L1                               | `ubi9/nodejs-20`; PR #70 @ `8c44336`                            | ok                    |
| SDD specs index         | [`docs/specs/README.md`](../specs/README.md)                                     | CAP/KSRV/DRL **accepted** (MT-R3a pass)                         | ok (W5-P4)            |
| Wave 5 Partial closure  | [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) W5-P5                                   | MT-R6b — R3a pass + MT-2 evidence + waiver                      | ok (W5-P5 Partial)    |
| MT-GPU cloudtest2       | [`mt-gpu-20260702/report.md`](../validation/artifacts/mt-gpu-20260702/report.md) | MT-3A/3B/4b **pass** @ helm rev 14; PR #96                      | ok                    |

**Last verified:** fork `main` @ `b625b56` (2026-07-09); PR #157 merged (post-#156 closure); MT-E2E **pass** @ `mt-e2e-20260709`; Gate 0 YOLO health pass @ `yolo-restore-20260709`;
Phase 25 **pass**; Wave 7 E2E **pass** (PR #89);
Wave 8 T4 **pass** (PR #94 + #96); Wave 9 cloudtest2 **partial pass** (PR #92); psi-21 Path A operator upgrade **pass** (2026-07-03);
Chart GPU **resolved** @ PR #94; Wave 10 **complete**; OpenSSF Phases **26–29 + 31 complete** (PRs #104–107, #108, #114–116);
Scorecard **7.3** @ API 2026-07-09 (Batch 3b: Signed-Releases **5** pass; Packaging **-1** waiver ≤2026-07-11); SAST **10/10**

**Revalidate:** `docs/project/PLAN.md`, `docs/specs/`, `docs/validation/baseline-smoke.md`, `docs/validation/ci-timing.md`, `docs/spikes/README.md`,
`docs/spikes/scorecard-gaps.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** L40S/Hopper GPU tiers (no hardware); upstream outbound PR; Wave 5 **Full** closure blocked on `12-binary` / MT-2 binary

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

All phased work archived in [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Operational follow-up only:

| --------- | ---------------------- | ------------- | --------------------------------------------------------------------------------- |
| tests | Pytest scaffold | **pass** | W5-P1a merged — `tests/` + `make test`; CI `smoke-binary` |
| baseline | Phase 13 sign-off | **pass** | MT-R3a pass — `baseline-smoke.md` L157+; DRL-001 accepted |
| binary | 12-binary / Phase 14 | **waiver** | JSON pass / binary fail; RHOAI cases **deferred** — `binary-kserve-v2.md` |
| crop | Phase 16 sign-off | **pass** | CPU pass @ `e2a7704`; JSON 256→1024 — `baseline-smoke.md` |
| gpu | Phase 15 deferral | **pass** (T4) | T4 pass cloudtest2 PR #94/#96; L40S/Hopper N/A — `gpu-servingruntime.md` |
| scorecard | Wave 10 + Phases 26–31 | **complete** | **7.3** @ API 2026-07-09; SR **5** pass; Packaging **-1** waiver — `scorecard-gaps.md` |
| upstream | Outbound PR | **deferred** | PR to rh-ai-quickstart deferred; MT-1b + MT-2 recorded |
| ci-split | MT-CP-3 job split | **defer** | p50 gate OK; split cancelled — `ci-timing.md` |
| vite | CRA → Vite | **defer** | MT-VITE-SPIKE merged; CRA sufficient — `vite-migration.md` |
| phase-25 | S4 → SeaweedFS | **pass** | PR #85 SeaweedFS; Wave 7 E2E pass PR #88–#89; Phase 25 + Wave 7 summary |

---

## Spike outcomes (archived)

Detail in [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md#phases-1223-integration-pr-45) and spike docs. Summary:

| Spike             | Verdict                                                                 | Artifact                                                   |
| ----------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------- |
| SwinIR ONNX       | **pass** — dynamic H/W; 256→1024 native 4×                              | [`swinir-onnx.md`](../spikes/swinir-onnx.md)               |
| Binary KServe v2  | **fail** — JSON OK; binary HTTP 500                                     | [`binary-kserve-v2.md`](../spikes/binary-kserve-v2.md)     |
| RHOAI GPU runtime | **pass** (T4) — CPU pass; T4 MT-GPU pass @ helm rev 14; L40S/Hopper N/A | [`gpu-servingruntime.md`](../spikes/gpu-servingruntime.md) |
| YOLO11-OBB eval   | **skipped** — Phase 17 QA sufficient                                    | [`yolo11-obb-eval.md`](../spikes/yolo11-obb-eval.md)       |

---

## Decisions

| Topic         | Decision                                                                                                                                              |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Priority      | Larger context (512+ crop, tiled SR) — shipped Phase 16                                                                                               |
| GPU           | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override; tiers **deferred**                                                             |
| Detection     | Demo quality OK; YOLO11 eval **skipped**; OBB + SAHI shipped Phase 17                                                                                 |
| Git           | Push-as-you-go on feature branches; CI before push (`make push`)                                                                                      |
| PLAN source   | This file after Phase 3 merge; phased work archived post-23                                                                                           |
| Quay          | Phase 0 **pass** on fork (`thom_at_redhat/caisat` public mirror); upstream `rh-ai-quickstart` **fail**                                                |
| OpenSSF       | Phases 4–6 on fork first; badge uses fork slug                                                                                                        |
| Upstream      | Fork synced from upstream @ `0e4281e` (PR #43); PR back to `rh-ai-quickstart/CAIsat` still deferred                                                   |
| Scorecard     | **6.0** @ `acb9a79`; gap plan Phases 9–11 done; see `scorecard-gaps.md`                                                                               |
| 12-binary     | **fail** @ RHOAI 3.4.0 (2026-07-01); JSON pass / binary HTTP 500; Phase 14 **waiver** (Partial closure); RHOAI ticket for Full                        |
| Wave 5        | **Partial complete** @ 2026-07-01 — W5-P0–P5; R3a pass + MT-2 evidence; Full blocked on binary                                                        |
| Detect RCA    | Missing `KSERVE_PREFER_BINARY=false` on detection backend — chart fix PR #82 @ `7eb9a76`; same class as enhance MT-R3c                                |
| Spike docs    | Cluster names **never** in spike docs — use `<namespace>` placeholders                                                                                |
| Playwright CI | MT-E2E **deferred** from GHA — GPU + ≥15 min budget; enable when self-hosted GPU runner or mock + `CAISAT_GPU_EXCLUSIVE` — `baseline-smoke.md` MT-E2E |

---

## Open items

Follow-up after Phases **0–23** merge (PR #45 @ `ee3f1b3`; PLAN archive PR #47 @ `4abef20`). Code merged; cluster validation and spike gaps remain.

| Item              | Detail                                                                                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Wave 5 closure    | **Partial complete** W5-P0–P5 (2026-07-01); CPU path signed off; **Full** blocked on `12-binary` — see W5-P5 below                                                     |
| Binary spike fail | `12-binary` **fail** @ 3.4.0 (2026-07-01); JSON pass / binary HTTP 500; Phase 14 waiver; RHOAI ticket — `binary-kserve-v2.md`                                          |
| Phase 13 baseline | Cluster **pass** @ `b367b63` (PR #65); MT-R3a **pass** 2026-07-01 — `baseline-smoke.md` L157+                                                                          |
| Crop sign-off     | **pass (CPU)** @ `e2a7704`; JSON 256→1024; `KSERVE_PREFER_BINARY=false` — `baseline-smoke.md`                                                                          |
| GPU deferral      | T4 **pass** (cloud GPU cluster, helm rev 6); L40S/Hopper N/A; single-GPU UX contention — `gpu-servingruntime.md`                                                       |
| Cluster redeploy  | **pass** W5-P3 frontend + helm rev **3** (PR #82 chart); route **200** — `baseline-smoke.md`                                                                           |
| MT-R3a layout     | **pass** — Playwright 100%/150%; DRL-001 **accepted** — PR #83; artifacts `mt-r3a-20260701/`                                                                           |
| Detect RCA        | HTTP 500 on 1024 detect — missing `KSERVE_PREFER_BINARY=false`; fixed PR #82 @ `7eb9a76`                                                                               |
| Playwright CI     | **defer** scheduled E2E in GHA; manual gate `CAISAT_FRONTEND_URL=… CAISAT_GPU_EXCLUSIVE=1 node scripts/mt-e2e-workflow.mjs` — enablement in `baseline-smoke.md` MT-E2E |

### Wave 5 detection layout sign-off (W5-P4 / MT-R3a)

| Field     | Value                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------ |
| Git SHA   | `1e66830` (PR #83 @ fork `main`)                                                                 |
| Chart fix | PR #82 @ `7eb9a76` — `kserve.preferBinary: false` on enhance + detection backends                |
| Helm rev  | **3** (cluster)                                                                                  |
| DRL-001   | **accepted** — `detection-results-layout.md`                                                     |
| Verdict   | **pass** — enhance + detect 200; 100% row + 150% stack; 1 detection with OBB overlay             |
| Artifacts | `docs/validation/artifacts/mt-r3a-20260701/` (`01-100pct-*.png`, `02-150pct-*.png`, `report.md`) |

### Wave 5 Partial closure (W5-P5 / MT-R6b)

| Field        | Value                                                                                                                                    |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Git SHA      | `1e66830` (post PR #83; closure PR pending merge)                                                                                        |
| Closure path | **Partial** — user waiver 2026-07-01                                                                                                     |
| MT-R3a       | **pass** — PR #83; DRL-001 accepted                                                                                                      |
| MT-2         | **fail** (binary) — JSON pass / binary HTTP 500 @ 3.4.0; evidence `binary-kserve-v2.md`                                                  |
| Phase 14     | **waiver** — JSON fallback active; binary migration blocked upstream                                                                     |
| Detect RCA   | PR #82 — `KSERVE_PREFER_BINARY=false` on detection backend (same class as enhance MT-R3c)                                                |
| Wave 5 Full  | **blocked** — RHOAI ticket **pending operator filing**; ticket-based JSON-only waiver path available post-filing — `binary-kserve-v2.md` |

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

| Field                | Value                                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| Git SHA              | `2dd097b`                                                                                       |
| Method               | `oc rollout restart deployment/caisat-frontend` (`pullPolicy: Always`, tag `:frontend`)         |
| Helm                 | rev **3** post PR #82 chart upgrade (`kserve.preferBinary: false`); cluster verified 2026-07-01 |
| Pre-rollout imageID  | `sha256:158ea4995c01ca394f9b07ad5e34e8bd0b6006c0ead1a716ad632d57f36a8136`                       |
| Post-rollout imageID | `sha256:01ffd7825c5f71d35f84613822157380471dec4d70274aae69223632ee961a7e`                       |
| Pod (post)           | `caisat-frontend-6bf8f9754d-xnw7j`                                                              |
| Route smoke          | HTTP **200** (edge TLS)                                                                         |
| MT-R3a               | **pass** — detect 200 after `KSERVE_PREFER_BINARY=false` (PR #82); 100%/150% layout Playwright  |

### Wave 7 pipelines + storage (complete)

| Field           | Value                                                                                                                            |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Git SHA         | `6b281b7` (PR #89 @ fork `main`)                                                                                                 |
| Chart PRs       | #88 — seed/pipeline defaults `openshift/python:3.12-ubi9`; #89 — `pipelines.analysis.image` substitutes pipeline component image |
| runAnalysis E2E | **pass** — workflow `analyze-seed-images-b8hfb` **Succeeded**; SeaweedFS artifacts `metadata/*-stats.json`, `areas.json`         |
| Verdict         | **complete** — DSPA + SeaweedFS path validated; operator deferrals: RHOAI binary ticket, upstream PR, GPU tiers                  |

### Wave 8 GPU validation (pass — 2026-07-02)

| Field       | Value                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Cluster     | cloudtest2 — 1× Tesla T4; RHOAI **3.5.0-ea.2**; CAIsat helm rev **14** (post PR #94 @ `032cefa`)                                                             |
| CPU tier    | **pass** — psi-21: swinir Ready HTTP 200; JSON infer 52.6 s; `/api/capabilities` max_crop=256                                                                |
| T4 tier     | **pass** — MT-3A/3B/4b @ helm rev 14; caps `gpu_tier=t4`, `max_crop=512`; enhance 256→1024 + detect route OK                                                 |
| L40S/Hopper | **N/A** — no nodes on test cluster (MT-R4 deferred)                                                                                                          |
| Ops         | Chart GPU tolerations + minReplicas @ PR #94; operator mitigations in [`chart/README.md`](../../chart/README.md); single-GPU sequential pattern              |
| Doc         | [`gpu-servingruntime.md`](../spikes/gpu-servingruntime.md); artifact [`mt-gpu-20260702/report.md`](../validation/artifacts/mt-gpu-20260702/report.md) PR #96 |

### Wave 9 RHOAI ea.2 retry (partial pass — 2026-07-01; Path A complete 2026-07-03)

| Field                   | Value                                                                                                                                                          |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Path A (psi-21 upgrade) | **pass** — FBC `rhoai-ea2-catalog`; CSV `3.5.0-ea.2` Succeeded 2026-07-03                                                                                      |
| cloudtest2 validation   | **partial pass** — PR #92; RHOAI ea.2; helm rev 2 CPU profile; IS Ready                                                                                        |
| MT-2 @ ea.2             | cloudtest2 + psi-21: JSON **pass** / binary **fail** (2026-07-01 / 2026-07-06); MLServer `1.7.1+rhaiv.8` unchanged                                             |
| HTTP API                | `/health` **pass**; JSON enhance/detect **pass** with `KSERVE_PREFER_BINARY=false`                                                                             |
| MLServer                | `1.7.1+rhaiv.8` — **no ea.2 fix** for binary path                                                                                                              |
| Doc                     | [`binary-kserve-v2.md`](../spikes/binary-kserve-v2.md) — [MT-2-RETEST @ ea.2](../spikes/binary-kserve-v2.md#re-test-ods-qe-psi-21-mt-2-retest--ea2-2026-07-06) |
| Path A candidate        | **complete** @ 2026-07-03; MT-2 psi-21 infer retest **complete** 2026-07-06                                                                                    |

### Wave 10 ecosystem (complete — 2026-07-02)

| Item        | Verdict                                                                                                                                                              |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Upstream PR | ~175 commits / 97 files vs `rh-ai-quickstart/main` — **deferred** (user choice)                                                                                      |
| Scorecard   | **complete** — aggregate **7.3** @ API 2026-07-09; Fuzzing **10**; Signed-Releases **5** (Batch 3b pass); Packaging **-1** waiver ≤2026-07-11; Phase 30 @ 2026-09-27 |
| MT-CP-3     | **defer** — p50 gate OK; split cancelled — `ci-timing.md`                                                                                                            |
| Vite        | **defer** — MT-VITE-SPIKE (#101); CRA + overrides sufficient                                                                                                         |
| L40S/Hopper | **N/A** — GPU tier docs merged (#102)                                                                                                                                |

### Phases 26–31 — OpenSSF score improvement

**MT-ID = phase number** (`MT-SC26` … `MT-SC31`). Phases 26–29 + 31 merged @ `31606a8`; per-check score gates in Batch 3a/3b.

| Phase | MT-ID   | Check target             | Status       | Notes                                                                                        |
| ----- | ------- | ------------------------ | ------------ | -------------------------------------------------------------------------------------------- |
| 26    | MT-SC26 | Packaging -1 → ≥0        | **complete** | PR #104 — publish-chart workflow; operator **`v0.1.0`** tag (Batch 2) for Scorecard gate     |
| 27    | MT-SC27 | Signed-Releases -1 → ≥0  | **complete** | PR #105 — build provenance; **`v0.1.0`** tag; Batch 3b gate **pass** (SR **0** @ 2026-07-06) |
| 28    | MT-SC28 | Branch-Protection delta  | **complete** | PR #106 — CODEOWNERS rewrite; solo fork — **no** ruleset approver PUT                        |
| 29    | MT-SC29 | CII-Best-Practices 2 → ↑ | **complete** | PR #107 — [bestpractices.dev](https://www.bestpractices.dev/) InProgress enrollment          |
| 30    | MT-SC30 | Maintained 0 → 10        | **deferred** | Re-query API after **2026-09-27** (fork created 2026-06-29)                                  |
| 31    | MT-SC31 | Fuzzing 0 → ≥7           | **complete** | PRs #108, #114–116 — Atheris spike + hardening + CFL CI green @ `31606a8`; score gate 3a     |

### Honest aggregate score expectations

| Milestone                  | Expected outcome                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------- |
| Phases 26–29               | Per-check improvements (Packaging, Signed-Releases, CII); aggregate may stay **~6.9** |
| Phase 30 (post 2026-09-27) | Maintained **0 → 10** — largest aggregate lift                                        |
| Sustained **7+**           | Phase 30 **plus** Contributors/Code-Review (collaborator or upstream PR)              |

---

## Open blockers

| Blocker              | Detail                                                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MLServer binary      | **fail** @ 3.5.0-ea.2 — JSON pass / binary HTTP 500; blocks Wave 5 **Full** until RHOAI ticket filed — `binary-kserve-v2.md`                            |
| RHOAI support ticket | **pending** — operator to file at Customer Portal; record case ID when available — [`mt-ticket-20260704/`](../validation/artifacts/mt-ticket-20260704/) |
| RHOAI ea.2 Path A    | **resolved** — psi-21 @ `3.5.0-ea.2` (CSV Succeeded 2026-07-03); MT-2 retest **complete** 2026-07-06 — `binary-kserve-v2.md`                            |
| Chart GPU            | **resolved** @ PR #94 @ `032cefa`; operator mitigations — [`chart/README.md`](../../chart/README.md) T4 section                                         |
| Pull secrets         | `quay-pull-secret` merged (PR #79); `rhoai-quay-pull` **not created**; psi-21 `quay.io/rhoai` credential **rotated** (2026-07-03)                       |

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
| Status       | **pass** (chart PR #85; cluster prove-out 2026-07-01)                                  |
| Branch       | `feature/seaweedfs-phase` (merged)                                                     |
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

- [x] Pin SeaweedFS image: mirror `docker.io/chrislusf/seaweedfs:<tag>` to Quay or use a public OCI mirror; record digest in `values.yaml`
- [x] Author `chart/templates/seaweedfs.yaml` — Deployment (`weed server -s3 -s3.port=7480 -dir=/data`), PVC (`/data`), ConfigMap (region, endpoint), Secret (accessKey/secretKey), Service (port 7480)
- [x] Remove `chart/templates/s4.yaml`
- [x] Rename and update `chart/templates/s4-seed-job.yaml` → `storage-seed-job.yaml`; init-container waits on SeaweedFS Deployment; S3 endpoint env `http://<release>-seaweedfs.<ns>.svc.cluster.local:7480`
- [x] Rename `chart/templates/s4-seed-serviceaccount.yaml` → `storage-seed-serviceaccount.yaml`; update component labels
- [x] Update `chart/values.yaml`: rename all `s4` keys to `seaweedfs`; update image repository/tag; keep `seed.bucketName: satellite-images`, credentials keys, `storageClassName`
- [x] Update `chart/templates/pipeline-dspa.yaml`: `externalStorage.host` → `<release>-seaweedfs.<ns>.svc.cluster.local:7480`
- [x] Update `chart/templates/pipeline-secret.yaml`: reference `seaweedfs` credentials Secret name
- [x] Update `chart/templates/backend-changedetection.yaml`: S3 endpoint env vars → SeaweedFS service
- [x] Update `chart/README.md`: replace S4 references with SeaweedFS; document `weed server` mode and port
- [x] `helm template test ./chart` passes (`make check`)
- [x] `pre-commit run --all-files` passes
- [x] Record Phase 25 outcome row in `PLAN_COMPLETED.md`

### Acceptance criteria

- [x] `helm template test ./chart` produces no `s4` component references
- [x] Bucket `satellite-images` created and S3 read/write confirmed (manual `aws-cli` probe; seed Job blocked on missing DS notebook image on `<cluster>`)
- [x] `DataSciencePipelinesApplication` `externalStorage.host` resolves to SeaweedFS service (live DSPA + SeaweedFS on `<cluster>`; helm template verified in PR #85)
- [x] `backend-changedetection` `/health` 200 + S3 R/W — image mirrored to `quay.io/thom_at_redhat/caisat:backend-changedetection`; cluster `/health` verified (Wave 7 ops 2026-07-01)
- [x] Pipeline run artifact uploads/downloads succeed (SeaweedFS S3 path) — runAnalysis E2E **pass** (workflow `analyze-seed-images-b8hfb`; `metadata/*-stats.json` + `areas.json` on SeaweedFS)
- [x] Enhance/detect backends unaffected — `/health` 200 both backends; no S3 path in enhance/detect code

### Notes

- SeaweedFS `weed server` runs master + volume + S3 gateway in a single process; no separate filer needed for demo scale.
- Port 7480 matches the former S4 S3 port; all existing service-internal references (`svc.cluster.local:7480`) carry over once the Service name changes from `s4` to `seaweedfs`.
- `KSERVE_PREFER_BINARY` is unrelated to this phase — change-detection uses direct S3, not KServe inference.
- Ties to the optional change-detection path only; core satellite enhance/detect UX is unaffected.

### Cluster prove-out (2026-07-01, `<cluster>`)

| Check                    | Result   | Evidence                                                                                                                       |
| ------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| SeaweedFS pod            | **pass** | `caisat-seaweedfs` 1/1 Running; helm rev 5 `deployed`                                                                          |
| PVC                      | **pass** | `caisat-seaweedfs-storage` Bound, `standard-csi`, 10Gi                                                                         |
| S3 bucket + R/W          | **pass** | `aws-cli` probe: `mb s3://satellite-images`, put/get `proveout-test.txt` via `<release>-seaweedfs.<ns>.svc.cluster.local:7480` |
| Enhance `/health`        | **pass** | `{"status":"healthy"}`                                                                                                         |
| Detect `/health`         | **pass** | `{"status":"healthy"}`                                                                                                         |
| Seed Job                 | **pass** | PR #88 — `openshift/python:3.12-ubi9` seed/pipeline image; lean-cluster path validated                                         |
| Change-detection backend | **pass** | Image mirrored to Quay; cluster `/health` 200 + S3 ok (`s3_connection":"ok"`) — Wave 7 ops rev 6 test                          |
| DSPA pipeline            | **pass** | `pipelines.enabled=true`; runAnalysis workflow **Succeeded**; component image via PR #89 `pipelines.analysis.image`            |
