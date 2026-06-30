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

**Status:** 3 of 3 target post–MT-CP-1 merge runs recorded (1 post-merge @ `b07bc93` + 2 pre-merge baselines). Add more rows after MT-CP-2 merge when both jobs are required on every push.

**Aggregates (last N green `main` runs, N ≥ 5 recommended):**

| Job            | N   | p50 (min) | p95 (min) | Last updated |
| -------------- | --- | --------- | --------- | ------------ |
| `pre-commit`   | 3   | 1.17      | 2.43      | 2026-06-30   |
| `smoke-binary` | 3   | 0.68      | 0.82      | 2026-06-30   |

---

## Phase 3 decision threshold (MT-CP-3)

**Proceed with job split** (`lint-helm` + `smoke-health` parallel required jobs) only if:

- `pre-commit` job **p50 or p95 > ~12 minutes** over **≥ 5 green `main` runs**, sustained (not a single outlier), **and**
- Split complexity / ruleset migration cost is acceptable.

**Skip or defer MT-CP-3** if:

- p50 ≤ ~6 minutes sustained — monolithic `pre-commit` is fast enough; prefer MT-CP-4 perf tweaks or stop.

**Current read (2026-06-30):** p50 `pre-commit` ≈ 1.2 min — **defer MT-CP-3**.

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

---

## Path-filter impact (MT-CP-1, removed MT-CP-2)

MT-CP-1 (merged @ `b07bc93`) added `dorny/paths-filter` skips for helm and `smoke-binary`. MT-CP-2 removes all path filters because `smoke-binary` is a required check — skipped jobs would block merges.

| Change scope        | MT-CP-1 behavior (historical) | MT-CP-2+ behavior    |
| ------------------- | ----------------------------- | -------------------- |
| Docs only           | `smoke-binary` skipped        | Both jobs always run |
| `chart/**`          | Helm runs                     | Helm always runs     |
| Backend/smoke paths | `smoke-binary` runs           | Both jobs always run |
