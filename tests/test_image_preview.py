# Unit tests for enhance JPEG preview generation.
# Assisted by: cursor, claude

from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
_preview_path = REPO_ROOT / "backend" / "image_preview.py"
_spec = importlib.util.spec_from_file_location("caisat_image_preview", _preview_path)
assert _spec is not None and _spec.loader is not None
_preview_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_preview_mod)
make_jpeg_preview = _preview_mod.make_jpeg_preview


def _solid_image(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGB", size, color=(128, 64, 32))


def test_preview_keeps_small_images_at_native_size() -> None:
    img = _solid_image((1024, 1024))
    data, width, height = make_jpeg_preview(img, max_dimension=2048)
    assert width == 1024
    assert height == 1024
    assert Image.open(io.BytesIO(data)).format == "JPEG"


def test_preview_downscales_large_output() -> None:
    img = _solid_image((3072, 3072))
    data, width, height = make_jpeg_preview(img, max_dimension=2048)
    assert width == 2048
    assert height == 2048
    assert len(data) < 3_000_000
    assert Image.open(io.BytesIO(data)).format == "JPEG"


def test_preview_converts_rgba() -> None:
    img = Image.new("RGBA", (512, 512), color=(255, 0, 0, 128))
    data, width, height = make_jpeg_preview(img, max_dimension=2048)
    assert (width, height) == (512, 512)
    assert Image.open(io.BytesIO(data)).mode == "RGB"
