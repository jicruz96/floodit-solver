#!/usr/bin/env python3
from __future__ import annotations

from typing import Generator, List, Sequence, Tuple

from rich.console import Console
from rich.style import Style
from rich.text import Text

console = Console()
color_map = {
    "R": "red",
    "B": "blue",
    "O": "#FFA500",  # "orange" not supported by Rich
    "Y": "yellow",
    "W": "white",
    "K": "black",
    "?": "bright_black",  # or any fallback color
}


def apply_color_change(
    board: List[List[str]],
    region: List[Tuple[int, int]],
    new_color: str,
) -> None:
    """
    In-place change of board cells in region to new_color.
    """
    for r, c in region:
        board[r][c] = new_color


def copy_board(board: List[List[str]]) -> List[List[str]]:
    """
    Return a copy of the board.
    """
    return [row[:] for row in board]


def board_to_str(board: List[List[str]]) -> str:
    """
    Convert 2D board into a single string for hashing in visited sets.
    """
    return "\n".join("".join(row) for row in board)


def str_to_board(s: str) -> List[List[str]]:
    """
    Convert the single string form back to a 2D list of color codes.
    (Useful if needed, though we might not always do the reverse.)
    """
    return list(map(list, s.split("\n")))


def get_connected_region(
    board: List[List[str]],
    start_row: int = 0,
    start_col: int = 0,
) -> List[Tuple[int, int]]:
    rows = len(board)
    cols = len(board[0])
    start_color = board[start_row][start_col]
    visited = set[tuple[int, int]]()
    region: List[tuple[int, int]] = []
    queue: List[tuple[int, int]] = [(start_row, start_col)]
    while queue:
        r, c = queue.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        region.append((r, c))
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if board[nr][nc] == start_color and (nr, nc) not in visited:
                    queue.append((nr, nc))
    return region


def is_board_filled(board: List[List[str]] | str) -> bool:
    """
    Check if entire board is uniform color.
    """
    if not isinstance(board, str):
        board = board_to_str(board)
    return len(set(board) - {"\n"}) == 1


def get_neighboring_colors_of_region(
    board: List[List[str]],
    region: List[Tuple[int, int]],
) -> Generator[str]:
    """
    Return all distinct colors that are adjacent to the region
    """
    rows = len(board)
    cols = len(board[0])
    region_set = set(region)
    region_color = board[region[0][0]][region[0][1]]
    seen: set[str] = {region_color}
    for r, c in region:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and (nr, nc) not in region_set
                and board[nr][nc] not in seen
            ):
                yield board[nr][nc]
                seen.add(board[nr][nc])


def print_colored_board(board: List[List[str]], bold: Sequence[str] = ()) -> None:
    """
    Print each cell of the board in a color matching its letter.
    Cells whose letters appear in `bold` will be printed in bold.
    """
    for row in board:
        line = Text()
        for cell in row:
            line.append(
                # square unicode box
                "\u25a0",
                style=Style(
                    color=color_map.get(cell, "white"),
                    bold=(cell in bold),
                ),
            )
        console.print(line)
