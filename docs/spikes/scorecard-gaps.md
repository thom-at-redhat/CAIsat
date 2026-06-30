# OpenSSF Scorecard Gaps

<!-- Assisted by: cursor, claude -->

Actionable Scorecard checks, current scores, targets, and which PLAN phases address each gap.

**Baseline:** Scorecard **6.0** @ fork `main` `6b0a209` (2026-06-30, Phase 8 close). SAST **10/10** after Phase 6 CodeQL. Prior PLAN cited **5.2** — stale.

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
| Maintained          | 0     | No          | Repo &lt;90 days — **waiver** (see below)                   | **Phase 8** (doc)       |
| Contributors        | 3     | No          | Solo fork — **waiver** (see below)                          | **Phase 8** (doc)       |
| Fuzzing             | 0     | Defer       | OSS-Fuzz out of scope for now                               | —                       |
| CII-Best-Practices  | 2     | Defer       | OpenSSF best practices badge effort                         | —                       |

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

## Phase 9 triage (in progress)

**Branch:** `feat/phase-9-dependency-hygiene` (open PR).

**Pre-merge vuln snapshot:** GitHub Dependabot reported **98** open alerts on `main` @ `acb9a79` (15 high, 46 moderate, 37 low); post-merge count TBD after CI.

### Merged into Phase 9 branch

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

### Deferred (risky major / needs dedicated testing)

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
