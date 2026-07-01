# MT-R3a Playwright artifacts (2026-07-01)

<!-- Assisted by: cursor, claude -->

**Status:** PNG/screenshot artifacts **not archived** — `worktrees/wave5-signoff` was removed before Batch 0 `/tmp` backup; originals lived in gitignored `mt-r3a-artifacts/`.

**Evidence on `main` @ `2f71ca7`:** per-check table and detect HTTP 500 RCA in [`baseline-smoke.md`](../../baseline-smoke.md) L159–175.

**Expected files (when re-run or recovered):**

| File                        | Description                    |
| --------------------------- | ------------------------------ |
| `results.txt`               | Playwright session log         |
| `report.md`                 | Operator summary               |
| `detection-500-failure.png` | Detect gate failure screenshot |
| `01-100pct-*.png`           | 100% layout captures           |
| `02-150pct-*.png`           | 150% layout captures           |

Re-run MT-R3a (Batch 2) after MT-DETECT pass to populate this directory.
