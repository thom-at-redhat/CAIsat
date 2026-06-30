"""
FastAPI backend for Zoom & Enhance application.

This service receives images from the frontend, sends them to the
OpenShift AI model endpoint, and returns the enhanced result.
"""

# Assisted by: cursor, claude

from contextlib import asynccontextmanager
import io
import os
import traceback

import aiohttp
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image

from kserve_v2 import kserve_infer, sanitize_model_error

load_dotenv()

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT")
KSERVE_INPUT_NAME = os.getenv("KSERVE_INPUT_NAME", "input")
KSERVE_OUTPUT_NAME = os.getenv("KSERVE_OUTPUT_NAME", "output")

if not MODEL_ENDPOINT:
    raise ValueError("MODEL_ENDPOINT environment variable must be set. Example: http://model-service.namespace.svc.cluster.local:8080/v2/models/model-name/infer")

http_session: aiohttp.ClientSession | None = None
enhancement_counter = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_session
    http_session = aiohttp.ClientSession()
    yield
    if http_session is not None:
        await http_session.close()
        http_session = None


app = FastAPI(title="Zoom & Enhance API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def preprocess_image(image: Image.Image, crop_size: int = 256) -> np.ndarray:
    """Convert PIL image to NCHW float32 tensor in [0, 1]."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize((crop_size, crop_size), Image.LANCZOS)
    img_array = np.array(image).astype(np.float32) / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))
    return np.expand_dims(img_array, 0)


def postprocess_output(output_array: np.ndarray) -> Image.Image:
    """Convert model output tensor to PIL Image."""
    output_array = output_array[0]
    output_array = np.transpose(output_array, (1, 2, 0))
    output_array = np.clip(output_array, 0, 1)
    output_array = (output_array * 255).astype(np.uint8)
    return Image.fromarray(output_array)


@app.get("/")
async def root():
    return {"service": "Zoom & Enhance API", "status": "operational"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/stats")
async def get_stats():
    return {"total_enhancements": enhancement_counter, "status": "operational"}


@app.post("/api/enhance")
async def enhance_image(image: UploadFile = File(...)):
    global enhancement_counter

    if http_session is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        contents = await image.read()
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"Upload exceeds {MAX_UPLOAD_BYTES} byte limit")

        img = Image.open(io.BytesIO(contents))
        tensor = preprocess_image(img)

        try:
            output_tensor, protocol = await kserve_infer(
                http_session,
                MODEL_ENDPOINT,
                tensor,
                input_name=KSERVE_INPUT_NAME,
                output_name=KSERVE_OUTPUT_NAME,
                timeout_seconds=300,
            )
        except aiohttp.ClientResponseError as exc:
            print(f"Model endpoint error ({exc.status}): {exc.message}")
            raise HTTPException(
                status_code=502,
                detail=sanitize_model_error(exc.status, exc.message or ""),
            ) from exc

        print(f"Inference completed via {protocol} protocol")

        enhanced_img = postprocess_output(output_tensor)
        enhanced_img = enhanced_img.resize((512, 512), Image.LANCZOS)

        img_byte_arr = io.BytesIO()
        enhanced_img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        enhancement_counter += 1

        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=enhanced.png"},
        )

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Error processing image: {type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Image enhancement failed") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
