# SAHI-style sliding window for large images.
# Assisted by: cursor, claude

from __future__ import annotations

from PIL import Image


def generate_slices(image: Image.Image, window: int = 640, overlap: float = 0.2) -> list[tuple[int, int, Image.Image]]:
    """Yield (offset_x, offset_y, crop) tiles covering the image."""
    w, h = image.size
    if w <= window and h <= window:
        return [(0, 0, image)]

    stride = max(1, int(window * (1 - overlap)))
    slices: list[tuple[int, int, Image.Image]] = []
    for y in range(0, max(h - window, 0) + 1, stride):
        for x in range(0, max(w - window, 0) + 1, stride):
            x2 = min(x + window, w)
            y2 = min(y + window, h)
            x1 = max(0, x2 - window)
            y1 = max(0, y2 - window)
            slices.append((x1, y1, image.crop((x1, y1, x2, y2))))
        if h <= window:
            break
    if not slices:
        slices.append((0, 0, image))
    return slices


def merge_detections(detections: list[dict], iou_threshold: float = 0.5) -> list[dict]:
    """Simple merge: keep highest-confidence box when axis-aligned IoU exceeds threshold."""
    if len(detections) <= 1:
        return detections

    def iou(a: list[float], b: list[float]) -> float:
        x1 = max(a[0], b[0])
        y1 = max(a[1], b[1])
        x2 = min(a[2], b[2])
        y2 = min(a[3], b[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    merged: list[dict] = []
    used = [False] * len(detections)
    order = sorted(range(len(detections)), key=lambda i: detections[i]["confidence"], reverse=True)
    for i in order:
        if used[i]:
            continue
        merged.append(detections[i])
        for j in order:
            if i == j or used[j]:
                continue
            if iou(detections[i]["box"], detections[j]["box"]) > iou_threshold:
                used[j] = True
    return merged


def offset_detection(det: dict, dx: int, dy: int) -> dict:
    """Shift box and OBB center by slice offset."""
    out = dict(det)
    out["box"] = [det["box"][0] + dx, det["box"][1] + dy, det["box"][2] + dx, det["box"][3] + dy]
    if "obb" in det:
        obb = list(det["obb"])
        obb[0] += dx
        obb[1] += dy
        out["obb"] = obb
    return out
