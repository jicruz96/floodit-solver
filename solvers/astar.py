#!/usr/bin/env python3
from __future__ import annotations

import heapq
import time
from typing import List, Set, Tuple

from helpers.board import (
    apply_color_change,
    board_to_str,
    get_connected_region,
    get_neighboring_colors_of_region,
    is_board_filled,
    str_to_board,
)


def heuristic(
    board: List[List[str]],
) -> float:
    """
    A simple heuristic:
      * how large is the top-left region?
    """
    region = get_connected_region(board)
    board_size = sum(map(len, board))
    return board_size - len(region)
    return (board_size - len(region)) / board_size


def replace_color(
    board: List[List[str]],
    new_color: str,
) -> List[List[str]]:
    """
    Replace all instances of color with new_color.
    """
    region = get_connected_region(board)
    for r, c in region:
        board[r][c] = new_color
    return board


def solve_color_fill_anytime(
    board: List[List[str]],
    time_limit: float | None = None,
    max_solutions: int = 5,
) -> List[List[str]]:
    """
    A best-first (A*) search that:
      - Prioritizes states with lowest g + h.
      - Keeps searching until time limit expires or no states remain.
      - Collects solutions (board is all one color) as we find them.
    Returns up to `max_solutions` solutions sorted from lowest cost
    to highest.
    """
    start_time = time.time()
    solutions_found: List[List[str]] = []
    # Priority queue entries are (f, g, board_string, move_sequence)
    # where f = g + h, g = cost so far, h = heuristic
    board = replace_color(board, "-")
    initial_board_str = board_to_str(board)
    visited: Set[str] = set([initial_board_str])
    pq: List[Tuple[float, int, str, List[str]]] = [
        (
            heuristic(board),
            0,
            initial_board_str,
            [],
        )
    ]
    elapsed = 0.0
    while (
        pq
        and (time_limit is None or elapsed < time_limit)
        and len(solutions_found) < max_solutions
    ):
        _, g, cur_str, moves = heapq.heappop(pq)
        print("".join(moves))
        if is_board_filled(cur_str):
            print(f"Solution found (cost={len(moves)}): {''.join(moves)}")
            solutions_found.append(moves)
        else:
            cur_board = str_to_board(cur_str)
            region = get_connected_region(cur_board)
            for color in get_neighboring_colors_of_region(cur_board, region):
                board_copy = [row[:] for row in cur_board]
                apply_color_change(board_copy, region, color)
                board_copy = replace_color(board_copy, "-")
                next_board_str = board_to_str(board_copy)
                if next_board_str not in visited:
                    visited.add(next_board_str)
                    heapq.heappush(
                        pq,
                        (
                            g + 1 + heuristic(board_copy),
                            g + 1,
                            next_board_str,
                            moves + [color],
                        ),
                    )
        elapsed = time.time() - start_time
    # Sort all solutions found by cost ascending
    solutions_found.sort(key=lambda x: x[1])
    return solutions_found[:max_solutions]
