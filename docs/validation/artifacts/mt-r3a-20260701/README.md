# MT-R3a Playwright artifacts (2026-07-01)

<!-- Assisted by: cursor, claude -->

**Status:** **pass** — MT-R3a complete after detect gate remediation (`KSERVE_PREFER_BINARY=false`).

**Evidence:** per-check table in [`baseline-smoke.md`](../../baseline-smoke.md) L154+; operator summary in `report.md`.

| File                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `01-100pct-detection-results.png` | 100% wide layout — 3-panel horizontal row |
| `02-150pct-detection-results.png` | 150% effective width — vertical stack     |
| `mt-r3a-playwright-summary.json`  | Playwright pass/fail metrics              |
| `playwright-run.log`              | Session log                               |
| `results.txt`                     | Machine-readable session summary          |
| `report.md`                       | Operator summary                          |
| `detect-response-rerun.json`      | Post-fix API probe (200)                  |
