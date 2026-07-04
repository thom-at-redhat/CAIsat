# KServe v2 encode/decode unit tests — spec: docs/specs/kserve-v2-tensors.md (MT-W13).
# Assisted by: cursor, claude

from __future__ import annotations

import json

import numpy as np
import pytest


@pytest.fixture
def sample_tensor() -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.random((1, 3, 256, 256), dtype=np.float32)


def test_encode_kserve_json_shape_and_dtype(kserve_v2, sample_tensor: np.ndarray) -> None:
    payload = kserve_v2.encode_kserve_json("input", sample_tensor)
    assert payload["inputs"][0]["name"] == "input"
    assert payload["inputs"][0]["shape"] == list(sample_tensor.shape)
    assert payload["inputs"][0]["datatype"] == "FP32"
    assert len(payload["inputs"][0]["data"]) == sample_tensor.size


def test_decode_kserve_json_roundtrip(kserve_v2, sample_tensor: np.ndarray) -> None:
    response = {
        "outputs": [
            {
                "name": "output",
                "shape": list(sample_tensor.shape),
                "data": sample_tensor.flatten().tolist(),
            }
        ]
    }
    roundtrip = kserve_v2.decode_kserve_json(response)
    assert np.allclose(roundtrip, sample_tensor)


def test_encode_kserve_binary_header_length(kserve_v2, sample_tensor: np.ndarray) -> None:
    headers, body = kserve_v2.encode_kserve_binary("input", sample_tensor, "output")
    header_len = int(headers["Inference-Header-Content-Length"])
    assert header_len > 0
    meta = json.loads(body[:header_len].decode("utf-8"))
    assert meta["inputs"][0]["name"] == "input"
    assert headers["Content-Type"] == "application/octet-stream"


def test_encode_kserve_binary_body_size(kserve_v2, sample_tensor: np.ndarray) -> None:
    headers, body = kserve_v2.encode_kserve_binary("input", sample_tensor, "output")
    header_len = int(headers["Inference-Header-Content-Length"])
    tensor_bytes = sample_tensor.astype(np.float32).tobytes(order="C")
    assert len(body) == header_len + len(tensor_bytes)
    assert int(headers["Content-Length"]) == len(body)


@pytest.mark.parametrize(
    "body,header_length",
    [
        (b"0", 1),
        (b"[]", 2),
        (b'{"outputs": 0}', 14),
        (b'{"outputs": []}', 15),
        (b'{"outputs": [0]}', 16),
    ],
    ids=["scalar", "array", "outputs-not-list", "outputs-empty", "output-not-object"],
)
def test_decode_kserve_binary_rejects_non_object_header(
    kserve_v2,
    body: bytes,
    header_length: int,
) -> None:
    """Malformed binary headers raise ValueError (MT-SC31-HARDEN; fuzz spike Finding 1)."""
    with pytest.raises(ValueError, match="KServe binary"):
        kserve_v2.decode_kserve_binary(body, header_length)


def test_decode_kserve_binary_roundtrip(kserve_v2, sample_tensor: np.ndarray) -> None:
    """Round-trip binary response body (baseline-smoke L66 overclaim fix — risk #12)."""
    tensor_bytes = sample_tensor.astype(np.float32).tobytes(order="C")
    meta = {
        "outputs": [
            {
                "name": "output",
                "shape": list(sample_tensor.shape),
                "datatype": "FP32",
                "parameters": {"binary_data_size": len(tensor_bytes)},
            }
        ]
    }
    meta_bytes = json.dumps(meta).encode("utf-8")
    header_len = len(meta_bytes)
    body = meta_bytes + tensor_bytes
    decoded = kserve_v2.decode_kserve_binary(body, header_len)
    assert np.allclose(decoded, sample_tensor)
