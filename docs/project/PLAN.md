# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for phase sequencing, merge gates, and spike gates. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `12c0494` (2026-06-29). Phase 8 next — use feature branches; never push `main`.

**Archive:** Completed work → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary, archived):** Cursor artifact `~/.cursor/plans/caisat_plan_bootstrap_3c3a4d19.plan.md` — archived 2026-06-29; historical OpenSSF detail, parallel execution, smoke profiles;
`~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only.

**Renumbering (2026-06-29):** Removed serial suffixes (`1A`/`1B` → Phases 1–2). OpenSSF supply-chain = Phases **4–6**.
Former phases 3–18 → **7–19**. Parallel spike tracks keep `-onnx`/`-binary` suffixes only.

---

## Verification artifact

| Claim                   | Path                                                                                         | Evidence                                        | Status                   |
| ----------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------ |
| MODEL_ENDPOINT required | [`backend/app.py`](../../backend/app.py) L35–39                                              | `if not MODEL_ENDPOINT: raise`                  | ok                       |
| CI + Helm template      | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | pre-commit + helm template                      | ok                       |
| Helm metadata fix       | [`chart/templates/backend-deployment.yaml`](../../chart/templates/backend-deployment.yaml)   | single metadata block                           | ok                       |
| `make smoke` health     | [`Makefile`](../../Makefile), [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)       | health profile; CI step in pre-commit workflow  | ok                       |
| Baseline smoke phases   | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md)                       | phases 7/9/10/12                                | ok                       |
| Quay gate               | [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md)                                         | **fail** (unauthorized)                         | ok                       |
| Chart image default     | [`chart/values.yaml`](../../chart/values.yaml)                                               | `rh-ai-quickstart/caisat`                       | ok (mirror or auth)      |
| OpenSSF Scorecard       | [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) | `main` `f0e582a`; PR #21/#24; Scorecard **5.2** | ok                       |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                                           | PR #24; reporting + supported versions          | ok                       |
| Workflow permissions    | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | PR #24; `permissions: contents: read`           | ok                       |
| README Scorecard badge  | [`README.md`](../../README.md)                                                               | contributor fork slug (see badge URL)           | ok (fork until upstream) |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                                | `pre-commit` + Scorecard required on `main`     | ok (fork)                |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #26; `markdown-link-check@3.14.2` pinned     | ok                       |
| CodeQL SAST             | [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml)       | PR #29; Python + JS; default setup disabled     | ok                       |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                                 | not started                                     | ok                       |

**Last verified:** `main` (2026-06-29); fork `main` @ `12c04945` (PR #31 PLAN tip sync); Phase 7 close pending PR

**Revalidate:** `docs/project/PLAN.md`, `docs/validation/baseline-smoke.md`, `docs/spikes/README.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** cluster baseline sign-off; ONNX/binary/GPU runtime (Phase 8 spikes)

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

Sync with bootstrap plan frontmatter; update on phase close.

| ID       | Phase / track       | Status                  | Next action                                         |
| -------- | ------------------- | ----------------------- | --------------------------------------------------- |
| 0        | Quay gate           | **cancelled** (blocked) | Personal mirror only; re-gate before chart defaults |
| 1        | Sanitization        | **completed**           | —                                                   |
| 2        | CI + Makefile       | **completed**           | —                                                   |
| 3        | PLAN bootstrap      | **completed**           | —                                                   |
| 3-review | Skeptical re-review | **completed**           | Cycle 5 light delta → Proceed                       |
| 4        | OpenSSF Scorecard   | **completed**           | —                                                   |
| 5        | OpenSSF quick wins  | **completed**           | —                                                   |
| 6        | OpenSSF CodeQL      | **completed**           | —                                                   |
| 7        | Baseline smoke      | **completed**           | —                                                   |
| 8        | Spikes              | pending                 | Parallel `8-onnx` + `8-binary`                      |
| 9–13     | Core ML             | pending                 | Per merge gates (health + manual checklists)        |
| 14–19    | Deferred            | pending                 | After Phase 13                                      |

---

## Status

