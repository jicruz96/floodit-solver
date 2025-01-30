from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

############################################
# General Shared Helpers (unchanged)
############################################


def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> int:
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2


def closest_named_color(rgb: Tuple[int, int, int]) -> str:
    """
    Map (R,G,B) to the nearest color in our defined set.
    Returns a single-letter code.
    """
    known_colors = {
        (255, 0, 0): "R",  # Red
        (0, 0, 255): "B",  # Blue
        (255, 255, 0): "Y",  # Yellow
        (255, 165, 0): "O",  # Orange
        (0, 0, 0): "K",  # Black
        (255, 255, 255): "W",  # White
    }
    best_color = None
    min_dist = float("inf")
    for kc, letter in known_colors.items():
        dist = color_distance(rgb, kc)
        if dist < min_dist:
            min_dist = dist
            best_color = letter
    return best_color if best_color else "?"


def most_common_pixel_in_region(
    pil_img: Image.Image, x0: int, y0: int, x1: int, y1: int
) -> Tuple[int, int, int]:
    """
    For the region [x0:x1, y0:y1], return the most frequent (R,G,B) color.
    """
    cell = pil_img.crop((x0, y0, x1, y1))
    colors_count = cell.getcolors(maxcolors=256 * 256)
    if not colors_count:
        return (0, 0, 0)
    most_common = max(colors_count, key=lambda x: x[0])
    return most_common[1]  # type: ignore


############################################
# 1) Largest Square Detection, from Bytes
############################################


def find_largest_square_artifact_from_bytes(
    image_bytes: bytes, aspect_tolerance: float = 0.05
) -> Optional[Image.Image]:
    """
    Use OpenCV to find the largest 'square-ish' bounding rectangle in an
    image provided as raw bytes. Return that region as a Pillow Image, or
    None if not found.
    """
    # Decode raw bytes into a CV2 image (BGR)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_box = None
    best_area = 0.0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 5 or h < 5:
            continue
        aspect_ratio = float(w) / float(h)
        area = w * h
        if (1.0 - aspect_tolerance) <= aspect_ratio <= (1.0 + aspect_tolerance):
            if area > best_area:
                best_area = area
                best_box = (x, y, w, h)

    if best_box is None:
        return None

    x, y, w, h = best_box
    region = cv_img[y : y + h, x : x + w]
    pil_img = Image.fromarray(cv2.cvtColor(region, cv2.COLOR_BGR2RGB))
    return pil_img


############################################
# 2) Board Extraction, from Bytes
############################################


def extract_board_from_image_bytes(
    image_bytes: bytes, grid_size: int = 14
) -> List[List[str]]:
    """
    1) Finds the largest square artifact in the raw image bytes.
    2) Partitions into grid_size x grid_size cells.
    3) Picks the most frequent pixel => color code for each cell.
    4) Returns a 2D array of single-letter color codes.
    """
    square_img = find_largest_square_artifact_from_bytes(image_bytes)
    if square_img is None:
        raise ValueError("No square-ish region found in the provided image bytes.")

    width, height = square_img.size
    cell_w = width // grid_size
    cell_h = height // grid_size

    board: List[List[str]] = []
    for r in range(grid_size):
        row_colors: List[str] = []
        for c in range(grid_size):
            x0 = c * cell_w
            y0 = r * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            mode_rgb = most_common_pixel_in_region(square_img, x0, y0, x1, y1)
            color_code = closest_named_color(mode_rgb)
            row_colors.append(color_code)
        board.append(row_colors)
    return board


def extract_board_from_image_path(
    image_path: str, grid_size: int = 14
) -> List[List[str]]:
    """
    Same as extract_board_from_image_bytes, but reads the image from disk.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return extract_board_from_image_bytes(image_bytes, grid_size)
