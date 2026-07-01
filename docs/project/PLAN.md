# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for operational follow-up, merge gates, and spike outcomes. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `8c44336` (2026-07-01). **All planned phases (0–23) complete.** Wave 5 in progress (W5-P0 **done** — PR #70 nodejs-20 Containerfile).
CI parallelization MT-CP-0→5 **complete** (MT-CP-3 deferred).
Open operational items below; use feature branches for follow-up; never push `main`.

**Archive:** Completed phased work (phases **0–23**) → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary, archived):** Cursor artifact `~/.cursor/plans/caisat_plan_bootstrap_3c3a4d19.plan.md` — archived 2026-06-29; historical OpenSSF detail, parallel execution, smoke profiles;
`~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only.

**Renumbering (2026-06-29):** Removed serial suffixes (`1A`/`1B` → Phases 1–2). OpenSSF supply-chain = Phases **4–6**. Former phases 3–18 → **7–19**.

**Renumbering (2026-06-30):** Inserted Phases **8–11** (OpenSSF score improvement); former **8–19 → 12–23**. Spike tracks `8-onnx`/`8-binary` → **`12-onnx`/`12-binary`**.

---

## Verification artifact

| Claim                   | Path                                                                                         | Evidence                                      | Status                |
| ----------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------- | --------------------- |
| MODEL_ENDPOINT required | [`backend/app.py`](../../backend/app.py) L35–39                                              | `if not MODEL_ENDPOINT: raise`                | ok                    |
| CI harden-runner block  | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | egress block + allowlists; MT-CP-5 PR #62     | ok                    |
| CI binary smoke job     | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | required CI job `smoke-binary`; MT-CP-2 #60   | ok                    |
| CI timing metrics       | [`docs/validation/ci-timing.md`](../validation/ci-timing.md)                                 | MT-CP-1 #59; MT-CP-3 gate p50 ≈ 1.2 min       | ok (MT-CP-3 deferred) |
| CI smoke venv cache     | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | `.venv-smoke` cache; MT-CP-4 PR #61 −14.7%    | ok                    |
| Helm metadata fix       | [`chart/templates/backend.yaml`](../../chart/templates/backend.yaml)                         | single metadata block                         | ok                    |
| `make smoke` health     | [`Makefile`](../../Makefile), [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)       | health in required CI job `pre-commit`        | ok                    |
| Baseline smoke phases   | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md)                       | phases 7/13/14/16                             | ok                    |
| Quay gate               | [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md)                                         | **pass** (fork mirror); upstream **fail**     | ok                    |
| Chart image default     | [`chart/values.yaml`](../../chart/values.yaml)                                               | `thom_at_redhat/caisat` (public)              | ok                    |
| OpenSSF Scorecard       | [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) | **6.0** triaged @ `a98e062` (MT-W14)          | ok                    |
| Scorecard gap plan      | [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md)                               | Phases 8–11 + Wave 5                          | ok                    |
| SAST (CodeQL)           | [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml)       | PR #29; Python + JS; **10/10**                | ok                    |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                                           | PR #24; reporting + supported versions        | ok                    |
| Workflow permissions    | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | PR #24; `permissions: contents: read`         | ok                    |
| README Scorecard badge  | [`README.md`](../../README.md)                                                               | contributor fork slug (see badge URL)         | ok (fork)             |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                                | pre-commit, smoke-binary, Scorecard, CodeQL   | ok (fork)             |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #26; `markdown-link-check@3.14.2` pinned   | ok                    |
| Pre-commit SHA pins     | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | Phase 11 PR #41; 13 hook repos + exact pins   | ok                    |
| Scorecard pre-commit    | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #42; local Scorecard hook + npm vuln fix   | ok                    |
| Upstream sync           | fork `main` @ `4abef20`                                                                      | PR #43 inbound sync                           | ok (inbound)          |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                                 | ML spikes documented (PR #45)                 | ok                    |
| Phases 12–23 merge      | PR #45 @ `ee3f1b3`                                                                           | phases-12-23 integration                      | ok                    |
| PLAN post-23 archive    | PR #47 @ `4abef20`                                                                           | PLAN archive merged                           | ok                    |
| Local smoke profiles    | [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh) L133–143                            | `health` + `binary` (pytest `tests/`)         | ok                    |
| Pytest suite            | [`tests/`](../../tests/)                                                                     | kserve_v2 + capabilities; both backends       | ok                    |
| `make test`             | [`Makefile`](../../Makefile)                                                                 | pytest via `requirements-dev.txt`             | ok                    |
| Cluster baseline        | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) L101–106              | **pass** @ `b367b63` 2026-07-01               | ok (layout partial)   |
| Frontend Containerfile  | [`frontend/Containerfile`](../../frontend/Containerfile) L1                                  | `ubi9/nodejs-20`; PR #70 @ `8c44336`          | ok                    |
| SDD specs index         | [`docs/specs/README.md`](../specs/README.md)                                                 | CAP/KSRV accepted; DRL draft (MT-R3a pending) | ok (W5-P1b)           |

**Last verified:** fork `main` @ `8c44336` (2026-07-01); Wave 5 W5-P0 PR #70 merged; prior MT-R5 @ `e2a7704`; CI parallelization MT-CP-3 deferred;
Scorecard **6.0** expected (MT-W14 triaged @ `a98e062`); SAST **10/10**

**Revalidate:** `docs/project/PLAN.md`, `docs/specs/`, `docs/validation/baseline-smoke.md`, `docs/validation/ci-timing.md`, `docs/spikes/README.md`,
`docs/spikes/scorecard-gaps.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** MT-1b detection 150% layout (pre-PR #54 frontend image); MT-4a full crop after redeploy @ `b367b63`; GPU tiers **deferred**; upstream outbound PR

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

All phased work archived in [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Operational follow-up only:

| ID        | Track                | Status       | Next action                                                                                               |
| --------- | -------------------- | ------------ | --------------------------------------------------------------------------------------------------------- |
| tests     | Pytest scaffold      | **pass**     | W5-P1a merged — `tests/` + `make test` in `make check`; CI `smoke-binary` runs standalone pytest          |
| baseline  | Phase 13 sign-off    | **pass**     | 150% layout partial — W5-P2 Quay push + redeploy frontend @ `8c44336` (PR #70 merged)                     |
| binary    | 12-binary / Phase 14 | **fail**     | ea.1 JSON pass / binary HTTP 500; RHOAI ticket required for waiver — `binary-kserve-v2.md`                |
| crop      | Phase 16 sign-off    | **partial**  | CPU partial @ `b367b63` — capabilities 404 on stale deploy; redeploy for full MT-4a — `baseline-smoke.md` |
| gpu       | Phase 15 deferral    | **waiver**   | MT-3 skipped; T4/L40S/Hopper deferred; re-test 2026-07-31 or GPU clusters — `gpu-servingruntime.md`       |
| scorecard | Optional             | **triaged**  | **6.0** @ `a98e062`; pin 10/10 (W14a); OSV triage done (W14b) — `scorecard-gaps.md`                       |
| upstream  | Outbound PR          | **deferred** | PR back to `rh-ai-quickstart/CAIsat` deferred; gate MT-1b + MT-2 outcomes recorded (user decision)        |
| ci-split  | MT-CP-3 job split    | **deferred** | p50 `pre-commit` ≈ 1.2 min; gate > ~12 min — `ci-timing.md`; revisit if CI grows or hooks add weight      |

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

| Topic       | Decision                                                                                                                                 |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Priority    | Larger context (512+ crop, tiled SR) — shipped Phase 16                                                                                  |
| GPU         | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override; tiers **deferred**                                                |
| Detection   | Demo quality OK; YOLO11 eval **skipped**; OBB + SAHI shipped Phase 17                                                                    |
| Git         | Push-as-you-go on feature branches; CI before push (`make push`)                                                                         |
| PLAN source | This file after Phase 3 merge; phased work archived post-23                                                                              |
| Quay        | Phase 0 **pass** on fork (`thom_at_redhat/caisat` public mirror); upstream `rh-ai-quickstart` **fail**                                   |
| OpenSSF     | Phases 4–6 on fork first; badge uses fork slug                                                                                           |
| Upstream    | Fork synced from upstream @ `0e4281e` (PR #43); PR back to `rh-ai-quickstart/CAIsat` still deferred                                      |
| Scorecard   | **6.0** @ `acb9a79`; gap plan Phases 9–11 done; see `scorecard-gaps.md`                                                                  |
| 12-binary   | **fail** @ RHOAI 3.5.ea.1 (2026-07-01 cluster retest); JSON pass / binary HTTP 500; RHOAI ticket required; Phase 14 JSON-fallback active |
| Spike docs  | Cluster names **never** in spike docs — use `<namespace>` placeholders                                                                   |

---

## Open items

Follow-up after Phases **0–23** merge (PR #45 @ `ee3f1b3`; PLAN archive PR #47 @ `4abef20`). Code merged; cluster validation and spike gaps remain.

| Item              | Detail                                                                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Binary spike fail | `12-binary` **fail** @ ea.1 (2026-07-01); JSON pass / binary HTTP 500; RHOAI ticket required — `binary-kserve-v2.md`                         |
| Phase 13 baseline | Cluster **pass** @ `b367b63` (PR #65); detection 150% layout partial pending redeploy — `baseline-smoke.md`                                  |
| Crop sign-off     | **pass (CPU)** @ `e2a7704` post-redeploy; JSON enhance 256→1024; `KSERVE_PREFER_BINARY=false` on cluster — `baseline-smoke.md`               |
| GPU deferral      | MT-3 **skipped**; T4/L40S not found; Hopper cluster unhealthy — `gpu-servingruntime.md`                                                      |
| Cluster redeploy  | **partial** — backends @ `e2a7704`; frontend Containerfile @ `8c44336` (PR #70); Quay push + rollout **W5-P2** pending — `baseline-smoke.md` |

---

## Open blockers

| Blocker               | Detail                                                                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| MLServer binary       | **fail** @ ea.1 (2026-07-01): MLServer `1.7.1+rhaiv.8`; JSON pass / binary HTTP 500 both predictors; RHOAI ticket required for waiver |
| KSERVE binary default | `KSERVE_PREFER_BINARY=true` breaks enhance when binary infer fails; CPU cluster set to `false` until MLServer binary passes           |
| Phase 14 binary-only  | JSON fallback active until binary round-trip passes on cluster                                                                        |

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
