# GT9X16 Forward OPT-V3: D1-v2 and NTT9 wavefront W1

## Scope

This checkpoint executes the deliberately small/large pair selected after the
Forward register-flow audit:

1. a complete D1 sign-orientation peephole candidate; and
2. a conservative one-row NTT9-to-NTT16 wavefront schedule.

The frozen wire ABI, scale-1 contract, Natural-Q identities, paper-R2
arithmetic, reduction mask, and caller graph are unchanged.

## Small result: D1 sign orientation v2

The exhaustive orientation search permits the D1 plus/minus convention to be
changed lane-wise when the matching constant is negated.  Two additional
tiles (`b0/p2` and `b1/p7`) then reach the frozen wire ABI without their final
byte shuffle.

The namespaced linked candidate has the following exact delta:

| linked metric | control | D1-v2 | delta |
|---|---:|---:|---:|
| instructions | 2779 | 2771 | -8 |
| `vpshufb` | 56 | 48 | -8 |
| `vpermq` | 72 | 72 | 0 |
| `vperm2i128` | 72 | 72 | 0 |
| Montgomery / Barrett | unchanged | unchanged | 0 |
| `.text` | 15449 B | 15377 B | -72 B |
| `.rodata` | 12192 B | 12416 B | +224 B |

The differential covers zero, alternating input, 1003 random small inputs,
and both signs of every impulse.  It checks canonical equality, the proven
signed-i16 range, unaligned state, and front/tail canaries.  ASan/UBSan and the
no-call/no-frame/no-spill/no-branch/no-`vzeroupper` linked gates pass.  The
candidate also passes the installed SUPERCOP implementation KAT.

### Native SUPERCOP result

Both campaigns use pinned SUPERCOP 20260627, CPU 1, nine fresh processes and
864 observations per KEM operation.  Native compiler selection was allowed,
as required for this layer.

| campaign | control compiler | candidate compiler | control `enc` StQ2 | candidate `enc` StQ2 | delta |
|---|---|---|---:|---:|---:|
| 001 | GCC 15.2 `-O2` | GCC 15.2 `-O3` | 44094.95 | 43885.92 | -209.03 |
| 002 | GCC 15.2 `-O3` | GCC 15.2 `-O2` | 43890.22 | 44002.68 | +112.46 |

The compiler choice reversed between independent campaigns and the apparent
performance direction reversed with it.  These scheme-level deltas therefore
cannot be attributed to the removal of eight `vpshufb` instructions.  Under
the Native-SUPERCOP-only benchmark policy, D1-v2 remains a correctness-complete
peephole experiment and is **not promoted** to the research or production
baseline.

## Large result: conservative NTT9 wavefront W1

The current Forward stores all 72 NTT9 output vectors and later reloads all 72
for NTT16.  W1 does not attempt full zero-copy.  It retains exactly one output
row per branch across the four q-block calls and immediately feeds that row to
NTT16; the other eight rows retain the current materialized boundary.

The enabling change is a register-renamed, low-temporary realization of the
existing 12-instruction radix-3 macro.  With
`P = kappa*(B-C)`, exact affine replay proves both realizations produce:

```text
out0 = 2A + 2B + 2C
out1 = 2A - B - C + P
out2 = 2A - B - C - P
```

The candidate changes only the physical destinations:

```text
C = out0
B = out1
S = out2
```

It adds no instructions, constants, multiplication chains, reduction, or
representative change.

### Register flow

| q-block | retained rows before current block | nine NTT9 data | constants | R3 temp | peak |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 9 | 3 | 1 | 13 |
| 1 | 1 | 9 | 3 | 1 | 14 |
| 2 | 2 | 9 | 3 | 1 | 15 |
| 3 | 3 | 9 | 3 | 1 | 16 |

At the fourth q-block peak:

```text
ymm0..ymm3   retained selected row, q-blocks 0..3
ymm4         kappa_qinv
ymm5         kappa
ymm6         q
ymm7..ymm15  current nine NTT9 data vectors
```

After the last selected radix-3 group, the eight non-selected rows are stored
as today and the selected four-vector row runs through the existing NTT16
arithmetic before it is written to the final ABI.

The expected full-Forward boundary delta is:

```text
intermediate stores    -8 vectors
intermediate reloads   -8 vectors
bytes written          -256
bytes read             -256
extra moves             0
extra constants         0
recomputed arithmetic   0
```

Two retained rows are not authorized: at the fourth q-block they require 19
YMM registers with cached constants.  Moving constants to memory might fit but
introduces a separate load-port tradeoff that must be priced independently.

## Decision

- D1-v2: keep as an experiment; no baseline promotion because Native SUPERCOP
  cannot resolve its effect independently of compiler selection.
- W1: the one-row ASM prototype is authorized.  It must preserve the exact
  radix-3 arithmetic, current reduction mask and wire ABI, and must demonstrate
  exactly eight fewer stores and reloads with no spill or added constant load.
- Only Native SUPERCOP KEM measurement may decide whether W1 advances after
  correctness and linked structural gates.

Reproduce the local gates with:

```sh
make d1-wire-orientation-v2-check
make d1-wire-orientation-v2-sanitize
make ntt9-wavefront-w1-check
```
