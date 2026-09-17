# GT9X16 Forward OPT-V4 W1 ASM and Native result

## Scope

W1 is a namespaced one-row NTT9-to-NTT16 wavefront.  It keeps final `p=5`
live across the four q-blocks of each branch, immediately executes the frozen
NTT16/wire epilogue for that row, and leaves the other eight rows on the
existing materialized boundary.

The arithmetic DAG, scale-1 gauge, reduction mask 79, twiddles, wire ABI and
caller are unchanged.  The candidate is not installed into production.

## Machine realization

The low-temporary R3 rotates its scratch through the dead old-A register and
produces the same representatives exactly:

```text
C = 2A + 2B + 2C
B = 2A - B - C + kappa(B-C)
S = 2A - B - C - kappa(B-C)
```

At q-block 3 the exact peak is 16/16 YMM:

```text
ymm0..ymm3   retained p=5, q-blocks 0..3
ymm4..ymm6   kappa_qinv, kappa, q
ymm7..ymm15  current NTT9 data
```

Linked control-to-W1 delta:

| metric | control | W1 | delta |
| --- | ---: | ---: | ---: |
| instructions | 2779 | 2763 | -16 |
| rdi data loads | 144 | 136 | -8 |
| rdi data stores | 144 | 136 | -8 |
| RIP constant operands | 618 | 618 | 0 |
| `.text` | 15449 B | 15577 B | +128 B |
| `.rodata` | 12192 B | 12192 B | 0 |

Arithmetic and routing mnemonic counts are identical.  Both objects have
32-byte text/rodata alignment and aligned entries, with no call, branch,
`rsp` traffic, spill, frame, or `vzeroupper`.

The `+128 B` text correction is real: using low-numbered scratch/destination
registers changes VEX encoding geometry across the low-temporary R3 bodies,
more than offsetting the bytes removed with 16 `vmovdqu` instructions.

## Correctness gates

- raw bit-exact control/W1 output;
- zero and alternating inputs;
- 1003 random `[-1,1]` inputs;
- both signs of every one of 1152 impulses;
- signed-i16 envelope `[-21469,21469]`;
- deliberately unaligned state plus front/tail canaries;
- ASan/UBSan;
- existing wire-monotone Forward, serializer, H3 and complete-island
  regression suite;
- installed complete KEM KAT.

All gates pass.

## Native SUPERCOP

Source of truth is pinned SUPERCOP 20260831.  Each implementation used CPU 1,
performance governor, disabled turbo, nine fresh processes, 864 observations
per operation, unmodified `crypto_kem/measure.c`, and Native compiler
selection.  All three selected GCC 15.2 O3.

| implementation | keypair StQ2 | enc StQ2 | dec StQ2 |
| --- | ---: | ---: | ---: |
| Official `avx2` | 34312.56 | 43025.86 | 30502.56 |
| exp006 control | 34271.21 | 43812.84 | 30325.67 |
| W1 exp007 | 35046.90 | 43996.87 | 30349.71 |

The changed operation gives:

```text
W1 - control       +184.03 enc cycles
W1 - Official      +971.01 enc cycles
control - Official +786.98 enc cycles
```

Keypair and decapsulation retain the source path and are controls, not W1
credits.  The large W1 keypair movement shows that code placement/frontend
effects exist in separate Native ELFs, consistent with W1's unexpected text
growth.  This does not rescue W1: the predeclared gate required a negative
Native Encap direction before spending a fixed-ELF campaign on a 16-memory-op
change.

## Decision

W1 is **rejected for performance**.  It proves that the one-row wavefront is
arithmetically and register-feasible and that the exact 8+8 boundary deletion
can be realized without spill or constant traffic.  It does not prove that
this L1 boundary is machine debt; the Native caller became slower.

Do not implement the bounded W2 variants.  They remove only 2/4/6/8 more
stores and reloads than W1 while adding up to 76 constant-memory accesses, so
W1's failed machine control closes this same-DAG wavefront family.  Reopen the
axis boundary only with a materially different NTT9 microkernel or arithmetic
DAG.

The Forward roadmap moves to Phase 2: NTT9 arithmetic and alpha co-design.

## Evidence

```text
generated/ntt9-wavefront-w1-schedule.json
generated/ntt9-wavefront-w1-linked-audit.json
results/20260915-110748/ntt9-wavefront-w1-native-kat.json
results/w1-official-sc20260831-intel155h-20260915-001/
results/w1-control-sc20260831-intel155h-20260915-001/
results/w1-native-sc20260831-intel155h-20260915-001/
```
