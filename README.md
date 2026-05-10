# Tiered Bill Calculator

A terminal-based electricity bill calculator. Enter two meter readings and get an instant tiered breakdown.

<img height="30px" src="https://ziadoua.github.io/m3-Markdown-Badges/badges/Python/python3.svg">

<div>
<img height="20px" src="https://m3-markdown-badges.vercel.app/stars/8/1/ravmax-rdl/tiered-bill-calculator">
<img height="20px" src="https://m3-markdown-badges.vercel.app/issues/8/1/ravmax-rdl/tiered-bill-calculator">
</div>

## Tier rules

Let `k = current_reading − previous_reading` (units consumed).

| Tier      | Condition      | Formula                                    | Fixed fee | Total       |
|-----------|----------------|--------------------------------------------|-----------|-------------|
| low       | k ≤ 30         | value = k × 5                              | +800      | value + 800 |
| normal    | 30 < k ≤ 60    | value = 30×5 + (k−30)×10                  | +800      | value + 800 |
| high      | 60 < k ≤ 90    | value = 30×5 + 30×10 + (k−60)×20          | +800      | value + 800 |
| very high | k > 90         | value = 30×5 + 30×10 + 30×20 + (k−90)×30  | +800      | value + 800 |

## Requirements

- Python ≥ 3.14.3

## Interactive TUI

```bash
python -m tiered_bill_calculator
```

The TUI runs in your existing terminal window:

1. Enter the **previous month reading** and press Enter.
2. Enter the **current reading** and press Enter.
3. The result screen shows the color-coded tier, full calculation, and a slab breakdown table.
4. Press **Enter** to recalculate or **Q** to quit.

Previously entered values are shown in brackets as defaults — press Enter to reuse them.

To disable screen clearing:

```bash
python -m tiered_bill_calculator --no-clear
```

## One-shot (non-interactive) mode

Print a single plain-text report without entering the TUI:

```bash
python -m tiered_bill_calculator --previous 100 --current 140
```

Example output (`k = 40`, normal tier):

```
                        Tiered Bill Calculator
--------------------------------------------------------------------------------
+----------------------------+
| Previous reading : 100     |
| Current reading  : 140     |
| Units used (k)   : 40      |
| Tier              : normal |
+----------------------------+

+-------------------------------------+
| Calculation                         |
| k         : 40                      |
| Formula  : Value = 30*5 + (k-30)*10 |
| Value    : 250.00                   |
| Fixed fee: 800.00                   |
| Total     : 1050.00                 |
+-------------------------------------+

Breakdown
+-------------------------------------------+
| Slab           | Units | Rate  | Subtotal |
| ---------------+-------+-------+--------- |
| First 30 units | 30    | 5.00  | 150.00   |
| Next 30 units  | 10    | 10.00 | 100.00   |
+-------------------------------------------+
```

## Tests

```bash
python -m unittest discover -s tests
```

Covers all four tier boundaries, exact value/total figures, and the
invalid-input error case (current reading < previous reading).

## Documentation

| Document | Contents |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Module map, data-flow diagram, design principles |
| [docs/bill-logic.md](docs/bill-logic.md) | Tier rules, rate table, worked example, edge cases |
