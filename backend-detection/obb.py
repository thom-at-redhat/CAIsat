# YOLOv8-OBB decode helpers.
# Assisted by: cursor, claude

from __future__ import annotations

import cv2
import numpy as np


def decode_yolov8_obb(
    output_array: np.ndarray,
    scale: float,
    padding: tuple,
    original_shape: tuple,
    class_names: list[str],
    conf_threshold: float,
    iou_threshold: float,
) -> list[dict]:
    """Decode YOLOv8-OBB tensor including angle channel (index 19)."""
    output = output_array.squeeze(0).T
    boxes_cxcywh = output[:, :4]
    class_scores = output[:, 4:19]
    angles = output[:, 19]
    max_scores = np.max(class_scores, axis=1)
    class_ids = np.argmax(class_scores, axis=1)
    mask = max_scores > conf_threshold
    boxes_cxcywh = boxes_cxcywh[mask]
    scores = max_scores[mask]
    class_ids = class_ids[mask]
    angles = angles[mask]

    if len(boxes_cxcywh) == 0:
        return []

    x1 = boxes_cxcywh[:, 0] - boxes_cxcywh[:, 2] / 2
    y1 = boxes_cxcywh[:, 1] - boxes_cxcywh[:, 3] / 2
    x2 = boxes_cxcywh[:, 0] + boxes_cxcywh[:, 2] / 2
    y2 = boxes_cxcywh[:, 1] + boxes_cxcywh[:, 3] / 2
    boxes_xyxy = np.stack([x1, y1, x2, y2], axis=1)

    indices = cv2.dnn.NMSBoxes(
        boxes_xyxy.tolist(),
        scores.tolist(),
        score_threshold=conf_threshold,
        nms_threshold=iou_threshold,
    )
    if len(indices) == 0:
        return []

    indices = indices.flatten()
    pad_w, pad_h = padding
    orig_w, orig_h = original_shape
    detections = []

    for idx in indices:
        cx = float(boxes_cxcywh[idx, 0])
        cy = float(boxes_cxcywh[idx, 1])
        w = float(boxes_cxcywh[idx, 2])
        h = float(boxes_cxcywh[idx, 3])
        angle = float(angles[idx])
        cx = (cx - pad_w) / scale
        cy = (cy - pad_h) / scale
        w = w / scale
        h = h / scale
        x1o = max(0.0, cx - w / 2)
        y1o = max(0.0, cy - h / 2)
        x2o = min(float(orig_w), cx + w / 2)
        y2o = min(float(orig_h), cy + h / 2)
        class_id = int(class_ids[idx])
        class_name = class_names[class_id] if class_id < len(class_names) else f"Class {class_id}"
        detections.append(
            {
                "class": class_name,
                "confidence": float(scores[idx]),
                "box": [x1o, y1o, x2o, y2o],
                "obb": [cx, cy, w, h, angle],
            }
        )

    detections.sort(key=lambda x: x["confidence"], reverse=True)
    return detections
