# Async detect jobs API — FastAPI TestClient (ENH-001)
# Assisted by: cursor, claude

from __future__ import annotations

import time

from fastapi import HTTPException
from fastapi.testclient import TestClient

from conftest import tiny_png_bytes


def _poll_until_terminal(client: TestClient, job_id: str, *, timeout_s: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        response = client.get(f"/api/detect/jobs/{job_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in ("complete", "error"):
            return payload
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not reach terminal state")


def test_create_detect_job_polls_complete(detection_app, monkeypatch) -> None:
    async def mock_upload(_contents: bytes) -> dict:
        return {
            "detections": [{"class": "ship", "confidence": 0.9}],
            "count": 1,
            "image_size": {"width": 64, "height": 64},
            "sahi_slices": 1,
        }

    monkeypatch.setattr(detection_app, "_detect_upload", mock_upload)
    client = TestClient(detection_app.app)

    response = client.post(
        "/api/detect/jobs",
        files={"image": ("test.png", tiny_png_bytes(), "image/png")},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert "job_id" in body

    payload = _poll_until_terminal(client, body["job_id"])
    assert payload["status"] == "complete"
    assert payload["count"] == 1
    assert len(payload["detections"]) == 1


def test_create_detect_job_records_error(detection_app, monkeypatch) -> None:
    async def mock_upload(_contents: bytes) -> dict:
        raise HTTPException(status_code=413, detail="Upload exceeds limit")

    monkeypatch.setattr(detection_app, "_detect_upload", mock_upload)
    client = TestClient(detection_app.app)

    response = client.post(
        "/api/detect/jobs",
        files={"image": ("test.png", tiny_png_bytes(), "image/png")},
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    payload = _poll_until_terminal(client, job_id)
    assert payload["status"] == "error"
    assert payload["error"] == "Upload exceeds limit"


def test_get_detect_job_404(detection_app) -> None:
    client = TestClient(detection_app.app)
    response = client.get("/api/detect/jobs/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Detect job not found"
