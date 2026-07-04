#!/usr/bin/env python3
# Atheris fuzz target for decode_kserve_binary (KServe v2 octet-stream response).
# Assisted by: cursor, claude

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import atheris

REPO_ROOT = Path(__file__).resolve().parent.parent


def _import_decode_kserve_binary():
    """Load decode_kserve_binary from backend/kserve_v2.py (same path as tests/conftest.py)."""
    path = REPO_ROOT / "backend" / "kserve_v2.py"
    spec = importlib.util.spec_from_file_location("caisat_backend_kserve_v2_fuzz", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load kserve_v2 from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_kserve_binary


decode_kserve_binary = _import_decode_kserve_binary()


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
