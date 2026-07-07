# Compute profile and /api/capabilities helpers.
# Assisted by: cursor, claude

from __future__ import annotations

import os
from typing import Any

DEFAULT_CROP = 256

PROFILE_LIMITS: dict[str, dict[str, Any]] = {
    "cpu": {
        "gpu_tier": "cpu",
        "max_crop": 256,
        "max_tile": 256,
        "tiling_enabled": False,
        "scale_factor": 4,
        "infer_timeout_seconds": 60,
    },
    "t4": {
        "gpu_tier": "t4",
        "max_crop": 512,
        "max_tile": 512,
        "tiling_enabled": True,
        "scale_factor": 4,
        "infer_timeout_seconds": 60,
    },
    "l40s": {
        "gpu_tier": "l40s",
        "max_crop": 768,
        "max_tile": 512,
        "tiling_enabled": True,
        "scale_factor": 4,
        "infer_timeout_seconds": 60,
    },
    "hopper": {
        "gpu_tier": "hopper",
        "max_crop": 1024,
        "max_tile": 512,
        "tiling_enabled": True,
        "scale_factor": 4,
        "infer_timeout_seconds": 60,
    },
}

DEFERRED_GPU_CAP = {
    "max_crop": 256,
    "max_tile": 256,
    "tiling_enabled": False,
}

CPU_INFERENCE_GPU_CAP = {
    "max_crop": 512,
    "max_tile": 512,
    "tiling_enabled": True,
}


def get_capabilities() -> dict[str, Any]:
    profile = os.getenv("COMPUTE_PROFILE", "cpu").lower()
    gpu_available = os.getenv("GPU_AVAILABLE", "false").lower() in ("1", "true", "yes")
    inference_accelerator = os.getenv("INFERENCE_ACCELERATOR", "cpu").lower()
    base = dict(PROFILE_LIMITS.get(profile, PROFILE_LIMITS["cpu"]))
    base["profile"] = profile
    base["default_crop"] = DEFAULT_CROP
    base["inference_accelerator"] = inference_accelerator

    if profile != "cpu" and not gpu_available:
        base.update(DEFERRED_GPU_CAP)
        base["gpu_deferred"] = True
        base["gpu_tier"] = profile
    else:
        base["gpu_deferred"] = False
        if profile != "cpu" and inference_accelerator != "gpu":
            for key, value in CPU_INFERENCE_GPU_CAP.items():
                if key == "max_crop":
                    base[key] = min(int(base[key]), int(value))
                else:
                    base[key] = value

    base["kserve_prefer_binary"] = os.getenv("KSERVE_PREFER_BINARY", "true").lower() in ("1", "true", "yes")
    return base
