# CAIsat — Completed Phases

<!-- Assisted by: cursor, claude -->

Archive of merged foundation work. Active sequencing lives in [`PLAN.md`](PLAN.md).

**Renumbering (2026-06-29):** Serial suffixes removed (`1A`/`1B` → Phases 1–2). OpenSSF = Phases 4–6. Former phases 3–18 → 7–19.

**Branch tip (2026-06-29):** `chore/phase-3-plan-close` @ `e933394`. Phase 0 Quay gate **fail** for `rh-ai-quickstart`; personal mirror documented in [`../spikes/quay-tags.md`](../spikes/quay-tags.md).

---

## Baseline (upstream)

| Field | Value                                      |
| ----- | ------------------------------------------ |
| Goal  | Upstream CAIsat: 256 crop, CPU ONNX, no CI |
| Gate  | upstream `main` ref                        |

---

## Pre-commit + handover

| Field       | Value                                                           |
| ----------- | --------------------------------------------------------------- |
| Goal        | Pre-commit hooks, handover rules, `make check`, hook exclusions |
| Gate commit | `bf67549`                                                       |
| Branch      | `chore/pre-commit-and-handover`                                 |

Deliverables: `.pre-commit-config.yaml`, local Cursor rules (`.cursor/rules/` gitignored — copy from `~/.cursor/rule-templates/` or project bootstrap), `Makefile` (`check`, `pre-commit`, `install-hooks`).

---

## Phase 1 — Sanitization + helm metadata

| Field  | Value                                                         |
| ------ | ------------------------------------------------------------- |
| Goal   | Remove cluster defaults, cluster-info hook, helm metadata fix |
| Commit | `f6419cc`                                                     |

- `backend/app.py`, `backend-detection/app.py` — require `MODEL_ENDPOINT`; no endpoint in root JSON
- `backend/.env.example`, `backend-detection/.env.example`
- `scripts/check-no-cluster-info.sh` + pre-commit hook
- `chart/templates/backend-deployment.yaml` — duplicate `metadata` removed
- **Quay gate failed** — chart `values.yaml` / `chart/README.md` Quay migration **not** committed

---

## Phase 2 — CI + Makefile push workflow

| Field  | Value                                          |
| ------ | ---------------------------------------------- |
| Goal   | Pre-commit CI workflow + Makefile push targets |
| Commit | `c843a2d`                                      |

Deliverables:

- `.github/workflows/pre-commit.yaml` — pre-commit + `helm template test ./chart`
- `Makefile` — `helm-template`, `push-check`, `push`

---

## Phase 3 — PLAN bootstrap

| Field  | Value                                                                                        |
| ------ | -------------------------------------------------------------------------------------------- |
| Goal   | In-repo PLAN, spike templates, phase-ID sync, smoke automation table, Cycle 5 plan revisions |
| Branch | `chore/phase-3-plan-close`                                                                   |
| Commit | `e933394`                                                                                    |
| Gate   | `make check`                                                                                 |

Deliverables:

- [`PLAN.md`](PLAN.md) — phases 0–19, verification artifact, active todos, OpenSSF 4–6, smoke automation table
- [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) — Phase 1–3 archive
- [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — phase IDs aligned to PLAN
- [`docs/spikes/README.md`](../spikes/README.md) — GPU deferral gate Phase 11
- [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md) — integer phase IDs
- README **Where to Start** → `docs/project/PLAN.md` (pre-existing)

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.

---
