# Bill Calculation Logic

## Overview

The bill is calculated from two meter readings. The difference between the
current and previous reading gives the number of units consumed (`k`). Units
are priced in progressive tiers; a fixed fee is added on top.

All arithmetic uses `decimal.Decimal` throughout to guarantee exact results
with no floating-point rounding errors.

## Variables

| Symbol | Meaning |
|---|---|
| `k` | Units consumed: `current_reading − previous_reading` |
| `value` | Energy charge computed from tier rates |
| `total` | Final bill: `value + 800` (fixed fee) |

## Tier rules

| Tier | Condition | Formula |
|---|---|---|
| low | k ≤ 30 | `value = k × 5` |
| normal | 30 < k ≤ 60 | `value = 30×5 + (k−30)×10` |
| high | 60 < k ≤ 90 | `value = 30×5 + 30×10 + (k−60)×20` |
| very high | k > 90 | `value = 30×5 + 30×10 + 30×20 + (k−90)×30` |

The fixed fee of **800** is added to `value` regardless of tier to produce `total`.

## Rate table

| Slab | Units covered | Rate per unit |
|---|---|---|
| First bracket | 1 – 30 | 5 |
| Second bracket | 31 – 60 | 10 |
| Third bracket | 61 – 90 | 20 |
| Fourth bracket | 91 + | 30 |

## Implementation in `bill.py`

The four bracket amounts are computed with `min`/`max` expressions so a single
code path handles all tiers:

```python
u1 = min(units_used, 30)                          # first  30 units at  5
u2 = min(max(units_used - 30, 0), 30)             # next   30 units at 10
u3 = min(max(units_used - 60, 0), 30)             # next   30 units at 20
u4 = max(units_used - 90, 0)                      # remainder      at 30

value = u1*5 + u2*10 + u3*20 + u4*30
total = value + 800
```

The tier label and formula string are derived from `units_used` separately
for display purposes.

## Worked example

**Inputs:** previous = 100, current = 140

**Step 1 — units used:**
```
k = 140 − 100 = 40
```

**Step 2 — tier:**
```
30 < 40 ≤ 60  →  tier = normal
```

**Step 3 — bracket split:**
```
u1 = min(40, 30)              = 30   (@ 5  each → 150)
u2 = min(max(40−30, 0), 30)  = 10   (@ 10 each → 100)
u3 = 0
u4 = 0
```

**Step 4 — value and total:**
```
value = 30×5 + 10×10 = 150 + 100 = 250
total = 250 + 800 = 1050
```

## Edge cases

| Scenario | Behaviour |
|---|---|
| `k = 0` (readings identical) | Tier = low, value = 0, total = 800 |
| `current < previous` | `ValueError` raised; TUI shows inline error |
| Non-numeric input | `ValueError` raised via `parse_reading()`; TUI prompts again |
| Decimal readings (e.g. 123.5) | Fully supported; `Decimal` preserves exact precision |
