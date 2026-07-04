# KServe v2 JSON and binary tensor helpers.
# Assisted by: cursor, claude

from __future__ import annotations

import json
import os
from typing import Any

import aiohttp
import numpy as np

KSERVE_PREFER_BINARY = os.getenv("KSERVE_PREFER_BINARY", "true").lower() in ("1", "true", "yes")
KSERVE_BINARY_TOLERANCE = float(os.getenv("KSERVE_BINARY_TOLERANCE", "1e-4"))


def encode_kserve_json(input_name: str, tensor: np.ndarray) -> dict[str, Any]:
    """Build a KServe v2 JSON infer request."""
    return {
        "inputs": [
            {
                "name": input_name,
                "shape": list(tensor.shape),
                "datatype": "FP32",
                "data": tensor.astype(np.float32).flatten().tolist(),
            }
        ]
    }


def decode_kserve_json(response: dict[str, Any]) -> np.ndarray:
    """Decode the first output tensor from a KServe v2 JSON response."""
    output = response["outputs"][0]
    return np.array(output["data"], dtype=np.float32).reshape(output["shape"])


def encode_kserve_binary(
    input_name: str,
    tensor: np.ndarray,
    output_name: str,
) -> tuple[dict[str, str], bytes]:
    """Build KServe v2 binary extension request (octet-stream body)."""
    tensor_bytes = tensor.astype(np.float32).tobytes(order="C")
    meta = {
        "inputs": [
            {
                "name": input_name,
                "shape": list(tensor.shape),
                "datatype": "FP32",
                "parameters": {"binary_data_size": len(tensor_bytes)},
            }
        ],
        "outputs": [{"name": output_name, "parameters": {"binary_data": True}}],
    }
    meta_bytes = json.dumps(meta).encode("utf-8")
    headers = {
        "Content-Type": "application/octet-stream",
        "Inference-Header-Content-Length": str(len(meta_bytes)),
        "Content-Length": str(len(meta_bytes) + len(tensor_bytes)),
    }
    return headers, meta_bytes + tensor_bytes


def decode_kserve_binary(body: bytes, header_length: int) -> np.ndarray:
    """Decode the first binary output tensor from an octet-stream response."""
    meta = json.loads(body[:header_length].decode("utf-8"))
    if not isinstance(meta, dict):
        raise ValueError("KServe binary header must be a JSON object")
    outputs = meta.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("KServe binary header must contain a non-empty outputs array")
    output_meta = outputs[0]
    if not isinstance(output_meta, dict):
        raise ValueError("KServe binary output metadata must be a JSON object")
    offset = int(output_meta.get("parameters", {}).get("binary_data_offset", header_length))
    size = int(output_meta["parameters"]["binary_data_size"])
    shape = output_meta["shape"]
    return np.frombuffer(body[offset : offset + size], dtype=np.float32).reshape(shape)


async def kserve_infer(
    session: aiohttp.ClientSession,
    url: str,
    tensor: np.ndarray,
    *,
    input_name: str,
    output_name: str,
    timeout_seconds: float = 60,
    prefer_binary: bool | None = None,
) -> tuple[np.ndarray, str]:
    """Run KServe v2 infer; try binary first when enabled, fall back to JSON."""
    use_binary = KSERVE_PREFER_BINARY if prefer_binary is None else prefer_binary
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    if use_binary:
        try:
            headers, body = encode_kserve_binary(input_name, tensor, output_name)
            async with session.post(url, data=body, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "")
                    raw = await response.read()
                    if "octet-stream" in content_type:
                        header_len = int(response.headers.get("Inference-Header-Content-Length", 0))
                        return decode_kserve_binary(raw, header_len), "binary"
                    result = json.loads(raw.decode("utf-8"))
                    return decode_kserve_json(result), "binary"
        except (aiohttp.ClientError, json.JSONDecodeError, KeyError, ValueError, TypeError, IndexError):
            pass

    payload = encode_kserve_json(input_name, tensor)
    async with session.post(url, json=payload, timeout=timeout) as response:
        if response.status != 200:
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                status=response.status,
                message=await response.text(),
            )
        result = await response.json()
    return decode_kserve_json(result), "json"


def sanitize_model_error(status: int, raw_body: str) -> str:
    """Return a client-safe model error message without leaking stack traces."""
    if status >= 500:
        return "Model inference failed (upstream error)"
    if status == 408 or "timeout" in raw_body.lower():
        return "Model inference timed out"
    return "Model inference failed"
