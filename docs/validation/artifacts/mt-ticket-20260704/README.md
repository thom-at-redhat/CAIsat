# MT-TICKET — RHOAI support case prep (2026-07-04)

<!-- Assisted by: cursor, claude -->

**Status:** Prep complete — operator files case in Red Hat Customer Portal; record ticket ID in [`docs/project/PLAN.md`](../../../project/PLAN.md) Open blockers.

**Spike source:** [`docs/spikes/binary-kserve-v2.md`](../../../spikes/binary-kserve-v2.md) — section
[RHOAI support ticket (operator prep)](../../../spikes/binary-kserve-v2.md#rhoai-support-ticket-operator-prep).

## Suggested ticket title

```text
RHOAI MLServer 1.7.1+rhaiv.8 rejects KServe v2 binary infer (application/octet-stream) — HTTP 500 UnicodeDecodeError
```

## Artifacts

| File                                                     | Description                                                                                 |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [`ticket-body.txt`](ticket-body.txt)                     | Paste-ready case body for Customer Portal (replace `<namespace>` before filing)             |
| [`predictor-log-snippet.txt`](predictor-log-snippet.txt) | Reference log lines from prior spike re-tests — attach **fresh** predictor logs when filing |

## Filing steps (operator)

1. Sign in to [Red Hat Customer Portal](https://access.redhat.com/support/cases/) → **Open a new case**.
2. **Product:** Red Hat OpenShift AI. **Version:** 3.4.0 (or current cluster version if upgraded to 3.5.0-ea.2).
3. **Subject:** use suggested title above.
4. **Description:** paste contents of [`ticket-body.txt`](ticket-body.txt); replace `<namespace>` with the CAIsat namespace (e.g. `caisat`).
5. **Attachments:** predictor logs from a binary infer attempt (see evidence checklist below). Do **not** include cluster API FQDNs or credentials in attachments shared outside the portal.
6. After submission, record the case number in [`docs/project/PLAN.md`](../../../project/PLAN.md) Open blockers (MLServer binary).

## Evidence checklist (attach to case)

- [ ] RHOAI / ODS operator version (`oc get csv -n redhat-ods-operator`)
- [ ] MLServer image on predictor pods (`oc get pod -n <namespace> -l serving.kserve.io/inferenceservice=swinir -o jsonpath='{.items[0].spec.containers[?(@.name=="kserve-container")].image}'`)
- [ ] InferenceService Ready status (`oc get inferenceservice -n <namespace>`)
- [ ] JSON infer **pass** output (latency + output shape) — confirms predictors healthy
- [ ] Binary infer **fail** HTTP 500 response snippet
- [ ] **Predictor logs** after binary attempt:
  - `oc logs -n <namespace> deploy/swinir-predictor -c kserve-container --tail=50`
  - `oc logs -n <namespace> deploy/yolov8m-satelite-predictor -c kserve-container --tail=50`
- [ ] Optional: backend pod repro command output (binary POST returning 500)

### Capture fresh logs (in-cluster)

From a pod in `<namespace>` with CAIsat deployed and both InferenceServices Ready:

```bash
# Trigger binary infer (SwinIR example — see spike doc for full Python one-liner)
POD=$(oc get pod -n <namespace> -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
# ... run binary infer per docs/spikes/binary-kserve-v2.md ...

# Then capture predictor logs
oc logs -n <namespace> deploy/swinir-predictor -c kserve-container --tail=50 > swinir-predictor-binary-infer.log
oc logs -n <namespace> deploy/yolov8m-satelite-predictor -c kserve-container --tail=50 > yolo-predictor-binary-infer.log
```

Redact any cluster-specific hostnames before committing logs to git; portal attachments may include internal names as required by support.

## Log capture status (2026-07-04 prep session)

**Fresh logs not captured** — `oc` session unauthorized on psi-21 and cloudtest2 contexts at prep time. Operator must run binary infer and attach
current predictor logs manually. Reference snippets in [`predictor-log-snippet.txt`](predictor-log-snippet.txt) document the expected
`UnicodeDecodeError` from prior re-tests.

## Impact summary

- `KSERVE_PREFER_BINARY=true` breaks enhance/detect; chart sets `kserve.preferBinary: false` (PR #82).
- Phase 14 binary migration blocked; JSON fallback active.
- Full Wave 5 closure requires RHOAI fix + MT-2 binary pass after ticket resolution.
