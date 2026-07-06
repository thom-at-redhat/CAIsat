# SAHI slice coverage tests.
# Assisted by: cursor, claude

from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
SAHI_PATH = REPO_ROOT / "backend-detection" / "sahi.py"


def _load_sahi():
    spec = importlib.util.spec_from_file_location("caisat_sahi", SAHI_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _covered_mask(width: int, height: int, slices: list[tuple[int, int, Image.Image]]) -> list[list[bool]]:
    mask = [[False] * width for _ in range(height)]
    for x0, y0, tile in slices:
        tw, th = tile.size
        for y in range(y0, min(y0 + th, height)):
            for x in range(x0, min(x0 + tw, width)):
                mask[y][x] = True
    return mask


def _assert_full_coverage(width: int, height: int, slices: list[tuple[int, int, Image.Image]]) -> None:
    mask = _covered_mask(width, height, slices)
    assert all(all(row) for row in mask), "slice grid must cover the full image"


def test_small_image_single_slice() -> None:
    sahi = _load_sahi()
    img = Image.new("RGB", (512, 512), color="red")
    slices = sahi.generate_slices(img, window=640, overlap=0.2)
    assert len(slices) == 1
    assert slices[0][0:2] == (0, 0)


def test_1024_includes_trailing_edge_tiles() -> None:
    sahi = _load_sahi()
    img = Image.new("RGB", (1024, 1024), color="blue")
    slices = sahi.generate_slices(img, window=640, overlap=0.2)
    origins = {(x, y) for x, y, _ in slices}
    assert (384, 384) in origins
    assert len(slices) == 4
    _assert_full_coverage(1024, 1024, slices)


def test_2048_includes_trailing_edge_tiles() -> None:
    sahi = _load_sahi()
    img = Image.new("RGB", (2048, 2048), color="green")
    slices = sahi.generate_slices(img, window=640, overlap=0.2)
    origins = {(x, y) for x, y, _ in slices}
    assert (1408, 1408) in origins
    assert len(slices) == 16
    _assert_full_coverage(2048, 2048, slices)


def test_axis_positions_trailing_edge() -> None:
    sahi = _load_sahi()
    assert sahi._axis_positions(1024, 640, 512) == [0, 384]
    assert sahi._axis_positions(2048, 640, 512) == [0, 512, 1024, 1408]
    assert sahi._axis_positions(640, 640, 512) == [0]
