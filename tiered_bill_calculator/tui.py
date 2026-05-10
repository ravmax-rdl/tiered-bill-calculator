from __future__ import annotations

import os
import shutil
from decimal import Decimal

from .bill import BillResult, calculate_bill, parse_reading, quantize_money


_RESET = "\033[0m"
_BOLD  = "\033[1m"
_DIM   = "\033[2m"
_CYAN  = "\033[36m"

_TIER_COLOR: dict[str, str] = {
    "low":       "\033[32m",
    "normal":    "\033[33m",
    "high":      "\033[91m",
    "very high": "\033[31m",
}


def _term_width(default: int = 80) -> int:
    try:
        return shutil.get_terminal_size(fallback=(default, 20)).columns
    except Exception:
        return default


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _hr(width: int | None = None, char: str = "-") -> str:
    return char * (width if width is not None else _term_width())


def _fit(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: max(0, width - 1)] + "…"


def _fmt_units(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    return str(value.normalize())


def _fmt_money(value: Decimal) -> str:
    return str(quantize_money(value))


def _box(lines: list[str], *, width: int | None = None, padding: int = 1) -> str:
    used_width = width if width is not None else _term_width()
    inner_width = max(
        1,
        min(
            used_width - 2 - 2 * padding,
            max((len(l) for l in lines), default=0),
        ),
    )
    fixed = [_fit(l, inner_width) for l in lines]
    top = "+" + "-" * (inner_width + 2 * padding) + "+"
    rows = ["|" + " " * padding + l.ljust(inner_width) + " " * padding + "|" for l in fixed]
    return "\n".join([top, *rows, top])


def _format_table_rows(result: BillResult) -> list[str]:
    headers = ["Slab", "Units", "Rate", "Subtotal"]
    rows = [
        [line.label, _fmt_units(line.units), _fmt_money(line.rate), _fmt_money(line.subtotal)]
        for line in result.breakdown
    ]
    cols = list(zip(*([headers] + rows))) if rows else [tuple(headers)]
    widths = [max(len(str(x)) for x in col) for col in cols]
    cap = min(_term_width(), 120)
    if sum(widths) + 3 * len(widths) > cap:
        widths[0] = max(5, widths[0] - (sum(widths) + 3 * len(widths) - cap))

    def fmt_row(parts: list[str]) -> str:
        return " | ".join(str(p).ljust(widths[i]) for i, p in enumerate(parts))

    separator = "-+-".join("-" * w for w in widths)
    return (
        [fmt_row(headers), separator]
        + [fmt_row([_fit(r[0], widths[0])] + r[1:]) for r in rows]
    )


def render_bill_to_text(result: BillResult) -> str:
    width = _term_width()
    inputs = [
        f"Previous reading : {_fmt_units(result.previous_reading)}",
        f"Current reading  : {_fmt_units(result.current_reading)}",
        f"Units used (k)   : {_fmt_units(result.units_used)}",
        f"Tier              : {result.tier}",
    ]
    calc = [
        "Calculation",
        f"k         : {_fmt_units(result.units_used)}",
        f"Formula  : {result.formula}",
        f"Value    : {_fmt_money(result.value)}",
        f"Fixed fee: 800.00",
        f"Total     : {_fmt_money(result.total)}",
    ]
    table_lines = _format_table_rows(result)
    return "\n".join([
        f"{'Tiered Bill Calculator':^{width}}",
        _hr(width),
        _box(inputs, width=width),
        "",
        _box(calc, width=width),
        "",
        "Breakdown",
        _box(table_lines, width=width),
    ])


def _print_header(width: int) -> None:
    print(_CYAN + _BOLD + f"{'Tiered Bill Calculator':^{width}}" + _RESET)
    print(_DIM + _hr(width) + _RESET)


def _print_result(result: BillResult, width: int) -> None:
    tier_color = _TIER_COLOR.get(result.tier, "")

    inputs = [
        f"Previous reading : {_fmt_units(result.previous_reading)}",
        f"Current reading  : {_fmt_units(result.current_reading)}",
        f"Units used (k)   : {_fmt_units(result.units_used)}",
    ]
    print(_box(inputs, width=width))
    print()

    calc_plain = [
        "Calculation",
        f"k         : {_fmt_units(result.units_used)}",
        f"Formula  : {result.formula}",
        f"Value    : {_fmt_money(result.value)}",
        f"Fixed fee: 800.00",
        f"Total     : {_fmt_money(result.total)}",
    ]
    print(_box(calc_plain, width=width))
    print()

    print("Breakdown")
    print(_box(_format_table_rows(result), width=width))
    print()

    print(
        f"  Tier  : {tier_color}{_BOLD}{result.tier.upper()}{_RESET}"
        f"   |   Total : {_BOLD}{_fmt_money(result.total)}{_RESET}"
    )


def run_tui(*, clear_screen: bool = True) -> None:
    previous: Decimal | None = None
    current: Decimal | None = None

    while True:
        if clear_screen:
            _clear()

        width = _term_width()
        _print_header(width)
        print()

        intro = [
            "Compute tiered bill from two meter readings.",
            f"Units  k = current - previous  |  Fixed fee = +800",
            "",
            "Tip: decimal values are accepted (e.g. 123.5).",
        ]
        print(_box(intro, width=width))
        print()

        prev_hint = f" [{_fmt_units(previous)}]" if previous is not None else ""
        curr_hint = f" [{_fmt_units(current)}]" if current is not None else ""

        while True:
            raw = input(f"  Previous month reading{prev_hint}: ").strip()
            if raw == "" and previous is not None:
                break
            try:
                previous = parse_reading(raw)
                break
            except ValueError as exc:
                print(f"  {_BOLD}Error:{_RESET} {exc}")

        while True:
            raw = input(f"  Current reading       {curr_hint}: ").strip()
            if raw == "" and current is not None:
                break
            try:
                current = parse_reading(raw)
                break
            except ValueError as exc:
                print(f"  {_BOLD}Error:{_RESET} {exc}")

        try:
            result = calculate_bill(previous, current)
        except ValueError as exc:
            print()
            print(_box([f"Error: {exc}", "Press Enter to re-enter readings."], width=width))
            input()
            previous = None
            current = None
            continue

        if clear_screen:
            _clear()

        _print_header(width)
        print()
        _print_result(result, width)
        print()
        print(_DIM + "  [Enter] recalculate   [Q] quit" + _RESET)

        if input("  > ").strip().lower() == "q":
            break


__all__ = ["run_tui", "render_bill_to_text"]
