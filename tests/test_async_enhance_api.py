# Async enhance jobs API — FastAPI TestClient (ENH-001)
# Assisted by: cursor, claude

from __future__ import annotations

import time

from fastapi import HTTPException
from fastapi.testclient import TestClient

from conftest import tiny_png_bytes


def _poll_until_terminal(client: TestClient, job_id: str, *, timeout_s: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        response = client.get(f"/api/enhance/jobs/{job_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in ("complete", "error"):
            return payload
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not reach terminal state")


def test_create_enhance_job_polls_complete(enhance_app, monkeypatch) -> None:
    async def mock_upload(_contents: bytes) -> dict:
        return {
            "preview": "YWJj",
            "media_type": "image/jpeg",
            "width": 1024,
            "height": 1024,
            "preview_width": 512,
            "preview_height": 512,
        }

    monkeypatch.setattr(enhance_app, "_enhance_upload", mock_upload)
    client = TestClient(enhance_app.app)

    response = client.post(
        "/api/enhance/jobs",
        files={"image": ("test.png", tiny_png_bytes(), "image/png")},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert "job_id" in body

    payload = _poll_until_terminal(client, body["job_id"])
    assert payload["status"] == "complete"
    assert payload["preview"] == "YWJj"
    assert payload["media_type"] == "image/jpeg"
    assert payload["width"] == 1024


def test_create_enhance_job_records_error(enhance_app, monkeypatch) -> None:
    async def mock_upload(_contents: bytes) -> dict:
        raise HTTPException(status_code=413, detail="Crop too large")

    monkeypatch.setattr(enhance_app, "_enhance_upload", mock_upload)
    client = TestClient(enhance_app.app)

    response = client.post(
        "/api/enhance/jobs",
        files={"image": ("test.png", tiny_png_bytes(), "image/png")},
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    payload = _poll_until_terminal(client, job_id)
    assert payload["status"] == "error"
    assert payload["error"] == "Crop too large"


def test_get_enhance_job_404(enhance_app) -> None:
    client = TestClient(enhance_app.app)
    response = client.get("/api/enhance/jobs/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Enhance job not found"
