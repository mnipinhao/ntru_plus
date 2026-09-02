# M5U-CF0 — FR-ISO2 Forward live-out absorption

This default-off experiment measures the simplest zero-conversion Forward
producer for M5U-A's FR-ISO2 leaf basis.  It starts from the frozen M5R-D
Forward and, for component banks 1 and 2, applies the exact `tau` or `tau^2`
Algorithm-10 multiplication while all eighteen NTT9 output vectors are still
live.  The existing stores then write FR-ISO2 directly; there is no normalize
buffer, coefficient reload, or new coefficient-memory boundary.

The experiment is deliberately an attribution baseline rather than the final
scaled-NTT9 design.  Its 72 output multiplications and 72 paired constant loads
measure the upper bound that a future fused DAG must beat.

```sh
make check
python3 run_pi5.py       # authorized Pi 5 target: pi@100.99.191.9
```

The checked-in runner keeps raw PMU rows and synchronized build inputs under
ignored `build/`.  Production and the frozen local SUPERCOP `20260627` package
are unchanged.
