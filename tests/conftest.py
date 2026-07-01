# Shared pytest fixtures for backend and backend-detection modules.
# Assisted by: cursor, claude

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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
