# Spike: YOLO11-OBB evaluation

<!-- Assisted by: cursor, claude -->

Re-opened **2026-07-06** after Phase 20 deferral. Assesses whether YOLO11-OBB can replace
`yolov8m-satelite` (chart `detection.image` tag `yoloobb`; see [`chart/values.yaml`](../../chart/values.yaml)) without backend decode changes.

---

## Summary table

| Field              | Value                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| Date               | 2026-07-06 (re-open); prior skip 2026-06-30                                                         |
| Verdict            | **partial** — format + decode smoke **pass**; quality/latency **not measured**                      |
| Recommendation     | **skip** production migration until satellite fine-tune + cluster GPU eval                          |
| Cluster/profile    | N/A this session; baselines on `<GPU cluster>` T4 + `<namespace>` @ RHOAI 3.5.0-ea.2                |
| Current production | `yolov8m-satelite` — JSON infer `(1,20,8400)` @ 640px; [`binary-kserve-v2.md`](binary-kserve-v2.md) |
| Blocks             | No `yolo11m-satelite` weights; no labeled eval set in repo; cluster mAP/latency pending             |

| Candidate               | DOTA mAP50 (Ultralytics)  | Params | CAIsat fit                                  |
| ----------------------- | ------------------------- | ------ | ------------------------------------------- |
| yolov8m-satelite (prod) | unknown (satellite-tuned) | ~26M   | **baseline**                                |
| yolo11m-obb.pt (stock)  | 80.9                      | 20.9M  | Drop-in ONNX shape; **not** satellite-tuned |
| yolo11l-obb.pt (stock)  | 81.0                      | 26.1M  | +latency; marginal DOTA gain vs 11m         |

---

## Command

Local export + shape/decode smoke (2026-07-06, Fedora, CPU):

```bash
python3 -m venv .venv-yolo11
source .venv-yolo11/bin/activate
pip install 'ultralytics>=8.3.232' onnx onnxruntime numpy opencv-python-headless

yolo export model=yolo11m-obb.pt format=onnx imgsz=640 nms=False simplify=True opset=12

python3 <<'PY'
import sys
from pathlib import Path
import numpy as np
import onnxruntime as ort

sess = ort.InferenceSession('yolo11m-obb.onnx', providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0]
x = np.random.randn(1, 3, 640, 640).astype(np.float32)
y = sess.run(None, {inp.name: x})[0]
assert y.shape == (1, 20, 8400), y.shape

sys.path.insert(0, 'backend-detection')
from obb import decode_yolov8_obb
CLASS_NAMES = [
    'plane', 'ship', 'storage-tank', 'baseball-diamond', 'tennis-court',
    'basketball-court', 'ground-track-field', 'harbor', 'bridge',
    'large-vehicle', 'small-vehicle', 'helicopter', 'roundabout',
    'soccer-ball-field', 'swimming-pool',
]
dets = decode_yolov8_obb(y, 1.0, (0, 0), (640, 640), CLASS_NAMES, 0.25, 0.45)
print('decode_ok', len(dets))
PY
```

---

## Output (snippet)

```text
Ultralytics 8.4.89 Python-3.14.6 torch-2.12.1+cu130 CPU
YOLO11m-obb summary (fused): 134 layers, 20,890,048 parameters, 0 gradients, 71.4 GFLOPs

PyTorch: input shape (1, 3, 640, 640) BCHW and output shape(s) (1, 20, 8400) (40.5 MB)
ONNX: export success, saved as 'yolo11m-obb.onnx' (79.9 MB)

input: images [1, 3, 640, 640] tensor(float)
output: output0 [1, 20, 8400] tensor(float)
runtime shape: (1, 20, 8400)
decode_ok: detections= 117
sample: {'class': 'small-vehicle', 'confidence': 0.407, 'box': [114.32, 378.28, 119.45, 383.13]}
```

---

## Compatibility

### Tensor contract (640×640, 15 DOTA classes, `nms=False`)

| Tensor | Shape                   | Notes                                                                         |
| ------ | ----------------------- | ----------------------------------------------------------------------------- |
| Input  | `(1, 3, 640, 640)` FP32 | Name `images`; letterbox pad 114 — [`app.py`](../../backend-detection/app.py) |
| Output | `(1, 20, 8400)`         | Channels: `[cx,cy,w,h] + 15 class logits + angle`                             |

YOLO11-OBB matches YOLOv8-OBB layout at **640px**. At **1024px** export, anchors increase (e.g. 21504) — CAIsat must keep inference at 640 via letterbox/SAHI.

### Backend decode

[`decode_yolov8_obb`](../../backend-detection/obb.py) works **unchanged** on exported `yolo11m-obb.onnx` when:

- Export uses `nms=False`
- Class count remains 15 with DOTA ordering matching `CLASS_NAMES` in [`app.py`](../../backend-detection/app.py)
- Angle at index 19 (radians)

Known shared limitations (v8 and v11):

- `cv2.dnn.NMSBoxes` — axis-aligned NMS, not rotated
- [`sahi.py`](../../backend-detection/sahi.py) merge — axis-aligned IoU on `box`
- 1024×1024 enhanced images produce **one** 640×640 SAHI tile (top-left) with current slice logic

### Chart / deploy diff (yolo11m vs yolo11l)

