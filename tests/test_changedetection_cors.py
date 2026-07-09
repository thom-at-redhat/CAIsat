# Change-detection backend CORS — Brazil user report / PR #155 regression guard.
# Assisted by: cursor, claude

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent


def _import_changedetection_app(monkeypatch: pytest.MonkeyPatch, cors_origins: str):
    monkeypatch.setenv("S3_ENDPOINT", "http://127.0.0.1:7480")
    monkeypatch.setenv("S3_ACCESS_KEY", "test-key")
    monkeypatch.setenv("S3_SECRET_KEY", "test-secret")
    monkeypatch.setenv("S3_BUCKET", "satellite-images")
    monkeypatch.setenv("CORS_ORIGINS", cors_origins)

    backend_path = REPO_ROOT / "backend-changedetection"
    path_str = str(backend_path.resolve())
    for name in list(sys.modules):
        mod = sys.modules.get(name)
        mod_file = getattr(mod, "__file__", None)
        if mod_file is not None and backend_path.resolve() in Path(mod_file).resolve().parents:
            sys.modules.pop(name, None)
    if path_str in sys.path:
        sys.path.remove(path_str)
    sys.path.insert(0, path_str)

    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": []}

    with patch("boto3.client", return_value=mock_s3):
        spec = importlib.util.spec_from_file_location("caisat_changedetection_app", backend_path / "app.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


@pytest.fixture
def changedetection_client(monkeypatch: pytest.MonkeyPatch):
    origin = "https://caisat-caisat.apps.qualitycustomer-pool-tv8j5.aws.rh-ods.com"
    module = _import_changedetection_app(monkeypatch, origin)
    return TestClient(module.app), origin


def test_changedetection_get_health_cors_echoes_origin(changedetection_client) -> None:
    client, origin = changedetection_client
    response = client.get("/health", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"
    acao = response.headers.get("access-control-allow-origin")
    acac = response.headers.get("access-control-allow-credentials")
    assert not (acao == "*" and acac == "true")


def test_changedetection_options_preflight(changedetection_client) -> None:
    client, origin = changedetection_client
    response = client.options(
        "/api/areas",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "GET" in allow_methods


def test_changedetection_default_wildcard_cors_not_invalid_pair(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default CORS_ORIGINS=* must not emit ACAO * with credentials (browser-blocked)."""
    origin = "https://caisat-caisat.apps.example.com"
    module = _import_changedetection_app(monkeypatch, "*")
    client = TestClient(module.app)
    response = client.get("/health", headers={"Origin": origin})
    acao = response.headers.get("access-control-allow-origin")
    acac = response.headers.get("access-control-allow-credentials")
    assert not (acao == "*" and acac == "true")
