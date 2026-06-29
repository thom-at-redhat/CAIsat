# CAIsat — Completed Phases

<!-- Assisted by: cursor, claude -->

Archive of merged foundation work. Active sequencing lives in [`PLAN.md`](PLAN.md).

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

Deliverables: `.pre-commit-config.yaml`, `.cursor/rules/handover-notes.mdc`, `Makefile` (`check`, `pre-commit`, `install-hooks`).

---

## Phase 1 — Sanitization + CI

| Field   | Value                                                                             |
| ------- | --------------------------------------------------------------------------------- |
| Goal    | Remove cluster defaults, cluster-info hook, helm metadata fix, CI + push workflow |
| Commits | `f6419cc` (1A), `c843a2d` (1B)                                                    |

### Phase 1A (`f6419cc`)

- `backend/app.py`, `backend-detection/app.py` — require `MODEL_ENDPOINT`; no endpoint in root JSON
- `backend/.env.example`, `backend-detection/.env.example`
- `scripts/check-no-cluster-info.sh` + pre-commit hook
- `chart/templates/backend-deployment.yaml` — duplicate `metadata` removed
- **Quay gate failed** — chart `values.yaml` / `chart/README.md` Quay migration **not** committed

### Phase 1B (`c843a2d`)

- `.github/workflows/pre-commit.yaml` — pre-commit + `helm template test ./chart`
- `Makefile` — `helm-template`, `push-check`, `push`
