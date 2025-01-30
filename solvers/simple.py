#!/usr/bin/env python3
from __future__ import annotations

import functools
import time
from typing import Generator

from helpers.board import (
    apply_color_change,
    board_to_str,
    copy_board,
    get_connected_region,
    get_neighboring_colors_of_region,
    is_board_filled,
    print_colored_board,
    str_to_board,
)


def find_best_color(board: list[list[str]], max_depth: int = 4) -> str:
    scores = get_score_of_playing_each_color(
        board_to_str(board),
        current_depth=1,
        max_depth=max_depth,
    )
    return max(scores, key=scores.get)  # type: ignore


@functools.cache
def get_score_of_playing_each_color(
    board_str: str,
    *,
    current_depth: int,
    max_depth: int,
) -> dict[str, int]:
    board = str_to_board(board_str)
    region = get_connected_region(board)
    if current_depth == max_depth or is_board_filled(board_str):
        return {
            board[0][0]: len(region),
        }
    return {
        color: max(
            get_score_of_playing_each_color(
                board_str=board_to_str(
                    new_board_with_region_updated_to_color(board, region, color)
                ),
                current_depth=current_depth + 1,
                max_depth=max_depth,
            ).values()
        )
        for color in get_neighboring_colors_of_region(board, region)
    }


def new_board_with_region_updated_to_color(
    board: list[list[str]],
    region: list[tuple[int, int]],
    new_color: str,
) -> list[list[str]]:
    board = copy_board(board)
    apply_color_change(board, region, new_color)
    return board


def solve_color_fill_simple(
    board: list[list[str]],
    step: bool = False,
    max_depth: int = 4,
) -> Generator[str]:
    while not is_board_filled(board):
        best_color = find_best_color(board, max_depth=max_depth)
        yield best_color
        board = new_board_with_region_updated_to_color(
            board,
            get_connected_region(board),
            best_color,
        )
        if step:
            print_colored_board(board)
            print(f"Best color: {best_color}")
            if max_depth < 6:
                time.sleep(4)
            elif max_depth < 8:
                time.sleep(2)
