# CI job timing metrics

<!-- Assisted by: cursor, claude -->

Track GitHub Actions job wall times on fork `main` to decide whether Phase 3 job split (MT-CP-3) is justified.

Local `make check` always runs helm template; CI runs helm on every push/PR (MT-CP-2 removed MT-CP-1 helm skip).

**Plan reference:** Cursor plan `ci_parallelization_phases.plan.md` — MT-CP-1 (metrics doc), MT-CP-2 (require `smoke-binary`), MT-CP-3 gate.

---

## How to read job duration

1. Open the workflow run on GitHub: **Actions** → **pre-commit** → select a green run on `main`.
2. **Job wall time** — duration shown on each job tile (`pre-commit`, `smoke-binary`). This is start-to-finish including queue, checkout, caches, and all steps.
3. **Step timings** — click a job → expand steps. Bottlenecks usually appear under **Run pre-commit**, **Helm template test**, **Smoke (health profile)**, or **Smoke (binary profile)**.
4. Record **UTC date**, **commit SHA** (short), and duration in **minutes:seconds** (or decimal minutes for p50/p95 math).

Use **green runs only** for baseline tables; failed runs skew p95.

---

## Baseline table (green `main` runs)

| Job            | Run date (UTC) | Commit    | Wall time (min) | Notes                                                |
| -------------- | -------------- | --------- | --------------- | ---------------------------------------------------- |
| `pre-commit`   | 2026-06-30     | `b07bc93` | 1.13            | Post–MT-CP-1 merge; helm skipped (no chart change)   |
| `smoke-binary` | 2026-06-30     | `b07bc93` | 0.68            | Ran (workflow change touched `.github/workflows/**`) |
| `pre-commit`   | 2026-06-30     | `3134052` | 1.17            | Pre–MT-CP-1; no path filters                         |
| `smoke-binary` | 2026-06-30     | `3134052` | 0.62            | Optional parallel                                    |
| `pre-commit`   | 2026-06-30     | `f933c82` | 2.43            | PR #57 GHA hardening merge                           |
| `smoke-binary` | 2026-06-30     | `f933c82` | 0.82            | First required parallel job on main                  |
| `pre-commit`   | 2026-07-01     | `6f0f7d4` | 1.05            | Green main @ run 28549776729                         |
| `smoke-binary` | 2026-07-01     | `6f0f7d4` | 0.48            | Green main @ run 28549776729                         |
| `pre-commit`   | 2026-07-01     | `f6b50cb` | 0.80            | Green main @ run 28551287950                         |
| `smoke-binary` | 2026-07-01     | `f6b50cb` | 0.48            | Green main @ run 28551287950                         |
| `pre-commit`   | 2026-07-01     | `52ee726` | 1.18            | Green main @ run 28553421674                         |
| `smoke-binary` | 2026-07-01     | `52ee726` | 0.47            | Green main @ run 28553421674                         |
| `pre-commit`   | 2026-07-02     | `4bcfb9a` | 0.98            | Green main @ run 28561555756                         |
| `smoke-binary` | 2026-07-02     | `4bcfb9a` | 0.47            | Green main @ run 28561555756                         |
| `pre-commit`   | 2026-07-02     | `032cefa` | 0.80            | Green main @ run 28591618940                         |
| `smoke-binary` | 2026-07-02     | `032cefa` | 0.60            | Green main @ run 28591618940                         |
| `pre-commit`   | 2026-07-02     | `dd90f20` | 1.17            | Green main @ run 28596639278                         |
| `smoke-binary` | 2026-07-02     | `dd90f20` | 0.68            | Green main @ run 28596639278                         |
| `pre-commit`   | 2026-07-02     | `9f66915` | 0.98            | Green main @ run 28598453587 (MT-CP-3 assess tip)    |
| `smoke-binary` | 2026-07-02     | `9f66915` | 0.60            | Green main @ run 28598453587 (MT-CP-3 assess tip)    |

**Status:** 10 green `main` runs recorded (7 post–MT-CP-4 @ `b48bb55`+). Sufficient for MT-CP-3 gate assessment.

**Aggregates (last N green `main` runs, N ≥ 5 recommended):**

| Job            | N   | p50 (min) | p95 (min) | Last updated |
| -------------- | --- | --------- | --------- | ------------ |
| `pre-commit`   | 7   | 0.98      | 1.18      | 2026-07-02   |
| `smoke-binary` | 7   | 0.48      | 0.68      | 2026-07-02   |

_Last-7 subset (2026-07-01–02 runs only; excludes 2026-06-30 baselines). Full table N=10: `pre-commit` p50 ≈ 0.98 min, p95 ≈ 1.18 min._

---

## Phase 3 decision threshold (MT-CP-3)

**Proceed with job split** (`lint-helm` + `smoke-health` parallel required jobs) only if:

- `pre-commit` job **p50 or p95 > ~12 minutes** over **≥ 5 green `main` runs**, sustained (not a single outlier), **and**
- Split complexity / ruleset migration cost is acceptable.

**Skip or defer MT-CP-3** if:

