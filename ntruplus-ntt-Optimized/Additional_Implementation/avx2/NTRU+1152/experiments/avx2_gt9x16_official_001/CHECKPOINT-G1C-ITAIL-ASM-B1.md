# Checkpoint G1C-ITAIL-ASM-B1

## Decision

Implement the exact B1R reduction cover and retain B1 as the inverse-NTT9
kernel candidate.  Relative to B0, B1 removes only the inter-layer Barrett
reducers on physical-P wires 1 and 2.  Input reduction, the `{0,3,6}`
inter-layer cover, all final Barrett reductions, and centered-output
corrections are unchanged.  This is a selected experiment kernel, not a clean
production promotion.

## Correctness and static attribution

B1 passes the independent inverse-DFT matrix oracle, B0 differential, 1,003
arbitrary transform inputs, 257 real C2 producer inputs, all nine basis
vectors, in-place alias, input immutability, output range, canary, ASan, and
UBSan gates.

The linked-object audit proves the only arithmetic delta from B0 over the
eight vector inverse9 bodies:

| Instruction | Delta versus B0 |
| --- | ---: |
| `vpmulhrsw` | -16 |
| `vpmullw` | -16 |
| `vpsubw` | -16 |
| Total | -48 |

The 80 Montgomery chains, 15-YMM peak, zero spills, and leaf properties are
unchanged.  There are no calls, conditional branches, frames, stack accesses,
lane permutations, or `vzeroupper`.

## SUPERCOP-derived serious price

The formal primitive price uses pinned SUPERCOP 20260627 in a disposable
campaign, candidate implementation `avx2-gt9x16-exp001`, CPU 1, performance
governor, turbo disabled, and the fixed O3GC compiler recipe.  A single
SUPERCOP-built measure ELF executes B0-first/B1-second and
B1-first/B0-second slots.  Nine fresh launches produce 1,728 balanced
observations per combined kernel.

| Complete eight-vector inverse9 | SUPERCOP StQ2 cycles |
| --- | ---: |
| B0 | 902.7917 |
| B1 | 890.0000 |
| Pooled B1 - B0 | -12.7917 (-1.42%) |

The per-launch StQ2 delta has median -12.9792 cycles and is negative in 9/9
launches.  This is labelled `supercop-derived-itail`; it is not native
SUPERCOP KEM output and cannot by itself promote production.  The exact ELF,
lock, metadata, SUPERCOP data, fresh output, and stabilized-quartile report are
under `results/itail-asm-b1-supercop-derived-intel155h-20260824-003/`.

## Next gate

Freeze B1 as the inverse9 arithmetic control.  The next architectural test is
the live D8-to-inverse9 handoff: determine whether two physical-P triads can be
scheduled directly from producer registers without increasing Montgomery
chains or paying a lane permutation.  First build the exact register-lifetime
and range contract; only then implement a linked variant and price it against
the materialized B1 control.  Native SUPERCOP KEM benchmarking remains gated
on a complete caller path.
