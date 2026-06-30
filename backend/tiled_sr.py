# Tiled super-resolution for SwinIR (all-tiles-or-abort).
# Assisted by: cursor, claude

from __future__ import annotations

import aiohttp
import numpy as np
from PIL import Image

from kserve_v2 import kserve_infer, sanitize_model_error


def image_to_tensor(image: Image.Image) -> np.ndarray:
    """Convert square PIL RGB image to NCHW float32 tensor without resizing."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    w, h = image.size
    if w != h:
        side = min(w, h)
        image = image.crop((0, 0, side, side))
    arr = np.array(image).astype(np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    return np.expand_dims(arr, 0)


def tensor_to_image(output_array: np.ndarray) -> Image.Image:
    """Convert model output tensor to PIL Image at native resolution."""
    plane = output_array[0]
    plane = np.transpose(plane, (1, 2, 0))
    plane = np.clip(plane, 0, 1)
    plane = (plane * 255).astype(np.uint8)
    return Image.fromarray(plane)


async def infer_tile(
    session: aiohttp.ClientSession,
    endpoint: str,
    tile: Image.Image,
    *,
    input_name: str,
    output_name: str,
    timeout_seconds: float,
) -> Image.Image:
    tensor = image_to_tensor(tile)
    output_tensor, _protocol = await kserve_infer(
        session,
        endpoint,
        tensor,
        input_name=input_name,
        output_name=output_name,
        timeout_seconds=timeout_seconds,
    )
    return tensor_to_image(output_tensor)


async def enhance_image_tiled(
    session: aiohttp.ClientSession,
    endpoint: str,
    image: Image.Image,
    *,
    input_name: str,
    output_name: str,
    max_tile: int,
    scale_factor: int,
    tiling_enabled: bool,
    timeout_seconds: float,
) -> Image.Image:
    """Run SwinIR on image with optional tiling. All-tiles-or-abort on any failure."""
    side = min(image.size)
    if image.size[0] != image.size[1]:
        image = image.crop((0, 0, side, side))

    if not tiling_enabled or side <= max_tile:
        return await infer_tile(
            session,
            endpoint,
            image,
            input_name=input_name,
            output_name=output_name,
            timeout_seconds=timeout_seconds,
        )

    out_side = side * scale_factor
    output_canvas = Image.new("RGB", (out_side, out_side))
    tile_count = 0

    for y in range(0, side, max_tile):
        for x in range(0, side, max_tile):
            tw = min(max_tile, side - x)
            th = min(max_tile, side - y)
            tile = image.crop((x, y, x + tw, y + th))
            if tw != max_tile or th != max_tile:
                padded = Image.new("RGB", (max_tile, max_tile))
                padded.paste(tile, (0, 0))
                tile = padded
            try:
                enhanced_tile = await infer_tile(
                    session,
                    endpoint,
                    tile,
                    input_name=input_name,
                    output_name=output_name,
                    timeout_seconds=timeout_seconds,
                )
            except aiohttp.ClientResponseError as exc:
                raise RuntimeError(f"Tile ({x},{y}) failed: {sanitize_model_error(exc.status, exc.message or '')}") from exc
            tile_count += 1
            out_x = x * scale_factor
            out_y = y * scale_factor
            crop_w = tw * scale_factor
            crop_h = th * scale_factor
            output_canvas.paste(enhanced_tile.crop((0, 0, crop_w, crop_h)), (out_x, out_y))

    print(f"Tiled enhancement completed: {tile_count} tiles")
    return output_canvas
