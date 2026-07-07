# JPEG preview generation for /api/enhance responses.
# Assisted by: cursor, claude

from __future__ import annotations

import io
import os

from PIL import Image

PREVIEW_MAX_DIMENSION = int(os.getenv("ENHANCE_PREVIEW_MAX_DIMENSION", "2048"))
PREVIEW_JPEG_QUALITY = int(os.getenv("ENHANCE_PREVIEW_JPEG_QUALITY", "85"))


def make_jpeg_preview(
    img: Image.Image,
    max_dimension: int = PREVIEW_MAX_DIMENSION,
    quality: int = PREVIEW_JPEG_QUALITY,
) -> tuple[bytes, int, int]:
    """Return JPEG bytes and preview (width, height), downscaling if needed."""
    preview = img.copy()
    width, height = preview.size
    longest = max(width, height)
    if longest > max_dimension:
        scale = max_dimension / longest
        preview = preview.resize(
            (max(1, int(width * scale)), max(1, int(height * scale))),
            Image.Resampling.LANCZOS,
        )

    if preview.mode not in ("RGB", "L"):
        preview = preview.convert("RGB")

    buf = io.BytesIO()
    preview.save(buf, format="JPEG", quality=quality, optimize=True)
    pw, ph = preview.size
    return buf.getvalue(), pw, ph
