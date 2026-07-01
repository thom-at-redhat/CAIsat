# KServe v2 Tensor Encode/Decode

<!-- Assisted by: cursor, claude -->

| Field      | Value                                                                                         |
| ---------- | --------------------------------------------------------------------------------------------- |
| Status     | accepted                                                                                      |
| Spec ID    | KSRV-001                                                                                      |
| Tests      | `tests/test_kserve_v2.py`                                                                     |
| Validation | `baseline-smoke.md` L66; cluster spike [`binary-kserve-v2.md`](../spikes/binary-kserve-v2.md) |
| Modules    | `backend/kserve_v2.py`, `backend-detection/kserve_v2.py`                                      |

## Overview

Pure-function helpers for KServe v2 JSON and the [binary tensor extension](https://kserve.github.io/website/docs/concepts/architecture/data-plane/v2-protocol/binary-tensor-data-extension).
Used by `kserve_infer()` for SwinIR enhancement and YOLO detection predictors. Encode/decode logic is **identical** in both backend copies;
`kserve_infer()` default timeout differs (`300` s enhancement, `60` s detection).

Cluster note: MLServer `1.7.1+rhaiv.8` rejects binary infer with HTTP 500 (Phase 12/14 spike **fail**); production CPU cluster sets `KSERVE_PREFER_BINARY=false` until RHOAI fix.

## Requirements

### KSRV-001-R1: JSON encode (`encode_kserve_json`)

- Input: `input_name` (string), `tensor` (`np.ndarray`, FP32)
- Output: dict with single `inputs` entry:
  - `name`, `shape` (list), `datatype` `"FP32"`
  - `data`: flattened `tensor.astype(np.float32).tolist()`

### KSRV-001-R2: JSON decode (`decode_kserve_json`)

- Input: KServe v2 response dict
- Output: `np.ndarray` reshaped to `outputs[0].shape`, dtype `float32`
- Uses first output tensor only

### KSRV-001-R3: Binary encode (`encode_kserve_binary`)

- Input: `input_name`, `tensor`, `output_name`
- Tensor bytes: `tensor.astype(np.float32).tobytes(order="C")`
- Metadata JSON includes `parameters.binary_data_size` on input and `parameters.binary_data: true` on output
- Returns `(headers, body)` where:
  - `headers["Content-Type"]` = `application/octet-stream`
  - `headers["Inference-Header-Content-Length"]` = UTF-8 metadata byte length
  - `headers["Content-Length"]` = metadata length + tensor byte length
  - `body` = metadata bytes concatenated with tensor bytes

### KSRV-001-R4: Binary decode (`decode_kserve_binary`)

- Input: full response `body` (bytes), `header_length` (int)
- Parse metadata JSON from `body[:header_length]`
- Read `outputs[0].parameters.binary_data_offset` (default `header_length`) and `binary_data_size`
- Return `np.frombuffer(..., dtype=float32).reshape(shape)`

### KSRV-001-R5: Environment and tolerance

| Variable                  | Default | Effect                                                         |
| ------------------------- | ------- | -------------------------------------------------------------- |
| `KSERVE_PREFER_BINARY`    | `true`  | Module-level flag; `kserve_infer` tries binary first when true |
| `KSERVE_BINARY_TOLERANCE` | `1e-4`  | Reserved for round-trip float comparisons in tests             |

### KSRV-001-R6: `kserve_infer` protocol selection

1. When `prefer_binary` is true (default from env), POST octet-stream body with KSRV-001-R3 headers
2. On HTTP 200 with `Content-Type` containing `octet-stream`, decode via KSRV-001-R4
3. On binary failure (non-200, wrong content type, parse error), fall back to JSON encode/decode
4. Non-200 JSON response raises `aiohttp.ClientResponseError`

## Acceptance criteria

- [x] Both `backend/` and `backend-detection/` modules implement identical encode/decode helpers
- [x] JSON infer passes on cluster for both predictors — `binary-kserve-v2.md`
- [x] Binary infer fails HTTP 500 on cluster @ ea.1 — documented waiver; JSON fallback active
- [ ] `test_encode_kserve_json_shape_and_dtype` — shape list and FP32 datatype (MT-W12)
- [ ] `test_decode_kserve_json_roundtrip` — encode → decode preserves values within tolerance (MT-W12)
- [ ] `test_encode_kserve_binary_header_length` — `Inference-Header-Content-Length` matches metadata size (MT-W12)
- [ ] `test_encode_kserve_binary_body_size` — `Content-Length` = header + tensor bytes (MT-W12)
- [ ] `test_decode_kserve_binary_roundtrip` — local encode/decode parity (MT-W12; fixes `baseline-smoke.md` L66 overclaim)
