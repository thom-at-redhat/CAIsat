# CAIsat Project Plan

<!-- Assisted by: cursor, claude -->

**Canonical source of truth** for operational follow-up, merge gates, and spike outcomes. Edit this file — not Cursor plan artifacts — after bootstrap.

**Branch:** `main` @ `dd40d02` (2026-06-30). **All planned phases (0–23) complete.** Open operational items below; use feature branches for follow-up; never push `main`.

**Archive:** Completed phased work (phases **0–23**) → [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Spike results → [`../spikes/`](../spikes/).

**Deep-dive (secondary, archived):** Cursor artifact `~/.cursor/plans/caisat_plan_bootstrap_3c3a4d19.plan.md` — archived 2026-06-29; historical OpenSSF detail, parallel execution, smoke profiles;
`~/.cursor/plans/caisat_comprehensive_review_bde83bb3.plan.md` — technical detail only.

**Renumbering (2026-06-29):** Removed serial suffixes (`1A`/`1B` → Phases 1–2). OpenSSF supply-chain = Phases **4–6**. Former phases 3–18 → **7–19**.

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
| OpenSSF Scorecard       | [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) | fork `main` `4abef20`; Scorecard **6.0**       | ok                       |
| Scorecard gap plan      | [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md)                               | checks, targets; Phases 8–11 archived          | ok                       |
| SAST (CodeQL)           | [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml)       | PR #29; Python + JS; **10/10**                 | ok                       |
| SECURITY.md             | [`.github/SECURITY.md`](../../.github/SECURITY.md)                                           | PR #24; reporting + supported versions         | ok                       |
| Workflow permissions    | [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml)               | PR #24; `permissions: contents: read`          | ok                       |
| README Scorecard badge  | [`README.md`](../../README.md)                                                               | contributor fork slug (see badge URL)          | ok (fork until upstream) |
| Branch protection       | GitHub ruleset `protect-main` (ID `18274842`)                                                | `pre-commit` + Scorecard + CodeQL on `main`    | ok (fork)                |
| Markdown link check pin | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #26; `markdown-link-check@3.14.2` pinned    | ok                       |
| Pre-commit SHA pins     | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | Phase 11 PR #41; 13 hook repos + exact pins    | ok                       |
| Scorecard pre-commit    | [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)                                   | PR #42; local Scorecard hook + npm vuln fix    | ok                       |
| Upstream sync           | fork `main` @ `4abef20`                                                                      | PR #43; change detection + S4/DSPA pipelines   | ok (inbound only)        |
| Spike doc index         | [`docs/spikes/`](../spikes/)                                                                 | ML spikes documented (PR #45)                  | ok                       |
| Phases 12–23 merge      | PR #45 @ `ee3f1b3`                                                                           | `integration/phases-12-23`                     | ok                       |
| PLAN post-23 archive    | PR #47 @ `4abef20`                                                                           | stop_work PLAN archive merged                  | ok                       |
| Local smoke profiles    | [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh) L133–143                            | `health` + `binary` (encode/decode unit test)  | ok                       |
| Cluster baseline        | [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) L97–102               | waiver — no deployed stack 2026-06-30          | unchecked                |

**Last verified:** fork `main` @ `dd40d02` (2026-06-30); PR #50 merged (cropSize + MT-1a columns); MT-0 PR #48; local health+binary smoke pass; Phases 0–23 merged; Scorecard **6.0**; SAST **10/10**

**Revalidate:** `docs/project/PLAN.md`, `docs/validation/baseline-smoke.md`, `docs/spikes/README.md`, `docs/spikes/scorecard-gaps.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `chart/values.yaml`

**Claims not checked:** Phase 13 cluster baseline (React 19 / three / map UX); Phase 16 crop sign-off; 12-binary cluster round-trip **fail**; GPU tiers **deferred**; post-Phase-11 Scorecard re-run

**Skeptical review:** Cycle 5 (2026-06-29) **Proceed** — Phase 5 fork gate closed: PR #24 merged @ `f0e582a`; SECURITY.md + pre-commit permissions verified on fork `main`.

---

## Active todos

All phased work archived in [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md). Operational follow-up only:

| ID        | Track                | Status      | Next action                                                                                        |
| --------- | -------------------- | ----------- | -------------------------------------------------------------------------------------------------- |
| baseline  | Phase 13 sign-off    | **waiver**  | No CAIsat stack (2026-06-30); local pass @ `64a472b`; cluster when deployed — `baseline-smoke.md`  |
| binary    | 12-binary / Phase 14 | **waiver**  | ea.2 blocked @ `2aa6343`; no deploy; JSON fallback; re-test w/ Quay egress — `binary-kserve-v2.md` |
| crop      | Phase 16 sign-off    | **blocked** | CPU partial after MT-1b; GPU full after MT-3 — `baseline-smoke.md`                                 |
| gpu       | Phase 15 deferral    | **waiver**  | T4/L40S/Hopper deferred; re-test 2026-07-31 or 512+ demo — `gpu-servingruntime.md`                 |
| scorecard | Optional             | **open**    | Re-run Scorecard on `main`; Branch-Protection score may lag API                                    |
| upstream  | Outbound PR          | **open**    | PR back to `rh-ai-quickstart/CAIsat` still deferred per decision                                   |

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

| Topic       | Decision                                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Priority    | Larger context (512+ crop, tiled SR) — shipped Phase 16                                                                                                      |
| GPU         | 3 clusters (T4, L40S, Hopper) + CPU; auto-detect with manual override; tiers **deferred**                                                                    |
| Detection   | Demo quality OK; YOLO11 eval **skipped**; OBB + SAHI shipped Phase 17                                                                                        |
| Git         | Push-as-you-go on feature branches; CI before push (`make push`)                                                                                             |
| PLAN source | This file after Phase 3 merge; phased work archived post-23                                                                                                  |
| Quay        | Phase 0 **pass** on fork (`thom_at_redhat/caisat` public mirror); upstream `rh-ai-quickstart` **fail**                                                       |
| OpenSSF     | Phases 4–6 on fork first; badge uses fork slug                                                                                                               |
| Upstream    | Fork synced from upstream @ `0e4281e` (PR #43); PR back to `rh-ai-quickstart/CAIsat` still deferred                                                          |
| Scorecard   | **6.0** @ `acb9a79`; gap plan Phases 9–11 done; see `scorecard-gaps.md`                                                                                      |
| 12-binary   | **fail** @ RHOAI 3.5.ea.1 (binary HTTP 500); ea.2 re-test **blocked/inconclusive** @ `2aa6343` — same MLServer version; Phase 14 JSON-fallback waiver stands |
| Spike docs  | Cluster names **never** in spike docs — use `<namespace>` placeholders                                                                                       |

---

## Open items

Follow-up after Phases **0–23** merge (PR #45 @ `ee3f1b3`; PLAN archive PR #47 @ `4abef20`). Code merged; cluster validation and spike gaps remain.

| Item              | Detail                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------- |
| Binary spike fail | `12-binary` **fail** @ ea.1; ea.2 **blocked** @ `2aa6343`; JSON fallback active         |
| Phase 13 baseline | Cluster **waiver** (no deploy 2026-06-30); local pass @ `64a472b` — `baseline-smoke.md` |
| Crop sign-off     | **blocked** on MT-1b; CPU partial then GPU full after MT-3 — `baseline-smoke.md`        |
| GPU deferral      | T4/L40S/Hopper **waiver**; re-test 2026-07-31 — `gpu-servingruntime.md`                 |

---

## Open blockers

| Blocker              | Detail                                                                                                                                        |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| MLServer binary      | ea.2 re-test **blocked/inconclusive** @ `2aa6343`: RHOAI 3.5.0-ea.2; MLServer 1.7.1+rhaiv.8; binary infer not re-run (Quay pull unauthorized) |
| Phase 14 binary-only | JSON fallback active until binary round-trip passes on cluster                                                                                |

---

## Smoke profiles

| Profile      | Phases | Assertions                                           | Automation                                                        |
| ------------ | ------ | ---------------------------------------------------- | ----------------------------------------------------------------- |
| **health**   | 7+     | `/health` 200 on both backends                       | `make smoke` (CI; health only)                                    |
| **baseline** | 13+    | health + enhance/detect 200 + valid payloads         | Manual — `baseline-smoke.md`                                      |
| **post-p0**  | 13+    | baseline + capture/zoom 1×/2×/4×                     | Manual                                                            |
| **binary**   | 14+    | Local: encode/decode test. Cluster: infer round-trip | Local: `SMOKE_PROFILE=binary make smoke` (not CI); cluster manual |
| **crop**     | 16+    | baseline/binary + profile default crop size          | Manual                                                            |

See [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md).

---

## Git rules

Feature branches only; never push `main`; no `--no-verify`. Run `make check` before push (`make push`).