- p50 ≤ ~6 minutes sustained — monolithic `pre-commit` is fast enough; prefer MT-CP-4 perf tweaks or stop.

**Current read (2026-06-30):** p50 `pre-commit` ≈ 1.2 min — **defer MT-CP-3**.

**MT-CP-3-ASSESS refresh (2026-07-02):** Last 7 green `main` runs — `pre-commit` p50 **0.98 min**, p95 **1.18 min**; `smoke-binary` p50 **0.48 min**, p95 **0.68 min**. Both well below 12 min gate.

**MT-CP-3-SPLIT verdict:** **defer** — monolithic `pre-commit` remains fast; split + ruleset `18274842` migration not justified. Re-assess if p50 or p95 exceeds ~12 min sustained over ≥5 runs.

Update this section and [`scorecard-gaps.md`](../spikes/scorecard-gaps.md) when aggregates change a gate decision.

---

## MT-CP-4 — smoke venv cache (before merge)

**Change:** `actions/cache` on `backend/.venv-smoke` and `backend-detection/.venv-smoke` in both jobs. Key: Python 3.12 + `requirements.txt` hashes. Skips venv recreate and pip install when deps unchanged.

**Baseline (pre–MT-CP-4, green `main` @ `41d00e8`):**

| Job            | p50 (min) | Notes                                |
| -------------- | --------- | ------------------------------------ |
| `pre-commit`   | 1.02      | Run `28481387018` post–MT-CP-2 merge |
| `smoke-binary` | 0.72      | Run `28481387018` post–MT-CP-2 merge |

Prior aggregate p50 from baseline table: `pre-commit` 1.17 min, `smoke-binary` 0.68 min.

**Target:** ≥10% p50 reduction on cache-warm runs (second consecutive green `main` run after merge).

**Post-merge timings:** Record here after MT-CP-4 PR merges (cold run may match baseline; warm run shows delta).

**Post-merge (MT-CP-4 @ `b48bb55`, run `28483105946`, cache warm):**

| Job            | Wall time (min) | vs pre–MT-CP-4 p50 | Notes                 |
| -------------- | --------------- | ------------------ | --------------------- |
| `pre-commit`   | 0.87 (52s)      | −14.7% (61s→52s)   | Meets ≥10% target     |
| `smoke-binary` | 0.67 (40s)      | −7.0% (43s→40s)    | Marginal; cache helps |

Cold first run on PR #61 head (`be3da31`): `pre-commit` 1.07 min, `smoke-binary` 0.68 min — populates cache.

---

## e2e-playwright (optional stub MT-R3a)

Optional GitHub Actions job for DRL-001 layout validation against local stub APIs (no cluster).
Workflow: `.github/workflows/e2e-playwright.yml`. Triggers: `workflow_dispatch`, path-filtered `pull_request`, weekly Monday 06:00 UTC.
**Not** a required check on ruleset `18274842`.

Local gate before merge: `make e2e-stub-local` (exit 0).

### Baseline table (green runs)

| Job              | Run date (UTC) | Commit    | Wall time (min) | Notes                                                                           |
| ---------------- | -------------- | --------- | --------------- | ------------------------------------------------------------------------------- |
| `e2e-playwright` | 2026-07-10     | `6fc8b33` | 2.13            | First green stub-stack; PR #160 pull_request; run 29096428608                   |
| `e2e-playwright` | 2026-07-10     | `b58048c` | 2.05            | Post-merge `main` `workflow_dispatch`; run 29100020669; summary `verdict: pass` |

**Estimated wall time:** 5–10 min warm (Playwright browser cache hit); 12–18 min cold.

### Post-merge verification

**Done @ 2026-07-10:** `workflow_dispatch` on `main` (run `29100020669`, commit `b58048c`, 2.05 min, `verdict: pass`).

To re-run manually:

1. **Actions** → **e2e-playwright** → **Run workflow** → branch `main` → **Run workflow**.
2. Confirm green run; download artifact `e2e-playwright-<run_id>`.
3. Verify `mt-r3a-playwright-summary.json` has `"verdict": "pass"` and screenshots `01-100pct-detection-results.png`, `02-150pct-detection-results.png`.
4. Record run date (UTC), commit SHA, and wall time in the baseline table above.
5. If egress fails (Playwright CDN blocked), add the blocked host to `allowed-endpoints` in the workflow and re-dispatch.

No secrets, no ruleset change, no self-hosted runner required.

**Rollback:** disable cron schedule or restrict to `workflow_dispatch` only; job is not required for merges.

---

## Path-filter impact (MT-CP-1, removed MT-CP-2)

MT-CP-1 (merged @ `b07bc93`) added `dorny/paths-filter` skips for helm and `smoke-binary`. MT-CP-2 removes all path filters because `smoke-binary` is a required check — skipped jobs would block merges.

| Change scope        | MT-CP-1 behavior (historical) | MT-CP-2+ behavior    |
| ------------------- | ----------------------------- | -------------------- |
| Docs only           | `smoke-binary` skipped        | Both jobs always run |
| `chart/**`          | Helm runs                     | Helm always runs     |
| Backend/smoke paths | `smoke-binary` runs           | Both jobs always run |
