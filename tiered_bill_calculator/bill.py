from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class TierBreakdownLine:
    label: str
    units: Decimal
    rate: Decimal
    subtotal: Decimal


@dataclass(frozen=True)
class BillResult:
    previous_reading: Decimal
    current_reading: Decimal
    units_used: Decimal
    tier: str
    value: Decimal
    fixed_fee: Decimal
    total: Decimal
    breakdown: list[TierBreakdownLine]
    formula: str


def _d(value: str | int | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _parse_decimal(text: str) -> Decimal:
    try:
        return Decimal(text.strip())
    except (InvalidOperation, AttributeError) as e:
        raise ValueError(f"Invalid number: {text!r}") from e


def parse_reading(text: str) -> Decimal:
    value = _parse_decimal(text)
    if value != value.to_integral_value():
        raise ValueError(f"Reading must be a whole number, got {text!r}.")
    return value


def calculate_bill(previous_reading: str | int | Decimal, current_reading: str | int | Decimal) -> BillResult:
    prev = previous_reading if isinstance(previous_reading, Decimal) else _parse_decimal(str(previous_reading))
    curr = current_reading if isinstance(current_reading, Decimal) else _parse_decimal(str(current_reading))

    if prev < 0:
        raise ValueError("Previous reading cannot be negative.")
    if curr < 0:
        raise ValueError("Current reading cannot be negative.")

    units_used = curr - prev
    if units_used < 0:
        raise ValueError(
            "Current reading must be greater than or equal to previous reading."
        )

    rate1 = _d("5")
    rate2 = _d("10")
    rate3 = _d("20")
    rate4 = _d("30")

    u1 = min(units_used, _d("30"))
    u2 = min(max(units_used - _d("30"), _d("0")), _d("30"))
    u3 = min(max(units_used - _d("60"), _d("0")), _d("30"))
    u4 = max(units_used - _d("90"), _d("0"))

    if units_used <= _d("30"):
        tier = "low"
        fee = _d("200")
        formula = "Value = k*5"
    elif units_used <= _d("60"):
        tier = "normal"
        fee = _d("400")
        formula = "Value = 30*5 + (k-30)*10"
    elif units_used <= _d("90"):
        tier = "high"
        fee = _d("600")
        formula = "Value = 30*5 + 30*10 + (k-60)*20"
    else:
        tier = "very high"
        fee = _d("800")
        formula = "Value = 30*5 + 30*10 + 30*20 + (k-90)*30"

    value = (u1 * rate1) + (u2 * rate2) + (u3 * rate3) + (u4 * rate4)
    total = value + fee

    breakdown: list[TierBreakdownLine] = []
    if u1 > 0 or units_used == _d("0"):
        breakdown.append(TierBreakdownLine("First 30 units", u1, rate1, u1 * rate1))
    if u2 > 0:
        breakdown.append(TierBreakdownLine("Units 31-60", u2, rate2, u2 * rate2))
    if u3 > 0:
        breakdown.append(TierBreakdownLine("Units 61-90", u3, rate3, u3 * rate3))
    if u4 > 0:
        breakdown.append(TierBreakdownLine("Units 91+", u4, rate4, u4 * rate4))

    return BillResult(
        previous_reading=prev,
        current_reading=curr,
        units_used=units_used,
        tier=tier,
        value=value,
        fixed_fee=fee,
        total=total,
        breakdown=breakdown,
        formula=formula,
    )


def quantize_money(amount: Decimal) -> Decimal:
    return amount.quantize(_d("0.01"))