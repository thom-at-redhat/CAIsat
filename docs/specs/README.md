# CAIsat — Spec-Driven Development Index

<!-- Assisted by: cursor, claude -->

Spec-driven development (SDD) artifacts for testable backend and frontend surfaces. Each spec file defines requirements with stable **Spec IDs**, links to automated tests (Wave 5 MT-W12),
and maps to manual validation rows in [`baseline-smoke.md`](../validation/baseline-smoke.md).

Operational follow-up and merge gates: [`PLAN.md`](../project/PLAN.md).

## Spec format

Every feature spec includes a metadata table:

| Field          | Description                                                            |
| -------------- | ---------------------------------------------------------------------- |
| **Status**     | `draft` or `accepted` — see each spec; UI specs need operator sign-off |
| **Spec ID**    | Stable prefix (`CAP-`, `KSRV-`, `DRL-`) for traceability               |
| **Tests**      | pytest module and function names (MT-W12)                              |
| **Validation** | `baseline-smoke.md` line references for operator checks                |

Requirements use `### <SPEC-ID>-R<n>:` headings. Acceptance criteria are checkboxes for PR and operator review.

## Traceability

| Spec ID  | Spec file                                                    | Tests                          | Validation                                                                            |
| -------- | ------------------------------------------------------------ | ------------------------------ | ------------------------------------------------------------------------------------- |
| CAP-001  | [`capabilities-api.md`](capabilities-api.md)                 | `tests/test_capabilities.py`   | `baseline-smoke.md` L188, L203                                                        |
| KSRV-001 | [`kserve-v2-tensors.md`](kserve-v2-tensors.md)               | `tests/test_kserve_v2.py`      | `baseline-smoke.md` L66; spike [`binary-kserve-v2.md`](../spikes/binary-kserve-v2.md) |
| DRL-001  | [`detection-results-layout.md`](detection-results-layout.md) | _(manual / Playwright MT-R3a)_ | `baseline-smoke.md` L145–157                                                          |

## Backend module parity

`backend/` (enhancement) and `backend-detection/` (detection) each ship `capabilities.py` and `kserve_v2.py`. Encode/decode helpers are identical; **infer timeout** differs (`300` s vs `60` s).
CAP-001 and KSRV-001 specs document both modules; pytest parametrizes over both paths (MT-W12).

## Follow-up (not blocking W5-P1b)

| Item                                 | Owner          | Notes                                            |
| ------------------------------------ | -------------- | ------------------------------------------------ |
| `tests/test_app_import.py`           | MT-W12+        | `MODEL_ENDPOINT` import guard with `monkeypatch` |
| `baseline-smoke.md` intro cross-link | MT-R6 (W5-P5)  | Pointer to this index                            |
| DRL-001 → `accepted`                 | MT-R3a (W5-P4) | 150% layout operator sign-off                    |