| Phase | Track                     | Status             | Merge gate                                                                                               |
| ----- | ------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------- |
| 0     | Quay gate                 | **Blocked (fail)** | All five `rh-ai-quickstart` tags pull; personal mirror documented                                        |
| 1     | Sanitization + helm fix   | **Done**           | `make check`; Quay chart defaults **deferred** (Phase 0 fail)                                            |
| 2     | CI + Makefile push        | **Done**           | `make check` + `make helm-template` + green Actions                                                      |
| 3     | PLAN bootstrap            | **Done**           | `make check` + Phase 3 close checklist (see below)                                                       |
| 4     | OpenSSF Scorecard install | **Done**           | `make check` + green Scorecard on fork `main`; ruleset `protect-main` requires Scorecard                 |
| 5     | OpenSSF quick wins        | **Done**           | `make check` + Phase 5 checklist (see OpenSSF section)                                                   |
| 6     | OpenSSF broader           | **Done**           | `make check` + CodeQL green (CI-Tests defers to Phase 7)                                                 |
| 7     | Baseline smoke            | **Done**           | `make check` + `make smoke` (**health** only; see smoke note)                                            |
| 8     | ONNX + binary spikes      | Planned            | Spike docs with pass/fail                                                                                |
| 9     | Capture/zoom (#5)         | Planned            | `make check` + `make smoke` (health) + manual **baseline** + **post-p0** sign-off in `baseline-smoke.md` |
| 10    | Binary KServe tensors     | Planned            | `make check` + `make smoke` (health) + manual **binary** checklist (script TBD)                          |
| 11    | GPU profiles              | Planned            | `make check` + `make smoke` (health) + GPU spike deferral table                                          |
| 12    | Crop + tiled SR           | Planned            | `make check` + `make smoke` (health) + manual **crop** checklist (script TBD)                            |
| 13    | OBB + SAHI                | Planned            | `make check` + `make smoke` (health) + manual sign-off per profiles exercised                            |
| 14–19 | Deferred                  | Planned (after 13) | Per phase in sections below                                                                              |

---

## Phase one-liners

| Phase  | Goal                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------ |
| **0**  | Quay gate — `podman pull` all five `rh-ai-quickstart/caisat` tags before chart default staging         |
| **1**  | Sanitize cluster defaults, cluster-info hook, helm metadata fix (+ Quay chart if gate passed)          |
| **2**  | CI workflow (pre-commit + Helm template), Makefile `helm-template` / `push-check` / `push`             |
| **3**  | In-repo PLAN, spike templates, README link, handover canonical PLAN                                    |
| **4**  | OpenSSF Scorecard workflow on fork; verify Code scanning (upstream PR deferred — fork-only validation) |
| **5**  | `SECURITY.md`, workflow `permissions:`, README Scorecard badge; branch-protection visibility           |
| **6**  | CodeQL SAST workflow; CI test job when tests exist; org rulesets / `SCORECARD_TOKEN` if needed         |
| **7**  | Baseline smoke doc + `make smoke` health profile                                                       |
| **8**  | SwinIR ONNX shape spike + binary KServe v2 round-trip spike (parallel tracks `8-onnx`, `8-binary`)     |
| **9**  | Capture/zoom alignment (upstream #5) — helm metadata fixed in Phase 1                                  |
| **10** | Binary tensor encode/decode + shared `aiohttp` session in both backends                                |
| **11** | GPU ServingRuntime spike per tier + compute profiles + `/api/capabilities`                             |
| **12** | Profile-aware crop chain + tiled SwinIR + cross-path parity                                            |
| **13** | OBB decode + rotated draw, SAHI slicing, route/resource tuning                                         |
| **14** | Structured logging, metrics, model-endpoint health probes                                              |
| **15** | CORS, upload limits, error sanitization, NetworkPolicy, Route OAuth                                    |
| **16** | YOLO11-OBB eval — **skip** if Phase 13 QA acceptable                                                   |
| **17** | kube-linter + re-enable pre-commit exclusions                                                          |
| **18** | Repo hygiene (backup file, chart README sync, pin deps)                                                |
| **19** | UX: coordinate search (#4), progress, error UI, detection health polling                               |

---

## OpenSSF supply-chain (Phases 4–6)

Install on a **contributor fork** of [`rh-ai-quickstart/CAIsat`](https://github.com/rh-ai-quickstart/CAIsat) first.

**Upstream PR deferred** (2026-06-29): fork-only validation for OpenSSF; no PR to `rh-ai-quickstart/CAIsat` until user re-opens upstream track.

README Scorecard badge uses the contributor fork slug (see README badge URL) until/unless upstream merge later.

| Phase | Deliverables                                               | Key files (Phase 4–6)                                   |
| ----- | ---------------------------------------------------------- | ------------------------------------------------------- |
| **4** | Scorecard workflow — pinned SHAs, `publish_results`, SARIF | `.github/workflows/scorecard-analysis.yml`              |
| **5** | `SECURITY.md`; workflow permissions; README badge          | `.github/SECURITY.md`, pre-commit workflow, `README.md` |
| **6** | CodeQL Python + JS; CI tests when present; org rulesets    | `.github/workflows/codeql-analysis.yml`                 |

**Merge gates:** Phase 4 — green Scorecard workflow on fork `main` + Security → Code scanning alerts.
Phase 5 — `SECURITY.md` committed, `permissions: contents: read` on pre-commit workflow, README badge live (fork slug until upstream merge).
Phase 6 — CodeQL workflow green; optional `tests/` + CI job may land in Phase 7 (document waiver if deferred).

**PR sequence (fork):** #21 Phase 4 Scorecard; #24 Phase 5 quick wins; #25 PLAN close; #26 markdown-link-check pin; #28 PLAN archive; #29 Phase 6 CodeQL; #31 PLAN tip sync; Phase 7 smoke next.

---

## Phase 4 close checklist

**Status:** Done (2026-06-29). Gate branch: `chore/phase-4-close` → merged PR #21 @ `ab1371c`.

Before marking Phase 4 **Done**:

1. [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) on fork `main` (merged via PR #21)
2. Green **Scorecard analysis** on fork `main`; OpenSSF Scorecard **5.2** (merge `ab1371c`)
3. Security → **Code scanning alerts** present (Scorecard SARIF)
4. Ruleset `protect-main` (ID `18274842`): `pre-commit` + **Scorecard analysis**; `strict_required_status_checks_policy: true`
5. Commit PLAN close; record tip SHA in handover

---

## Phase 5 close checklist

**Status:** Done (2026-06-29). Gate branch: `feat/phase-5-openssf-quick-wins` → merged PR #24 @ `f0e582a`.

Before marking Phase 5 **Done**:

1. [`.github/SECURITY.md`](../../.github/SECURITY.md) — reporting, supported versions, contact
2. [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — workflow-level `permissions: contents: read`
3. [`README.md`](../../README.md) — OpenSSF Scorecard badge (contributor fork slug; no change unless wrong/missing)
4. Branch protection on fork `main` — ruleset `protect-main` already requires `pre-commit` + Scorecard (documented in verification artifact)
5. `make check` green; PR to fork `main`; commit PLAN close; record tip SHA

---

## Phase 7 close checklist

**Status:** Done (2026-06-29). Gate branch: `feat/phase-7-baseline-smoke` → PR pending.

Before marking Phase 7 **Done**:

1. [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — health profile documented; cluster baseline sign-off optional until Phase 9
2. [`Makefile`](../../Makefile) — `smoke` target; [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh) — health profile only (`SMOKE_PROFILE=health`)
3. [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — `make smoke` step after Helm template (no cluster required)
4. `make check` + `make smoke` green locally; green **pre-commit** workflow on PR (includes smoke)
5. CI test job **waived** — no `tests/` directory; pytest job deferred until functional tests land (Phase 8+ or when tests added)
6. Commit PLAN close; record tip SHA

---

## Phase 6 close checklist

**Status:** Done (2026-06-29). Gate branch: `feat/phase-6-codeql` → merged PR #29 @ `31f058d`.

Before marking Phase 6 **Done**:

1. [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml) — Python + JavaScript/TypeScript matrix; pinned SHAs; `permissions: read-all`
2. Triggers: `push` + `pull_request` to `main`; weekly schedule aligned with Scorecard
3. GitHub default CodeQL setup **disabled** (API `state: not-configured`) — advanced workflow only; no duplicate dynamic CodeQL
4. Green **CodeQL** on PR #29 (Analyze python + javascript-typescript); `make check` green
5. Ruleset `protect-main`: CodeQL **not** added to required checks yet (PR validation first; add after push-to-main run confirms)
6. CI test job **deferred to Phase 7** (no `tests/` directory yet)
7. Commit PLAN close; record tip SHA

---

## Phase 3 close checklist

**Status:** Done (2026-06-29). Gate branch: `chore/phase-3-plan-close`.

Before marking Phase 3 **Done**:

1. [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) phase column matches [Smoke profiles](#smoke-profiles) below
2. [`docs/spikes/README.md`](../spikes/README.md) GPU deferral gate references **Phase 11** (not Phase 7)
3. [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md) uses integer phase IDs (no letter suffixes)
4. README **Where to Start** → this file (already linked)
5. Commit PLAN + cross-ref fixes; record tip SHA in handover

---

## Smoke automation vs merge gates

| Profile      | Automated (`make smoke`)                       | Merge gate                              |
| ------------ | ---------------------------------------------- | --------------------------------------- |
| **health**   | Yes (Phase 7)                                  | Required from Phase 7                   |
| **baseline** | No — cluster checklist in `baseline-smoke.md`  | Required from Phase 9 (manual sign-off) |
| **post-p0**  | No — manual capture/zoom                       | Required from Phase 9                   |
| **binary**   | No — implement in script or manual (Phase 10+) | Required from Phase 10                  |
| **crop**     | No — implement in script or manual (Phase 12+) | Required from Phase 12                  |

Do not treat Phases 9–13 as fully automated until `smoke-local.sh` implements the profile or the checklist is signed off in `baseline-smoke.md`.

---

## Spike gate table

| Spike             | Artifact                                           | Pass criteria                                        | Blocks                                                    |
| ----------------- | -------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------- |
| Quay tags         | [`../spikes/quay-tags.md`](../spikes/quay-tags.md) | All five `quay.io/rh-ai-quickstart/caisat` tags pull | Chart default image migration (blocked — personal mirror) |
| SwinIR ONNX       | `../spikes/swinir-onnx.md`                         | Input/output shapes documented; branch chosen        | Phase 12                                                  |
| Binary KServe v2  | `../spikes/binary-kserve-v2.md`                    | Round-trip binary infer vs MLServer                  | Phase 10                                                  |
| RHOAI GPU runtime | `../spikes/gpu-servingruntime.md`                  | Per-tier Ready + infer 200 (or deferral signed)      | `nvidia.com/gpu` in chart                                 |

---

## Parallel execution (multitask mode)

### Serial (Phases 1–7)

Phases 1 → 2 → 3 → 4 → 5 → 6 → 7 must complete in order on one branch/worktree. OpenSSF (4–6) precedes baseline smoke.

### After Phase 7

| Track        | Work                    | Merge rule                                          |
| ------------ | ----------------------- | --------------------------------------------------- |
| **8-onnx**   | SwinIR ONNX spike doc   | Both `8-onnx` and `8-binary` done before Phase 10   |
| **8-binary** | Binary KServe spike doc | Same                                                |
| **9**        | Capture/zoom #5         | Before Phase 12; do not parallel with Phase 12 crop |

### Critical path (serial)

Phase 8 → 10 → 11 → 12 → 13. Phase 9 → 10. Never Phase 10 before `8-binary` pass. Never Phase 12 before `8-onnx` pass.

### Do not parallelize

- Phase 10 + Phase 12 (binary blocks crop >256)
- Phase 11 + Phase 12 (profiles required for crop UX)
- Phase 9 capture + Phase 12
- Phase 8 spikes + Phase 11 GPU (do not start GPU spike work during Phase 8)
- Phase 4 + Phase 5 (5 needs Scorecard baseline from 4)
- Two agents, same phase, same files

### Per-merge checklist (Phases 9–13)

1. `git status` — no secrets staged
2. `make check`
3. `make helm-template` (if chart touched)
4. `make smoke` (health) or manual checklist in `baseline-smoke.md` for other profiles
5. `git push -u origin HEAD`

---

## Decisions

| Topic       | Decision                                                                                             |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| Priority    | Larger context (512+ crop, tiled SR)                                                                 |
| GPU         | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override                                |
| Detection   | Demo quality OK; defer YOLO11 eval; OBB fix before SAHI                                              |
| Git         | Push-as-you-go on feature branches; CI before push (`make push`)                                     |
| PLAN source | This file after Phase 3 merge                                                                        |
| Quay        | Phase 0 **fail** for rh-ai-quickstart; personal mirror + `values-quay-local.yaml.example` documented |
| OpenSSF     | Phases 4–6 on fork first; **upstream PR deferred** (fork-only validation; badge uses fork slug)      |
| Numbering   | Integer phases only; `-onnx`/`-binary` suffixes for parallel tracks                                  |

---

## Smoke profiles

| Profile      | Phases | Assertions                                        |
| ------------ | ------ | ------------------------------------------------- |
| **health**   | 7+     | `/health` 200 on both backends                    |
| **baseline** | 9+     | health + enhance/detect HTTP 200 + valid payloads |
| **post-p0**  | 9+     | baseline + manual capture/zoom sign-off 1×/2×/4×  |
| **binary**   | 10+    | baseline + binary content-type + decode           |
| **crop**     | 12+    | baseline/binary + profile default crop size       |

See [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md).

---

## Push-as-you-go

| Phase | Push after          |
| ----- | ------------------- |
| 0     | — (local gate only) |
| 1     | commit              |
| 2     | commit              |
| 3     | commit              |
| 4–6   | each phase          |
| 7     | commit              |
| 8+    | each phase          |

**Git rules:** feature branches only; never push `main`; no `--no-verify`.
