# Shared pytest fixtures for backend and backend-detection modules.
# Assisted by: cursor, claude

from __future__ import annotations

import importlib
import importlib.util
import io
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent

BACKEND_DIRS = [
    pytest.param("backend", id="enhance"),
    pytest.param("backend-detection", id="detection"),
]

_ENV_KEYS = ("COMPUTE_PROFILE", "GPU_AVAILABLE", "KSERVE_PREFER_BINARY")


def _import_from_backend(backend_dir: str, module_name: str):
    path = REPO_ROOT / backend_dir / f"{module_name}.py"
    unique_name = f"caisat_{backend_dir.replace('-', '_')}_{module_name}"
    spec = importlib.util.spec_from_file_location(unique_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=BACKEND_DIRS)
def backend_dir(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def kserve_v2(backend_dir: str):
    return _import_from_backend(backend_dir, "kserve_v2")


@pytest.fixture
def capabilities(backend_dir: str):
    return _import_from_backend(backend_dir, "capabilities")


@pytest.fixture
def clear_profile_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _drop_backend_modules(backend_path: Path) -> None:
    resolved = backend_path.resolve()
    to_drop = [name for name, mod in list(sys.modules.items()) if (mod_file := getattr(mod, "__file__", None)) is not None and resolved in Path(mod_file).resolve().parents]
    for name in to_drop:
        sys.modules.pop(name, None)


def import_app_module(monkeypatch: pytest.MonkeyPatch, backend_dir: str):
    """Import backend ``app`` after MODEL_ENDPOINT is set (required at import time)."""
    monkeypatch.setenv(
        "MODEL_ENDPOINT",
        "http://test-predictor.example:8080/v2/models/test/infer",
    )
    backend_path = REPO_ROOT / backend_dir
    path_str = str(backend_path.resolve())
    for dir_name in ("backend", "backend-detection"):
        _drop_backend_modules(REPO_ROOT / dir_name)
    sys.modules.pop("app", None)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    elif sys.path[0] != path_str:
        sys.path.remove(path_str)
        sys.path.insert(0, path_str)
    return importlib.import_module("app")


@pytest.fixture
def enhance_app(monkeypatch: pytest.MonkeyPatch):
    return import_app_module(monkeypatch, "backend")


@pytest.fixture
def detection_app(monkeypatch: pytest.MonkeyPatch):
    return import_app_module(monkeypatch, "backend-detection")


def tiny_png_bytes(size: tuple[int, int] = (64, 64)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color=(100, 150, 200)).save(buf, format="PNG")
    return buf.getvalue()
