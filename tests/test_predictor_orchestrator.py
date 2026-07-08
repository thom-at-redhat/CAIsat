# Tests for predictor_orchestrator.py
# Assisted by: cursor, claude

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_orchestrator():
    path = REPO_ROOT / "backend" / "predictor_orchestrator.py"
    spec = importlib.util.spec_from_file_location("predictor_orchestrator", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ensure_predictor_active_noop_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator = _load_orchestrator()
    monkeypatch.delenv("GPU_EXCLUSIVE_MODE", raising=False)

    async def fail_if_called(*_args, **_kwargs):
        raise AssertionError("orchestrator should not call Kubernetes when disabled")

    monkeypatch.setattr(orchestrator, "_scale_deployment", fail_if_called)

    asyncio.run(orchestrator.ensure_predictor_active("swinir"))


def test_ready_timeout_defaults_when_env_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator = _load_orchestrator()
    monkeypatch.setenv("PREDICTOR_READY_TIMEOUT_SECONDS", "")
    assert orchestrator._ready_timeout() == 300.0


def test_gpu_exclusive_enabled_parses_truthy(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator = _load_orchestrator()
    monkeypatch.setenv("GPU_EXCLUSIVE_MODE", "true")
    assert orchestrator.gpu_exclusive_enabled() is True
    monkeypatch.setenv("GPU_EXCLUSIVE_MODE", "0")
    assert orchestrator.gpu_exclusive_enabled() is False