| File / key                                     | Change                                    |
| ---------------------------------------------- | ----------------------------------------- |
| `chart/values.yaml` `detection.name`           | `yolo11m-obb` or `yolo11m-satelite`       |
| `detection.image.tag`                          | New OCI tag (e.g. `yolo11m-obb`)          |
| `chart/templates/yolobb-inferenceservice.yaml` | Replace hardcoded `yolov8m-satelite` (4×) |
| `detection.resources.limits.memory`            | 6Gi (m) / consider 8Gi (l)                |
| `backend-detection/`                           | **No change** if shape holds              |

---

## Export procedure

Run **outside repo** (model OCI images are built externally):

```bash
pip install 'ultralytics>=8.3.232' onnx onnxruntime
yolo export model=yolo11m-obb.pt format=onnx imgsz=640 nms=False simplify=True opset=12
```

Package for MLServer KServe (match existing `yoloobb` image layout):

1. Place ONNX under `/mnt/models/` with MLServer `model-settings.json` (ONNX runtime, name aligned to `detection.name`)
2. Confirm `/v2/models/<name>` metadata: input `images`, output `output0`
3. Push to chart `detection.image` repository with new tag (see [`chart/values.yaml`](../../chart/values.yaml))

For **production-quality** satellite detection, fine-tune before export:

```bash
yolo obb train model=yolo11m-obb.pt data=<satellite_dota.yaml> epochs=100 imgsz=640
yolo export model=runs/obb/train/weights/best.pt format=onnx imgsz=640 nms=False
```

---

## Resource estimates

Baselines from [`gpu-servingruntime.md`](gpu-servingruntime.md) and [`binary-kserve-v2.md`](binary-kserve-v2.md) (T4, JSON path):

| Metric                          | yolov8m-satelite (measured)       | yolo11m (estimate) | yolo11l (estimate) |
| ------------------------------- | --------------------------------- | ------------------ | ------------------ |
| Single-slice KServe JSON        | 1.41–2.18 s                       | 0.9–2.0 s          | 1.2–2.8 s          |
| `/api/detect` (1024, ~1 slice)  | ~1.76 s                           | ~1.1–2.2 s         | ~1.4–3.0 s         |
| `/api/detect` (2048, ~9 slices) | ~9× slice + overhead              | ~7–9× slice        | ~10–12× slice      |
| T4 GPU memory (predictor)       | Fits 16 GB (sequential w/ SwinIR) | Similar            | +10–20% headroom   |

JSON payload ~24.9 MB/slice dominates wall time vs raw TRT. Phase 14 binary KServe remains **fail** on RHOAI MLServer `1.7.1+rhaiv.8`.

---

## Eval plan

### Pass criteria (cluster — not run)

| #   | Criterion                                          | Pass threshold                                           |
| --- | -------------------------------------------------- | -------------------------------------------------------- |
| 1   | KServe contract                                    | JSON infer 200; output `(1,20,8400)`                     |
| 2   | Rotated mAP50 (ship, large-vehicle, small-vehicle) | ≥ v8m-satelite + **2 pp** on held-out satellite tiles    |
| 3   | Visual QA                                          | No regression on rotated ship/vehicle recall @ conf=0.5  |
| 4   | p95 `/api/detect`                                  | ≤ **1.25×** baseline @ 1024 enhanced; ≤ **1.35×** @ 2048 |
| 5   | T4 memory                                          | No OOM; predictor Ready under sequential GPU pattern     |

### Local steps (complete)

1. Export + assert `(1,20,8400)` — **pass** 2026-07-06
2. CPU onnxruntime → `decode_yolov8_obb` on random tensor — **pass** 2026-07-06

### Cluster steps (pending)

1. Push OCI; helm upgrade with new `detection.name` / tag
2. `KSERVE_PREFER_BINARY=false` (required)
3. JSON infer matrix (reuse [`binary-kserve-v2.md`](binary-kserve-v2.md) YOLO section)
4. Latency harness: 100 requests × 1024 and 2048 PNGs → p50/p95
5. Label ≥50 tiles → compute class-specific mAP50/recall

---

## Verdict

| Session (2026-07-06)          | Result                                                         |
| ----------------------------- | -------------------------------------------------------------- |
| Format / decode compatibility | **pass** — export `(1,20,8400)`; `decode_yolov8_obb` unchanged |
| Export smoke                  | **pass** — Ultralytics 8.4.89, `yolo11m-obb.onnx` 79.9 MB      |
| mAP / latency / GPU memory    | **not run** — needs `<GPU cluster>` access                     |
| Production migration          | **skip** — stay on `yolov8m-satelite`                          |

Prior skip (2026-06-30) remains directionally valid for production: Phase 17 OBB + SAHI + MT-R3a layout QA **pass**.
Re-open cluster eval if rotated ship/vehicle recall fails acceptance testing **or** satellite YOLO11 fine-tune is scheduled.

---

## Next steps

1. **If recall fails QA:** Curate labeled satellite tile set; fine-tune `yolo11m-obb.pt` → `yolo11m-satelite`
2. **Cluster eval:** Deploy stock `yolo11m-obb` ONNX to `<GPU cluster>` for shape/latency smoke
3. **Fix SAHI trailing-edge** for 1024×1024 enhanced images (independent of YOLO11)
4. **Chart cleanup:** Templatize `yolov8m-satelite` strings in `yolobb-inferenceservice.yaml`
5. **Optional:** Unit test `decode_yolov8_obb` with synthetic `(1,20,8400)` tensor

---

## Notes

Phase 17 delivers OBB decode with angle channel, SAHI slicing, and rotated frontend overlay. Stock YOLO11-OBB is ONNX-compatible with
CAIsat's KServe contract but is **not** a drop-in quality replacement for satellite-tuned `yolov8m-satelite` without fine-tuning and cluster validation.
