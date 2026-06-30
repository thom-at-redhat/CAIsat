# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for phase sequencing, merge gates, and spike gates. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `0e4281e` (2026-06-30). Phase 12 next — use feature branches; never push `main`.

**Archive:** Completed work (phases **0–11**) → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

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
| Helm metadata fix       | [`chart/templates/backend.yaml`](../../chart/templates/backend.yaml)                         | single metadata block                          | ok                       |
| `make smoke` health     | [`Makefile`](../../Makefile), [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)       | health profile; CI step in pre-commit workflow | ok                       |
| Baseline smoke phases   | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md)                       | phases 7/13/14/16                              | ok                       |
| Quay gate               | [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md)                                         | **pass** (fork mirror); upstream **fail**      | ok                       |
| Chart image default     | [`chart/values.yaml`](../../chart/values.yaml)                                               | `thom_at_redhat/caisat` (public)               | ok                       |
| OpenSSF Scorecard       | [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) | fork `main` `0e4281e`; Scorecard **6.0**       | ok                       |
| Scorecard gap plan      | [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md)                               | checks, targets; Phases 8–11 archived          | ok                       |
| SAST (CodeQL)           | [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml)       | PR #29; Python + JS; **10/10**                 | ok                       |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                                           | PR #24; reporting + supported versions         | ok                       |
| Workflow permissions    | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | PR #24; `permissions: contents: read`          | ok                       |
| README Scorecard badge  | [`README.md`](../../README.md)                                                               | contributor fork slug (see badge URL)          | ok (fork until upstream) |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                                | `pre-commit` + Scorecard + CodeQL on `main`    | ok (fork)                |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #26; `markdown-link-check@3.14.2` pinned    | ok                       |
| Pre-commit SHA pins     | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | Phase 11 PR #41; 13 hook repos + exact pins    | ok                       |
| Scorecard pre-commit    | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #42; local Scorecard hook + npm vuln fix    | ok                       |
| Upstream sync           | fork `main` @ `0e4281e`                                                                      | PR #43; change detection + S4/DSPA pipelines   | ok (inbound only)        |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                                 | not started (ML spikes)                        | ok                       |

**Last verified:** fork `main` @ `0e4281e` (2026-06-30); Phases 0–11 merged (#33–#43); Scorecard **6.0**; SAST **10/10**; Dependabot **21** (8H/12M/1L)

**Revalidate:** `docs/project/PLAN.md`, `docs/validation/baseline-smoke.md`, `docs/spikes/README.md`, `docs/spikes/scorecard-gaps.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** cluster baseline sign-off (React 19 / three / react-leaflet UX → Phase 13); Phase 12 ONNX/binary/GPU spikes; post-Phase-11 Scorecard overall re-run

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

Sync with bootstrap plan frontmatter; update on phase close. Phases **0–11** → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md).

| ID    | Phase / track | Status  | Next action                                  |
| ----- | ------------- | ------- | -------------------------------------------- |
| 12    | Spikes        | pending | Parallel `12-onnx` + `12-binary`             |
| 13–17 | Core ML       | pending | Per merge gates (health + manual checklists) |
| 18–23 | Deferred      | pending | After Phase 17                               |

---

## Status

Phases **0–11** done — see [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md).

| Phase | Track                 | Status             | Merge gate                                                                                               |
| ----- | --------------------- | ------------------ | -------------------------------------------------------------------------------------------------------- |
| 12    | ONNX + binary spikes  | Planned            | Spike docs with pass/fail (`12-onnx`, `12-binary`)                                                       |
| 13    | Capture/zoom (#5)     | Planned            | `make check` + `make smoke` (health) + manual **baseline** + **post-p0** sign-off in `baseline-smoke.md` |
| 14    | Binary KServe tensors | Planned            | `make check` + `make smoke` (health) + manual **binary** checklist (script TBD)                          |
| 15    | GPU profiles          | Planned            | `make check` + `make smoke` (health) + GPU spike deferral table                                          |
| 16    | Crop + tiled SR       | Planned            | `make check` + `make smoke` (health) + manual **crop** checklist (script TBD)                            |
| 17    | OBB + SAHI            | Planned            | `make check` + `make smoke` (health) + manual sign-off per profiles exercised                            |
| 18–23 | Deferred              | Planned (after 17) | Per phase one-liners below                                                                               |

---

## Phase one-liners

| Phase  | Goal                                                                                                 |
| ------ | ---------------------------------------------------------------------------------------------------- |
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

**Done** — install, quick wins, and CodeQL on contributor fork. Phases **8–11** (score baseline, dependency hygiene, branch protection, pin dependencies) also archived. Detail → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md#openssf-supply-chain-phases-46).

**Upstream:** fork synced from upstream @ `0e4281e` (PR #43); PR back to `rh-ai-quickstart/CAIsat` still deferred (2026-06-29 decision).

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

### Serial prerequisite (Phases 0–11)

Phases 0 → 1 → … → 11 must complete in order. All **done** — see [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Phase 12 next.

### Phase 12 (parallel tracks)

| Track         | Work                    | Merge rule                                          |
| ------------- | ----------------------- | --------------------------------------------------- |
| **12-onnx**   | SwinIR ONNX spike doc   | Both `12-onnx` and `12-binary` done before Phase 14 |
| **12-binary** | Binary KServe spike doc | Same                                                |

### After Phase 12

| Track  | Work            | Merge rule                                          |
| ------ | --------------- | --------------------------------------------------- |
| **13** | Capture/zoom #5 | Before Phase 16; do not parallel with Phase 16 crop |

### Critical path (serial)

Phase 12 → 14 → 15 → 16 → 17. Phase 13 → 14. Never Phase 14 before `12-binary` pass. Never Phase 16 before `12-onnx` pass.

### Do not parallelize

- Phase 14 + Phase 16 (binary blocks crop >256)
- Phase 15 + Phase 16 (profiles required for crop UX)
- Phase 13 capture + Phase 16
- Phase 12 spikes + Phase 15 GPU (do not start GPU spike work during Phase 12)
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
| OpenSSF     | Phases 4–6 on fork first; badge uses fork slug                                                         |
| Upstream    | Fork synced from upstream @ `0e4281e` (PR #43); PR back to `rh-ai-quickstart/CAIsat` still deferred    |
| Scorecard   | **6.0** @ `acb9a79`; gap plan Phases 9–11 done; see `scorecard-gaps.md`                                |
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

| Phase | Push after         |
| ----- | ------------------ |
| 0–11  | done (see archive) |
| 12+   | each phase         |

**Git rules:** feature branches only; never push `main`; no `--no-verify`.
