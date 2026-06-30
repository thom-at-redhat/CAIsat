# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for phase sequencing, merge gates, and spike gates. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `6b0a209` (2026-06-30). Phase 9 in progress — use feature branches; never push `main`.

**Archive:** Completed work → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary, archived):** Cursor artifact `~/.cursor/plans/caisat_plan_bootstrap_3c3a4d19.plan.md` — archived 2026-06-29; historical OpenSSF detail, parallel execution, smoke profiles;
`~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only.

**Renumbering (2026-06-29):** Removed serial suffixes (`1A`/`1B` → Phases 1–2). OpenSSF supply-chain = Phases **4–6**.
Former phases 3–18 → **7–19**. Parallel spike tracks keep `-onnx`/`-binary` suffixes only.

**Renumbering (2026-06-30):** Inserted Phases **8–11** (OpenSSF score improvement); former **8–19 → 12–23**. Spike tracks `8-onnx`/`8-binary` → **`12-onnx`/`12-binary`**.

---

## Verification artifact

| Claim                   | Path                                                                                         | Evidence                                       | Status                   |
| ----------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------ |
| MODEL_ENDPOINT required | [`backend/app.py`](../../backend/app.py) L35–39                                              | `if not MODEL_ENDPOINT: raise`                 | ok                       |
| CI + Helm template      | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | pre-commit + helm template                     | ok                       |
| Helm metadata fix       | [`chart/templates/backend-deployment.yaml`](../../chart/templates/backend-deployment.yaml)   | single metadata block                          | ok                       |
| `make smoke` health     | [`Makefile`](../../Makefile), [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)       | health profile; CI step in pre-commit workflow | ok                       |
| Baseline smoke phases   | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md)                       | phases 7/13/14/16                              | ok                       |
| Quay gate               | [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md)                                         | **pass** (fork mirror); upstream **fail**      | ok                       |
| Chart image default     | [`chart/values.yaml`](../../chart/values.yaml)                                               | `thom_at_redhat/caisat` (public)               | ok                       |
| OpenSSF Scorecard       | [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) | fork `main` `acb9a79`; Scorecard **6.0**       | ok                       |
| Scorecard gap plan      | [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md)                               | checks, targets, Phases 8–11                   | ok                       |
| SAST (CodeQL)           | [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml)       | PR #29; Python + JS; **10/10**                 | ok                       |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                                           | PR #24; reporting + supported versions         | ok                       |
| Workflow permissions    | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | PR #24; `permissions: contents: read`          | ok                       |
| README Scorecard badge  | [`README.md`](../../README.md)                                                               | contributor fork slug (see badge URL)          | ok (fork until upstream) |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                                | `pre-commit` + Scorecard required on `main`    | ok (fork)                |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #26; `markdown-link-check@3.14.2` pinned    | ok                       |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                                 | not started (ML spikes)                        | ok                       |

**Last verified:** fork `main` @ `acb9a79` (2026-06-30); Scorecard **6.0**; SAST **10/10**; Phase 0 merged PR #33; Phase 8 merged (score baseline)

**Revalidate:** `docs/project/PLAN.md`, `docs/validation/baseline-smoke.md`, `docs/spikes/README.md`, `docs/spikes/scorecard-gaps.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** cluster baseline sign-off; ONNX/binary/GPU runtime (Phase 12 spikes); post-Phase-11 Scorecard re-run

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

Sync with bootstrap plan frontmatter; update on phase close. Phases 1–7 → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md).

| ID    | Phase / track      | Status        | Next action                                             |
| ----- | ------------------ | ------------- | ------------------------------------------------------- |
| 0     | Quay gate          | **completed** | Fork mirror in chart defaults; upstream still fail      |
| 8     | Score baseline     | **completed** | Archived — see [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) |
| 9     | Dependency hygiene | in progress   | PR open — safe Dependabot batch merged                  |
| 10    | Branch protection  | pending       | Ruleset: CodeQL required, maximal fork settings         |
| 11    | Pin dependencies   | pending       | Workflow/pre-commit SHA pins → 10/10                    |
| 12    | Spikes             | pending       | Parallel `12-onnx` + `12-binary`                        |
| 13–17 | Core ML            | pending       | Per merge gates (health + manual checklists)            |
| 18–23 | Deferred           | pending       | After Phase 17                                          |

---

## Status

Phases **0, 1–8** done — see [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). OpenSSF install detail (Phases 4–6) and score baseline (Phase 8) archived there.

