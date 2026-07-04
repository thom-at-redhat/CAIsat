#!/usr/bin/env python3
# Atheris fuzz target for decode_kserve_binary (KServe v2 octet-stream response).
# Assisted by: cursor, claude

from __future__ import annotations

import json
import sys

import atheris
import numpy as np


def decode_kserve_binary(body: bytes, header_length: int) -> np.ndarray:
    """Decode the first binary output tensor from an octet-stream response.

    Keep in sync with backend/kserve_v2.py::decode_kserve_binary (PyInstaller cannot load that module at runtime).
    """
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


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    header_length = fdp.ConsumeIntInRange(0, 8192)
    body = fdp.ConsumeBytes(fdp.remaining_bytes())
    try:
        decode_kserve_binary(body, header_length)
    except (json.JSONDecodeError, KeyError, ValueError):
        pass


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
