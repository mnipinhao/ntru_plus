# P135: NTRU+768 poly_frombytes_encap, measured before touching production

Question: does the run/pair idea from P133 apply to 768's encaps decoder, and
what is it worth?

## Layout (perm.c, perm.txt, encap_halves.h)

Each 4-lane half of each of the 96 output vectors of the production
`poly_frombytes_encap` holds four consecutive, 4-aligned wire coefficients,
i.e. six contiguous bytes.  All 192 halves start at distinct offsets; only two
(vectors 48 and 49, offsets 1146 and 1140) would read past byte 1152 with a
16-byte load.  So one output vector = two 16-byte loads + one `tbl` (two
registers) + a per-lane shift and mask, with no transpose at all.

## Prototype (frombytes_encap_pairs.c, C intrinsics)

Per vector: 2 loads, `tbl` {0,1,1,2,3,4,4,5 | 16,17,17,18,...}, `ushl`
(0,-4,...), `bic` to 12 bits, running `umax`, 1 store; the two late halves load
the 16 bytes ending at 1152 with the index shifted.  One compare at the end,
no data-dependent branch.  clang: 762 instructions (production: 1,107), 79 of
them address `add`s a hand-written version would fold into immediates.

check.c: bit-identical to production on 200,000 inputs (canonical and random),
input ending at a guard page, and every one of the 768 positions rejected when
it alone is out of range.  Same result on M2 and on the Pi.

## Timing

Per call (bench.c, same binary, best of 400x100):

| | production | prototype | |
|---|---:|---:|---:|
| M2 Pro | 65.5 ns (~229 cyc) | 37.5 ns (~131 cyc) | -43% |
| Cortex-A76 | 502.6 cyc | 328.8 cyc | -35% |

(Official's decoder on M2 was ~130 cycles in P104: the prototype closes that gap.)

KEM level (kem_ab.sh: only kem.c's call swapped; P129 harness, three sessions,
all identical to within a few ns):

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 base / prototype (ns) | 3,795 / 3,790 | 4,080 / 4,040 (**-1.0%**) | 3,107 / 3,106 |
| A76 base / prototype (ns) | 13,130 / 13,136 | 12,267 / 12,188 (**-0.64%**) | 11,354 / 11,354 |

keygen does not call the decoder; its +6 ns on A76 (+0.05%) is layout.

## Upper bound of a hand-written version

- M2: 192 loads + 96 stores + ~480 SIMD ops; the prototype at ~131 cycles is
  already near the load/store floor.  Folding the address adds is worth maybe
  10-20 cycles (<6 ns, ~0.1% of encaps).
- A76: two-register `tbl` is two µops, so ~6 SIMD µops/vector on two pipes
  ~= 290 cycles; the prototype is at 329.  `ldr d` + `ld1 {.d}[1]` + one-register
  `tbl` is ~5 µops/vector ~= 240 cycles: at most ~-90 cycles more (~-0.3% of
  encaps).

## Decision input

Promotion rules: encaps gains on both machines, decaps unchanged, keygen
within layout noise.  The prototype alone takes most of the available gain;
landing it as a C file (as 864's unpack.c) replacing pack.S's
`poly_frombytes_encap` is the proportionate step.  A hand-scheduled A76
variant is optional, worth a further ~0.3% of encaps on A76 only.

## Integration (branch gt768-frombytes-encap, from main 4aa65073)

`unpack.c` replaces the `unpack.S` section of `pack.S` (-1,162 lines); same
symbol and signature, so kem.c, encap.h and the ABI sentinel are unchanged.
The two late vectors (48, 49) are peeled out of the loop, so nothing depends
on the compiler resolving the load offsets; `#pragma GCC unroll` is still
required for speed: without it the loop runs at 48.3 ns on M2 against 37.9
(bench3.c; the first SUPERCOP run caught this at -18 cycles on encaps and was
discarded).

Checks:

- check.c against the previous decoder, via prod_shim.c: 0 mismatches on
  200,000 inputs, 768/768 single out-of-range positions, M2 and Pi;
- `make check` (KAT byte-identical, canonical-boundary 9,216 cases, ABI
  masks, zeroization, release check) on macOS and Linux;
- TIMECOP (timecop.sh, P119 staging, the exported leaf as `gt-p135`): pass at
  -O, -O2, -O3, -Os with TIMECOP=16 and TIMECOP=256.

Per call, same binary (bench3.c):

| | previous asm | unpack.c |
|---|---:|---:|
| M2 (clang) | 65.5 ns | 37.9 ns |
| A76 (gcc -O3) | 502.6 cyc | 323.6 cyc |
| A76 (gcc -march=native, SUPERCOP's flags) | 502.6 cyc | 326.0 cyc |

SUPERCOP 20260831 on the Pi 5 (supercop_run.py = P119's run.py with the P135
trees; six rotated rounds, core 3; `throttled=0x50000` at every reading
including the first, i.e. sticky bits from before the session, current bits
clear; Official's numbers match P119 within 0.1%):

| cycles, median | Official | GT before | GT after | after - before |
|---|---:|---:|---:|---:|
| keypair | 38,425.5 | 31,638.0 | 31,653.5 | +15.5 (+0.05%) |
| enc | 38,600.5 | 29,439.5 | 29,276.5 | **-163.0 (-0.55%)** |
| dec | 33,586.0 | 27,320.0 | 27,319.5 | -0.5 (0.00%) |

Paired rounds: enc -163, -148, -177, -176, -182, -148 (all six); keypair +63,
-17, -92, +50, -51, +32 (noise, the decoder is not on its path); dec within
+-8.

Package harnesses (tree_ab.sh / build_hasheq.sh, each tree from its own
Makefile source list):

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 perop5 (ns) before / after | 3,789 / 3,788 | 4,079 / 4,039 (-1.0%) | 3,105 / 3,106 |
| M2 bench_min (ns) before / after | 3,827 / 3,826 | 4,134 / 4,106 (-0.7%) | 3,111 / 3,111 |
| A76 bench_min (cyc) before / after | 31,677 / 31,642 | 29,654 / 29,469 (-0.62%) | 27,252 / 27,248 |

Hash layer held equal (P120's three builds, same digest for all five):
GT + Official hash vs Official on the A76 is -5.7% / -4.1% / -5.6% (before:
-5.7% / -3.8% / -5.6%).

Linked text of test_kem (Linux, gc-sections): 91,514 -> 89,898 B.
