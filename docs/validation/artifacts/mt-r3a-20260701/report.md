# MT-R3a operator report (2026-07-01)

<!-- Assisted by: cursor, claude -->

## Summary

| MT-ID     | Verdict           | Notes                                                                          |
| --------- | ----------------- | ------------------------------------------------------------------------------ |
| MT-DETECT | **pass**          | Detect gate green after live `KSERVE_PREFER_BINARY=false` on detection backend |
| MT-R3a    | **pass**          | Playwright 100% row + 150% vertical stack; 1 detection with box overlay        |
| MT-2      | **fail** (binary) | JSON pass / binary HTTP 500 (unchanged — upstream MLServer)                    |

## MT-R3a detail

- Enhance: ~65 s CPU (256→1024)
- Detect: HTTP 200; 1 detection; OBB overlay on Detected Objects panel
- 100% layout @ 1600×900: `flex-direction: row`; 3 panels visible
- 150% layout @ 1067×900 (1600/1.5 effective width): `flex-direction: column`; third panel visible after scroll

## Detect RCA (resolved)

Missing `KSERVE_PREFER_BINARY=false` on `caisat-detection-backend`. Live env fix applied; chart fix PR #82 codifies both backends.

## Artifacts

| File                              | Description                                        |
| --------------------------------- | -------------------------------------------------- |
| `01-100pct-detection-results.png` | 100% wide layout with 3-panel row                  |
| `02-150pct-detection-results.png` | 150% effective width vertical stack                |
| `mt-r3a-playwright-summary.json`  | Machine-readable pass/fail summary                 |
| `playwright-run.log`              | Playwright session log                             |
| `detect-response-rerun.json`      | API probe post-fix (200, 0 detections on test PNG) |

## DRL-001

**accepted** — MT-R3a pass satisfies layout acceptance criteria.
