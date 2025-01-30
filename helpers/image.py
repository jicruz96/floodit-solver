from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


class Rectangle:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @classmethod
    def from_cv2_rect(cls, rect: cv2.typing.Rect) -> Rectangle:
        return cls(*rect)

    @property
    def area(self) -> int:
        return self.w * self.h

    @property
    def aspect_ratio(self) -> float:
        return self.w / self.h

    @property
    def slice(self) -> tuple[slice[int], slice[int]]:
        return (slice(self.y, self.y + self.h), slice(self.x, self.x + self.w))

    def is_square_like_and_not_too_small(self) -> bool:
        return self.w >= 5 and self.h >= 5 and (0.95 <= self.aspect_ratio <= 1.05)


def find_largest_square_in_image(img: bytes) -> Image.Image:
    """
    Use OpenCV to find the largest 'square-like' bounding rectangle in an
    image provided as raw bytes. Returns that region as a Pillow Image or None if not found.
    """
    cv_img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
    contours, _ = cv2.findContours(
        image=cv2.Canny(
            image=cv2.cvtColor(
                src=cv_img,
                code=cv2.COLOR_BGR2GRAY,
            ),
            # high sensitivity thresholds
            threshold1=30,
            threshold2=100,
        ),
        mode=cv2.RETR_EXTERNAL,
        method=cv2.CHAIN_APPROX_SIMPLE,
    )
    pil_img = Image.fromarray(
        cv2.cvtColor(
            src=cv_img[
                max(
                    filter(
                        lambda box: box.is_square_like_and_not_too_small(),
                        map(Rectangle.from_cv2_rect, map(cv2.boundingRect, contours)),
                    ),
                    key=lambda box: box.area,
                ).slice
            ],
            code=cv2.COLOR_BGR2RGB,
        )
    )
    pil_img.save("tmp.png")
    return pil_img


def _most_common_pixel_in_region(
    pil_img: Image.Image, x0: int, y0: int, x1: int, y1: int
) -> tuple[int, int, int]:
    """
    For the region [x0:x1, y0:y1], return the most frequent (R,G,B) color.
    """
    cell = pil_img.crop((x0, y0, x1, y1))
    colors_count = cell.getcolors(maxcolors=256 * 256)
    if not colors_count:
        return (0, 0, 0)
    most_common = max(colors_count, key=lambda x: x[0])
    return most_common[1]  # type: ignore


def rgb_to_color_code(rgb: tuple[int, int, int]) -> str:
    """Convert (R, G, B) to a hex color code."""
    return "#" + "".join(f"{v:02x}" for v in rgb)


def extract_board_from_image_bytes(
    image_bytes: bytes, grid_size: int = 14
) -> list[list[str]]:
    """
    1) Finds the largest square artifact in the raw image bytes.
    2) Partitions into grid_size x grid_size cells.
    3) Picks the most frequent pixel => color code for each cell.
    4) Returns a 2D array of single-letter color codes.
    """
    square_img = find_largest_square_in_image(image_bytes)
    if square_img is None:
        raise ValueError("No square-ish region found in the provided image bytes.")

    width, height = square_img.size
    cell_w = width // grid_size
    cell_h = height // grid_size

    board: list[list[str]] = []
    for r in range(grid_size):
        row_colors: list[str] = []
        for c in range(grid_size):
            x0 = c * cell_w
            y0 = r * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            mode_rgb = _most_common_pixel_in_region(square_img, x0, y0, x1, y1)
            color_code = rgb_to_color_code(mode_rgb)
            row_colors.append(color_code)
        board.append(row_colors)
    return board


def extract_board_from_image_path(
    image_path: str, grid_size: int = 14
) -> list[list[str]]:
    """
    Same as extract_board_from_image_bytes, but reads the image from disk.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return extract_board_from_image_bytes(image_bytes, grid_size)
