# OpenSSF Scorecard Gaps

<!-- Assisted by: cursor, claude -->

Actionable Scorecard checks, current scores, targets, and which PLAN phases address each gap.

**Baseline:** Scorecard **6.0** @ fork `main` `6b0a209` (2026-06-30, Phase 8 close). SAST **10/10** after Phase 6 CodeQL. Prior PLAN cited **5.2** — stale.

See [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) and [`docs/project/PLAN.md`](../project/PLAN.md) Phases 8–11.

## Local and pre-commit

Full-repo OpenSSF Scorecard runs locally via pre-commit on **every commit** (read-only; does not publish to bestpractices.dev or api.scorecard.dev).

| Command                     | Purpose                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `git commit`                | [`scorecard-pre-commit.sh`](../../scripts/scorecard-pre-commit.sh): `--local` scan of git index via Podman `v5.5.0` |
| `make scorecard-local`      | Manual `--repo` scan → `scorecard-local.json` (needs `GITHUB_AUTH_TOKEN`)                                           |
| `SKIP=scorecard git commit` | Break-glass skip (use sparingly)                                                                                    |

**Setup (optional):** `export GITHUB_AUTH_TOKEN="<fine-grained PAT, contents:read>"` — enables richer local checks; hook runs without it.

**Fail gate:** commit blocked when an actionable check scores **0** (Binary-Artifacts, Dangerous-Workflow, License, Pinned-Dependencies, SAST, Security-Policy, Token-Permissions, Vulnerabilities).
Waived checks (Maintained, Contributors, CII-Best-Practices, Fuzzing, Packaging, Signed-Releases) do not block.

**Latency:** expect ~1–3 min per commit after first container pull. CI workflow remains authoritative for published badge and SARIF.

**Vulnerabilities (2026-06-30):** cleared via `npm overrides` in [`frontend/package.json`](../../frontend/package.json) for transitive `react-scripts` toolchain deps; `npm audit` reports 0 findings.

**Note:** pre-commit fails when actionable checks score 0; `SKIP=scorecard` is break-glass only.

---

## Check inventory

| Check               | Score | Actionable? | Target / waiver                                             | Addressed by          |
| ------------------- | ----- | ----------- | ----------------------------------------------------------- | --------------------- |
| SAST                | 10    | —           | Maintain                                                    | Phase 6 (done)        |
| Vulnerabilities     | 0     | Yes         | Triage/merge Dependabot PRs; reduce OSV count               | **Phase 9**           |
| Branch-Protection   | 4→TBD | Yes         | Ruleset `protect-main`: CodeQL required, block force push   | **Phase 10** (done)   |
| Pinned-Dependencies | 10    | —           | Pin remaining workflow/pre-commit refs → 10/10              | **Phase 11** (done)   |
| Packaging           | -1    | Maybe       | Release/publish workflow (lower priority)                   | Deferred              |
| Signed-Releases     | -1    | Maybe       | GitHub releases with provenance (lower priority)            | Deferred              |
| Code-Review         | 0     | Partial     | Require 1 approving review on ruleset; solo fork may stay 0 | **Phase 10** (waiver) |
| Maintained          | 0     | No          | Repo &lt;90 days — **waiver** (see below)                   | **Phase 8** (doc)     |
| Contributors        | 3     | No          | Solo fork — **waiver** (see below)                          | **Phase 8** (doc)     |
| Fuzzing             | 0     | Defer       | OSS-Fuzz out of scope for now                               | —                     |
| CII-Best-Practices  | 2     | Defer       | OpenSSF best practices badge effort                         | —                     |

---

## Documented waivers (Phase 8)

These checks are **not** targeted for improvement on the contributor fork; rationale recorded for Scorecard gap triage.

### Maintained (score 0)

- **Reason:** Fork created from upstream recently; Scorecard “Maintained” expects sustained commit activity over ~90 days.
- **Action:** No code change. Re-evaluate after Phases 9–11 if score remains 0 on a mature fork tip.
- **Phase:** 8 baseline doc only.

### Contributors (score 3)

- **Reason:** Solo contributor fork; limited distinct contributor count is expected (see [`PLAN.md`](../project/PLAN.md) Decisions).
- **Action:** No code change. Upstream merge or additional collaborators may raise this organically.
- **Phase:** 8 baseline doc only.

---

## Phase mapping

| Phase  | Goal                        | Merge gate                                  |
| ------ | --------------------------- | ------------------------------------------- |
| **8**  | OpenSSF score baseline      | `make check` + doc only; record 6.0 in PLAN |
| **9**  | Dependency hygiene          | `make check` + `make smoke`; green CI       |
| **10** | Branch protection hardening | `make check`; document ruleset changes      |
| **11** | Pin remaining dependencies  | `make check`; Pinned-Dependencies → 10/10   |

---

