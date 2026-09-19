# P60 — the fused terminal, built and measured

P60 changes no production code.  It builds the design P58 and P59 cleared: emit
the natural-order `ST3` inside the paired-I16 producer instead of running
`p29_main_route` as a separate pass.

- `emit.py` rewrites P28's allocated producer, replacing each output `str` with
  a normalise-and-deliver chain in physical registers.  Three kernels come out:
  `fused_bank2` (normalises its own output and keeps the store, since both halves
  are consumed later), `fused_bank0` (`ST3#1`) and `fused_bank1` (`ST3#2`).
- `emit_residual.py` covers the groups that cannot be fused.
- `verify_regs.py` is an independent check that no inserted chain clobbers a
  register the producer reads later.
- `schedule2.py` runs P59's phase-2 recipe, reorder-only.
- `finish.sh` installs the scheduled kernels, re-proves byte-identical output and
  measures both hosts.

Coordinate map: `n = top*432 + t*27 + row*3 + component`, so the ST3 base for
`(top,t)` is `864*top + 54*t`.  `ST3#1 = {b0.low, b0.high, b2.low}` at that base
and `ST3#2 = {b1.low, b1.high, b2.high}` at base+24.  The map is linear; no
permutation table is needed.

See [RESULTS.md](RESULTS.md).
