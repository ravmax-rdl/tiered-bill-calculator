from __future__ import annotations

import os
import shutil
from decimal import Decimal

from .bill import (
    BillResult,
    TIER_DISPLAY_NAMES,
    TIER_FIXED_FEES,
    TIER_ORDER,
    calculate_bill,
    parse_reading,
    quantize_money,
)


_RESET   = "\033[0m"
_BOLD    = "\033[1m"
_DIM     = "\033[2m"
_CYAN    = "\033[36m"
_WHITE   = "\033[97m"
_RED     = "\033[31m"
_ERR_BG  = "\033[41m"

_TIER_COLOR: dict[str, str] = {
    "low":       "\033[32m",
    "normal":    "\033[33m",
    "high":      "\033[91m",
    "very high": "\033[31m",
}

_TIER_BG: dict[str, str] = {
    "low":       "\033[42m",
    "normal":    "\033[43m",
    "high":      "\033[101m",
    "very high": "\033[41m",
}


def _term_width(default: int = 80) -> int:
    try:
        return shutil.get_terminal_size(fallback=(default, 20)).columns
    except Exception:
        return default


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _hr(width: int | None = None, char: str = "─") -> str:
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


def _badge(text: str, bg: str, fg: str = _WHITE) -> str:
    return f"{bg}{_BOLD}{fg} {text} {_RESET}"


def _section_label(text: str, color: str = _CYAN) -> str:
    return f"{color}{_BOLD}▸ {text}{_RESET}"


def _fixed_fee_schedule_text() -> str:
    return "  ".join(
        f"{TIER_DISPLAY_NAMES[tier]}={_fmt_money(TIER_FIXED_FEES[tier])}"
        for tier in TIER_ORDER
    )


def _box(lines: list[str], *, width: int | None = None, padding: int = 1, border_color: str = "") -> str:
    rs = _RESET if border_color else ""
    used_width = width if width is not None else _term_width()
    inner_width = max(
        1,
        min(
            used_width - 2 - 2 * padding,
            max((len(l) for l in lines), default=0),
        ),
    )
    fixed = [_fit(l, inner_width) for l in lines]
    bc = border_color
    top = bc + "+" + "-" * (inner_width + 2 * padding) + "+" + rs
    rows = [bc + "|" + rs + " " * padding + l.ljust(inner_width) + " " * padding + bc + "|" + rs for l in fixed]
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
        f"Units used       : {_fmt_units(result.units_used)}",
        f"Tier             : {result.tier}",
    ]
    calc = [
        "Calculation",
        f"Formula  : {result.formula}",
        f"Value    : {_fmt_money(result.value)}",
        f"Fixed fee: {_fmt_money(result.fixed_fee)}",
        f"Total     : {_fmt_money(result.total)}",
    ]
    table_lines = _format_table_rows(result)
    return "\n".join([
        f"{'Tiered Bill Calculator':^{width}}",
        "-" * width,
        _box(inputs, width=width),
        "",
        _box(calc, width=width),
        "",
        "Breakdown",
        _box(table_lines, width=width),
    ])


def _print_header(width: int) -> None:
    print(_CYAN + _BOLD + f"{'Tiered Bill Calculator':^{width}}" + _RESET)
    print(_DIM + _CYAN + _hr(width) + _RESET)


def _print_result(result: BillResult, width: int) -> None:
    tier_color = _TIER_COLOR.get(result.tier, "")
    tier_bg    = _TIER_BG.get(result.tier, "")

    inputs = [
        f"Previous reading : {_fmt_units(result.previous_reading)}",
        f"Current reading  : {_fmt_units(result.current_reading)}",
        f"Units used       : {_fmt_units(result.units_used)}",
    ]
    print(_box(inputs, width=width, border_color=_DIM + _CYAN))
    print()

    calc_plain = [
        "Calculation",
        f"Formula  : {result.formula}",
        f"Value    : {_fmt_money(result.value)}",
        f"Fixed fee: {_fmt_money(result.fixed_fee)}",
        f"Total     : {_fmt_money(result.total)}",
    ]
    print(_box(calc_plain, width=width, border_color=tier_color))
    print()

    print(_section_label("Breakdown"))
    print(_box(_format_table_rows(result), width=width, border_color=_DIM + _CYAN))
    print()

    tier_badge = _badge(result.tier.upper(), bg=tier_bg)
    print(
        f"  {_DIM}Tier{_RESET} : {tier_badge}"
        f"   {_DIM}Total{_RESET} : {tier_color}{_BOLD}{_fmt_money(result.total)}{_RESET}"
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
            f"Units  k = current - previous  |  Fixed fee by tier: {_fixed_fee_schedule_text()}",
            "",
        ]
        print(_box(intro, width=width, border_color=_DIM + _CYAN))
        print()

        while True:
            raw = input(f"  {_DIM}Previous month reading{_RESET}: ").strip()
            try:
                previous = parse_reading(raw)
                break
            except ValueError as exc:
                print(f"  {_badge('ERROR', bg=_ERR_BG)} {exc}")

        while True:
            raw = input(f"  {_DIM}Current reading       {_RESET}: ").strip()
            try:
                current = parse_reading(raw)
                break
            except ValueError as exc:
                print(f"  {_badge('ERROR', bg=_ERR_BG)} {exc}")

        try:
            result = calculate_bill(previous, current)
        except ValueError as exc:
            print()
            print(_box([f"Error: {exc}", "Press Enter to re-enter readings."], width=width, border_color=_RED))
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
        print(_DIM + "  [Enter] new readings   [Q] quit" + _RESET)

        if input("  > ").strip().lower() == "q":
            break


__all__ = ["run_tui", "render_bill_to_text"]
