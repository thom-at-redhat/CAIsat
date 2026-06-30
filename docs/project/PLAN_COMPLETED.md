# CAIsat — Completed Phases

<!-- Assisted by: cursor, claude -->

Archive of merged foundation work. Active sequencing lives in [`PLAN.md`](PLAN.md).

**Renumbering (2026-06-29):** Serial suffixes removed (`1A`/`1B` → Phases 1–2). OpenSSF = Phases 4–6. Former phases 3–18 → 7–19.

**Renumbering (2026-06-30):** Inserted Phases 8–11 (OpenSSF score improvement); former 8–19 → 12–23. Active plan now phases **12–23** (Phase 12 next).

**Branch tip (2026-06-30):** fork `main` @ `0e4281e`; phases **0–11** complete. Upstream Quay gate **fail** for `rh-ai-quickstart`; fork mirror in [`../spikes/quay-tags.md`](../spikes/quay-tags.md).

Fork synced from upstream via PR #43; outbound PR to rh-ai-quickstart still deferred.

## Phase one-liners (0, 8–11)

| Phase  | Goal                                                                                      |
| ------ | ----------------------------------------------------------------------------------------- |
| **0**  | Quay gate — anonymous pull of all five chart tags; fork public mirror (see quay-tags)     |
| **8**  | OpenSSF score baseline — sync PLAN/badge, `scorecard-gaps.md`, record Scorecard 6.0       |
| **9**  | Dependency hygiene — enable/merge Dependabot updates; reduce OSV vulnerability count      |
| **10** | Branch protection hardening — ruleset: CodeQL required, maximal settings feasible on fork |
| **11** | Pin remaining dependencies — pre-commit/workflow SHA pins to 10/10 Pinned-Dependencies    |

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

**Score at Phase 4 close:** 5.2. **Score after Phase 6 + fork tip sync:** **6.0** @ `12c04945` (2026-06-30); SAST **10/10**. **Re-baseline Phase 8:** **6.0** @ `acb9a79`.

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
| Branch | `feat/phase-7-baseline-smoke` → merged PR #32 @ `b1ee8da`       |
| Gate   | `make check` + `make smoke` (health only)                       |

Deliverables:

