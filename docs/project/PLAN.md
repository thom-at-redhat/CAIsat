# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for phase sequencing, merge gates, and spike gates. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `chore/pre-commit-and-handover` (Phases 1–2); optionally `feat/caisat-core` from Phase 3 onward.

**Archive:** Completed work → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary):** Cursor artifact `~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only; not authoritative for sequencing.

---

## Status

| Phase | Track                 | Status            | Merge gate                                   |
| ----- | --------------------- | ----------------- | -------------------------------------------- |
| 1     | Foundation            | **Done**          | `make check` (+ `make helm-template` for 1B) |
| 2     | PLAN bootstrap        | **In progress**   | `make check`                                 |
| 3     | Baseline smoke        | Planned           | `make check` + `make smoke` (health)         |
| 4     | ONNX + binary spikes  | Planned           | Spike docs with pass/fail                    |
| 5     | Capture/zoom (#5)     | Planned           | `make smoke` (baseline)                      |
| 6     | Binary KServe tensors | Planned           | `make smoke` (binary)                        |
| 7     | GPU profiles          | Planned           | `make smoke` + spike deferral table          |
| 8     | Crop + tiled SR       | Planned           | `make smoke` (crop)                          |
| 9     | OBB + SAHI            | Planned           | `make smoke`                                 |
| 10–15 | Deferred              | Planned (after 9) | Per phase in sections below                  |

---

## Phase one-liners

| Phase  | Goal                                                                                                |
| ------ | --------------------------------------------------------------------------------------------------- |
| **1**  | Sanitize cluster defaults, cluster-info hook, helm metadata fix, CI workflow, Makefile push targets |
| **2**  | In-repo PLAN, spike templates, README link, handover canonical PLAN                                 |
| **3**  | Baseline smoke doc + `make smoke` health profile                                                    |
| **4**  | SwinIR ONNX shape spike + binary KServe v2 round-trip spike (hard gates before crop >256)           |
| **5**  | Capture/zoom alignment (upstream #5) — no helm metadata (fixed in Phase 1A)                         |
| **6**  | Binary tensor encode/decode + shared `aiohttp` session in both backends                             |
| **7**  | GPU ServingRuntime spike per tier + compute profiles + `/api/capabilities`                          |
| **8**  | Profile-aware crop chain + tiled SwinIR + cross-path parity                                         |
| **9**  | OBB decode + rotated draw, SAHI slicing, route/resource tuning                                      |
| **10** | Structured logging, metrics, model-endpoint health probes                                           |
| **11** | CORS, upload limits, error sanitization, NetworkPolicy, Route OAuth                                 |
| **12** | YOLO11-OBB eval — **skip** if Phase 9 QA acceptable                                                 |
| **13** | kube-linter + re-enable pre-commit exclusions                                                       |
| **14** | Repo hygiene (backup file, chart README sync, pin deps)                                             |
| **15** | UX: coordinate search (#4), progress, error UI, detection health polling                            |

---

## Spike gate table

| Spike             | Artifact                                           | Pass criteria                                        | Blocks                        |
| ----------------- | -------------------------------------------------- | ---------------------------------------------------- | ----------------------------- |
| Quay tags         | [`../spikes/quay-tags.md`](../spikes/quay-tags.md) | All five `quay.io/rh-ai-quickstart/caisat` tags pull | Chart default image migration |
| SwinIR ONNX       | `../spikes/swinir-onnx.md`                         | Input/output shapes documented; branch chosen        | Phase 8                       |
| Binary KServe v2  | `../spikes/binary-kserve-v2.md`                    | Round-trip binary infer vs MLServer                  | Phase 6                       |
| RHOAI GPU runtime | `../spikes/gpu-servingruntime.md`                  | Per-tier Ready + infer 200 (or deferral signed)      | `nvidia.com/gpu` in chart     |

---

## Parallel execution (multitask mode)

### Serial (Phases 1–3)

Phases 1 → 2 → 3 must complete in order on one branch/worktree.

### After Phase 3

| Track        | Work                    | Merge rule                                        |
| ------------ | ----------------------- | ------------------------------------------------- |
| **4-onnx**   | SwinIR ONNX spike doc   | Both 4-onnx and 4-binary done before Phase 6      |
| **4-binary** | Binary KServe spike doc | Same                                              |
| **5**        | Capture/zoom #5         | Before Phase 8; do not parallel with Phase 8 crop |

### Critical path (serial)

Phase 4 → 6 → 7 → 8 → 9. Phase 5 → 6. Never Phase 6 before Phase 4 binary pass. Never Phase 8 before Phase 4 ONNX pass.

### Do not parallelize

- Phase 6 + Phase 8 (binary blocks crop >256)
- Phase 7 + Phase 8 (profiles required for crop UX)
- Phase 5 capture + Phase 8
- Phase 4 + Phase 7 (GPU needs Phase 6)
- Two agents, same phase, same files

### Per-merge checklist (Phases 5–9)

1. `git status` — no secrets staged
2. `make check`
3. `make helm-template` (if chart touched)
4. `make smoke` (profile for target phase)
5. `git push -u origin HEAD`

---

## Decisions

| Topic       | Decision                                                              |
| ----------- | --------------------------------------------------------------------- |
| Priority    | Larger context (512+ crop, tiled SR)                                  |
| GPU         | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override |
| Detection   | Demo quality OK; defer YOLO11 eval; OBB fix before SAHI               |
| Git         | Push-as-you-go on feature branches; CI before push (`make push`)      |
| PLAN source | This file after Phase 2 merge                                         |
| Quay        | Chart migration deferred until Quay gate passes (see spike doc)       |

---

## Smoke profiles

| Profile      | Phases | Assertions                                        |
| ------------ | ------ | ------------------------------------------------- |
| **health**   | 3+     | `/health` 200 on both backends                    |
| **baseline** | 5+     | health + enhance/detect HTTP 200 + valid payloads |
| **post-p0**  | 5+     | baseline + manual capture/zoom sign-off 1×/2×/4×  |
| **binary**   | 6+     | baseline + binary content-type + decode           |
| **crop**     | 8+     | baseline/binary + profile default crop size       |

See [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md).

---

## Push-as-you-go

| Phase group | Push after |
| ----------- | ---------- |
| 1 (1A + 1B) | 1B         |
| 2           | commit     |
| 3           | commit     |
| 4+          | each phase |

**Git rules:** feature branches only; never push `main`; no `--no-verify`.
