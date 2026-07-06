# MT-2-RETEST @ ods-qe-psi-21 ea.2 (2026-07-06)

<!-- Assisted by: cursor, claude -->

**Cluster:** `ods-qe-psi-21` | **Namespace:** `caisat` | **RHOAI:** `3.5.0-ea.2` | **MLServer:** `1.7.1+rhaiv.8`

## Preconditions

| Check              | Result                                           |
| ------------------ | ------------------------------------------------ |
| `oc whoami`        | **pass** — `htpasswd-cluster-admin-user`         |
| RHOAI operator CSV | **pass** — `rhods-operator.3.5.0-ea.2` Succeeded |
| Helm release       | **pass** — `caisat` rev 19, deployed             |
| InferenceServices  | **pass** — SwinIR + YOLOv8-OBB Ready             |

## Infer matrix (from `caisat-backend` pod)

| Predictor  | JSON infer                                              | Binary round-trip   | Predictor log (binary)                                       |
| ---------- | ------------------------------------------------------- | ------------------- | ------------------------------------------------------------ |
| SwinIR     | **pass** — 48.56 s; out `[1,3,1024,1024]`; req ~3.98 MB | **fail** — HTTP 500 | `UnicodeDecodeError` parsing `application/octet-stream` body |
| YOLOv8-OBB | **pass** — 2.18 s; out `[1,20,8400]`; req ~24.9 MB      | **fail** — HTTP 500 | Same FastAPI validation-handler decode error                 |

## Verdict

**fail** (binary) — JSON **pass** / binary **fail** on both predictors @ RHOAI 3.5.0-ea.2. Matches cloudtest2 @ ea.2 (2026-07-01) and psi-21 @ ea.1 (2026-07-01). No upstream fix in MLServer `1.7.1+rhaiv.8`.

## Cross-links

- [`docs/spikes/binary-kserve-v2.md`](../../../spikes/binary-kserve-v2.md#re-test-ods-qe-psi-21-mt-2-retest--ea2-2026-07-06)
- RHOAI support case prep: [`docs/validation/artifacts/mt-ticket-20260704/`](../mt-ticket-20260704/)
