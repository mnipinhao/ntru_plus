# Decision

Status: `keep_as_algebra_oracle`

The root gate passes. The exact current leaf-root set admits the declared
9-by-32 grid, and the current leaf order has a stable bijection to that grid.

This decision permits the next default-off direct scalar
evaluation/interpolation experiment. It does not prove the forward transform,
inverse transform, Montgomery scale placement, coefficient bounds, or the
campaign's arithmetic CRT permutation as the correct physical transform order.
It therefore does not permit Neon implementation or timing.

Production default changed: no.
