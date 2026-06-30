"""
FastAPI backend for object detection in satellite imagery.

This service receives images from the frontend, preprocesses them for YOLOv8-OBB,
sends to the OpenShift AI model endpoint, and returns detected objects.
"""

# Assisted by: cursor, claude

from contextlib import asynccontextmanager
import io
import os
import traceback

import aiohttp
import cv2
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from kserve_v2 import kserve_infer, sanitize_model_error

load_dotenv()

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")
KSERVE_INPUT_NAME = os.getenv("KSERVE_INPUT_NAME", "images")
KSERVE_OUTPUT_NAME = os.getenv("KSERVE_OUTPUT_NAME", "output0")

if not MODEL_ENDPOINT:
    raise ValueError("MODEL_ENDPOINT environment variable must be set. Example: http://<predictor>.<namespace>.svc.cluster.local:8080/v2/models/<model-name>/infer")

http_session: aiohttp.ClientSession | None = None
detection_counter = 0

CLASS_NAMES = [
    "plane",
    "ship",
    "storage-tank",
    "baseball-diamond",
    "tennis-court",
    "basketball-court",
    "ground-track-field",
    "harbor",
    "bridge",
    "large-vehicle",
    "small-vehicle",
    "helicopter",
    "roundabout",
    "soccer-ball-field",
    "swimming-pool",
]

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_session
    http_session = aiohttp.ClientSession()
    yield
    if http_session is not None:
        await http_session.close()
        http_session = None


app = FastAPI(title="Satellite Object Detection API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def preprocess_image(image: Image.Image, input_size: int = 640) -> tuple[np.ndarray, float, tuple, tuple]:
    if image.mode != "RGB":
        image = image.convert("RGB")
    img_array = np.array(image)
    orig_h, orig_w = img_array.shape[:2]
    scale = min(input_size / orig_w, input_size / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    resized = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    padded = np.full((input_size, input_size, 3), 114, dtype=np.uint8)
    pad_w = (input_size - new_w) // 2
    pad_h = (input_size - new_h) // 2
    padded[pad_h : pad_h + new_h, pad_w : pad_w + new_w] = resized
    preprocessed = padded.astype(np.float32) / 255.0
    preprocessed = np.transpose(preprocessed, (2, 0, 1))
    preprocessed = np.expand_dims(preprocessed, axis=0)
    return preprocessed, scale, (pad_w, pad_h), (orig_w, orig_h)


def non_max_suppression(
    boxes: np.ndarray,
    scores: np.ndarray,
    classes: np.ndarray,
    iou_threshold: float = 0.45,
) -> tuple:
    if len(boxes) == 0:
        return np.array([]), np.array([]), np.array([])
    indices = cv2.dnn.NMSBoxes(
        boxes.tolist(),
        scores.tolist(),
        score_threshold=CONFIDENCE_THRESHOLD,
        nms_threshold=iou_threshold,
    )
    if len(indices) > 0:
        indices = indices.flatten()
        return boxes[indices], scores[indices], classes[indices]
    return np.array([]), np.array([]), np.array([])


def postprocess_yolov8_obb(
    output_array: np.ndarray,
    scale: float,
    padding: tuple,
    original_shape: tuple,
    conf_threshold: float = 0.5,
    iou_threshold: float = 0.45,
) -> list[dict]:
    output = output_array.squeeze(0).T
    boxes_cxcywh = output[:, :4]
    class_scores = output[:, 4:19]
    max_scores = np.max(class_scores, axis=1)
    class_ids = np.argmax(class_scores, axis=1)
    mask = max_scores > conf_threshold
    boxes_cxcywh = boxes_cxcywh[mask]
    scores = max_scores[mask]
    class_ids = class_ids[mask]
    if len(boxes_cxcywh) == 0:
        return []
    x1 = boxes_cxcywh[:, 0] - boxes_cxcywh[:, 2] / 2
    y1 = boxes_cxcywh[:, 1] - boxes_cxcywh[:, 3] / 2
    x2 = boxes_cxcywh[:, 0] + boxes_cxcywh[:, 2] / 2
    y2 = boxes_cxcywh[:, 1] + boxes_cxcywh[:, 3] / 2
    boxes_xyxy = np.stack([x1, y1, x2, y2], axis=1)
    boxes, scores, class_ids = non_max_suppression(boxes_xyxy, scores, class_ids, iou_threshold)
    if len(boxes) == 0:
        return []
    boxes = np.array(boxes)
    pad_w, pad_h = padding
    boxes[:, [0, 2]] = (boxes[:, [0, 2]] - pad_w) / scale
    boxes[:, [1, 3]] = (boxes[:, [1, 3]] - pad_h) / scale
    centers_x = (boxes[:, 0] + boxes[:, 2]) / 2
    centers_y = (boxes[:, 1] + boxes[:, 3]) / 2
    widths = boxes[:, 2] - boxes[:, 0]
    heights = boxes[:, 3] - boxes[:, 1]
    new_widths = heights
    new_heights = widths
    boxes[:, 0] = centers_x - new_widths / 2
    boxes[:, 1] = centers_y - new_heights / 2
    boxes[:, 2] = centers_x + new_widths / 2
    boxes[:, 3] = centers_y + new_heights / 2
    orig_w, orig_h = original_shape
    boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, orig_w)
    boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, orig_h)
    detections = []
    for i in range(len(boxes)):
        box = boxes[i]
        class_id = int(class_ids[i])
        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f"Class {class_id}"
        detections.append(
            {
                "class": class_name,
                "confidence": float(scores[i]),
                "box": [float(box[0]), float(box[1]), float(box[2]), float(box[3])],
            }
        )
    detections.sort(key=lambda x: x["confidence"], reverse=True)
    return detections


@app.get("/")
async def root():
    return {
        "service": "Satellite Object Detection API",
        "status": "operational",
        "classes": CLASS_NAMES,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/stats")
async def get_stats():
    return {
        "total_detections": detection_counter,
        "status": "operational",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "classes": len(CLASS_NAMES),
    }


@app.post("/api/detect")
async def detect_objects(image: UploadFile = File(...)):
    global detection_counter

    if http_session is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        contents = await image.read()
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"Upload exceeds {MAX_UPLOAD_BYTES} byte limit")

        img = Image.open(io.BytesIO(contents))
        tensor, scale, padding, original_shape = preprocess_image(img)

        try:
            output_tensor, protocol = await kserve_infer(
                http_session,
                MODEL_ENDPOINT,
                tensor,
                input_name=KSERVE_INPUT_NAME,
                output_name=KSERVE_OUTPUT_NAME,
                timeout_seconds=60,
            )
        except aiohttp.ClientResponseError as exc:
            print(f"Model endpoint error ({exc.status}): {exc.message}")
            raise HTTPException(
                status_code=502,
                detail=sanitize_model_error(exc.status, exc.message or ""),
            ) from exc

        print(f"Inference completed via {protocol} protocol")
        detections = postprocess_yolov8_obb(
            output_tensor,
            scale,
            padding,
            original_shape,
            conf_threshold=CONFIDENCE_THRESHOLD,
            iou_threshold=IOU_THRESHOLD,
        )
        detection_counter += 1
        return JSONResponse(
            content={
                "detections": detections,
                "count": len(detections),
                "image_size": {"width": original_shape[0], "height": original_shape[1]},
            }
        )

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Error processing image: {type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Object detection failed") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
