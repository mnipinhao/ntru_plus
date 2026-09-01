# M5F: forward NTT16/NTT9 Barrett composition gate

This experiment answers the register/layout question that must be closed
before writing the fused Forward assembly. It consumes the exact P8+tail ABI,
uses compile-time Algorithm-10 `(b,bprime)` tables for both NTT16 and NTT9,
and writes FR-0 directly. The C function is a readable schedule oracle, not a
performance implementation and not Production.

The important schedule is per `(top, component)` bank. Gather the sixteen
`s=8` halfwords in bit-reversed order into two Neon registers and finish that
NTT16 within lanes. Keep its two eight-column outputs live. Then load the
sixteen main `t` vectors once, perform lane-wise NTT16, transpose one
eight-column block in place, attach the matching tail vector, and run NTT9.
Repeat for the other block. Thus every meaningful P8 coefficient is loaded
once in pass 2 and every FR-0 coefficient is stored once; no NTT16 result is
materialized in memory.

M5F-r2 first proved that the original four-product B3 schedule needs no
identity reductions. M5G then changes the B3 instruction DAG itself. It uses
only the two mathematical products by `rho` and `rho2`, and derives the third
output as `(a-y0)+(a-y1)+a`. The correlation-aware proof bounds NTT16 by 9342
and every node in this exact two-product Forward DAG by 28568. Therefore
`s=0`, `b0`, and `c0` remain unreduced. M5F-r2 remains the historical proof
for the old four-product schedule; it must not be used as the range proof for
this changed arithmetic order.

`prove_schedule.py` proves exact P8 coverage, untouched padding, the range
bound, and a maximum 24 caller-saved-vector register budget. The intended
assembly uses four-way expansion only during main NTT16; the two-product NTT9
phase has an estimated 22-register peak while the other column block remains
live.

Run `make check`. Passing proves mod-q composition and schedule feasibility;
it does not prove handwritten code shape, Slothy scheduling, SUPERCOP cycles,
or full-KEM integration.
