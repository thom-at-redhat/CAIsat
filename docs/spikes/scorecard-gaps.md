# OpenSSF Scorecard Gaps

<!-- Assisted by: cursor, claude -->

Actionable Scorecard checks, current scores, targets, and which PLAN phases address each gap.

**Baseline:** Scorecard **6.0** @ fork `main` `6b0a209` (2026-06-30, Phase 8 close).
Post–PR #57 re-run: **operator** — `workflow_dispatch` on Scorecard workflow (PAT lacks dispatch scope 2026-06-30); weekly schedule or push to `main` refreshes SARIF.

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

| Check               | Score | Actionable? | Target / waiver                                                  | Addressed by                              |
| ------------------- | ----- | ----------- | ---------------------------------------------------------------- | ----------------------------------------- |
| SAST                | 10    | —           | Maintain                                                         | Phase 6 (done)                            |
| Vulnerabilities     | 0     | Yes         | Triage/merge Dependabot PRs; reduce OSV count                    | **Phase 9**                               |
| Branch-Protection   | 4→TBD | Yes         | Ruleset `protect-main`: CodeQL required, block force push        | **Phase 10** (done)                       |
| Pinned-Dependencies | 10    | —           | Pin remaining workflow/pre-commit refs → 10/10                   | **Phase 11** (done)                       |
| Packaging           | -1    | Maybe       | Helm publish workflow + GitHub Release                           | **Phase 26** (complete; Batch 3b API lag) |
| Signed-Releases     | -1    | Maybe       | Tagged release + build provenance                                | **Phase 27** (complete; Batch 3b API lag) |
| Code-Review         | 0     | Partial     | Require 1 approving review on ruleset; solo fork may stay 0      | **Phase 10** (waiver)                     |
| Maintained          | 0     | No          | Repo &lt;90 days — **waiver** (see below)                        | **Phase 8** (doc)                         |
| Contributors        | 3     | No          | Solo fork — **waiver** (see below)                               | **Phase 8** (doc)                         |
| Fuzzing             | 10    | —           | ClusterFuzzLite CI @ `31606a8` (PRs #115–116); Batch 3a **pass** | **Phase 31** (complete)                   |
| CII-Best-Practices  | 2     | Defer       | OpenSSF best practices badge effort                              | **Phase 29** (MT-SC29)                    |

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

| Phase  | Goal                        | Merge gate                                                         |
| ------ | --------------------------- | ------------------------------------------------------------------ |
| **8**  | OpenSSF score baseline      | `make check` + doc only; record 6.0 in PLAN                        |
| **9**  | Dependency hygiene          | `make check` + `make smoke`; green CI; optional `smoke-binary` job |
| **10** | Branch protection hardening | `make check`; document ruleset changes                             |
| **11** | Pin remaining dependencies  | `make check`; Pinned-Dependencies → 10/10                          |

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

**Last verified:** fork `main` @ `d15eafe` (2026-07-01, MT-W14 post-merge). Scorecard **6.9** @ API + CI run `28524709942` (PR #76 merge); `scripts/scorecard-local.sh` skipped (`GITHUB_AUTH_TOKEN` unset).

---

## MT-W14b — OSV triage (Wave 5 follow-up)

**MT-ID:** MT-W14b | **Date:** 2026-07-01 | **Tip SHA:** `2dd097b` (pre-fix); merge SHA TBD

**Scope:** Triage **22 OSV/GHSA IDs** from Scorecard Vulnerabilities check @ `2dd097b` (was 21 @ `a98e062`; +1 pytest GHSA added since MT-W14).

**Sources:** `api.scorecard.dev` + CI run `28523536217` @ `2dd097b`; GitHub Advisory API per ID; `pip-audit` per-backend (0 findings after floor bump); `npm audit` (0).

**Root cause:** Scorecard OSV scanner evaluates **declared dependency ranges**, not lockfile-resolved versions only.

- `backend/requirements.txt`: `aiohttp>=3.13.3` allowed versions below 3.14.1.
- `requirements-dev.txt` + pre-commit mypy: `pytest==8.3.5` (&lt; 9.0.3).
- `backend-detection/requirements.txt`: already `aiohttp==3.14.1`.
- Frontend: `npm audit` clean (Phase 9 overrides still effective).

**Verdict summary:**

| Disposition           | Count  | Notes                                                   |
| --------------------- | ------ | ------------------------------------------------------- |
| **Fixed** (this PR)   | **22** | Backend aiohttp floor + pytest bump                     |
| **Already satisfied** | 0      | Detection aiohttp 3.14.1 counted under fixed root cause |
| **Waived**            | 0      | —                                                       |
| **Deferred upstream** | 0      | —                                                       |
| **False positive**    | 0      | —                                                       |

**Repo changes:**

| Path                       | Change                                            |
| -------------------------- | ------------------------------------------------- |
| `backend/requirements.txt` | `aiohttp>=3.13.3` → `aiohttp>=3.14.1`             |
| `requirements-dev.txt`     | `pytest==8.3.5` → `pytest==9.0.3`                 |
| `.pre-commit-config.yaml`  | mypy `additional_dependencies` pytest pin → 9.0.3 |

**Expected Scorecard impact:** Vulnerabilities check should rise from **0** when OSV count clears (re-run via push or `workflow_dispatch`; API may lag).

Aggregate **7+** not guaranteed — Maintained, Code-Review, Fuzzing, Contributors still cap score per MT-W14 verdict.

### Per-OSV triage table @ `2dd097b`

| OSV / GHSA                           | Package | Severity | Patched in | Manifest                                | Disposition | Rationale                  |
| ------------------------------------ | ------- | -------- | ---------- | --------------------------------------- | ----------- | -------------------------- |
| GHSA-2fqr-mr3j-6wp8                  | aiohttp | low      | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Floor raised to `>=3.14.1` |
| GHSA-2vrm-gr82-f7m5                  | aiohttp | low      | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-3wq7-rqq7-wx6j                  | aiohttp | low      | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-4fvr-rgm6-gqmc                  | aiohttp | medium   | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-4m7w-qmgq-4wj5 / PYSEC-2026-237 | aiohttp | low      | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-63hf-3vf5-4wqf                  | aiohttp | low      | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-63hw-fmq6-xxg2                  | aiohttp | medium   | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-966j-vmvw-g2g9                  | aiohttp | low      | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-9x8q-7h8h-wcw9                  | aiohttp | low      | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-c427-h43c-vf67                  | aiohttp | medium   | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-g3cq-j2xw-wf74                  | aiohttp | medium   | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-hcc4-c3v8-rx92                  | aiohttp | low      | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-hg6j-4rv6-33pg                  | aiohttp | medium   | 3.14.0     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-hpj7-wq8m-9hgp                  | aiohttp | medium   | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-jg22-mg44-37j8                  | aiohttp | medium   | 3.14.0     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-m5qp-6w8w-w647                  | aiohttp | medium   | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-m6qw-4cw2-hm4m                  | aiohttp | low      | 3.14.0     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-mwh4-6h8g-pg8w                  | aiohttp | low      | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-p998-jp59-783m                  | aiohttp | medium   | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-w2fm-2cpv-w7v5                  | aiohttp | medium   | 3.13.4     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-xcgm-r5h9-7989                  | aiohttp | medium   | 3.14.1     | backend `>=3.13.3`                      | **fixed**   | Same                       |
| GHSA-6w46-j5rx-g56g                  | pytest  | medium   | 9.0.3      | `requirements-dev.txt`, pre-commit mypy | **fixed**   | Bumped to `pytest==9.0.3`  |

**Note:** All 21 aiohttp IDs share one fix (minimum version floor). Detection backend already had `aiohttp==3.14.1`; Scorecard flagged the enhancement backend loose floor.

### Fixable follow-ups (not in MT-W14 scope)

| Gap                      | Suggested action                                   | Est. impact                   | Status          |
| ------------------------ | -------------------------------------------------- | ----------------------------- | --------------- |
| Pinned-Dependencies 8→10 | Hash-pin pre-commit pip install in workflow        | +0 aggregate (one check only) | MT-W14a pending |
| Vulnerabilities 0        | Triage OSV IDs; tighten declared ranges            | May raise Vulnerabilities     | MT-W14b done    |
| Branch-Protection 4→7+   | Requires approvers + second reviewer or bypass     | Blocked on solo fork          | waived          |
| Maintained 0             | Wait until fork &gt;90 days with sustained commits | Time-based                    | waived          |
| Contributors 3           | Upstream merge or additional collaborators         | Org diversity required        | waived          |

## Phase 24 — CI egress hardening

**Audit mode merged:** PR #57 @ `f933c82` (2026-06-30).

**Block mode merged:** MT-CP-5 (PR pending) @ fork `main` tip after PR #61 (`b48bb55`).

**Scope:** `step-security/harden-runner` on all workflow jobs (pre-commit, smoke-binary, CodeQL matrix, Scorecard).

**Pinned:** `step-security/harden-runner@f808768d1510423e83855289c910610ca9b43176` (# v2.17.0).

### Audit mode (2026-06-30 — PR #57)

`egress-policy: audit` — telemetry to StepSecurity; no outbound blocking.

### Block mode (MT-CP-5 / MT-6d)

**Sources:** StepSecurity audit logs from green `main` runs @ `b48bb55` and `41d00e8` (runs `28483105946`, `28483105949`, `28481387004`).

**Rollback:** Revert workflows to `egress-policy: audit` (remove `allowed-endpoints`) in one PR.

**`pre-commit` (port 443):**

- `api.osv.dev`, `files.pythonhosted.org`, `get.helm.sh`, `ghcr.io`, `github.com`, `pypi.org`
- `oss-fuzz-build-logs.storage.googleapis.com`, `pkg-containers.githubusercontent.com`
- `results-receiver.actions.githubusercontent.com`, `*.blob.core.windows.net`, `*.githubapp.com`

**`smoke-binary`:** `files.pythonhosted.org`, `github.com`, `pypi.org`, `results-receiver.actions.githubusercontent.com`, `*.blob.core.windows.net`, `*.githubapp.com`

**CodeQL (`Analyze`):** `api.github.com`, `github.com`, `results-receiver.actions.githubusercontent.com`, `uploads.github.com`, `*.blob.core.windows.net`, `*.githubapp.com`

**Scorecard analysis (port 443):**

- `api.deps.dev`, `api.github.com`, `api.osv.dev`, `api.scorecard.dev`, `codeload.github.com`, `github.com`
- `fulcio.sigstore.dev`, `rekor.sigstore.dev`, `tuf-repo-cdn.sigstore.dev`, `www.bestpractices.dev`
- `oss-fuzz-build-logs.storage.googleapis.com`, `results-receiver.actions.githubusercontent.com`
- `*.actions.githubusercontent.com`, `*.blob.core.windows.net`, `*.githubapp.com`

StepSecurity agent endpoints (`agent.api.stepsecurity.io`, `prod.app-api.stepsecurity.io`) are auto-allowed by harden-runner and omitted from job lists.

---

## MT-CP-2 — Require `smoke-binary` (branch protection)

**Ruleset:** `protect-main` (ID `18274842`) on contributor fork.

### Before (2026-06-30, post Phase 10)

```json
{
  "required_status_checks": ["pre-commit", "Scorecard analysis", "CodeQL"]
}
```

### After (2026-06-30, MT-CP-2)

```json
{
  "required_status_checks": ["pre-commit", "smoke-binary", "Scorecard analysis", "CodeQL"]
}
```

**Rollback:** Restore pre-edit snapshot `/tmp/ruleset-18274842-pre-mt-cp-2.json` via rulesets API PUT (operator). Revert workflow PR if required check blocks merges.

### Expected Branch-Protection impact

- Adds `smoke-binary` to required contexts alongside `pre-commit`, Scorecard analysis, and CodeQL.
- Every PR/push must pass both parallel CI jobs; MT-CP-2 removes MT-CP-1 path filters so the job always runs (required checks cannot be skipped).
- Scorecard Branch-Protection score may improve when binary smoke is enforced; re-run Scorecard on `main` after ruleset update (may lag via `api.scorecard.dev`).

**Dependabot (MT-5a):** Zero open Dependabot PRs on fork @ 2026-06-30; re-check via GitHub Dependabot alerts UI (PAT lacks alerts API).

---

## Wave 5 — Scorecard 6.0 investigation

**MT-ID:** MT-W14 (W5-P1c) | **Date:** 2026-07-01 | **Tip SHA:** `a98e062` (PR #71 merged)

**Question:** Why is Scorecard still **6.0** after Phases 8–11 (pinned deps, SAST, branch protection, `smoke-binary`)?

**Verdict:** **6.0 is expected** on this solo fork. Waived checks (Maintained, Code-Review, Fuzzing, Contributors) plus Vulnerabilities 0 (21 OSV) and Branch-Protection 4 cap the score.

**No further repo work is required** unless the operator chooses fixable gaps below. Reaching **7+** needs upstream/collaborators, time (Maintained), and OSV triage.

### Evidence sources

| Source                 | Result                         | Notes                                                                                              |
| ---------------------- | ------------------------------ | -------------------------------------------------------------------------------------------------- |
| `api.scorecard.dev`    | **6.0** @ 2026-07-01T13:38:23Z | Authoritative for README badge                                                                     |
| README badge URL       | **6.0**                        | Same API endpoint — **consistent**, no lag                                                         |
| CI run `28521726670`   | **6.0** @ commit `a98e062`     | Push trigger (PR #71); Scorecard v5.3.0 in SARIF                                                   |
| Ruleset `18274842`     | 4 required contexts            | `pre-commit`, `smoke-binary`, `Scorecard analysis`, `CodeQL`; `required_approving_review_count: 0` |
| Dependabot alerts API  | **403**                        | PAT lacks `dependabot` scope — use GitHub UI                                                       |
| `make scorecard-local` | Skipped                        | `GITHUB_AUTH_TOKEN` unset in agent session                                                         |

### Per-check triage @ `a98e062`

| Check                  | Score | Actionable? | Fixable? | Blocks 7+? | Notes                                                                 |
| ---------------------- | ----- | ----------- | -------- | ---------- | --------------------------------------------------------------------- |
| Maintained             | 0     | No          | No       | **Yes**    | Fork &lt;90 days — **waiver** (Phase 8)                               |
| Code-Review            | 0     | Partial     | No       | **Yes**    | 0 approvers — **solo fork waiver** (Phase 10)                         |
| Fuzzing                | 0     | Defer       | No       | **Yes**    | No OSS-Fuzz — out of scope                                            |
| Vulnerabilities        | 0     | Yes         | Partial  | **Yes**    | 22 OSV @ `2dd097b`; **MT-W14b fixed** — re-run pending                |
| Contributors           | 3     | No          | No       | **Yes**    | Single org — **waiver** (Phase 8)                                     |
| Branch-Protection      | 4     | Yes         | Partial  | **Yes**    | 4 CI contexts OK; approvers blocked solo fork                         |
| CII-Best-Practices     | 2     | Defer       | Partial  | No         | InProgress badge                                                      |
| Pinned-Dependencies    | 10    | —           | —        | No         | **Fixed** MT-W14a — hash-locked `.github/requirements-pre-commit.txt` |
| Packaging              | -1    | Defer       | Partial  | No         | Publish workflow merged PR #104; operator tag Batch 2 for Scorecard   |
| Signed-Releases        | -1    | Defer       | Partial  | No         | Provenance merged PR #105; first release via `v0.1.0` tag Batch 2     |
| Dependency-Update-Tool | 10    | —           | —        | No         | Dependabot configured                                                 |
| Dangerous-Workflow     | 10    | —           | —        | No         | Clean                                                                 |
| Security-Policy        | 10    | —           | —        | No         | `.github/SECURITY.md`                                                 |
| Token-Permissions      | 10    | —           | —        | No         | Least privilege                                                       |
| Binary-Artifacts       | 10    | —           | —        | No         | Clean                                                                 |
| License                | 10    | —           | —        | No         | Apache-2.0                                                            |
| SAST                   | 10    | —           | —        | No         | CodeQL on all commits                                                 |
| CI-Tests               | 10    | —           | —        | No         | 27/27 merged PRs CI-checked                                           |

**Checks scoring ≥7:** 11 checks at 10/10 (Pinned-Dependencies restored MT-W14a).

### Hypothesis triage

| Hypothesis                     | Result                                                                                                            |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Waived checks drag aggregate   | **Confirmed** — Maintained 0, Code-Review 0, Fuzzing 0, Contributors 3 documented in Phase 8                      |
| API lag behind `main`          | **Rejected** — API, badge, and CI SARIF all **6.0** @ `a98e062` same day                                          |
| Branch-Protection still low    | **Confirmed** — 4/10; ruleset has 4 required contexts but Scorecard penalizes missing approvers/CODEOWNERS        |
| Vulnerabilities / OSV          | **Confirmed** — 21 findings (Scorecard OSV scanner); contradicts prior “npm audit 0” note for frontend-only scope |
| Pinned-Dependencies regression | **Fixed** MT-W14a — was 8/10 (unpinned `pipCommand`); hash-locked requirements + `--require-hashes` in workflow   |

### Ruleset vs Scorecard Branch-Protection gap

Ruleset `protect-main` (ID `18274842`) @ 2026-07-01:

```json
{
  "required_status_checks": ["pre-commit", "smoke-binary", "Scorecard analysis", "CodeQL"],
  "strict_required_status_checks_policy": true,
  "required_approving_review_count": 0,
  "dismiss_stale_reviews_on_push": true
}
```

Scorecard Branch-Protection (4/10) still warns:

- Branch `main` does not require approvers
- CODEOWNERS review not required
- Last push approval disabled
- Admin enforcement message present but approver count is zero

**Impact:** MT-CP-2 added `smoke-binary` as required; did not raise Branch-Protection score. Approver requirement is intentionally waived for solo self-merge.

### Fixable follow-ups (not in MT-W14 scope)

| Gap                      | Suggested action                                                                 | Est. impact                          | Status   |
| ------------------------ | -------------------------------------------------------------------------------- | ------------------------------------ | -------- |
| Pinned-Dependencies 8→10 | **Done** MT-W14a — `.github/requirements-pre-commit.txt` + `--require-hashes`    | +0 aggregate (one check only)        | done     |
| Vulnerabilities 0        | Triage 22 OSV IDs; tighten declared ranges (MT-W14b)                             | Uncertain — may raise if count drops | **done** |
| Branch-Protection 4→7+   | Requires `required_approving_review_count: 1` + second reviewer or bypass policy | Blocked on solo fork                 | waived   |
| Maintained 0             | Wait until fork &gt;90 days with sustained commits                               | Time-based                           | waived   |
| Contributors 3           | Upstream merge or additional collaborators                                       | Org diversity required               | waived   |

### Badge vs API consistency

README badge: `https://api.scorecard.dev/projects/github.com/thom-at-redhat/CAIsat/badge` — same score (**6.9** @ 2026-07-01) and scan date as REST API query. No stale-badge issue.

---

## MT-W14 post-merge verification (PR #75 + #76)

**MT-ID:** MT-W14a / MT-W14b follow-up | **Date:** 2026-07-01 | **Tip SHA:** `d15eafe`

**Pre-fix baseline** (Wave 5 investigation @ `a98e062`, pre MT-W14a/b merge): aggregate **6.0**; Pinned-Dependencies **8**; Vulnerabilities **0** (22 OSV IDs).

**Post-merge** (@ `d15eafe`, after #75 hash-pinned pre-commit pip + #76 OSV triage):

| Metric              | Pre-fix | Post-merge | Delta    |
| ------------------- | ------- | ---------- | -------- |
| Aggregate           | 6.0     | **6.9**    | **+0.9** |
| Pinned-Dependencies | 8       | **10**     | **+2**   |
| Vulnerabilities     | 0       | **10**     | **+10**  |

**Evidence:**

| Source                       | Result                         | Notes                                             |
| ---------------------------- | ------------------------------ | ------------------------------------------------- |
| `api.scorecard.dev`          | **6.9** @ 2026-07-01T14:25:46Z | Commit `d15eafeb77ff39fd52bdde83fe244af2678011dc` |
| CI run `28524709942`         | **success** @ `d15eafe`        | Push trigger (#76 squash merge); SARIF uploaded   |
| `scripts/scorecard-local.sh` | Skipped                        | `GITHUB_AUTH_TOKEN` unset in agent session        |
| README badge                 | **6.9** (expected)             | Same API endpoint as REST query                   |

**Checks still capping 7+:** Maintained **0**, Code-Review **0**, Fuzzing **0**, Contributors **3**, Branch-Protection **4** — unchanged solo-fork waivers (MT-W14).

**Verdict:** MT-W14a/b goals met — Pinned-Dependencies **10/10**, Vulnerabilities **10/10**, aggregate **+0.9** vs baseline. Informational (not R3a-gated).

---

## MT-SCORECARD-ASSESS — Wave 10 refresh

**MT-ID:** MT-SCORECARD-ASSESS | **Date:** 2026-07-02 | **Tip SHA:** `1294cc0` (closed)

**Question:** Can aggregate Scorecard reach **7+** on current fork tip after MT-W14a/b fixes?

**Sources:** `api.scorecard.dev` @ 2026-07-02T14:37:55Z; zero open Dependabot PRs (`gh pr list --author app/dependabot`).

### Current score @ `1294cc0` (closed)

| Metric              | Score   | vs MT-W14 post-merge         |
| ------------------- | ------- | ---------------------------- |
| **Aggregate**       | **6.9** | unchanged                    |
| Pinned-Dependencies | 10      | unchanged                    |
| Vulnerabilities     | 10      | unchanged (0 OSV)            |
| Branch-Protection   | 4       | unchanged                    |
| Maintained          | 0       | unchanged (fork &lt;90 days) |
| Code-Review         | 0       | unchanged (0 approvers)      |
| Fuzzing             | 0       | unchanged                    |
| Contributors        | 3       | unchanged                    |

### Fixable vs waived gaps

| Check               | Score | Fixable? | Disposition                              |
| ------------------- | ----- | -------- | ---------------------------------------- |
| Vulnerabilities     | 10    | —        | **done** (MT-W14b)                       |
| Pinned-Dependencies | 10    | —        | **done** (MT-W14a)                       |
| Branch-Protection   | 4     | Partial  | **waived** — approvers blocked solo fork |
| Maintained          | 0     | No       | **waived** — time-based (&lt;90 days)    |
| Code-Review         | 0     | No       | **waived** — solo fork                   |
| Contributors        | 3     | No       | **waived** — single org                  |
| Fuzzing             | 0     | Defer    | **out of scope** (OSS-Fuzz)              |
| Packaging           | -1    | Yes      | **Phase 26** (MT-SC26-PACKAGING)         |
| Signed-Releases     | -1    | Yes      | **Phase 27** (MT-SC27-SIGNED-RELEASES)   |
| CII-Best-Practices  | 2     | Partial  | **Phase 29** (MT-SC29-CII-BADGE)         |

**Verdict:** **7+ not reachable** without upstream/collaborators, fork maturity (Phase 30), and per-check Phases 26–29 hygiene. Fixable dependency gaps are closed; **MT-SCORECARD-ASSESS closed** @ `1294cc0`.

### MT-SCORECARD-FIX

**Scope:** Merge safe Dependabot/OSV patches if trivial open PRs exist.

**Result @ 2026-07-02:** Zero open Dependabot PRs on fork. No trivial patches to merge.

**Disposition:** **defer** — re-check after new Dependabot alerts; no repo changes required for OSV at tip.

---

## Phase 26 — Packaging (MT-SC26-PACKAGING)

**Status:** **complete** @ `31606a8` | **MT-ID:** MT-SC26-PACKAGING | **Branch:** `feat/sc-packaging` (merged PR #104) | **Target:** Packaging **-1 → ≥0**

| Item     | Detail                                                                                                                                                                           |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Workflow | [`.github/workflows/publish-chart.yml`](../../.github/workflows/publish-chart.yml) — `workflow_dispatch` + `v*` tag push; `helm package chart/`; attach `.tgz` to GitHub Release |
| Docs     | [`chart/README.md`](../../chart/README.md) chart releases section                                                                                                                |
| Operator | Push first `v*` tag post-merge for Scorecard Packaging refresh                                                                                                                   |

**Score gate:** Packaging ≥0 @ `api.scorecard.dev` within ~7d of first tagged release, or SARIF Packaging check pass. Per-check hygiene only — aggregate **7+** not expected from Phase 26 alone.

---

## Phase 27 — Signed releases (MT-SC27-SIGNED-RELEASES)

**Status:** **complete** @ `31606a8` | **MT-ID:** MT-SC27-SIGNED-RELEASES | **Branch:** `feat/sc-signed-releases` (merged PR #105) | **Target:** Signed-Releases **-1 → ≥0**

| Item        | Detail                                                                                                                 |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| Provenance  | `actions/attest-build-provenance` on packaged `.tgz` in [publish-chart.yml](../../.github/workflows/publish-chart.yml) |
| Permissions | Job `id-token: write`, `contents: write`, `attestations: write`                                                        |
| Operator    | **Required:** push a `v*` tag to trigger release + attestation (fork had **0** releases @ 2026-07-02)                  |

**Score gate:** Batch 3b — Packaging/Signed-Releases still **-1** @ `api.scorecard.dev` (2026-07-04, same-day tag).

**Waiver:** GitHub Release `v0.1.0` with chart asset `caisat-0.1.0.tgz` + build provenance attestation
(`sha256:bee33e59…`; publish-chart workflow run 28714006058). Re-check within 7d.

---

## Batch 3a/3b — Score gate refresh @ `31606a8` (2026-07-04)

**Source:** `api.scorecard.dev` @ 2026-07-04 (post-#116 merge + `v0.1.0` tag same day).

| Check              | Before (Wave 10) | After @ `31606a8` | Batch | Verdict                                      |
| ------------------ | ---------------- | ----------------- | ----- | -------------------------------------------- |
| **Aggregate**      | **6.9**          | **7.4**           | 3a    | **pass** — Fuzzing lift                      |
| Fuzzing            | 0                | **10**            | 3a    | **pass**                                     |
| Branch-Protection  | 4                | 4                 | 3a    | **pass** (documented solo-fork cap)          |
| CII-Best-Practices | 2                | 2                 | 3a    | **pass** (InProgress badge; no regression)   |
| Packaging          | -1               | -1                | 3b    | **waiver** — release exists; API lag ≤7d     |
| Signed-Releases    | -1               | -1                | 3b    | **waiver** — attestation exists; API lag ≤7d |
| Maintained         | 0                | 0                 | —     | Phase 30 @ **2026-09-27**                    |

---

## Phase 28 — Branch protection (MT-SC28-BRANCH-PROT)

**Status:** **complete** @ `31606a8` | **MT-ID:** MT-SC28-BRANCH-PROT | **Branch:** `feat/sc-branch-prot` (merged PR #106) | **Target:** Document Branch-Protection delta (not aggregate **7+**)

| Item               | Detail                                                                                                                                         |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| CODEOWNERS         | Rewritten to fork owner (see [`.github/CODEOWNERS`](../../.github/CODEOWNERS)); replaces upstream team entry                                   |
| Ruleset `18274842` | **No PUT** on solo fork — `required_approving_review_count: 1` would block self-merge without raising Scorecard (see MT-CP-2 / L482 precedent) |
| Second reviewer    | If collaborator added later: snapshot ruleset → `docs/validation/artifacts/ruleset-18274842-pre-sc28.json` before PUT                          |

**Score gate:** Record API Branch-Protection score after merge; success = documented delta, not ≥6.

---

## Phase 29 — CII Best Practices (MT-SC29-CII-BADGE)

**Status:** **complete** @ `31606a8` | **MT-ID:** MT-SC29-CII-BADGE | **Branch:** `feat/sc-cii-badge` (merged PR #107) | **Target:** CII-Best-Practices **2 → higher**

| Item                                                           | Status         | Notes                                                                    |
| -------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------ |
| [bestpractices.dev](https://www.bestpractices.dev/) enrollment | **InProgress** | README links self-certification; operator completes project registration |
| SECURITY.md                                                    | **done**       | [`.github/SECURITY.md`](../../.github/SECURITY.md)                       |
| License                                                        | **done**       | Apache-2.0                                                               |
| Public CI                                                      | **done**       | pre-commit + smoke-binary + CodeQL + Scorecard workflows                 |
| README consumer docs                                           | **done**       | Deploy + validation sections                                             |

**Score gate:** CII check increase @ `api.scorecard.dev` after badge progress, or documented remaining gaps. Does not alone unlock aggregate **7+**.

---

## Phase 30 — Maintained re-check (MT-SC30-MAINTAINED)

**Status:** **deferred** (time-gated) | **Earliest gate:** **2026-09-27** (fork created `2026-06-29T15:20:04Z`)

**Operator:** Re-query `api.scorecard.dev` after gate date; update this file and [`PLAN.md`](../project/PLAN.md).

**Target:** Maintained **0 → 10** when fork age exceeds 90 days with sustained commits.

---

## Phase 31 — Fuzzing (MT-SC31-FUZZING)

**Status:** **complete** @ `31606a8` — local Atheris spike, hardening, and ClusterFuzzLite CI merged.

| MT-ID           | Item                                                             | Status / PR                                                                        |
| --------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| MT-SC31-FUZZING | Local Atheris harness (`make fuzz-kserve-binary`)                | **done** — PR #108 @ `750f028`; see [`fuzzing-harnesses.md`](fuzzing-harnesses.md) |
| MT-SC31-HARDEN  | `decode_kserve_binary` header validation                         | **done** — PR #114 @ `d5470d4`                                                     |
| MT-SC31-CFL     | `.github/workflows/clusterfuzzlite.yml`                          | **done** — PR #115 @ `a747f53`; PR #116 atheris pin @ `31606a8`; CFL CI green      |
| MT-SC31-CFL     | `.clusterfuzzlite/` (project.yaml, Dockerfile, build.sh, fuzzer) | **done** @ `31606a8`                                                               |

**CI posture:** `step-security/harden-runner` with `egress-policy: audit` (not block) until ClusterFuzzLite egress is catalogued (Batch 4 optional).

**Score gate:** Batch 3a **pass** — Fuzzing **10** @ `api.scorecard.dev` @ `31606a8` (2026-07-04); CFL CI green evidence no longer needed.
