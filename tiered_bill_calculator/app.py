from __future__ import annotations

import argparse

from .bill import calculate_bill, parse_reading
from .tui import run_tui, render_bill_to_text


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tiered-bill-calculator",
        description="Simple tiered bill calculator.",
    )
    parser.add_argument(
        "--previous", type=str, help="Previous month reading (e.g., 100)"
    )
    parser.add_argument("--current", type=str, help="Current reading (e.g., 140)")
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Do not clear the screen in the interactive TUI.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.previous is None or args.current is None:
        run_tui(clear_screen=not args.no_clear)
        return

    prev = parse_reading(args.previous)
    curr = parse_reading(args.current)
    result = calculate_bill(prev, curr)
    print(render_bill_to_text(result))


__all__ = ["main"]
