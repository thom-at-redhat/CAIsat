# CAIsat — Completed Phases

<!-- Assisted by: cursor, claude -->

Archive of merged foundation work. Active sequencing lives in [`PLAN.md`](PLAN.md).

**Renumbering (2026-06-29):** Serial suffixes removed (`1A`/`1B` → Phases 1–2). OpenSSF = Phases 4–6. Former phases 3–18 → 7–19.

**Renumbering (2026-06-30):** Inserted Phases 8–11 (OpenSSF score improvement); former 8–19 → 12–23. Active plan now phases 0 + 8–23.

**Branch tip (2026-06-30):** fork `main` @ `12c04945`; Phase 7 close in PR #32 (open). Phase 0 Quay gate **fail** for `rh-ai-quickstart`; personal mirror in [`../spikes/quay-tags.md`](../spikes/quay-tags.md).

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

- [`PLAN.md`](PLAN.md) — phases 0–23 (after 2026-06-30 renumber), verification artifact, active todos
- [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) — Phase 1–7 archive
- [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — phase IDs aligned to PLAN
- [`docs/spikes/README.md`](../spikes/README.md) — GPU deferral gate Phase 15
- [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md) — integer phase IDs
- README **Where to Start** → `docs/project/PLAN.md` (pre-existing)

### Phase 3 close checklist

**Status:** Done (2026-06-29).

1. [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) phase column matches smoke profiles in PLAN
2. [`docs/spikes/README.md`](../spikes/README.md) GPU deferral gate references **Phase 15** (not Phase 7)
3. [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md) uses integer phase IDs (no letter suffixes)
4. README **Where to Start** → PLAN (already linked)
5. Commit PLAN + cross-ref fixes; record tip SHA in handover

---

## OpenSSF supply-chain (Phases 4–6)

Install on a **contributor fork** of [`rh-ai-quickstart/CAIsat`](https://github.com/rh-ai-quickstart/CAIsat) first.

**Upstream PR deferred** (2026-06-29): fork-only validation; no PR to upstream until user re-opens upstream track.

README Scorecard badge uses the contributor fork slug until/unless upstream merge later.

| Phase | Deliverables                                               | Key files                                          |
| ----- | ---------------------------------------------------------- | -------------------------------------------------- |
| **4** | Scorecard workflow — pinned SHAs, `publish_results`, SARIF | `.github/workflows/scorecard-analysis.yml`         |
| **5** | `SECURITY.md`; workflow permissions; README badge          | `.github/SECURITY.md`, pre-commit workflow, README |
| **6** | CodeQL Python + JS; CI tests when present; org rulesets    | `.github/workflows/codeql-analysis.yml`            |

**Merge gates:** Phase 4 — green Scorecard workflow on fork `main` + Security → Code scanning alerts.
Phase 5 — `SECURITY.md` committed, `permissions: contents: read` on pre-commit workflow, README badge live.
Phase 6 — CodeQL workflow green; CI test job deferred to Phase 7 (no `tests/` yet).

**PR sequence (fork):** #21 Phase 4 Scorecard; #24 Phase 5 quick wins; #25 PLAN close; #26 markdown-link-check pin; #28 PLAN archive; #29 Phase 6 CodeQL; #31 PLAN tip sync; #32 Phase 7 smoke.

**Score at Phase 4 close:** 5.2. **Score after Phase 6 + fork tip sync:** **6.0** @ `12c04945` (2026-06-30); SAST **10/10**.

---

## Phase 4 — OpenSSF Scorecard install

| Field  | Value                                             |
| ------ | ------------------------------------------------- |
| Goal   | Scorecard workflow on fork; Code scanning SARIF   |
| Branch | `chore/phase-4-close` → merged PR #21 @ `ab1371c` |
| Gate   | `make check` + green Scorecard on fork `main`     |

### Phase 4 close checklist

**Status:** Done (2026-06-29).

1. [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) on fork `main` (merged via PR #21)
2. Green **Scorecard analysis** on fork `main`; OpenSSF Scorecard **5.2** (merge `ab1371c`)
3. Security → **Code scanning alerts** present (Scorecard SARIF)
4. Ruleset `protect-main` (ID `18274842`): `pre-commit` + **Scorecard analysis**; `strict_required_status_checks_policy: true`
5. Commit PLAN close; record tip SHA in handover

---

## Phase 5 — OpenSSF quick wins

| Field  | Value                                                         |
| ------ | ------------------------------------------------------------- |
| Goal   | SECURITY.md, workflow permissions, README Scorecard badge     |
| Branch | `feat/phase-5-openssf-quick-wins` → merged PR #24 @ `f0e582a` |
| Gate   | `make check`                                                  |

### Phase 5 close checklist

**Status:** Done (2026-06-29).

1. [`.github/SECURITY.md`](../../.github/SECURITY.md) — reporting, supported versions, contact
2. [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — workflow-level `permissions: contents: read`
3. [`README.md`](../../README.md) — OpenSSF Scorecard badge (contributor fork slug)
4. Branch protection on fork `main` — ruleset `protect-main` requires `pre-commit` + Scorecard
5. `make check` green; PR to fork `main`; commit PLAN close; record tip SHA

---

## Phase 6 — OpenSSF CodeQL

| Field  | Value                                             |
| ------ | ------------------------------------------------- |
| Goal   | CodeQL SAST workflow; Python + JavaScript matrix  |
| Branch | `feat/phase-6-codeql` → merged PR #29 @ `31f058d` |
| Gate   | `make check` + green CodeQL                       |

### Phase 6 close checklist

**Status:** Done (2026-06-29).

1. [`.github/workflows/codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml) — Python + JavaScript/TypeScript matrix; pinned SHAs; `permissions: read-all`
2. Triggers: `push` + `pull_request` to `main`; weekly schedule aligned with Scorecard
3. GitHub default CodeQL setup **disabled** (API `state: not-configured`) — advanced workflow only
4. Green **CodeQL** on PR #29; `make check` green
5. Ruleset `protect-main`: CodeQL **not** added to required checks yet (PR validation first; Phase 10 adds)
6. CI test job **deferred to Phase 7** (no `tests/` directory yet)
7. Commit PLAN close; record tip SHA

---

## Phase 7 — Baseline smoke (health)

| Field  | Value                                                           |
| ------ | --------------------------------------------------------------- |
| Goal   | Baseline smoke doc + `make smoke` health profile; CI smoke step |
| Branch | `feat/phase-7-baseline-smoke` → PR #32 (open)                   |
| Gate   | `make check` + `make smoke` (health only)                       |

Deliverables:

- [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — health profile; cluster baseline optional until Phase 13
- [`Makefile`](../../Makefile) — `smoke` target → [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)
- [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — `make smoke` after Helm template
- [`PLAN.md`](PLAN.md) — Phase 7 archived; PLAN renumber 8–23 (PR #32)

Waived: `tests/` + CI pytest job (no test suite yet; deferred to Phase 12+).

### Phase 7 close checklist

**Status:** Done (2026-06-30). Gate branch: `feat/phase-7-baseline-smoke` → PR #32 pending merge.

1. [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — health profile documented; cluster baseline sign-off optional until Phase 13
2. [`Makefile`](../../Makefile) — `smoke` target; [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh) — health profile only (`SMOKE_PROFILE=health`)
3. [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — `make smoke` step after Helm template (no cluster required)
4. `make check` + `make smoke` green locally; green **pre-commit** workflow on PR (includes smoke)
5. CI test job **waived** — no `tests/` directory; pytest job deferred until functional tests land (Phase 12+ or when tests added)
6. Commit PLAN close + phase renumber; record tip SHA

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.
