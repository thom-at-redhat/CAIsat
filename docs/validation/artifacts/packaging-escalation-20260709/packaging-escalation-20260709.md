# Packaging Scorecard escalation — Track A (2026-07-09)

<!-- Assisted by: cursor, claude -->

| Field    | Value                                                                   |
| -------- | ----------------------------------------------------------------------- |
| Date     | 2026-07-09                                                              |
| Repo     | Contributor fork @ `main` post-#157 (`b625b56`)                         |
| Deadline | ≤ **2026-07-11** (waiver escalation)                                    |
| Outcome  | **blocked-on-dispatch** — release assets OK; API Packaging still **-1** |

## Pass/fail table

| Step | Action                                       | Result         | Evidence                                                                             |
| ---- | -------------------------------------------- | -------------- | ------------------------------------------------------------------------------------ |
| A1   | Query `api.scorecard.dev`                    | **recorded**   | Aggregate **7.3**; Packaging **-1**; SR **5**; Fuzzing **10** — `scorecard-api.json` |
| A2   | Verify `v0.1.1` release assets               | **pass**       | `caisat-0.1.0.tgz` + `provenance.intoto.jsonl` on tag `v0.1.1`                       |
| A3   | Packaging still **-1**                       | **fail (API)** | _packaging workflow not detected_ — publish-chart exists; API lag                    |
| A3b  | Human `workflow_dispatch` scorecard-analysis | **blocked**    | PAT HTTP 403 — missing `actions` scope                                               |
| A4   | Re-query ≥24h after dispatch                 | **pending**    | Blocked on A3b human browser dispatch                                                |
| A5   | scorecard-gaps Batch 3b update               | **done**       | Waiver extended; operator dispatch + re-check by 2026-07-11                          |

## Scorecard API excerpt (2026-07-09)

```text
GET https://api.scorecard.dev/projects/github.com/<contributor-fork>/CAIsat
aggregate: 7.3
Packaging: -1 — "packaging workflow not detected"
Signed-Releases: 5
Fuzzing: 10
repo.commit: b031b79 (API index lag vs main b625b56)
```

## Release verification

```bash
gh api "repos/${GITHUB_REPOSITORY}/releases/tags/v0.1.1" \
  --jq '{tag_name, assets: [.assets[] | {name, size}]}'
# v0.1.1: caisat-0.1.0.tgz + provenance.intoto.jsonl
```

## workflow_dispatch blocked (PAT)

```bash
gh api "repos/${GITHUB_REPOSITORY}/actions/workflows/scorecard-analysis.yml/dispatches" \
  -X POST -f ref=main
# HTTP 403 Resource not accessible by personal access token
```

**Human unblock:** GitHub → Actions → **Scorecard analysis** → **Run workflow** → branch `main`.

## Next actions (operator)

1. Browser-dispatch `scorecard-analysis.yml` on `main`.
2. Re-query API after ≥24h; target Packaging ≥0.
3. If still **-1** on 2026-07-11: extend waiver with release URL + attestation, or bump `Chart.yaml` + tag `v0.1.2` and re-dispatch `publish-chart.yml`.

## Verdict

**Waiver active** — release + provenance exist; Scorecard Packaging check not yet refreshed. Not a publish-chart regression.
