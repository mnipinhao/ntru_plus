# P130 — M2's thinnest cell, 864 decapsulation: overheads around the arithmetic

P129 left 864 decapsulation at -2.9% on M2 with the Keccak held equal, and
P127 showed GT's decapsulation *arithmetic* ~60 ns behind Official's there.
The unexamined pieces were the codec and the first product.  Callgrind
(`cg_comp.c`, `cg.sh` on the Pi, per call):

| | GT | Official | what differs |
|---|---|---|---|
| first product | 1,724 SIMD, 576 scalar, 72 `dup` | 1,724 SIMD, 136 scalar | identical arithmetic; 36 per-tile calls re-materialise constants |
| `tobytes` (full) | 958 SIMD, **288 stores** | 1,080 SIMD, 108 stores | each 9-byte run = 8-byte store + 1-byte lane store |
| `frombytes` | 592 SIMD + **388 lane inserts** + 108 lane loads | 1,082 SIMD | 12-byte load split in three; outputs built 64 bits at a time |

## Knockout upper bounds (`knockouts.py`, timing only)

| | M2 per call | A76 per call |
|---|---:|---:|
| frombytes: one 16-byte load per group (A) | -5.4 ns | -64 |
| frombytes: no half-inserts (B) | -8 ns | -81 |
| frombytes: A + B | -14.5 ns | -158 |
| tobytes: every run one 16-byte store | -12 ns full, -12 small | -195 full, -144 small |

## What landed

1. **A, exactly**: one 16-byte load per group; the group at byte 636 of a half
   loads the 16 bytes ending at its last byte.  AddressSanitizer on exact-size
   heap buffers (`asan_fb.c`): clean; with the plain load it reports the
   overflow.  (B is a real redesign -- the inserts are also 16- and 32-bit
   element scatters -- and was not attempted.)
2. **First product in one call**: the Slothy tile body loops over the 36
   tiles itself; constants set once (nothing in the body writes v2/v5).
3. **tobytes with 16-byte stores where safe**: a run's seven extra bytes may
   land in a neighbouring run that is written later.  `gen_store_order.py`
   searches the group and lane order (any order gives the same bytes), picks
   forward/backward/split per run, and verifies by simulating every byte's last
   writer: 113 of 144 runs take one store, 288 stores become 175.

## Result (min of blocks, deterministic RNG)

| | M2 keygen / encaps / decaps | A76 keygen / encaps / decaps |
|---|---|---|
| before | 4,169 / 4,752 / 3,874 ns | 36,770 / 35,802 / 34,091 cyc |
| after | 4,146 / 4,731 / **3,824.5** ns | 36,449 / 35,505 / **33,652** cyc |
| | -0.55% / -0.45% / **-1.28%** | -0.87% / -0.83% / **-1.29%** |

In P129's harness against the same Official builds (median of three sessions):

| 864 | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2, vs Official + CE | -9.4% | -11.2% | **-7.8%** (was -6.6%) |
| M2, Keccak held equal | -6.0% | -6.4% | **-4.2%** (was -2.9%) |
| A76, Keccak held equal | -10.8% | -12.1% | **-9.4%** (was -8.1%) |

KAT, M2 + Linux `make check` (incl. 10,368 canonical-decode cases), TIMECOP
(`-O`..`-Os`) pass.