| Phase | Track                  | Status                 | Merge gate                                                                                               |
| ----- | ---------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------- |
| 0     | Quay gate              | **Done (fork mirror)** | All five `thom_at_redhat/caisat` tags pull anonymously; upstream `rh-ai-quickstart` still fail           |
| 8     | OpenSSF score baseline | **Done**               | `make check` + doc only; Scorecard **6.0** @ `acb9a79`                                                   |
| 9     | Dependency hygiene     | Planned                | `make check` + `make smoke`; green CI; reduced vuln count                                                |
| 10    | Branch protection      | Planned                | `make check`; document ruleset `protect-main` changes                                                    |
| 11    | Pin dependencies       | Planned                | `make check`; Pinned-Dependencies → 10/10                                                                |
| 12    | ONNX + binary spikes   | Planned                | Spike docs with pass/fail (`12-onnx`, `12-binary`)                                                       |
| 13    | Capture/zoom (#5)      | Planned                | `make check` + `make smoke` (health) + manual **baseline** + **post-p0** sign-off in `baseline-smoke.md` |
| 14    | Binary KServe tensors  | Planned                | `make check` + `make smoke` (health) + manual **binary** checklist (script TBD)                          |
| 15    | GPU profiles           | Planned                | `make check` + `make smoke` (health) + GPU spike deferral table                                          |
| 16    | Crop + tiled SR        | Planned                | `make check` + `make smoke` (health) + manual **crop** checklist (script TBD)                            |
| 17    | OBB + SAHI             | Planned                | `make check` + `make smoke` (health) + manual sign-off per profiles exercised                            |
| 18–23 | Deferred               | Planned (after 17)     | Per phase one-liners below                                                                               |

---

## Phase one-liners

| Phase  | Goal                                                                                                 |
| ------ | ---------------------------------------------------------------------------------------------------- |
| **0**  | Quay gate — anonymous pull of all five chart tags; fork uses `thom_at_redhat/caisat` mirror          |
| **8**  | OpenSSF score baseline — sync PLAN/badge, `scorecard-gaps.md`, record Scorecard 6.0                  |
| **9**  | Dependency hygiene — enable/merge Dependabot updates; reduce OSV vulnerability count                 |
| **10** | Branch protection hardening — ruleset: CodeQL required, maximal settings feasible on fork            |
| **11** | Pin remaining dependencies — pre-commit/workflow SHA pins to 10/10 Pinned-Dependencies               |
| **12** | SwinIR ONNX shape spike + binary KServe v2 round-trip spike (parallel tracks `12-onnx`, `12-binary`) |
| **13** | Capture/zoom alignment (upstream #5) — helm metadata fixed in Phase 1                                |
| **14** | Binary tensor encode/decode + shared `aiohttp` session in both backends                              |
| **15** | GPU ServingRuntime spike per tier + compute profiles + `/api/capabilities`                           |
| **16** | Profile-aware crop chain + tiled SwinIR + cross-path parity                                          |
| **17** | OBB decode + rotated draw, SAHI slicing, route/resource tuning                                       |
| **18** | Structured logging, metrics, model-endpoint health probes                                            |
| **19** | CORS, upload limits, error sanitization, NetworkPolicy, Route OAuth                                  |
| **20** | YOLO11-OBB eval — **skip** if Phase 17 QA acceptable                                                 |
| **21** | kube-linter + re-enable pre-commit exclusions                                                        |
| **22** | Repo hygiene (backup file, chart README sync, pin deps)                                              |
| **23** | UX: coordinate search (#4), progress, error UI, detection health polling                             |

---

## OpenSSF supply-chain (Phases 4–6)

**Done** — install, quick wins, and CodeQL on contributor fork. Detail, checklists, and PR sequence → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md#openssf-supply-chain-phases-46).

**Upstream PR deferred** (2026-06-29): fork-only validation; no PR to `rh-ai-quickstart/CAIsat` until user re-opens upstream track.

---

## Smoke automation vs merge gates

| Profile      | Automated (`make smoke`)                       | Merge gate                               |
| ------------ | ---------------------------------------------- | ---------------------------------------- |
| **health**   | Yes (Phase 7)                                  | Required from Phase 7                    |
| **baseline** | No — cluster checklist in `baseline-smoke.md`  | Required from Phase 13 (manual sign-off) |
| **post-p0**  | No — manual capture/zoom                       | Required from Phase 13                   |
| **binary**   | No — implement in script or manual (Phase 14+) | Required from Phase 14                   |
| **crop**     | No — implement in script or manual (Phase 16+) | Required from Phase 16                   |

Do not treat Phases 13–17 as fully automated until `smoke-local.sh` implements the profile or the checklist is signed off in `baseline-smoke.md`.

---

## Spike gate table

| Spike             | Artifact                                           | Pass criteria                                      | Blocks                    |
| ----------------- | -------------------------------------------------- | -------------------------------------------------- | ------------------------- |
| Quay tags         | [`../spikes/quay-tags.md`](../spikes/quay-tags.md) | Fork mirror: five tags pull; upstream unauthorized | — (fork unblocked)        |
| SwinIR ONNX       | `../spikes/swinir-onnx.md`                         | Input/output shapes documented; branch chosen      | Phase 16                  |
| Binary KServe v2  | `../spikes/binary-kserve-v2.md`                    | Round-trip binary infer vs MLServer                | Phase 14                  |
| RHOAI GPU runtime | `../spikes/gpu-servingruntime.md`                  | Per-tier Ready + infer 200 (or deferral signed)    | `nvidia.com/gpu` in chart |

---

## Parallel execution (multitask mode)

### Serial (Phases 1–11)

Phases 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 must complete in order. Phases 1–7 **done** (see archive). OpenSSF score improvement (8–11) precedes ML spikes.

### After Phase 11

| Track         | Work                    | Merge rule                                          |
| ------------- | ----------------------- | --------------------------------------------------- |
| **12-onnx**   | SwinIR ONNX spike doc   | Both `12-onnx` and `12-binary` done before Phase 14 |
| **12-binary** | Binary KServe spike doc | Same                                                |
| **13**        | Capture/zoom #5         | Before Phase 16; do not parallel with Phase 16 crop |

### Critical path (serial)

Phase 12 → 14 → 15 → 16 → 17. Phase 13 → 14. Never Phase 14 before `12-binary` pass. Never Phase 16 before `12-onnx` pass.

### Do not parallelize

- Phase 14 + Phase 16 (binary blocks crop >256)
- Phase 15 + Phase 16 (profiles required for crop UX)
- Phase 13 capture + Phase 16
- Phase 12 spikes + Phase 15 GPU (do not start GPU spike work during Phase 12)
- Phase 8 + Phase 9 (9 needs dependency baseline from 8 doc sync)
- Two agents, same phase, same files

### Per-merge checklist (Phases 13–17)

1. `git status` — no secrets staged
2. `make check`
3. `make helm-template` (if chart touched)
4. `make smoke` (health) or manual checklist in `baseline-smoke.md` for other profiles
5. `git push -u origin HEAD`

---

## Decisions

| Topic       | Decision                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| Priority    | Larger context (512+ crop, tiled SR)                                                                   |
| GPU         | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override                                  |
| Detection   | Demo quality OK; defer YOLO11 eval; OBB fix before SAHI                                                |
| Git         | Push-as-you-go on feature branches; CI before push (`make push`)                                       |
| PLAN source | This file after Phase 3 merge                                                                          |
| Quay        | Phase 0 **pass** on fork (`thom_at_redhat/caisat` public mirror); upstream `rh-ai-quickstart` **fail** |
| OpenSSF     | Phases 4–6 on fork first; **upstream PR deferred** (fork-only validation; badge uses fork slug)        |
| Scorecard   | **6.0** @ `acb9a79`; gap plan Phases 9–11; see `scorecard-gaps.md`                                     |
| Numbering   | Integer phases only; `-onnx`/`-binary` suffixes for parallel tracks                                    |

---

## Smoke profiles

| Profile      | Phases | Assertions                                        |
| ------------ | ------ | ------------------------------------------------- |
| **health**   | 7+     | `/health` 200 on both backends                    |
| **baseline** | 13+    | health + enhance/detect HTTP 200 + valid payloads |
| **post-p0**  | 13+    | baseline + manual capture/zoom sign-off 1×/2×/4×  |
| **binary**   | 14+    | baseline + binary content-type + decode           |
| **crop**     | 16+    | baseline/binary + profile default crop size       |

See [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md).

---

## Push-as-you-go

| Phase | Push after                    |
| ----- | ----------------------------- |
| 0     | commit (fork mirror defaults) |
| 1–7   | done (see archive)            |
| 8–11  | each phase                    |
| 12+   | each phase                    |

**Git rules:** feature branches only; never push `main`; no `--no-verify`.
