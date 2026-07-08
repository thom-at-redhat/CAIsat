# In-memory async enhance jobs to avoid long-lived HTTP connections through route/LB idle timeouts.
# Assisted by: cursor, claude

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any
from collections.abc import Awaitable, Callable

JOB_TTL_SECONDS = 3600.0


@dataclass
class EnhanceJob:
    job_id: str
    status: str
    created_at: float
    result: dict[str, Any] | None = None
    error: str | None = None


_jobs: dict[str, EnhanceJob] = {}
_lock = asyncio.Lock()


def _prune_old_jobs() -> None:
    cutoff = time.time() - JOB_TTL_SECONDS
    stale = [job_id for job_id, job in _jobs.items() if job.created_at < cutoff]
    for job_id in stale:
        _jobs.pop(job_id, None)


async def create_job(work: Callable[[], Awaitable[dict[str, Any]]]) -> str:
    job_id = uuid.uuid4().hex
    job = EnhanceJob(job_id=job_id, status="pending", created_at=time.time())
    async with _lock:
        _prune_old_jobs()
        _jobs[job_id] = job
    asyncio.create_task(_run_job(job, work))
    return job_id


async def _run_job(job: EnhanceJob, work: Callable[[], Awaitable[dict[str, Any]]]) -> None:
    job.status = "processing"
    try:
        job.result = await work()
        job.status = "complete"
    except Exception as exc:
        job.status = "error"
        job.error = str(exc)


def get_job(job_id: str) -> EnhanceJob | None:
    return _jobs.get(job_id)
