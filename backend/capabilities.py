# Compute profile and /api/capabilities helpers.
# Assisted by: cursor, claude

from __future__ import annotations

import os
from typing import Any

# Per-tier limits; deferred tiers use conservative caps (Phase 15 plan).
PROFILE_LIMITS: dict[str, dict[str, Any]] = {
    "cpu": {
        "gpu_tier": "cpu",
        "max_crop": 256,
        "max_tile": 256,
        "tiling_enabled": False,
        "scale_factor": 4,
        "infer_timeout_seconds": 300,
    },
    "t4": {
        "gpu_tier": "t4",
        "max_crop": 512,
        "max_tile": 512,
        "tiling_enabled": True,
        "scale_factor": 4,
        "infer_timeout_seconds": 300,
    },
    "l40s": {
        "gpu_tier": "l40s",
        "max_crop": 768,
        "max_tile": 512,
        "tiling_enabled": True,
        "scale_factor": 4,
        "infer_timeout_seconds": 300,
    },
    "hopper": {
        "gpu_tier": "hopper",
        "max_crop": 1024,
        "max_tile": 512,
        "tiling_enabled": True,
        "scale_factor": 4,
        "infer_timeout_seconds": 300,
    },
}

# When a GPU tier is deferred/unavailable, cap to CPU limits.
DEFERRED_GPU_CAP = {
    "max_crop": 256,
    "max_tile": 256,
    "tiling_enabled": False,
}


def get_capabilities() -> dict[str, Any]:
    """Return runtime capabilities for the active compute profile."""
    profile = os.getenv("COMPUTE_PROFILE", "cpu").lower()
    gpu_available = os.getenv("GPU_AVAILABLE", "false").lower() in ("1", "true", "yes")
    base = dict(PROFILE_LIMITS.get(profile, PROFILE_LIMITS["cpu"]))
    base["profile"] = profile

    if profile != "cpu" and not gpu_available:
        base.update(DEFERRED_GPU_CAP)
        base["gpu_deferred"] = True
        base["gpu_tier"] = profile
    else:
        base["gpu_deferred"] = False

    base["kserve_prefer_binary"] = os.getenv("KSERVE_PREFER_BINARY", "true").lower() in ("1", "true", "yes")
    return base
