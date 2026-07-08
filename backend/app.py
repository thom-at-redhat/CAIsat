"""
FastAPI backend for Zoom & Enhance application.

This service receives images from the frontend, sends them to the
OpenShift AI model endpoint, and returns the enhanced result.
"""

# Assisted by: cursor, claude

from contextlib import asynccontextmanager
import base64
import io
import os
import traceback

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from capabilities import get_capabilities
from image_preview import make_jpeg_preview
from kserve_v2 import sanitize_model_error
from predictor_orchestrator import ensure_predictor_active
from tiled_sr import enhance_image_tiled
from logging_config import configure_logging, log_event

load_dotenv()

logger = configure_logging("caisat-enhance", os.getenv("LOG_LEVEL", "INFO"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

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
    log_event(logger, "enhancement backend started", model_endpoint=MODEL_ENDPOINT)
    yield
    if http_session is not None:
        await http_session.close()
        http_session = None


app = FastAPI(title="Zoom & Enhance API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"service": "Zoom & Enhance API", "status": "operational"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/capabilities")
async def api_capabilities():
    return get_capabilities()


@app.get("/api/stats")
async def get_stats():
    return {"total_enhancements": enhancement_counter, "status": "operational"}


@app.post("/api/enhance")
async def enhance_image(image: UploadFile = File(...)):
    global enhancement_counter

    if http_session is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    caps = get_capabilities()
    max_crop = int(caps["max_crop"])

    try:
        contents = await image.read()
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"Upload exceeds {MAX_UPLOAD_BYTES} byte limit")

        img = Image.open(io.BytesIO(contents))
        side = min(img.size)
        if side > max_crop:
            raise HTTPException(
                status_code=413,
                detail=f"Crop {side}px exceeds profile max_crop {max_crop}px",
            )

        try:
            await ensure_predictor_active("swinir", http_session=http_session)
            enhanced_img = await enhance_image_tiled(
                http_session,
                MODEL_ENDPOINT,
                img,
                input_name=KSERVE_INPUT_NAME,
                output_name=KSERVE_OUTPUT_NAME,
                max_tile=int(caps["max_tile"]),
                scale_factor=int(caps["scale_factor"]),
                tiling_enabled=bool(caps["tiling_enabled"]),
                timeout_seconds=float(caps["infer_timeout_seconds"]),
            )
        except RuntimeError as exc:
            print(f"Predictor orchestration failed: {exc}")
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except TimeoutError as exc:
            print(f"Predictor readiness timeout: {exc}")
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except aiohttp.ClientResponseError as exc:
            print(f"Model endpoint error ({exc.status}): {exc.message}")
            raise HTTPException(
                status_code=502,
                detail=sanitize_model_error(exc.status, exc.message or ""),
            ) from exc
        except RuntimeError as exc:
            print(f"Tiled enhancement aborted: {exc}")
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        full_w, full_h = enhanced_img.size
        print(f"Enhanced output: {full_w}x{full_h} (native 4x)")
        log_event(logger, "enhance complete", width=full_w, height=full_h)

        preview_bytes, preview_w, preview_h = make_jpeg_preview(enhanced_img)
        enhancement_counter += 1

        return JSONResponse(
            {
                "preview": base64.b64encode(preview_bytes).decode("ascii"),
                "media_type": "image/jpeg",
                "width": full_w,
                "height": full_h,
                "preview_width": preview_w,
                "preview_height": preview_h,
            }
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
