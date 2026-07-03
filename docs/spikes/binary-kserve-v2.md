# Spike: Binary KServe v2 tensor round-trip

<!-- Assisted by: cursor, claude -->

Per-predictor spike for Phase 14: compare KServe v2 JSON tensor payloads (`flatten().tolist()`) against the
[binary tensor data extension](https://kserve.github.io/website/docs/concepts/architecture/data-plane/v2-protocol/binary-tensor-data-extension)
on deployed MLServer predictors.

---

## SwinIR (`input`, shape `(1, 3, 256, 256)`)

| Field           | Value                                                                       |
| --------------- | --------------------------------------------------------------------------- |
| Date            | 2026-06-30                                                                  |
| Verdict         | **fail** — JSON infer OK; binary request returns HTTP 500                   |
| Cluster/profile | pre-production RHOAI 3.5.ea.1; MLServer `1.7.1+rhaiv.8`; namespace redacted |
| Blocks          | Phase 14 (binary tensor migration)                                          |

### Command

```bash
# Cluster access
oc whoami
oc get inferenceservice -n <namespace>
oc get pods -n <namespace>

# Model metadata (inside predictor pod)
oc exec -n <namespace> deploy/swinir-predictor -c kserve-container -- \
  curl -sf http://localhost:8080/v2/models/swinir

# JSON baseline + binary round-trip (from backend pod, in-cluster DNS)
POD=$(oc get pod -n <namespace> -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
oc exec -n <namespace> "${POD}" -- python3 -c "
import json, time, urllib.request, numpy as np
url = 'http://<swinir-predictor>.<namespace>.svc.cluster.local:8080/v2/models/swinir/infer'
data = np.random.default_rng(42).random((1,3,256,256), dtype=np.float32)
# JSON infer
payload = {'inputs':[{'name':'input','shape':[1,3,256,256],'datatype':'FP32','data':data.flatten().tolist()}]}
t0 = time.perf_counter()
with urllib.request.urlopen(urllib.request.Request(url, json.dumps(payload).encode(), headers={'Content-Type':'application/json'}, method='POST'), timeout=300) as r:
    j = json.loads(r.read())
print('JSON OK', round(time.perf_counter()-t0,2), 's', 'req_bytes', len(json.dumps(payload)), 'out', j['outputs'][0]['shape'])
# Binary infer (KServe binary extension)
bb = data.tobytes(order='C')
meta = {'inputs':[{'name':'input','shape':[1,3,256,256],'datatype':'FP32','parameters':{'binary_data_size':len(bb)}}], 'outputs':[{'name':'output','parameters':{'binary_data':True}}]}
mb = json.dumps(meta).encode()
body = mb + bb
req = urllib.request.Request(url, body, headers={'Content-Type':'application/octet-stream','Inference-Header-Content-Length':str(len(mb)),'Content-Length':str(len(body))}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        print('BINARY OK', r.headers.get('Content-Type'), len(r.read()))
except urllib.error.HTTPError as e:
    print('BINARY FAIL', e.code, e.read()[:200])
"

# Predictor log after binary attempt
oc logs -n <namespace> deploy/swinir-predictor -c kserve-container --tail=15
```

### Output (snippet)

```text
# oc get inferenceservice -n <namespace>
NAME               URL                                                      READY
swinir             http://<swinir-predictor>.<namespace>.svc.cluster.local         True
yolov8m-satelite   http://<yolov8-predictor>.<namespace>.svc.cluster.local   True

# Model metadata
{"name":"swinir","inputs":[{"name":"input","datatype":"FP32","shape":[-1,3,-1,-1]}],
 "outputs":[{"name":"output","datatype":"FP32","shape":[-1,3,-1,-1]}]}

# JSON infer (pass)
JSON OK 88.17 s req_bytes 3984396 out [1, 3, 1024, 1024]

# Binary infer (fail)
BINARY FAIL 500 b'Internal Server Error'

# Predictor log
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xfb in position 196: invalid start byte
  (FastAPI validation handler while parsing application/octet-stream body)
```

### Notes

**Platform:** RHOAI 3.5.ea.1 (pre-production).

| Path   | Request `Content-Type`      | Request size | Latency | Response output shape | Result |
| ------ | --------------------------- | ------------ | ------- | --------------------- | ------ |
| JSON   | `application/json`          | ~3.98 MB     | ~88 s   | `(1, 3, 1024, 1024)`  | pass   |
| Binary | `application/octet-stream`¹ | ~0.79 MB²    | —       | —                     | fail   |

¹ Headers: `Inference-Header-Content-Length` (JSON prefix length), `Content-Length` (JSON + FP32 tensor bytes). Output requested with `"parameters": {"binary_data": true}` on tensor `"output"`.

² Theoretical: `1×3×256×256×4` bytes FP32 + ~120-byte JSON header vs ~3.98 MB JSON float list (~80% smaller).

JSON infer matches current [`backend/app.py`](../../backend/app.py) path. Binary round-trip did not complete; MLServer returned HTTP 500 before a decodable tensor was returned.

---

## YOLOv8-OBB (`images`, shape `(1, 3, 640, 640)`)

| Field           | Value                                                                       |
| --------------- | --------------------------------------------------------------------------- |
| Date            | 2026-06-30                                                                  |
| Verdict         | **fail** — JSON infer OK; binary request returns HTTP 500                   |
| Cluster/profile | pre-production RHOAI 3.5.ea.1; MLServer `1.7.1+rhaiv.8`; namespace redacted |
| Blocks          | Phase 14 (binary tensor migration)                                          |

### Command

```bash
# Model metadata
oc exec -n <namespace> deploy/yolov8m-satelite-predictor -c kserve-container -- \
  curl -sf http://localhost:8080/v2/models/yolov8m-satelite

# JSON baseline + binary round-trip (from backend pod)
POD=$(oc get pod -n <namespace> -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
oc exec -n <namespace> "${POD}" -- python3 -c "
import json, time, urllib.request, numpy as np
url = 'http://<yolov8-predictor>.<namespace>.svc.cluster.local:8080/v2/models/yolov8m-satelite/infer'
data = np.random.default_rng(42).random((1,3,640,640), dtype=np.float32)
payload = {'inputs':[{'name':'images','shape':[1,3,640,640],'datatype':'FP32','data':data.flatten().tolist()}]}
t0 = time.perf_counter()
with urllib.request.urlopen(urllib.request.Request(url, json.dumps(payload).encode(), headers={'Content-Type':'application/json'}, method='POST'), timeout=300) as r:
    j = json.loads(r.read())
print('JSON OK', round(time.perf_counter()-t0,2), 's', 'req_bytes', len(json.dumps(payload)), 'out', j['outputs'][0]['shape'])
bb = data.tobytes(order='C')
meta = {'inputs':[{'name':'images','shape':[1,3,640,640],'datatype':'FP32','parameters':{'binary_data_size':len(bb)}}], 'outputs':[{'name':'output0','parameters':{'binary_data':True}}]}
mb = json.dumps(meta).encode()
body = mb + bb
req = urllib.request.Request(url, body, headers={'Content-Type':'application/octet-stream','Inference-Header-Content-Length':str(len(mb)),'Content-Length':str(len(body))}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        print('BINARY OK', r.headers.get('Content-Type'), len(r.read()))
except urllib.error.HTTPError as e:
    print('BINARY FAIL', e.code, e.read()[:200])
"

oc logs -n <namespace> deploy/yolov8m-satelite-predictor -c kserve-container --tail=15
```

### Output (snippet)

```text
# Model metadata
{"name":"yolov8m-satelite","inputs":[{"name":"images","datatype":"FP32","shape":[-1,3,-1,-1]}],
 "outputs":[{"name":"output0","datatype":"FP32","shape":[-1,-1,-1]}]}

# JSON infer (pass)
JSON OK 1.94 s req_bytes 24905346 out [1, 20, 8400]

# Binary infer (fail) — also fails with binary input only (no binary output requested)
BINARY FAIL 500 b'Internal Server Error'

# Predictor log
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xfb in position 128: invalid start byte
```

### Notes

| Path   | Request `Content-Type`     | Request size | Latency | Response output shape | Result |
| ------ | -------------------------- | ------------ | ------- | --------------------- | ------ |
| JSON   | `application/json`         | ~24.9 MB     | ~1.9 s  | `(1, 20, 8400)`       | pass   |
| Binary | `application/octet-stream` | ~4.9 MB²     | —       | —                     | fail   |

² Theoretical: `1×3×640×640×4` bytes FP32 + JSON header vs ~24.9 MB JSON (~80% smaller). YOLO would benefit most from binary payloads in
Phase 14.

Matches current [`backend-detection/app.py`](../../backend-detection/app.py) JSON path. Binary input-only requests (JSON response) also returned
HTTP 500 — the failure is on request parsing, not output encoding alone.

---

## Phase 14 scope: pipeline JSON path

A **third** KServe caller still uses JSON tensors. [`chart/files/analyze_seed_images_pipeline.yaml`](../../chart/files/analyze_seed_images_pipeline.yaml) embeds Python that posts:

```python
payload = {
    "inputs": [{
        "name": "input",
        "shape": list(image_array.shape),
        "datatype": "FP32",
        "data": image_array.flatten().tolist(),
    }]
}
url = f"{model_endpoint}/v2/models/{model_name}/infer"
response = requests.post(url, json=payload, timeout=60)
```

This pattern is duplicated across four pipeline component executors (`comp-analyze-location` through `comp-analyze-location-4`). Phase 14 must
migrate this Sentinel2 pipeline path to binary **or** document a tested JSON exception in this spike once MLServer binary support is verified.

Default pipeline model endpoint: `http://sentinel2-model-predictor.release-namespace.svc.cluster.local:8080` (Sentinel2 not deployed in fork namespace during this spike).

---

## Re-test: RHOAI 3.5.ea.2

| Field           | Value                                                                                   |
| --------------- | --------------------------------------------------------------------------------------- |
| Date            | 2026-06-30                                                                              |
| Verdict         | **blocked** — platform verified; CAIsat predictors not Ready; infer matrix not executed |
| Cluster/profile | pre-production RHOAI 3.5.ea.2; MLServer `1.7.1+rhaiv.8`; namespace redacted             |
| Blocks          | Phase 14 (binary tensor migration) — cannot confirm ea.2 fix without working predictors |

### Platform verification

```bash
# RHOAI operator CSV (version only; redact hostnames in notes)
oc get csv -n redhat-ods-operator | grep rhods
# rhods-operator.3.5.0-ea.2   3.5.0-ea.2   Succeeded

# MLServer version from ea.2 odh-mlserver image (in-cluster one-shot pod)
oc run mlserver-ver-check --restart=Never \
  --image=registry.redhat.io/rhoai/odh-mlserver-rhel9@sha256:<ea2-digest> \
  --command -- python3 -c "import mlserver; print(mlserver.__version__)"
# 1.7.1+rhaiv.8
```

### CAIsat deploy status

| Check                          | Result                                                             |
| ------------------------------ | ------------------------------------------------------------------ |
| InferenceServices (pre-deploy) | None found                                                         |
| Helm install attempted         | Yes — InferenceServices created but predictors not Ready           |
| Blocker                        | Model init container: Quay image pull `unauthorized` (fork mirror) |
| SwinIR / YOLO infer re-test    | **not run** — predictors stuck `Init:ImagePullBackOff`             |

### Per-predictor vs 3.5.ea.1

| Predictor  | 3.5.ea.1 (baseline)    | 3.5.ea.2 re-test | Notes                                         |
| ---------- | ---------------------- | ---------------- | --------------------------------------------- |
| SwinIR     | JSON pass; binary fail | **not tested**   | Blocked on deploy; MLServer version unchanged |
| YOLOv8-OBB | JSON pass; binary fail | **not tested**   | Blocked on deploy; MLServer version unchanged |

### Notes

RHOAI **3.5.0-ea.2** is installed (operator CSV `3.5.0-ea.2`). The ea.2 `odh-mlserver-rhel9` image digest differs from ea.1, but the
packaged MLServer Python version remains **`1.7.1+rhaiv.8`** — same as the ea.1 baseline spike. Without a running predictor, the JSON/binary
infer matrix could not be re-executed; **cannot confirm** whether ea.2 fixes the `application/octet-stream` HTTP 500 observed on ea.1.

**Follow-up:** Re-run this section after CAIsat deploy with valid Quay pull credentials on a 3.5.ea.2 cluster. If MLServer version is still
`1.7.1+rhaiv.8`, expect the same binary failure unless the image contains a patch not reflected in the Python package version string.

---

## Re-test: ods-qe-psi-21 (2026-07-01)

| Field           | Value                                                                               |
| --------------- | ----------------------------------------------------------------------------------- |
| Date            | 2026-07-01                                                                          |
| Verdict         | **fail** — JSON infer OK; binary request returns HTTP 500 (same root cause as ea.1) |
| Cluster/profile | pre-production RHOAI 3.5.0-ea.1; MLServer `1.7.1+rhaiv.8`; namespace `caisat`       |
| Blocks          | Phase 14 (binary tensor migration) — JSON fallback remains active                   |

### Preconditions verified

| Check              | Result                                                                  |
| ------------------ | ----------------------------------------------------------------------- |
| `quay-pull-secret` | **pass** — present; bound to `default` SA alongside `default-dockercfg` |
| InferenceServices  | **pass** — SwinIR + YOLOv8-OBB Ready                                    |
| MLServer version   | `1.7.1+rhaiv.8` (swinir-predictor pod)                                  |

### Per-predictor infer matrix

| Predictor  | JSON infer                               | Binary round-trip   | Predictor log (binary)                                       |
| ---------- | ---------------------------------------- | ------------------- | ------------------------------------------------------------ |
| SwinIR     | **pass** — 93.3 s; out `[1,3,1024,1024]` | **fail** — HTTP 500 | `UnicodeDecodeError` parsing `application/octet-stream` body |
| YOLOv8-OBB | **pass** — 3.3 s; out `[1,20,8400]`      | **fail** — HTTP 500 | Same FastAPI validation-handler decode error                 |

### Notes

CAIsat stack healthy on ods-qe-psi-21 (Helm rev 3). Binary failure is unchanged from ea.1 baseline despite working Quay pull — MLServer
`1.7.1+rhaiv.8` on RHOAI 3.5.0-ea.1 still rejects KServe v2 binary tensor requests.

**Waiver:** Not granted — RHOAI support ticket ID required before waiving Phase 14 binary migration (operator to file).

**Path A upgrade candidate (2026-07-02):** A candidate FBC `CatalogSource` (`rhoai-ea2-catalog`) was identified as a possible alternative
route to upgrade this cluster's RHOAI operator from 3.4.2 in place — see
[Candidate: FBC CatalogSource for Wave 9 Path A](#candidate-fbc-catalogsource-for-wave-9-path-a-2026-07-02). The screenshot it was sourced
from is confirmed to be from `cloudtest2` (2026-07-03), **not** this cluster — the `CatalogSource`/`Subscription` still need to be created
fresh on `ods-qe-psi-21` before Path A can be attempted here.

---

## Re-test: cloudtest2 Wave 9 / MT-EA2 (2026-07-01)

| Field           | Value                                                                             |
| --------------- | --------------------------------------------------------------------------------- |
| Date            | 2026-07-01                                                                        |
| Verdict         | **fail** (binary) — JSON infer OK; binary HTTP 500 unchanged from ea.1 / psi-21   |
| Cluster/profile | pre-production RHOAI **3.5.0-ea.2**; MLServer `1.7.1+rhaiv.8`; namespace `caisat` |
| Blocks          | Phase 14 binary migration; Wave 9 Path A still blocked (bundle tag not published) |

### Preconditions verified

| Check              | Result                                                                                                                |
| ------------------ | --------------------------------------------------------------------------------------------------------------------- |
| RHOAI operator CSV | **pass** — `3.5.0-ea.2` Succeeded                                                                                     |
| `quay-pull-secret` | **pass** — copied from cluster marketplace `quay-secret`; linked to `default` SA                                      |
| InferenceServices  | **pass** — SwinIR + YOLOv8-OBB Ready (CPU profile; GPU tier blocked on single T4 node)                                |
| MLServer image     | `registry.redhat.io/rhoai/odh-mlserver-rhel9@sha256:d76bea18afe7b361847babb7a8ebc51fdbcd8164435f1bcb971e1701ba1bc595` |
| MLServer version   | `1.7.1+rhaiv.8` (swinir-predictor pod)                                                                                |
| Helm release       | rev **2** (`failed` — post-install run-analysis hook; IS Ready)                                                       |

### Deploy notes

- Initial GPU profile (`t4`) failed scheduling: single T4 consumed by sentinel2 predictor; SwinIR/YOLO Pending (`Insufficient nvidia.com/gpu`).
- Switched to **CPU profile**; SwinIR + YOLO Ready. Minimal overrides: seed/pipelines/changedetection disabled.
- `kserve.preferBinary=true` in Helm values — HTTP `/api/enhance` and `/api/detect` return **500** (binary infer path). JSON API paths verified with temporary `KSERVE_PREFER_BINARY=false` on backends.

### Per-predictor infer matrix (MT-2)

| Predictor  | JSON infer                               | Binary round-trip   | Predictor log (binary)                                       |
| ---------- | ---------------------------------------- | ------------------- | ------------------------------------------------------------ |
| SwinIR     | **pass** — 22.9 s; out `[1,3,1024,1024]` | **fail** — HTTP 500 | `UnicodeDecodeError` parsing `application/octet-stream` body |
| YOLOv8-OBB | **pass** — 1.7 s; out `[1,20,8400]`      | **fail** — HTTP 500 | Same FastAPI validation-handler decode error                 |

### HTTP API (JSON fallback, `KSERVE_PREFER_BINARY=false`)

| Endpoint                     | Result                                                |
| ---------------------------- | ----------------------------------------------------- |
| `GET /health` (both)         | **pass**                                              |
| `POST /api/enhance` 256→1024 | **pass** — HTTP 200; output `(1024, 1024)`; ~37 s CPU |
| `POST /api/detect`           | **pass** — HTTP 200; `detections: []`; ~1.5 s         |

### vs 3.5.ea.1 / psi-21 baseline

| Predictor  | ea.1 / psi-21          | ea.2 cloudtest2 (2026-07-01) | Notes                      |
| ---------- | ---------------------- | ---------------------------- | -------------------------- |
| SwinIR     | JSON pass; binary fail | JSON pass; binary fail       | MLServer version unchanged |
| YOLOv8-OBB | JSON pass; binary fail | JSON pass; binary fail       | Same root cause on ea.2    |

### Notes

RHOAI **3.5.0-ea.2** on cloudtest2 confirms operator/catalog health without psi-21 upgrade. MLServer **1.7.1+rhaiv.8** on ea.2 image digest
`d76bea18…` still rejects KServe v2 binary tensor requests — **no ea.2 fix** for Phase 14 binary migration. Wave 9 Path A (psi-21 upgrade) remains
blocked on bundle tag publish; **validation path** on cloudtest2 is **partial pass** (MT-EA2 platform + JSON stack; binary **fail**).

---

## Candidate: FBC CatalogSource for Wave 9 Path A (2026-07-02)

**Status: unverified candidate — do not treat as resolving Wave 9 Path A.**

An OpenShift console "CatalogSource details" screenshot surfaced a File-Based Catalog (FBC) fragment that may be a different
distribution path from the previously-blocked `registry.redhat.io/rhoai/odh-operator-bundle:v3.5.0-ea.2` tag:

| Field                  | Value                                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- |
| CatalogSource name     | `rhoai-ea2-catalog`                                                                                           |
| Namespace              | `openshift-marketplace`                                                                                       |
| Status (in screenshot) | READY                                                                                                         |
| Display name           | `RHOAI 3.5 EA.2`                                                                                              |
| Publisher              | Red Hat                                                                                                       |
| Image                  | `quay.io/rhoai/rhoai-fbc-fragment:rhoai-3.5-ea.2` (digest in screenshot has likely OCR artifacts — see below) |
| Registry poll interval | `10m`                                                                                                         |
| Number of Operators    | 1                                                                                                             |

Draft manifests: [`manifests/rhoai-ea2-catalogsource.yaml`](manifests/rhoai-ea2-catalogsource.yaml) and
[`manifests/rhoai-ea2-subscription.yaml`](manifests/rhoai-ea2-subscription.yaml). **Neither has been applied to any cluster.**

### Open questions (must confirm before relying on this path)

1. ~~**Which cluster was the screenshot taken on?**~~ **Confirmed 2026-07-03: `cloudtest2`.** That cluster already runs RHOAI 3.5.0-ea.2 per
   [MT-EA2](#re-test-cloudtest2-wave-9--mt-ea2-2026-07-01), so this `CatalogSource` being present and `READY` there is consistent with (and
   plausibly how) that install happened — a mild positive signal that the FBC route is viable. It still must be created fresh on
   `ods-qe-psi-21` for Path A; presence on cloudtest2 does not carry over automatically.
2. **Operator channel name — still unresolved on psi-21.** No ea.2-specific channel is documented anywhere in this repo (the current
   subscription channel on psi-21 is `beta`, not `stable-3.4` as previously assumed — see
   [psi-21 apply attempt](#psi-21-apply-attempt-2026-07-03) below). The draft `Subscription` still carries the `TODO-CONFIRM-CHANNEL`
   placeholder because the `rhoai-ea2-catalog` `CatalogSource` never reached `READY` on psi-21 (see item below) — `packagemanifest` data is
   only populated from a catalog once its registry pod is serving, so the channel could not be inspected.
3. **Digest accuracy.** The screenshot's image digest (`sha256:e702d07e...`) reads as likely OCR-corrupted (mixed case in a hex digest, stray
   characters). The draft manifest pins the **tag** (`rhoai-3.5-ea.2`) rather than the digest; re-derive and verify the digest with
   `skopeo inspect docker://quay.io/rhoai/rhoai-fbc-fragment:rhoai-3.5-ea.2` before treating any specific digest as authoritative. **Moot for
   now** — the tag itself cannot be pulled at all (see below), independent of digest correctness.
4. **`quay.io/rhoai` pull credential is broken, not absent.** psi-21's cluster-wide pull secret (`openshift-config/pull-secret`) already
   contains a scoped auth entry for `quay.io/rhoai` (alongside a top-level `quay.io` entry), but Quay rejects it: the robot credential
   was not found / password did not match. This differs from `chart/README.md`'s "two-secret pattern"
   assumption that the `rhoai-quay-pull` secret is simply **not created** — on psi-21 an equivalent credential exists but is stale/invalid
   and needs rotation by whoever owns that robot account, not first-time creation.

### Apply / verify steps (psi-21, once the above are confirmed)

```bash
# 1. Apply the CatalogSource
oc apply -f docs/spikes/manifests/rhoai-ea2-catalogsource.yaml

# 2. If the quay.io/rhoai org requires auth (pre-GA/ea catalogs do — see chart/README.md
#    "Pull secrets" two-secret pattern), create + link the RHOAI catalog pull secret first:
oc create secret docker-registry rhoai-quay-pull \
  --docker-server=quay.io \
  --docker-username='<rhoai-robot-name>' \
  --docker-password='<rhoai-robot-token>' \
  -n openshift-marketplace
oc patch sa <catalog-sa> -n openshift-marketplace \
  --type=json -p '[{"op":"add","path":"/imagePullSecrets/-","value":{"name":"rhoai-quay-pull"}}]'

# 3. Verify the CatalogSource reaches READY (poll interval is 10m; may take a few minutes)
oc get catalogsource rhoai-ea2-catalog -n openshift-marketplace -o wide

# 4. Confirm the rhods-operator package/channel is visible from this catalog and resolves
#    to 3.5.0-ea.2 BEFORE subscribing (console Operators tab, or CLI):
oc get packagemanifest rhods-operator -n openshift-marketplace -o yaml

# 5. Only after step 4 confirms the channel: apply the Subscription (after filling in the
#    real channel name — do not apply with the TODO-CONFIRM-CHANNEL placeholder)
oc apply -f docs/spikes/manifests/rhoai-ea2-subscription.yaml

# 6. Confirm the CSV installs successfully
oc get csv -n redhat-ods-operator | grep rhods
# expect: rhods-operator.3.5.0-ea.2   3.5.0-ea.2   Succeeded
```

### psi-21 apply attempt (2026-07-03)

| Field           | Value                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------- |
| Date            | 2026-07-03                                                                                        |
| Verdict         | **blocked** — `CatalogSource` applied but not `READY`; `Subscription` not attempted               |
| Cluster/profile | `ods-qe-psi-21`; RHOAI operator unchanged at `rhods-operator.3.4.2` (Succeeded, replaces `3.4.0`) |
| Blocks          | Wave 9 Path A — cannot resolve ea.2 channel or subscribe without a working catalog pull           |

#### Pre-flight state

| Check                   | Result                                                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| RHOAI operator CSV      | `rhods-operator.3.4.2` — Succeeded (matches expected baseline)                                                                                   |
| Existing CatalogSources | Only the three defaults (`certified-operators`, `community-operators`, `redhat-operators`); no `rhoai-ea2-catalog` present — safe to apply fresh |
| Current subscription    | `rhods-operator` — package `rhods-operator`, source `redhat-operators`, channel `beta` (not `stable-3.4` as previously assumed in this repo)     |

#### CatalogSource apply result

```bash
oc apply -f docs/spikes/manifests/rhoai-ea2-catalogsource.yaml
# catalogsource.operators.coreos.com/rhoai-ea2-catalog created
```

Polled `oc get catalogsource rhoai-ea2-catalog -n openshift-marketplace` / pod status over ~65s; state was stable, not transient:

```text
connectionState.lastObservedState: TRANSIENT_FAILURE
pod rhoai-ea2-catalog-<id>: 0/1 ErrImagePull / ImagePullBackOff

Failed to pull image "quay.io/rhoai/rhoai-fbc-fragment:rhoai-3.5-ea.2":
unable to retrieve auth token: invalid username/password: unauthorized:
Could not find robot with username: <redacted robot credential> and supplied password.
```

Root cause: the cluster's global pull secret (`openshift-config/pull-secret`) already has a scoped `quay.io/rhoai` auth entry, but Quay
rejects the credential as invalid (robot not found / bad password). This is a **broken existing credential**, not a missing one — per
the safety instructions for this task, no attempt was made to create, guess, or rotate credentials.

**What's needed to unblock:** whoever owns the `quay.io/rhoai` robot account needs to verify it still exists and
rotate/reissue its token, then update the `quay.io/rhoai` entry in `openshift-config/pull-secret` (cluster-wide) — or add a separate
`rhoai-quay-pull` secret linked to the CatalogSource's service account per the `chart/README.md` "two-secret pattern", with a valid token.

Because the `CatalogSource` never reached `READY`, **steps 4 and 5 (channel resolution and Subscription apply) were not attempted** —
attempting either would have required guessing a channel name, which the task instructions explicitly prohibit. The `CatalogSource`
object itself was left applied on the cluster (purely additive; does not affect the running `3.4.2` operator) for whoever picks up the
credential fix to resume from without re-applying.

### Verdict

**Blocked on a broken Quay credential, not a confirmed fix.** The `CatalogSource` was applied to `ods-qe-psi-21` on 2026-07-03 but did not
reach `READY` — image pull for `quay.io/rhoai/rhoai-fbc-fragment:rhoai-3.5-ea.2` fails with `unauthorized` against an existing-but-invalid
`quay.io/rhoai` robot credential already in the cluster's global pull secret. No `Subscription` was created (channel could not be resolved
without a working catalog), and **the RHOAI operator on psi-21 remains unchanged at `3.4.2`** — no upgrade was installed, approved, or
triggered. Wave 9 Path A stays **blocked/deferred** (MT-RHOAI-RESUME) until (a) the `quay.io/rhoai` credential is fixed/rotated, (b) the
`CatalogSource` reaches `READY` and the real ea.2 channel is confirmed via `packagemanifest`, and (c) a human explicitly approves the
resulting `InstallPlan`. Cross-ref: [`docs/project/PLAN.md`](../project/PLAN.md) Wave 9 / Open blockers.

---

## RHOAI support ticket (operator prep)

Use this section when filing a Red Hat support case for MLServer binary infer failure. **Do not** include cluster FQDNs or personal identifiers in committed docs —
paste redacted values into the ticket only.

### Ticket title (suggested)

`RHOAI MLServer 1.7.1+rhaiv.8 rejects KServe v2 binary infer (application/octet-stream) — HTTP 500 UnicodeDecodeError`

### Environment

| Field         | Value                                                                                     |
| ------------- | ----------------------------------------------------------------------------------------- |
| RHOAI version | **3.4.0** (stable-3.4 fallback; ea.2 deferred)                                            |
| MLServer      | `1.7.1+rhaiv.8` (swinir-predictor pod)                                                    |
| KServe        | v2 JSON infer **pass**; binary `Content-Type: application/octet-stream` **fail** HTTP 500 |
| Workload      | CAIsat SwinIR + YOLOv8-OBB InferenceServices in `<namespace>`                             |

### Repro (in-cluster, from backend pod)

1. Confirm both InferenceServices Ready; JSON infer pass on SwinIR `(1,3,256,256)` and YOLO `(1,3,640,640)`.
2. POST binary infer with KServe v2 header `Inference-Header-Content-Length` + tensor body per [encode pattern](#re-test-ods-qe-psi-21-2026-07-01).
3. Observe HTTP **500** on both predictors; predictor log shows `UnicodeDecodeError` in FastAPI validation handler when parsing binary body as text.

### Expected vs actual

|                | Expected                                                       | Actual                                            |
| -------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| Binary infer   | Decoded output matches JSON within `1e-4` max abs diff         | HTTP 500; no binary tensor response               |
| Error handling | MLServer accepts `application/octet-stream` per KServe v2 spec | FastAPI `UnicodeDecodeError` on octet-stream body |

### Impact on CAIsat

- `KSERVE_PREFER_BINARY=true` breaks enhance and detect when binary infer fails — chart sets `kserve.preferBinary: false` on both backends (PR #82 @ `7eb9a76`).
- Detection backend HTTP 500 on 1024 SAHI (2026-07-01) traced to same root cause — missing `KSERVE_PREFER_BINARY=false`; fixed in PR #82.
- Phase 14 binary migration **blocked**; JSON fallback active in both backends.
- **Partial waiver (Wave 5):** Phase 14 JSON fallback accepted for Partial closure 2026-07-01; **Full** closure requires RHOAI ticket + MT-2 binary pass.

### Cross-links

- [Re-test: ods-qe-psi-21 (2026-07-01)](#re-test-ods-qe-psi-21-2026-07-01)
- [`docs/specs/kserve-v2-tensors.md`](../specs/kserve-v2-tensors.md)
- [`docs/project/PLAN.md`](../project/PLAN.md) Open blockers — MLServer binary

### Paste-ready ticket body (Red Hat Customer Portal)

Copy below into a new support case. Replace `<namespace>` and attach predictor logs from a binary infer attempt. **Do not** paste cluster FQDNs into committed docs.

```text
Summary: RHOAI MLServer 1.7.1+rhaiv.8 returns HTTP 500 on KServe v2 binary infer (Content-Type: application/octet-stream). JSON infer on the same predictors succeeds.

Product: Red Hat OpenShift AI
Version: 3.4.0 (stable-3.4 channel)
MLServer: 1.7.1+rhaiv.8 (swinir-predictor pod, kserve-container)

Symptoms:
- POST /v2/models/swinir/infer with application/octet-stream + Inference-Header-Content-Length → HTTP 500
- POST /v2/models/yolov8m-satelite/infer — same failure
- JSON infer (Content-Type: application/json) passes on both predictors

Predictor log (binary attempt):
UnicodeDecodeError: 'utf-8' codec can't decode byte ... in position ...: invalid start byte
(at FastAPI validation error handler when parsing binary request body as text)

Repro: From any pod in namespace <namespace>, send KServe v2 binary tensor request per
https://kserve.github.io/website/docs/concepts/architecture/data-plane/v2-protocol/binary-tensor-data-extension
Header: Content-Type: application/octet-stream, Inference-Header-Content-Length: <json-header-length>
Body: <json-metadata-bytes><raw-tensor-bytes>

Expected: Binary infer returns decoded output matching JSON infer within 1e-4 max abs diff.
Actual: HTTP 500 Internal Server Error on both SwinIR and YOLOv8-OBB predictors.

Impact: Cannot enable KSERVE_PREFER_BINARY=true; large JSON payloads (~25 MB YOLO) remain required.
Workaround: JSON infer only (KSERVE_PREFER_BINARY=false).

Request: Fix MLServer binary tensor extension handling or document required runtime configuration for RHOAI 3.4.0.
```

**Status:** Draft ready — operator to file and record ticket ID in PLAN Open blockers (no fake ID in repo).

---

## Summary

| Predictor           | Tensor   | Input shape        | JSON infer | Binary round-trip | Phase 14 blocker                                 |
| ------------------- | -------- | ------------------ | ---------- | ----------------- | ------------------------------------------------ |
| SwinIR              | `input`  | `(1, 3, 256, 256)` | **pass**   | **fail**          | MLServer binary extension returns HTTP 500       |
| YOLOv8-OBB          | `images` | `(1, 3, 640, 640)` | **pass**   | **fail**          | Same; largest JSON payload (~25 MB)              |
| Pipeline (Phase 14) | `input`  | varies (Sentinel2) | not tested | not tested        | Third JSON caller; migrate or exempt in Phase 14 |

**Pass criteria (plan):** decoded binary output matches JSON infer within `1e-4` max abs diff **per predictor**. Not met.

**Root cause (observed):** RHOAI MLServer `1.7.1+rhaiv.8` rejects `application/octet-stream` infer bodies; FastAPI raises `UnicodeDecodeError`
in the validation error handler when binary bytes appear in the request body. Re-test after MLServer/runtime upgrade or RHOAI binary-extension
configuration fix.

**Cluster access used:** `oc` authenticated cluster admin on `<cluster-profile>` (`<api-server>:6443`). Local `oc port-forward`
to svc port `8080` failed (service exposes port `80`); in-cluster calls via backend pod succeeded for JSON.

**Follow-up for Phase 14:**

1. Resolve MLServer binary support on cluster (upgrade, runtime flags, or RHOAI support ticket).
2. Re-run this spike matrix; both SwinIR and YOLO must **pass** before binary-only mode.
3. Backends ship `encode_kserve_binary()` / `decode_kserve_binary()` with **JSON fallback** until MLServer binary is fixed.
4. **Pipeline JSON exception (Phase 14):** [`chart/files/analyze_seed_images_pipeline.yaml`](../../chart/files/analyze_seed_images_pipeline.yaml)
   retains JSON `flatten().tolist()` for Sentinel2 batch analysis. Rationale: Kubeflow pipeline components run in notebook pods without shared
   backend helpers; MLServer binary is blocked cluster-wide. Revisit when binary spike passes or pipeline gets a shared infer library sidecar.

**Waiver (2026-06-30, MT-2):** `oc` authenticated; no CAIsat deploy for ea.2+ retest. Prior fail @ ea.1 and blocked retest @ `2aa6343` stand; JSON fallback active. Re-test when cluster + Quay egress verified.

**Re-test (2026-07-01, MT-2 @ ods-qe-psi-21):** Stack healthy; Quay pull **pass**; MLServer `1.7.1+rhaiv.8` on RHOAI 3.5.0-ea.1; JSON **pass** /
binary **fail** on both predictors — see [Re-test: ods-qe-psi-21](#re-test-ods-qe-psi-21-2026-07-01). Verdict **fail**; waiver blocked (no RHOAI ticket).

**Re-test (2026-07-01, MT-R3c post-redeploy @ ods-qe-psi-21):** After Quay push @ `8be4c58` / merge `e2a7704` and rollout restart; from `caisat-backend` pod — SwinIR JSON **pass**
(89.8 s, out `[1,3,1024,1024]`); SwinIR binary **fail** HTTP 500; YOLO JSON **pass** (3.4 s); YOLO binary **fail** HTTP 500. Verdict **fail** unchanged; waiver still blocked (no RHOAI ticket).

**Re-test (2026-07-01, MT-EA2 @ cloudtest2):** RHOAI **3.5.0-ea.2**; CAIsat deployed (helm rev 2, CPU profile); JSON **pass** / binary **fail** on both
predictors — see [Re-test: cloudtest2 Wave 9 / MT-EA2](#re-test-cloudtest2-wave-9--mt-ea2-2026-07-01). Verdict **fail** (binary); Wave 9 validation
**partial pass**.

**Candidate (2026-07-02, Wave 9 Path A):** FBC `CatalogSource` `rhoai-ea2-catalog` (`quay.io/rhoai/rhoai-fbc-fragment`) identified as a possible
alternative to the blocked `registry.redhat.io` bundle tag for upgrading `ods-qe-psi-21` in place — see
[Candidate: FBC CatalogSource for Wave 9 Path A](#candidate-fbc-catalogsource-for-wave-9-path-a-2026-07-02). **Unverified**: source cluster of the
screenshot, operator channel name, and image digest all need confirmation; not yet applied. Path A remains **blocked/deferred**.

**Apply attempt (2026-07-03, psi-21):** `CatalogSource` applied to `ods-qe-psi-21` — did **not** reach `READY`; `quay.io/rhoai/rhoai-fbc-fragment`
pull fails `unauthorized` against an existing-but-invalid `quay.io/rhoai` robot credential in the cluster's global pull secret — see
[psi-21 apply attempt](#psi-21-apply-attempt-2026-07-03). Channel not resolved; no `Subscription` applied; RHOAI operator on psi-21 unchanged at
`3.4.2`. Path A remains **blocked** pending credential rotation.
