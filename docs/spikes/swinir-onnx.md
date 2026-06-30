# Spike: SwinIR ONNX shapes

<!-- Assisted by: cursor, claude -->

| Field           | Value                                                              |
| --------------- | ------------------------------------------------------------------ |
| Date            | 2026-06-30                                                         |
| Verdict         | **pass** (dynamic H/W; native 4× super-resolution)                 |
| Cluster/profile | local podman + `caisat` namespace MLServer (CPU predictor)         |
| Blocks          | Phase 16 (tiled SR sizing); does **not** block — dynamic shapes OK |

## Command

```bash
# Pull model OCI image (fork mirror — repo from chart/values.yaml)
REPO=$(python3 -c "import yaml; print(yaml.safe_load(open('chart/values.yaml'))['model']['image']['repository'])")
TAG=$(python3 -c "import yaml; print(yaml.safe_load(open('chart/values.yaml'))['model']['image']['tag'])")
podman pull "${REPO}:${TAG}"

# Extract ONNX and inspect with onnx + onnxruntime
podman create --name caisat-onnx-spike "${REPO}:${TAG}"
podman export caisat-onnx-spike | tar -x models/model.onnx
podman rm caisat-onnx-spike
python3 -c "
import onnx, onnxruntime as ort, numpy as np
from onnx import TensorProto
m = onnx.load('models/model.onnx')
for t in m.graph.input:
    print('IN', t.name, TensorProto.DataType.Name(t.type.tensor_type.elem_type))
for t in m.graph.output:
    print('OUT', t.name, TensorProto.DataType.Name(t.type.tensor_type.elem_type))
sess = ort.InferenceSession('models/model.onnx', providers=['CPUExecutionProvider'])
x = np.random.rand(1, 3, 256, 256).astype(np.float32)
y = sess.run(None, {'input': x})[0]
print('256 infer output shape:', y.shape)
x512 = np.random.rand(1, 3, 512, 512).astype(np.float32)
y512 = sess.run(None, {'input': x512})[0]
print('512 infer output shape:', y512.shape)
"

# MLServer metadata + live infer (cluster — caisat namespace)
POD=$(oc -n caisat get pod -l serving.kserve.io/inferenceservice=swinir -o jsonpath='{.items[0].metadata.name}')
oc -n caisat port-forward "pod/${POD}" 18080:8080 &
curl -s http://127.0.0.1:18080/v2/models/swinir
# JSON KServe v2 infer — same payload shape as backend/app.py preprocess_image()
python3 -c "
import json, urllib.request, numpy as np
endpoint = 'http://127.0.0.1:18080/v2/models/swinir/infer'
batch = np.expand_dims(np.transpose(np.random.rand(256,256,3).astype(np.float32),(2,0,1)),0)
payload = {'inputs':[{'name':'input','shape':list(batch.shape),'datatype':'FP32','data':batch.flatten().tolist()}]}
req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=600) as resp:
    out = json.loads(resp.read().decode())['outputs'][0]
print('output shape:', out['shape'])
"
```

## Output (snippet)

```text
=== ONNX Model Metadata ===
file_size_bytes: 129644967
ir_version: 8
opset: [('ai.onnx', 17)]
producer: pytorch 2.7.1

=== Graph Inputs ===
  name='input' dtype=FLOAT shape=[batch_size, 3, height, width]

=== Graph Outputs ===
  name='output' dtype=FLOAT shape=[batch_size, 3, height, width]

=== ONNX Runtime Session ===
  input: name='input' shape=['batch_size', 3, 'height', 'width'] type=tensor(float)
  output: name='output' shape=['batch_size', 3, 'height', 'width'] type=tensor(float)

=== Inference test (256x256) ===
  output[0] name='output' shape=(1, 3, 1024, 1024) dtype=float32

=== Inference test (512x512) ===
  output[0] name='output' shape=(1, 3, 2048, 2048) dtype=float32

=== MLServer /v2/models/swinir ===
  inputs:  name=input  shape=[-1, 3, -1, -1]  datatype=FP32
  outputs: name=output shape=[-1, 3, -1, -1]  datatype=FP32

=== MLServer infer (256×256 input, JSON KServe v2) ===
  output name: predict
  output shape: [1, 3, 1024, 1024]
  output datatype: FP32
  data length: 3145728
  elapsed_sec: 157.7
```

## Backend comparison (`backend/app.py`)

| Assumption         | Backend today                               | ONNX / MLServer actual                    | Match                                  |
| ------------------ | ------------------------------------------- | ----------------------------------------- | -------------------------------------- |
| Input tensor name  | `"input"` (L72)                             | `input`                                   | yes                                    |
| Input shape        | `(1, 3, 256, 256)` via hard resize (L55–56) | dynamic `[-1, 3, -1, -1]`; 256 accepted   | yes for current path                   |
| Input dtype        | FP32 (L74)                                  | FLOAT / FP32                              | yes                                    |
| Output tensor      | `outputs[0]` (L94)                          | first output; MLServer names it `predict` | yes (index 0)                          |
| Native output size | implied 512 via post-resize (L193–194)      | **4× input**: 256→1024, 512→2048          | **no** — backend downscales            |
| Scale factor       | effective 2× (512/256) after L193–194       | native **4×** super-resolution            | mismatch — retire L193–194 in Phase 16 |

## Decision tree

| Branch                 | Applies? | Action                                                                                                       |
| ---------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| pass + fixed 256       | no       | model accepts dynamic H/W                                                                                    |
| **pass + dynamic H/W** | **yes**  | Phase 15/16: cap max tile/crop per GPU profile via `/api/capabilities`; tiled SR uses same 4× scale per tile |
| fail/blocked           | no       | re-export not required                                                                                       |

**Phase 16 guidance:** Remove unconditional `resize((512, 512))` at L193–194. For 256×256 single-tile path, deliver 1024×1024 (or profile-limited downscale if UX requires).

Tiled path: stitch tiles at 4× native scale; choose tile size from capabilities (memory-bound on CPU — 256 tile → 1024 output per tile is ~12 MB FP32).

## Notes

- Model file inside image: `models/model.onnx` (~124 MB).
- Output values may exceed 1.0 (observed max ~1.06); backend `postprocess_output` clips to `[0, 1]` — acceptable.
- MLServer renames graph output `output` → response field name `predict`; backend ignores name and uses `outputs[0]`.
- No blockers for Phase 16 from ONNX export; blocked only if Phase 15 profiles omit memory-aware tile caps.