## Phase 9 triage (batch 2 complete)

**Branch:** `feat/phase-9-dependency-hygiene-batch2` (open PR).

**Baseline:** Batch 1 merged @ `30c55ef` (PR #35, 2026-06-30).

### Batch 1 — merged @ `30c55ef` (PR #35)

| PR  | Package / area                      | Notes                                          |
| --- | ----------------------------------- | ---------------------------------------------- |
| #1  | `actions/checkout` 7.0.0            | All three workflows                            |
| #2  | `azure/setup-helm` 5.0.1            | pre-commit workflow                            |
| #3  | `actions/setup-python` 6.3.0        | pre-commit workflow                            |
| #23 | `codeql-action/upload-sarif` 4.36.2 | scorecard workflow                             |
| #6  | `python-dotenv` 1.2.2               | backend-detection                              |
| #8  | `python-dotenv` ≥1.2.2              | backend                                        |
| #10 | `python-multipart` ≥0.0.32          | backend                                        |
| #11 | `python-multipart` 0.0.32           | backend-detection                              |
| #15 | `axios` 1.18.1                      | frontend patch                                 |
| #22 | `aiohttp` 3.14.1 (partial)          | backend-detection security; pillow 12 deferred |

### Batch 2 — merged (all previously deferred PRs)

| PR  | Package / area            | Result / notes                                           |
| --- | ------------------------- | -------------------------------------------------------- |
| #4  | `Pillow` ≥12.2.0          | **Merged** — backend                                     |
| #5  | `fastapi` 0.138.2         | **Merged** — backend-detection                           |
| #7  | `fastapi` ≥0.138.2        | **Merged** — backend                                     |
| #9  | `numpy` 2.5.0             | **Merged** — backend-detection; smoke health pass        |
| #12 | `uvicorn` ≥0.49.0         | **Merged** — backend                                     |
| #13 | `opencv-python-headless`  | **Merged** — backend-detection 4.13.0.92                 |
| #14 | `react` 19.2.7            | **Merged** — frontend build pass (CRA + eslint fix)      |
| #16 | `react-dom` 19.2.7        | **Merged** — paired with #14                             |
| #17 | `react-leaflet` 5.0.0     | **Merged** — build pass; map UX not cluster-validated    |
| #18 | `three` 0.185.0           | **Merged** — globe build pass; cluster UX not validated  |
| #19 | `form-data` 4.0.6         | **Merged** — transitive patch via `npm update form-data` |
| #22 | `pillow` 12.2.0 (partial) | **Merged** — backend-detection remainder                 |

### Still deferred

None from the Phase 9 batch 2 scope. Re-run Dependabot alert count on `main` after batch 2 merge.

### Blockers resolved in batch 2

- **numpy 2:** requirements bump only; health smoke passes (no ONNX inference in smoke profile).
- **React 19:** CRA 5 build succeeds after removing unused imports in `App.js`.
- **react-leaflet 5:** peer deps satisfied with React 19; production build passes.

**Cluster validation gap:** React 19 / Three 0.185 / react-leaflet 5 map and globe UX remain unvalidated on cluster until Phase 13 baseline sign-off.

---

## Phase 10 — Branch protection hardening

**Ruleset:** `protect-main` (ID `18274842`) on contributor fork.

### Before (2026-06-29, Phase 4 close)

```json
{
  "rules": ["deletion", "non_fast_forward", "pull_request", "required_status_checks"],
  "required_status_checks": ["pre-commit", "Scorecard analysis"],
  "strict_required_status_checks_policy": true,
  "required_approving_review_count": 0
}
```

### After (2026-06-30, Phase 10)

```json
{
  "rules": ["deletion", "non_fast_forward", "pull_request", "required_status_checks"],
  "required_status_checks": ["pre-commit", "Scorecard analysis", "CodeQL"],
  "strict_required_status_checks_policy": true,
  "required_approving_review_count": 0
}
```

**Unchanged (already maximal for solo fork):** block branch deletion (`deletion`), block force push (`non_fast_forward`), require pull request before merge, strict status-check policy.

**CodeQL check name:** `CodeQL` — workflow rollup on PR heads (see PR #37 CI). Matrix jobs `Analyze (python)` and `Analyze (javascript-typescript)` roll up into this context.

### Code-Review waiver (solo fork)

- **Attempted:** `required_approving_review_count: 1` is feasible on ruleset API but blocks solo self-merge without bypass.
- **Decision:** Keep **0** approving reviews. Solo contributor fork; merges via PR + required checks; admin merge when checks green.
- **Scorecard impact:** Code-Review check likely remains **0**; documented waiver (same pattern as Maintained/Contributors in Phase 8).

### Expected Branch-Protection impact

- Adds CodeQL to required contexts alongside pre-commit and Scorecard analysis.
- Scorecard Branch-Protection was **4/10** @ `6b0a209`; re-run on `main` after Phase 10 merge (may lag via `api.scorecard.dev`).

---

## Phase 11 — Pin remaining dependencies

**Branch:** `feat/phase-11-pin-dependencies` (PR TBD).

**Baseline:** Pinned-Dependencies **7/10** @ `195369a` (2026-06-30); GitHub Actions already SHA-pinned from Phase 9.

### Pinned (mechanism only — no version bumps)

| Area                                      | Before                   | After                                           |
| ----------------------------------------- | ------------------------ | ----------------------------------------------- |
| `.pre-commit-config.yaml` — 13 hook repos | `rev: v*` tags           | Full commit SHAs with `# v*` comments           |
| `.pre-commit-config.yaml` — jshint        | `jshint@^2.13.6`         | `jshint@2.13.6`                                 |
| `.pre-commit-config.yaml` — prettier      | `prettier@^3.1.0`        | `prettier@3.1.0`                                |
| `.pre-commit-config.yaml` — mypy deps     | unpinned `pytest`        | `pytest==8.3.5`                                 |
| `.github/workflows/pre-commit.yaml`       | `pip install pre-commit` | `pip install pre-commit==4.6.0`                 |
| `.secrets.baseline`                       | —                        | 13 HexHighEntropy false positives for hook SHAs |

**Workflows:** All `uses:` refs already SHA-pinned (Phase 9 Dependabot batch 1); no workflow action changes in Phase 11.

### Pre-commit repo SHAs (tag → commit)

| Hook repo        | Tag            | SHA                                        |
| ---------------- | -------------- | ------------------------------------------ |
| pre-commit-hooks | v6.0.0         | `3e8a8703264a2f4a69428a0aa4dcb512790b2c8c` |
| ruff-pre-commit  | v0.15.6        | `4924b0e01e032fea073ad04a1c5cfa7e4add0afb` |
| pyupgrade        | v3.21.2        | `75992aaa40730136014f34227e0135f63fc951b4` |
| mirrors-mypy     | v1.15.0        | `f40886d54c729f533f864ed6ce584e920feb0af7` |
| mirrors-jshint   | v2.13.6        | `882622d2d13597740358203e9f2e2ae5976cd149` |
| mirrors-prettier | v4.0.0-alpha.8 | `f12edd9c7be1c20cfa42420fd0e6df71e42b51ea` |
| markdownlint-cli | v0.48.0        | `e72a3ca1632f0b11a07d171449fe447a7ff6795e` |
| codespell        | v2.4.2         | `2ccb47ff45ad361a21071a7eedda4c37e6ae8c5a` |
| yamllint         | v1.38.0        | `cba56bcde1fdd01c1deb3f945e69764c291a6530` |
| shellcheck-py    | v0.11.0.1      | `745eface02aef23e168a8afb6b5737818efbea95` |
| detect-secrets   | v1.5.0         | `01886c8a910c64595c47f186ca1ffc0b77fa5458` |
| actionlint       | v1.7.11        | `393031adb9afb225ee52ae2ccd7a5af5525e03e8` |
| hadolint         | v2.14.0        | `57e1618d78fd469a92c1e584e8c9313024656623` |

### Expected Pinned-Dependencies impact

- Scorecard target: **10/10** after merge (re-run via `api.scorecard.dev` may lag).

---

## Phase 9 triage (batch 1 archive)

_Pre-batch-2 deferral table — superseded by batch 2 results above._

### Deferred (risky major / needs dedicated testing) — historical

| PR  | Package / area            | Reason                                               |
| --- | ------------------------- | ---------------------------------------------------- |
| #4  | `Pillow` ≥12.2.0          | Major bump; backend image rebuild                    |
| #5  | `fastapi` 0.138.2         | Major API surface; test with backends                |
| #7  | `fastapi` ≥0.138.2        | Same as #5                                           |
| #9  | `numpy` 2.5.0             | numpy 1→2 breaking                                   |
| #12 | `uvicorn` ≥0.49.0         | Major serving stack                                  |
| #13 | `opencv-python-headless`  | Major 4.8→4.13; ONNX pipeline risk                   |
| #14 | `react` 19.2.7            | React 18→19                                          |
| #16 | `react-dom` 19.2.7        | Paired with #14                                      |
| #17 | `react-leaflet` 5.0.0     | Major; map UX                                        |
| #18 | `three` 0.185.0           | Major; globe rendering                               |
| #19 | npm group (frontend)      | Transitive; review after React/Three deferrals       |
| #22 | `pillow` 12.2.0 (partial) | Remainder of grouped PR; kept at 10.3.0 in detection |

---

## Verification

Re-run Scorecard on fork `main` after Phases 9–11 close. Record tip SHA and overall score in this file and [`PLAN.md`](../project/PLAN.md) verification artifact.
