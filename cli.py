#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

import solvers
from helpers.board import (
    print_colored_board,
)
from helpers.image import (
    extract_board_from_image_path,
)


def main():
    parser = argparse.ArgumentParser(
        description="Color Fill solver. Either use an anytime A* solver or a simple solver."
    )
    parser.add_argument(
        "--image", required=True, help="Path to the input screenshot/image file."
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=14,
        help="Number of rows/columns in the color grid (default=14).",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=5.0,
        help="Time limit in seconds for searching (default=5).",
    )
    parser.add_argument(
        "--max-solutions",
        type=int,
        default=5,
        help="Maximum number of solutions (default=5).",
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use the simple solver that picks the most frequent boundary color.",
    )
    parser.add_argument("--step", action="store_true", help="Print each step.")
    parser.add_argument("--depth", type=int, default=4, help="Depth of the lookahead.")
    args = parser.parse_args()

    # Extract the board from the image
    print(f"Extracting {args.grid_size}x{args.grid_size} board from '{args.image}'...")
    board = extract_board_from_image_path(args.image, grid_size=args.grid_size)
    print_colored_board(board)
    # Decide which solver to run
    if args.simple:
        print("Using the simple solver...")
        moves = list(
            solvers.solve_color_fill_simple(board, step=args.step, max_depth=args.depth)
        )
        if not args.step:
            cost = len(moves)
            print(f"Simple solver result (cost={cost}):\n{'\n'.join(moves)}")
    else:
        print(
            "Using the anytime A* solver with a time limit of "
            f"{args.time_limit:.1f}s, up to {args.max_solutions} solutions..."
        )
        solutions = solvers.solve_color_fill_anytime(
            board,
            time_limit=args.time_limit,
            max_solutions=args.max_solutions,
        )
        for i, moves in enumerate(solutions, start=1):
            cost = len(moves)
            moves_str = "".join(moves)
            print(f"Solution {i} (cost={cost}): {moves_str}")
        else:
            print("No solution found")


if __name__ == "__main__":
    sys.exit(main())
