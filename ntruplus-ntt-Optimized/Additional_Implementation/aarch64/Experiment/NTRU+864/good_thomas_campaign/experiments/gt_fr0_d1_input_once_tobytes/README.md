# D1-P3B6 — input-once composed-map ToBytes

This is the successor to rejected P3B5.  It targets the exact current AArch64
byte ABI, including `shuffle2`, without materializing Official or post-shuffle
coefficient arrays.

`prepare.py` generates the exact map, a peak-16 input order, and a straight-line
Neon core under `build/`.  Run `make check` on AArch64 for byte-exact and guard
tests.  Generated C, objects, disassembly and raw PMU logs remain ignored.

The Pi 5 result is 1502.463 cycles versus 1848.172 for the P3B4 `r9_to`
control.  This is a useful 18.71% improvement, but it misses the `<1250` cycle
promotion gate, so this directory remains an experiment and is not linked into
the selected full-KEM package.  See `results.md` and `DECISION.md`.
