# P137: NTRU+1152 frombytes, measured before touching production

P136 left 1152 `frombytes` as the largest arithmetic deficit against
SUPERCOP's Official: +15 ns / +124 cycles a call, x3 in decapsulation.
P103 had called its transpose structural; P133 (864) showed a transposing
decoder can still beat Official.

## The production decoder's work

Per pair of groups (18 pairs, eight 12-byte blocks each): 8 loads, an 8x8
transpose (24 trn), two `unfold4` (16 ops), 8 umax, 8 stores = 48 SIMD ops.
18 x 48 = 864 ops: an M2 floor of 216 cycles (~62 ns) against 70 measured;
Official needs ~576 (no transpose: its blocks are contiguous).

## Table lookups are cheaper than their name (`ubench_tbl.c`)

| per op, independent | trn1 | tbl, 1 reg | 2 regs | 3 regs | 4 regs |
|---|---:|---:|---:|---:|---:|
| M2 (4 SIMD ops/cycle) | 1 | 1 | **1** | 2 | 3.5 |
| A76 (2 V pipes) | 1 | 1 | **1** | 2 | 3 |

A two-register `tbl` costs one `trn` on both machines.

## Candidate A: the first transpose level and the byte expansion in one tbl

`frombytes_tbl2.c`: per block pair (2j, 2j+1), one `tbl` per half gathers
the halfword of coefficient i of both blocks as a 32-bit unit (bytes
floor(3i/2), +1); `trn .4s` and `trn .2d` finish the transpose; each output
vector then needs one `and 0xfff` (even i) or `ushr 4` (odd i), the same for
every lane.  8 tbl + 16 trn + 8 + 8 umax = **40 ops a pair (-17%)**.  The one
block past the end (pair 17, lane 7, byte 1716) loads the 16 bytes ending at
1728 with its indices shifted by four.  (Four-register tbl, which would save
the .4s level, costs 3-3.5 ops and loses.)

gcc cannot load a `uint8x16x2_t` into a consecutive register pair and emits
**270 `mov.16b`**: free on M2 (move elimination), one V-pipe op each on the
A76.  `gen_asm.py` emits the same algorithm as assembly with every load in
its tbl's register pair (v0-v7, v16-v29; v8-v15 untouched); `--imm` uses
immediate offsets where the encoding allows.  `--interleave` (next pair's
loads before this pair's transpose) needs moves and loses 36 cycles on the
A76.

Correctness (`check.c`, M2 clang and A76 gcc, C and asm): identical to
production on 200,000 inputs (half canonical, half random), and at each of
the 1,152 positions an out-of-range coefficient is rejected with identical
output; the input ends at a guard page.

## Per call, same binary (`bench.c`)

| | production | A, C | A, asm `--imm` | Official |
|---|---:|---:|---:|---:|
| M2 Pro (ns) | 70.0 | 52.1 | **54.6** | 54.6 |
| Cortex-A76 (cyc) | 607-612 | 595 | **478.6** | 485.7 |

The C version is 2.5 ns better on M2 and 116 cycles worse on the A76; the
assembly is the one that wins on both.

## KEM level (`kem_ab.sh`: only api_glue.c's poly_frombytes swapped; P129 harness, three sessions)

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 base / asm (ns) | 6,425 / 6,424 | 6,120 / 6,106 (-0.25%) | 4,950 / 4,909 (**-0.83%**) |
| A76 base / asm (ns) | 23,886 / 23,887 | 19,190 / 19,132 (-0.30%) | 17,971 / 17,799 (**-0.95%**) |

## What is left

- M2: 40 ops x 18 / 4 = 180 cycles (~51 ns); the asm is at 54.6.  ~3.6 ns
  a call remains, ~11 ns of decapsulation.
- A76: 720 V-pipe ops / 2 = 360 cycles against 479.  Up to ~120 cycles a call
  (~360 of decapsulation, ~0.8%) is not accounted for by the op count;
  loads/stores (144 + 144) are well under their limits.  Closing it would need
  cross-pair scheduling without moves, i.e. more registers (v8-v15 with a
  d8-d15 save).  Not attempted.

## Integration (branch gt1152-frombytes-tbl2, from main 21a1de6a)

`unpack.S` = `gen_asm.py codec_pairs.h --imm --symbol frombytes_asm`: the
body is byte-identical to the measured `frombytes_tbl2_asm.S`, only the
entry name and header differ.  `pack.c` loses the C decoder with `load12` and
`unfold4`; `api_glue.c` and `pack_asm.h` are unchanged.

The first SUPERCOP run failed to link the new leaf (`undefined reference to
frombytes_asm`): `export_supercop.py` keeps its own source list and did not
ship `unpack.S`, and `export-check` only checks that the export is
deterministic.  The script now compares its lists with the Makefile's
`C_SRC`/`ASM_SRC` and refuses to export on a difference (checked by dropping
`unpack.S` from its list).  864's lists match its Makefile today.

Checks: `make check` on macOS and Linux (KAT, 13,824 canonical-decode cases,
ABI mask 0 for `frombytes`); TIMECOP=256 passes at -O, -O2, -O3 and -Os (timecop.sh, the exported leaf as `gt-p137` in the P119 staging).

SUPERCOP 20260831 on the Pi 5 (`supercop_run.py`, six rotated rounds, core 3;
`throttled=0x50000` at every reading, the sticky bits of P135):

| cycles, median | Official | GT before | GT after | after - before |
|---|---:|---:|---:|---:|
| keypair | 63,901 | 54,780 | 54,683 | -97 (noise: +-7,000 between rounds) |
| enc | 59,005 | 46,039.5 | 45,886.5 | **-153 (-0.33%)** |
| dec | 52,505.5 | 43,405.5 | 42,966.5 | **-439 (-1.01%)** |

Paired rounds: dec -333, -428, -450, -454, -390, -517; enc -136, -139, -151,
-195, -125, -199.  keypair moves by thousands between rounds either way:
29% of 1152's f/g candidates fail inversion, and SUPERCOP's RNG differs
from round to round.  Against Official: dec -17.33% -> -18.17%, enc -21.97% ->
-22.23%.

M2, P129 harness, the two trees (`tree_ab.sh`, three sessions): keygen
6,429 / 6,428, encaps 6,122 -> 6,105 (-0.26%), decaps 4,952 -> 4,907 (-0.91%).
