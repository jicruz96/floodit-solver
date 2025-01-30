#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Generator

from webcolors import hex_to_name

from helpers.board import (
    apply_color_change,
    copy_board,
    get_connected_region,
    get_neighboring_colors_of_region,
    is_board_filled,
    print_colored_board,
)


def find_best_color(board: list[list[str]], max_depth: int = 4) -> str:
    scores = get_score_of_playing_each_color(
        board,
        current_depth=1,
        max_depth=max_depth,
    )
    return max(scores, key=lambda color: scores[color][0])


def find_best_color_path(board: list[list[str]], max_depth: int = 4) -> list[str]:
    scores = get_score_of_playing_each_color(
        board,
        current_depth=1,
        max_depth=max_depth,
    )
    return max(scores.values(), key=lambda score_path_tuple: score_path_tuple[0])[1]


def get_score_of_playing_each_color(
    board: list[list[str]],
    *,
    current_depth: int,
    max_depth: int,
) -> dict[str, tuple[int, list[str]]]:
    region = get_connected_region(board)
    if current_depth == max_depth or is_board_filled(board):
        return {
            board[0][0]: (len(region), []),
        }

    def recurse(color: str):
        iterable = get_score_of_playing_each_color(
            board=new_board_with_region_updated_to_color(board, region, color),
            current_depth=current_depth + 1,
            max_depth=max_depth,
        ).values()
        if not iterable:
            breakpoint()
        score, path = max(
            iterable,
            key=lambda score_path_tuple: score_path_tuple[0],
        )
        return (score, [color, *path])

    return {
        color: recurse(color)
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
        for best_color in find_best_color_path(board, max_depth=max_depth):
            try:
                best_color_name = hex_to_name(best_color)
            except ValueError:
                best_color_name = best_color
            yield best_color_name
            board = new_board_with_region_updated_to_color(
                board,
                get_connected_region(board),
                best_color,
            )
            if step:
                print_colored_board(board)
                print(f"Best color: {best_color_name}")
                if max_depth < 6:
                    time.sleep(4)
                elif max_depth < 8:
                    time.sleep(2)
