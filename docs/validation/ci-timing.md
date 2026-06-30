# CI job timing metrics

<!-- Assisted by: cursor, claude -->

Track GitHub Actions job wall times on fork `main` to decide whether Phase 3 job split (MT-CP-3) is justified.

Local `make check` always runs helm template; CI may skip helm when `chart/**` is unchanged (MT-CP-1).

**Plan reference:** Cursor plan `ci_parallelization_phases.plan.md` — MT-CP-1 (this doc), MT-CP-3 gate.

---

## How to read job duration

1. Open the workflow run on GitHub: **Actions** → **pre-commit** → select a green run on `main`.
2. **Job wall time** — duration shown on each job tile (`pre-commit`, `smoke-binary`). This is start-to-finish including queue, checkout, caches, and all steps.
3. **Step timings** — click a job → expand steps. Bottlenecks usually appear under **Run pre-commit**, **Helm template test**, **Smoke (health profile)**, or **Smoke (binary profile)**.
4. Record **UTC date**, **commit SHA** (short), and duration in **minutes:seconds** (or decimal minutes for p50/p95 math).

Use **green runs only** for baseline tables; failed runs skew p95.

---

## Baseline table template

Fill after MT-CP-1 merges and at least three consecutive green `main` runs post-merge.

| Job            | Run date (UTC) | Commit | Wall time (min) | Notes         |
| -------------- | -------------- | ------ | --------------- | ------------- |
| `pre-commit`   |                |        |                 |               |
| `smoke-binary` |                |        |                 | skipped / ran |

**Aggregates (last N green `main` runs, N ≥ 5 recommended):**

| Job            | N   | p50 (min) | p95 (min) | Last updated |
| -------------- | --- | --------- | --------- | ------------ |
| `pre-commit`   |     |           |           |              |
| `smoke-binary` |     |           |           |              |

**Post–MT-CP-1 initial row (pre-merge baseline @ `3134052`):**

| Job            | Run date (UTC) | Commit    | Wall time (min)      | Notes                                 |
| -------------- | -------------- | --------- | -------------------- | ------------------------------------- |
| `pre-commit`   | 2026-06-30     | `3134052` | _record after merge_ | Phase 0 serial lint → helm → health   |
| `smoke-binary` | 2026-06-30     | `3134052` | _record after merge_ | Optional parallel; no path filter yet |

---

## Phase 3 decision threshold (MT-CP-3)

**Proceed with job split** (`lint-helm` + `smoke-health` parallel required jobs) only if:

- `pre-commit` job **p50 or p95 > ~12 minutes** over **≥ 5 green `main` runs**, sustained (not a single outlier), **and**
- Split complexity / ruleset migration cost is acceptable.

**Skip or defer MT-CP-3** if:

- p50 ≤ ~6 minutes sustained — monolithic `pre-commit` is fast enough; prefer MT-CP-4 perf tweaks or stop.

Update this section and [`scorecard-gaps.md`](../spikes/scorecard-gaps.md) when aggregates change a gate decision.

---

## Path-filter impact (MT-CP-1)

After MT-CP-1 merges:

| Change scope                                    | `smoke-binary`                                               | Helm in `pre-commit`            |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------------------- |
| Docs / frontend only                            | Skipped (filter `smoke=false`)                               | Skipped if `chart/**` unchanged |
| `chart/**`                                      | Runs if other smoke paths also hit, or skipped if only chart | Runs                            |
| `backend/**`, smoke script, Makefile, workflows | Runs                                                         | Unchanged                       |

Phase 2 (MT-CP-2) removes smoke path filters when `smoke-binary` becomes a required check.
