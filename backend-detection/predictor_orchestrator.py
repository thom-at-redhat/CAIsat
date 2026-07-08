# Scale KServe predictor Deployments for single-GPU exclusive mode.
# Assisted by: cursor, claude

from __future__ import annotations

import asyncio
import os
import ssl
import time
from typing import Any

import aiohttp

SA_DIR = "/var/run/secrets/kubernetes.io/serviceaccount"
K8S_API = "https://kubernetes.default.svc"
POLL_INTERVAL_SECONDS = 2.0


def gpu_exclusive_enabled() -> bool:
    return os.getenv("GPU_EXCLUSIVE_MODE", "false").lower() in ("1", "true", "yes")


def _namespace() -> str:
    return os.getenv("PREDICTOR_NAMESPACE", "caisat")


def _ready_timeout() -> float:
    return float(os.getenv("PREDICTOR_READY_TIMEOUT_SECONDS", "300"))


def _predictor_config() -> dict[str, dict[str, str]]:
    namespace = _namespace()
    swinir_name = os.getenv("SWINIR_MODEL_NAME", "swinir")
    yolo_name = os.getenv("YOLO_MODEL_NAME", "yolov8m-satelite")
    swinir_deploy = os.getenv("SWINIR_DEPLOYMENT", "swinir-predictor")
    yolo_deploy = os.getenv("YOLO_DEPLOYMENT", "yolov8m-satelite-predictor")
    sentinel_deploy = os.getenv("SENTINEL2_DEPLOYMENT", "sentinel2-model-predictor")
    port = os.getenv("PREDICTOR_PORT", "8080")
    svc_suffix = f".{namespace}.svc.cluster.local:{port}"

    def ready_url(model_name: str, service_stem: str) -> str:
        return f"http://{service_stem}{svc_suffix}/v2/models/{model_name}/ready"

    return {
        "swinir": {
            "deployment": swinir_deploy,
            "ready_url": ready_url(swinir_name, f"{swinir_deploy}"),
            "peers": [yolo_deploy, sentinel_deploy],
        },
        "yolo": {
            "deployment": yolo_deploy,
            "ready_url": ready_url(yolo_name, f"{yolo_deploy}"),
            "peers": [swinir_deploy, sentinel_deploy],
        },
    }


def _k8s_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=f"{SA_DIR}/ca.crt")
    return ctx


def _k8s_headers() -> dict[str, str]:
    with open(f"{SA_DIR}/token", encoding="utf-8") as token_file:
        token = token_file.read().strip()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/strategic-merge-patch+json"}


async def _scale_deployment(k8s_session: aiohttp.ClientSession, deployment: str, replicas: int) -> None:
    namespace = _namespace()
    url = f"{K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}/scale"
    async with k8s_session.patch(url, json={"spec": {"replicas": replicas}}) as response:
        if response.status not in (200, 201):
            body = await response.text()
            raise RuntimeError(f"scale {deployment} -> {replicas} failed ({response.status}): {body}")


async def _deployment_available(k8s_session: aiohttp.ClientSession, deployment: str) -> bool:
    namespace = _namespace()
    url = f"{K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    async with k8s_session.get(url) as response:
        if response.status != 200:
            return False
        payload: dict[str, Any] = await response.json()
    status = payload.get("status") or {}
    desired = payload.get("spec", {}).get("replicas", 0)
    available = status.get("availableReplicas") or 0
    if desired == 0:
        return available == 0
    return available >= 1


async def _wait_deployment(k8s_session: aiohttp.ClientSession, deployment: str) -> None:
    deadline = time.monotonic() + _ready_timeout()
    while time.monotonic() < deadline:
        if await _deployment_available(k8s_session, deployment):
            return
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(f"deployment {deployment} not ready within {_ready_timeout():.0f}s")


async def _wait_predictor_ready(http_session: aiohttp.ClientSession, ready_url: str) -> None:
    deadline = time.monotonic() + _ready_timeout()
    while time.monotonic() < deadline:
        try:
            async with http_session.get(ready_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    return
        except (aiohttp.ClientError, TimeoutError):
            pass
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(f"predictor not ready at {ready_url} within {_ready_timeout():.0f}s")


async def ensure_predictor_active(
    predictor: str,
    *,
    k8s_session: aiohttp.ClientSession | None = None,
    http_session: aiohttp.ClientSession | None = None,
) -> None:
    """Scale peer predictors to 0, target to 1, and wait until the model /ready succeeds."""
    if not gpu_exclusive_enabled():
        return

    config = _predictor_config().get(predictor)
    if config is None:
        raise ValueError(f"unknown predictor {predictor!r}")

    owns_k8s = k8s_session is None
    owns_http = http_session is None
    if k8s_session is None:
        connector = aiohttp.TCPConnector(ssl=_k8s_ssl_context())
        k8s_session = aiohttp.ClientSession(connector=connector, headers=_k8s_headers())
    if http_session is None:
        http_session = aiohttp.ClientSession()

    try:
        for peer in config["peers"]:
            await _scale_deployment(k8s_session, peer, 0)
            await _wait_deployment(k8s_session, peer)
        await _scale_deployment(k8s_session, config["deployment"], 1)
        await _wait_deployment(k8s_session, config["deployment"])
        await _wait_predictor_ready(http_session, config["ready_url"])
    finally:
        if owns_k8s:
            await k8s_session.close()
        if owns_http:
            await http_session.close()