- [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — health profile; cluster baseline optional until Phase 13
- [`Makefile`](../../Makefile) — `smoke` target → [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh)
- [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — `make smoke` after Helm template
- [`PLAN.md`](PLAN.md) — Phase 7 archived; PLAN renumber 8–23 (PR #32)

Waived: `tests/` + CI pytest job (no test suite yet; deferred to Phase 12+).

### Phase 7 close checklist

**Status:** Done (2026-06-30). Merged PR #32 @ `b1ee8da`.

1. [`docs/validation/baseline-smoke.md`](../validation/baseline-smoke.md) — health profile documented; cluster baseline sign-off optional until Phase 13
2. [`Makefile`](../../Makefile) — `smoke` target; [`scripts/smoke-local.sh`](../../scripts/smoke-local.sh) — health profile only (`SMOKE_PROFILE=health`)
3. [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — `make smoke` step after Helm template (no cluster required)
4. `make check` + `make smoke` green locally; green **pre-commit** workflow on PR (includes smoke)
5. CI test job **waived** — no `tests/` directory; pytest job deferred until functional tests land (Phase 12+ or when tests added)
6. Commit PLAN close + phase renumber; record tip SHA

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.

---

## Phase 0 — Quay gate (fork mirror)

| Field  | Value                                                                                        |
| ------ | -------------------------------------------------------------------------------------------- |
| Goal   | Anonymous pull of all five chart tags via fork mirror                                        |
| Branch | `chore/phase-0-quay-mirror` → merged PR #33 @ `acb9a79`                                      |
| Gate   | `make check`; five tags pull from fork mirror (see [`quay-tags.md`](../spikes/quay-tags.md)) |

Deliverables:

- [`chart/values.yaml`](../../chart/values.yaml) — default image points to fork mirror (see [`quay-tags.md`](../spikes/quay-tags.md))
- [`docs/spikes/quay-tags.md`](../spikes/quay-tags.md) — **pass** on fork mirror; upstream `rh-ai-quickstart` still **fail**

### Phase 0 close checklist

**Status:** Done (2026-06-30). Merged PR #33 @ `acb9a79`.

1. All five chart tags pull anonymously from fork mirror (commands in [`quay-tags.md`](../spikes/quay-tags.md))
2. [`chart/values.yaml`](../../chart/values.yaml) defaults updated; upstream unauthorized pull documented
3. `make check` green; commit PLAN close; record tip SHA

---

## Phase 8 — OpenSSF score baseline

| Field  | Value                                                                   |
| ------ | ----------------------------------------------------------------------- |
| Goal   | Sync PLAN/badge, finalize `scorecard-gaps.md`, record Scorecard **6.0** |
| Branch | `chore/phase-8-score-baseline` → merged PR #34 @ `6b0a209`              |
| Gate   | `make check` (doc-only)                                                 |

Deliverables:

- [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — baseline @ `acb9a79`; Maintained/Contributors waivers documented
- [`PLAN.md`](PLAN.md) — verification artifact, todos, status synced; Phase 8 archived here
- Scorecard API confirms **6.0** @ fork `main` `acb9a79` (2026-06-30)

### Phase 8 close checklist

**Status:** Done (2026-06-30). Merged PR #34 @ `6b0a209`.

1. Scorecard API: **6.0** on contributor fork (verified via `api.scorecard.dev`; see README badge)
2. [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — baseline SHA `acb9a79`; explicit Maintained + Contributors waiver section
3. [`PLAN.md`](PLAN.md) — branch header, last verified, verification artifact, todos, status table updated
4. [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) — Phase 8 summary archived; Phase 0 close recorded
5. `make check` green locally; green **pre-commit** workflow on PR
6. Commit PLAN close; record tip SHA in handover

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.

---

## Phase 9 — Dependency hygiene

| Field  | Value                                                                                                                                                 |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Goal   | Enable/merge Dependabot updates; reduce OSV vulnerability count                                                                                       |
| Branch | Batch 1: `feat/phase-9-dependency-hygiene` → merged PR #35 @ `30c55ef`; batch 2: `feat/phase-9-dependency-hygiene-batch2` → merged PR #36 @ `7d2106b` |
| Gate   | `make check` + `make smoke` (health); green CI                                                                                                        |

Deliverables:

- Dependabot PR batches merged — safe patches in batch 1; previously deferred majors in batch 2 (Pillow 12, FastAPI, numpy 2, React 19, react-leaflet 5, three 0.185, etc.)
- [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — Phase 9 triage tables (batch 1 + batch 2)
- [`PLAN.md`](PLAN.md) — Phase 9 archived; Phase 10 next

### Caveats (from scorecard-gaps)

- **Cluster validation gap:** React 19 / Three 0.185 / react-leaflet 5 map and globe UX not validated on cluster until Phase 13 baseline sign-off.
- **numpy 2:** requirements bump only; health smoke passes (no ONNX inference in smoke profile).
- **Scorecard:** baseline remains **6.0** @ `6b0a209`; re-run on `main` @ `7d2106b` after Phase 9 close (TBD).
- **Dependabot:** alert count **98→21** on `main` post-batch-2 (8H/12M/1L per push notice); re-run alert count after merge for authoritative tally.

### Phase 9 close checklist

**Status:** Done (2026-06-30). Merged PR #35 @ `30c55ef` + PR #36 @ `7d2106b`.

1. Batch 1 — workflow pins, python-dotenv, python-multipart, axios patch, partial aiohttp (see scorecard-gaps batch 1 table)
2. Batch 2 — all previously deferred PRs merged; `make check` + health smoke green on batch 2 branch
3. [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — batch 2 complete; no remaining deferrals in Phase 9 scope
4. [`PLAN.md`](PLAN.md) — branch header @ `7d2106b`, todos, status table, last verified
5. [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) — Phase 9 summary archived (this section)
6. `make check` green; green **pre-commit** workflow on PLAN close PR

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.

---

## Phase 10 — Branch protection hardening

| Field  | Value                                                                                  |
| ------ | -------------------------------------------------------------------------------------- |
| Goal   | Harden ruleset `protect-main`: CodeQL required, maximal settings feasible on solo fork |
| Branch | `feat/phase-10-branch-protection` → merged PR #38 @ `5d02e74`                          |
| Gate   | `make check`; document ruleset before/after in `scorecard-gaps.md`                     |

Deliverables:

- GitHub ruleset `protect-main` (ID `18274842`) — added **CodeQL** to required status checks
- [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — Phase 10 section: before/after JSON, Code-Review waiver
- [`PLAN.md`](PLAN.md) — Phase 10 archived; Phase 11 next

### Ruleset summary

| Setting                         | Before (Phase 4)                   | After (Phase 10)                          |
| ------------------------------- | ---------------------------------- | ----------------------------------------- |
| Required checks                 | `pre-commit`, `Scorecard analysis` | + `CodeQL`                                |
| `strict_required_status_checks` | `true`                             | `true` (unchanged)                        |
| Block deletion                  | yes                                | yes (unchanged)                           |
| Block force push                | yes (`non_fast_forward`)           | yes (unchanged)                           |
| Require PR                      | yes                                | yes (unchanged)                           |
| Approving reviews               | 0                                  | 0 (solo fork waiver — see scorecard-gaps) |

### Phase 10 close checklist

**Status:** Done (2026-06-30). Merged PR #38 @ `5d02e74`.

1. `gh api` PUT ruleset `18274842` — CodeQL added; verified via GET
2. [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — Phase 10 before/after, Code-Review waiver, expected Branch-Protection impact
3. [`PLAN.md`](PLAN.md) — branch header, todos, status table, verification artifact updated
4. [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) — Phase 10 summary archived (this section)
5. `make check` green; green CI on PR (pre-commit + CodeQL + Scorecard)

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.

---

## Phase 11 — Pin remaining dependencies

| Field  | Value                                                               |
| ------ | ------------------------------------------------------------------- |
| Goal   | Pin remaining workflow/pre-commit refs; Pinned-Dependencies → 10/10 |
| Branch | `feat/phase-11-pin-dependencies` → merged PR #41 @ `18ad5dd`        |
| Gate   | `make check` + `make smoke` (health); green CI                      |

Deliverables:

- [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) — 13 hook repos `rev:` → full commit SHAs; exact npm/pip pins for additional_dependencies
- [`.github/workflows/pre-commit.yaml`](../../.github/workflows/pre-commit.yaml) — `pip install pre-commit==4.6.0`
- [`.secrets.baseline`](../../.secrets.baseline) — 13 HexHighEntropy false positives for hook SHAs
- [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — Phase 11 pin table and expected impact
- [`PLAN.md`](PLAN.md) — Phase 11 archived; Phase 12 next

### Phase 11 close checklist

**Status:** Done (2026-06-30). Merged PR #41 @ `18ad5dd`.

1. Pin 13 pre-commit hook repos to commit SHAs (same tag versions as before)
2. Pin floating npm/pip deps: `jshint@2.13.6`, `prettier@3.1.0`, `pytest==8.3.5`, `pre-commit==4.6.0`
3. Update `.secrets.baseline` for hook SHA false positives
4. [`docs/spikes/scorecard-gaps.md`](../spikes/scorecard-gaps.md) — Phase 11 section; Pinned-Dependencies target 10/10
5. [`PLAN.md`](PLAN.md) — branch header, todos, status table, verification artifact updated
6. [`PLAN_COMPLETED.md`](PLAN_COMPLETED.md) — Phase 11 summary archived (this section)
7. `make check` + `make smoke` green; green CI on PR

Handover SHA: record in local `.cursor/rules/handover-notes.mdc` (gitignored) after merge.

---

## Post–Phase 11 CI — Scorecard pre-commit hook (PR #42)

| Field  | Value                                                           |
| ------ | --------------------------------------------------------------- |
| Goal   | Add Scorecard pre-commit hook; clear npm vulnerability findings |
| Branch | `feat/scorecard-pre-commit-hook` → merged PR #42 @ `792a1a1`    |
| Gate   | `make check` + green CI                                         |

Deliverables:

- [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) — local OpenSSF Scorecard hook
- npm vulnerability cleanup from hook findings

### PR #42 close checklist

**Status:** Done (2026-06-30). Merged PR #42 @ `792a1a1`.

1. Scorecard pre-commit hook added and documented
2. npm audit findings addressed
3. `make check` green; green CI on PR

---

## Upstream sync (PR #43)

| Field  | Value                                                                   |
| ------ | ----------------------------------------------------------------------- |
| Goal   | Merge upstream `rh-ai-quickstart/CAIsat` features into contributor fork |
| Branch | `merge/upstream-main` → merged PR #43 @ `0e4281e`                       |
| Gate   | `make check` + green CI                                                 |

Deliverables:

- Change detection pipeline from upstream
- S4 and DSPA pipeline integrations
- Fork now tracks upstream ML/infra features; outbound PR to `rh-ai-quickstart/CAIsat` **still deferred** per PLAN decision

### PR #43 close checklist

**Status:** Done (2026-06-30). Merged PR #43 @ `0e4281e`.

1. Upstream changes merged without conflict on core paths
2. `make check` green; green CI on PR
3. PLAN decision updated: inbound sync done; outbound upstream PR deferred
