# D1-P3B11 — input-once composed-map FromBytes

This fixed-contract experiment is the inverse-side counterpart of P3B6.  It
targets the exact selected GT FR0 byte ABI and preserves every twelve-bit input
value, including noncanonical values in `[3457,4095]`.

`prepare.py` generates a peak-14 top-local schedule and straight-line Neon C
under `build/`.  The candidate reads each twelve-byte serialized group once,
uses no coefficient scratch, and stores an FR0 q-vector immediately when all
eight lanes have arrived.  P3B4 `c1_from` remains the baseline and Production
is unchanged.

Run `make check` on AArch64 for the independent scalar oracle and guarded-edge
tests.  `run_pi5.py` performs the paired Cortex-A76 correctness, object and PMU
gate.  That gate passed at 935.717 cycles versus 1181.090 for C1, with no
coefficient spill.  Full-KEM caller closure remains the next gate.
