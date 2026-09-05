# D1-P3B2 — composed byte-routing network search

This static/machine gate composes the authoritative FR0↔Official permutation
with the exact stock NTRU+864 `poly_shuffle2/poly_shuffle` coefficient maps.
The targets are the layouts immediately consumed or produced by the 12-bit
packer, not an intermediate Official polynomial.

`analyze_composed.py` proves the maps and inverse, replays tagged and random
vectors, reconstructs the Q-vector graph and 48-coefficient packing blocks,
and emits comparable machine ledgers. `audit_results.py` enforces the gate.

Run:

```sh
make audit
```

This gate intentionally does not implement serialization, benchmark cycles or
run Slothy. P3B3 must implement the same full byte boundary for M0, C1 and C2,
then use byte-exact correctness and Pi 5 PMU to select a candidate.
