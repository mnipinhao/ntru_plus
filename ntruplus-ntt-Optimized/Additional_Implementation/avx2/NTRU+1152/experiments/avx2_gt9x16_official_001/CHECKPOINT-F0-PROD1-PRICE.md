# Checkpoint F0-PROD1-PRICE

## Outcome

The production-shaped P1-H producer is correct but slower than the legacy
Official-transform-plus-adapter path. The serious producer-only comparison is
SUPERCOP-derived, uses one pinned P-core, one SUPERCOP-selected O2 measure ELF,
balanced order, 9 fresh processes, and 96 observations per named operation per
launch. It is not a native KEM result.

Both paths start from resident aligned coefficient-domain `[-1,1]` inputs and
end at the same materialized scale-four F0 contract. Input regeneration is
outside the timed region. P1-H retains the intentional 2,304-byte top-split
materialization and does not add representative centering.

## Serious result

Pooled balanced StQ2 values are:

| region | Legacy Official + adapter | P1-H | pooled delta |
| --- | ---: | ---: | ---: |
| one forward | 1607.8611 | 1766.9745 | +159.1134 |
| two forwards back-to-back | 3040.8750 | 3299.0463 | +258.1713 |

The paired per-launch median deltas are +158.7083 cycles for one forward and
+259.1875 cycles for two forwards. P1-H is slower in 9/9 launches for both
comparisons. The two-forward result is measured directly; it is not inferred
as twice the one-forward delta.

The requested screening credit is therefore -259.1875 cycles per two
forwards. It is in the poor/insufficient class and moves in the wrong direction
relative to the approximate +1,312-cycle MA2 encapsulation deficit.

## Attribution

Reset-only-subtracted `perf stat` diagnostics over 4,096 operations give:

| one forward | retired instructions | retired loads | retired stores |
| --- | ---: | ---: | ---: |
| Legacy | 4348.006 | 791.001 | 364.000 |
| P1-H | 4238.011 | 959.003 | 299.000 |
| P1-H - Legacy | -109.995 | +168.002 | -65.000 |

The two-forward counters scale consistently: Legacy/P1-H retire approximately
8701/8481 instructions, 1580/1916 loads, and 730/600 stores. These counters are
diagnostic attribution, not the timing headline.

P1-H's static ledger remains unchanged: 576 formation-routing instructions,
72 pre-twist Montgomery chains, 24 R2 radix-3 bodies, and four D1/R2-second
helper executions per forward. Its wrapper makes one top-split plus four pair
helper calls; Legacy makes one `poly_ntt` plus one adapter call. P1-H saves
instructions and stores but raises retired loads enough that the direct generic
F0 formation does not become a machine-level win.

## ELF and host controls

The formal replay ELF SHA-256, compiler identity, complete symbol placement,
symbol sizes, `.text`/`.rodata` sizes, raw launch observations, raw perf output,
and source hashes are stored with the result. All relevant benchmark wrappers
and P1-H symbols are 32-byte aligned. The serious preflight records CPU 1 as a
performance core with the `performance` governor and Intel turbo disabled.

During the first campaign build, the flat implementation exposed a basename
collision between `src/f0_prod1_p1h.c` and `asm/f0_prod1_p1h.S`. The C wrapper
was mechanically renamed to `src/f0_prod1_wrapper.c`; arithmetic, symbols, and
the P1-H ABI did not change. The rebuilt flat directory contains distinct C and
assembly objects.

## Decision

P1-H remains a correctness and attribution control, but the generic F0 ABI is
rejected as the next encapsulation-integration boundary. A/B/C MA2 caller
integration is not authorized. Top-split fusion, removal of its 2,304-byte
materialization, and blind per-map routing superoptimization also remain out of
scope.

The next checkpoint is a source/destination movement graph for a specialized
producer tail:

```text
unchanged top split
-> frozen R2 / D1 arithmetic
-> directly emit MA2 coefficient planes
-> MA2
```

This `F0-PROD2-MA2` investigation must first price which generic-F0 formation
and subsequent MA2 plane-formation movements can be removed. No assembly or
KEM benchmark is authorized by this checkpoint alone.
