# P0046 anchoring formulas

Scale clip range: (0.05, 20.0).

L1 level-only: `forecast[h] = shape[h] + mean(actual_anchor - shape_anchor)`.

L2 level + robust scale: ordinary least-squares slope on centered anchor values, forced finite/positive and clipped, then `level = mean(actual_anchor) - scale * mean(shape_anchor)`.

L3 shrink scale: same clipped L2 scale shrunk toward `1.0` with `weight = anchor_count / (anchor_count + 24)`.
