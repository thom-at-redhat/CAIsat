# Tests for detect_jobs.py (backend-detection)
# Assisted by: cursor, claude

from __future__ import annotations

import asyncio
import importlib.util
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_detect_jobs():
    path = REPO_ROOT / "backend-detection" / "detect_jobs.py"
    spec = importlib.util.spec_from_file_location("detect_jobs", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_create_job_completes_successfully() -> None:
    module = _load_detect_jobs()

    async def runner() -> None:
        async def work() -> dict:
            await asyncio.sleep(0.01)
            return {"detections": [], "count": 0}

        job_id = await module.create_job(work)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            job = module.get_job(job_id)
            assert job is not None
            if job.status == "complete":
                assert job.result == {"detections": [], "count": 0}
                return
            await asyncio.sleep(0.05)
        raise AssertionError("job did not complete")

    asyncio.run(runner())


def test_create_job_records_error() -> None:
    module = _load_detect_jobs()

    async def runner() -> None:
        async def work() -> dict:
            raise RuntimeError("boom")

        job_id = await module.create_job(work)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            job = module.get_job(job_id)
            assert job is not None
            if job.status == "error":
                assert job.error == "boom"
                return
            await asyncio.sleep(0.05)
        raise AssertionError("job did not fail")

    asyncio.run(runner())
