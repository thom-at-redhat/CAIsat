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

from capabilities import get_capabilities
from kserve_v2 import kserve_infer, sanitize_model_error
from obb import decode_yolov8_obb
from sahi import generate_slices, merge_detections, offset_detection

load_dotenv()

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")
KSERVE_INPUT_NAME = os.getenv("KSERVE_INPUT_NAME", "images")
KSERVE_OUTPUT_NAME = os.getenv("KSERVE_OUTPUT_NAME", "output0")
SAHI_WINDOW = int(os.getenv("SAHI_WINDOW", "640"))
SAHI_OVERLAP = float(os.getenv("SAHI_OVERLAP", "0.2"))

if not MODEL_ENDPOINT:
    raise ValueError("MODEL_ENDPOINT environment variable must be set.")

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


async def infer_slice(slice_img: Image.Image) -> list[dict]:
    tensor, scale, padding, original_shape = preprocess_image(slice_img, SAHI_WINDOW)
    output_tensor, protocol = await kserve_infer(
        http_session,
        MODEL_ENDPOINT,
        tensor,
        input_name=KSERVE_INPUT_NAME,
        output_name=KSERVE_OUTPUT_NAME,
        timeout_seconds=120,
    )
    print(f"Slice inference via {protocol}")
    return decode_yolov8_obb(
        output_tensor,
        scale,
        padding,
        original_shape,
        CLASS_NAMES,
        CONFIDENCE_THRESHOLD,
        IOU_THRESHOLD,
    )


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


@app.get("/api/capabilities")
async def api_capabilities():
    return get_capabilities()


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
        all_detections: list[dict] = []

        try:
            for ox, oy, slice_img in generate_slices(img, window=SAHI_WINDOW, overlap=SAHI_OVERLAP):
                slice_dets = await infer_slice(slice_img)
                all_detections.extend(offset_detection(d, ox, oy) for d in slice_dets)
        except aiohttp.ClientResponseError as exc:
            print(f"Model endpoint error ({exc.status}): {exc.message}")
            raise HTTPException(
                status_code=502,
                detail=sanitize_model_error(exc.status, exc.message or ""),
            ) from exc

        detections = merge_detections(all_detections, iou_threshold=IOU_THRESHOLD)
        detection_counter += 1
        return JSONResponse(
            content={
                "detections": detections,
                "count": len(detections),
                "image_size": {"width": img.size[0], "height": img.size[1]},
                "sahi_slices": len(generate_slices(img, window=SAHI_WINDOW, overlap=SAHI_OVERLAP)),
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
