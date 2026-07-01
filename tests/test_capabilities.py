# /api/capabilities unit tests — spec: docs/specs/capabilities-api.md (MT-W13).
# Assisted by: cursor, claude

from __future__ import annotations

import pytest


def test_cpu_profile_defaults(capabilities, backend_dir: str, clear_profile_env) -> None:
    caps = capabilities.get_capabilities()
    assert caps["profile"] == "cpu"
    assert caps["gpu_tier"] == "cpu"
    assert caps["max_crop"] == 256
    assert caps["max_tile"] == 256
    assert caps["tiling_enabled"] is False
    assert caps["scale_factor"] == 4
    assert caps["gpu_deferred"] is False
    assert caps["kserve_prefer_binary"] is True
    if backend_dir == "backend":
        assert caps["infer_timeout_seconds"] == 300
    else:
        assert caps["infer_timeout_seconds"] == 60


def test_gpu_deferred_caps_to_cpu(capabilities, clear_profile_env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMPUTE_PROFILE", "hopper")
    monkeypatch.setenv("GPU_AVAILABLE", "false")
    caps = capabilities.get_capabilities()
    assert caps["profile"] == "hopper"
    assert caps["gpu_tier"] == "hopper"
    assert caps["gpu_deferred"] is True
    assert caps["max_crop"] == 256
    assert caps["max_tile"] == 256
    assert caps["tiling_enabled"] is False


def test_gpu_available_uses_tier_limits(capabilities, clear_profile_env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMPUTE_PROFILE", "hopper")
    monkeypatch.setenv("GPU_AVAILABLE", "true")
    caps = capabilities.get_capabilities()
    assert caps["profile"] == "hopper"
    assert caps["gpu_tier"] == "hopper"
    assert caps["gpu_deferred"] is False
    assert caps["max_crop"] == 1024
    assert caps["max_tile"] == 512
    assert caps["tiling_enabled"] is True


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
    ],
)
def test_kserve_prefer_binary_env(
    capabilities,
    clear_profile_env,
    monkeypatch: pytest.MonkeyPatch,
    env_value: str,
    expected: bool,
) -> None:
    monkeypatch.setenv("KSERVE_PREFER_BINARY", env_value)
    caps = capabilities.get_capabilities()
    assert caps["kserve_prefer_binary"] is expected
