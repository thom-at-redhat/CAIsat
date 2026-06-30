# OpenSSF Scorecard Gaps

<!-- Assisted by: cursor, claude -->

Actionable Scorecard checks, current scores, targets, and which PLAN phases address each gap.

**Baseline:** Scorecard **6.0** @ fork `main` `12c04945` (2026-06-30). SAST **10/10** after Phase 6 CodeQL. Prior PLAN cited **5.2** — stale.

See [`.github/workflows/scorecard-analysis.yml`](../../.github/workflows/scorecard-analysis.yml) and [`docs/project/PLAN.md`](../project/PLAN.md) Phases 8–11.

---

## Check inventory

| Check               | Score | Actionable? | Target / waiver                                             | Addressed by            |
| ------------------- | ----- | ----------- | ----------------------------------------------------------- | ----------------------- |
| SAST                | 10    | —           | Maintain                                                    | Phase 6 (done)          |
| Vulnerabilities     | 0     | Yes         | Triage/merge Dependabot PRs; reduce OSV count               | **Phase 9**             |
| Branch-Protection   | 4     | Yes         | Ruleset `protect-main`: CodeQL required, block force push   | **Phase 10**            |
| Pinned-Dependencies | 7     | Yes         | Pin remaining workflow/pre-commit refs → 10/10              | **Phase 11**            |
| Packaging           | -1    | Maybe       | Release/publish workflow (lower priority)                   | Deferred                |
| Signed-Releases     | -1    | Maybe       | GitHub releases with provenance (lower priority)            | Deferred                |
| Code-Review         | 0     | Partial     | Require 1 approving review on ruleset; solo fork may stay 0 | **Phase 10** (document) |
| Maintained          | 0     | No          | Repo &lt;90 days — document waiver                          | **Phase 8** (doc)       |
| Contributors        | 3     | No          | Solo fork — document waiver                                 | **Phase 8** (doc)       |
| Fuzzing             | 0     | Defer       | OSS-Fuzz out of scope for now                               | —                       |
| CII-Best-Practices  | 2     | Defer       | OpenSSF best practices badge effort                         | —                       |

---

## Phase mapping

| Phase  | Goal                        | Merge gate                                  |
| ------ | --------------------------- | ------------------------------------------- |
| **8**  | OpenSSF score baseline      | `make check` + doc only; record 6.0 in PLAN |
| **9**  | Dependency hygiene          | `make check` + `make smoke`; green CI       |
| **10** | Branch protection hardening | `make check`; document ruleset changes      |
| **11** | Pin remaining dependencies  | `make check`; Pinned-Dependencies → 10/10   |

---

## Verification

Re-run Scorecard on fork `main` after Phases 9–11 close. Record tip SHA and overall score in this file and [`PLAN.md`](../project/PLAN.md) verification artifact.
