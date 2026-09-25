# P138: all three sets, both machines, one session each; and where the permutation-equal lead comes from

GT at main a6524aea (after P135, P133/P134, P137).  Official is SUPERCOP
20260831's `ntruplus{768,864,1152}/aarch64` (768 copied from the Pi's
SUPERCOP tree; 864/1152 checked identical to it).  P129's harness and
builds, extended to 768: `perop5.c` / `perop5_pi.c`, RNG reseeded per batch,
min of 401 x 300 under the clock gate (M2), median of three round-robin
sessions; each GT tree built from its own Makefile's sources and CFLAGS
(`gtsrc.sh`).  Every build is output-checked (`check_out.sh`): within a set
all builds give the same pk / ct / ss digest, on both machines.

## Part 1: margins (ns, medians of three sessions)

**M2 Pro**

| set | GT keygen / encaps / decaps | vs SUPERCOP's Official | vs Official + CE | vs Official sponge + GT permutation |
|---|---|---|---|---|
| 768 | 3,792 / 4,038 / 3,106 | -15.5 / -22.7 / -19.5% | -8.7 / -15.7 / -16.0% | -5.1 / -11.7 / -12.8% |
| 864 | 4,114 / 4,638 / 3,751 | -16.1 / -22.5 / -18.5% | -9.6 / -11.7 / -9.4% | -6.1 / -6.8 / -5.8% |
| 1152 | 6,429 / 6,115 / 4,916 | -16.3 / -22.0 / -18.4% | -9.5 / -12.1 / -10.4% | -6.1 / -6.9 / -6.6% |

Official (ns): 768 4,485/5,223/3,860, +CE 4,154/4,790/3,698, sponge+GT perm
3,997/4,572/3,562; 864 4,901/5,987/4,600, 4,551/5,254/4,139, 4,383/4,977/3,981;
1152 7,680/7,841/6,022, 7,107/6,953/5,485, 6,848/6,570/5,264.

**Cortex-A76 (Pi 5, core 3)** -- no FEAT_SHA3; "sponge + GT permutation" is
Official's sponge calling GT's scalar permutation.

| set | GT keygen / encaps / decaps | vs SUPERCOP's Official | vs Official sponge + GT permutation |
|---|---|---|---|
| 768 | 13,137 / 12,192 / 11,354 | -18.0 / -24.1 / -18.6% | -10.2 / -13.4 / -11.7% |
| 864 | 15,089 / 14,571 / 13,779 | -17.9 / -24.1 / -18.6% | -10.7 / -12.8 / -10.9% |
| 1152 | 23,885 / 19,133 / 17,797 | -15.0 / -22.1 / -18.4% | -7.7 / -10.6 / -10.6% |

Official (ns): 768 16,026/16,068/13,949, sponge+GT perm 14,635/14,072/12,854;
864 18,386/19,186/16,927, 16,899/16,713/15,464; 1152 28,103/24,576/21,819,
25,865/21,403/19,904.

768's permutation-equal figures here (-10.2 / -13.4 / -11.7% on the A76) are
not comparable with P120's -5.7 / -4.1 / -5.6%: P120 replaced GT's whole hash
layer *and* its permutation by Official's C code.  This table uses the one
definition 864 and 1152 always used: only the permutation is equalised.

## Part 2: the permutation-equal lead is mostly the sponge on M2

"Keccak held equal" equalises the permutation but not the code around it.
A third build separates the two (`build_offhash.sh`): **GT's arithmetic and
KEM flow with Official's `symmetric.c` and sponge, the permutation GT's**
(`offhash_glue.c` supplies GT's `hash_g_fr0` as serialize + Official
`hash_g`).  Output-checked; `nm` confirms no GT hash function is linked.

- Official -> GT_offhash: same sponge and permutation: **arithmetic + KEM glue**.
- GT_offhash -> GT: same arithmetic: **GT's hash layer** (sponge, fixed-length
  hashes, prefixed absorb) alone.

Three builds, round robin, three sessions each (`split.py`):

| | keygen | encaps | decaps |
|---|---|---|---|
| M2 768: hash layer / rest (ns) | -209 / +2 | -522 / -16 | -367 / -88 |
| M2 864 | -224 / -46 | -307 / -34 | -178 / -53 |
| M2 1152 | -290 / -130 | -441 / -15 | -289 / -61 |
| **M2 hash-layer share** | **69-101%** | **90-97%** | **77-83%** |
| A76 768 (ns) | -600 / -900 | -1,191 / -684 | -713 / -788 |
| A76 864 | -658 / -1,148 | -1,121 / -1,016 | -603 / -1,077 |
| A76 1152 | -957 / -1,024 | -1,561 / -709 | -885 / -1,216 |
| **A76 hash-layer share** | **36-48%** | **52-69%** | **36-48%** |

Cross-checks:
- The "rest" matches P136's component sums of the arithmetic (M2 864
  -39 / -39 / -40 ns, 1152 -113 / -8.5 / -25; A76 864 -2,806 / -2,255 / -2,506
  cycles = -1,169 / -940 / -1,044 ns): the KEM glue itself is small.
- The hash layer matches a per-call bench of the hash functions
  (`hashbench.c`, both sides on GT's permutation), weighted by kem.c's calls:
  M2 864 -203 / -310 / -166 ns, 1152 -277 / -470 / -280; A76 864 -1,549 /
  -2,745 / -1,488 cycles, 1152 -2,251 / -3,799 / -2,114.

Per call (`hashbench_m2.txt`, `hashbench_pi.txt`): nearly all of it is
`hash_f` and `hash_g`, which absorb a whole polynomial (1,152-1,728 bytes):
M2 -123 to -205 ns a call, A76 -1,118 to -1,804 cycles.  The adapter that
gives Official's sponge GT's permutation is one `b`, so none of this is the
adapter.

### Why: step by step (`hashattr.c`)

Official's `hash_g` exactly as written (O0), then one difference removed at a
time, ending at GT's `shake256_prefixed`; all forms give the same digest, both
on GT's permutation.  NTRU+864 `hash_g` (1 + 1,296 bytes in, 216 out); 768 and
1152 have the same shape (`hashattr_m2.txt`, `hashattr_pi.txt`):

| step | M2 (clang), ns | A76 (gcc), cycles |
|---|---:|---:|
| O0 Official as written | 1,820 | 11,845 |
| upstream `load64` byte loop -> one 64-bit load | **0** (clang merges the loop into one `ldr`) | **-912** (gcc vectorises it into a ~240-instruction `uzp`/`zip`/`shll` byte network per block) |
| no clear of the input copy | -15 | -18 to -57 |
| final partial block absorbed by lanes, not byte by byte | **-128** | -140 to -273 |
| output straight from the state, not through `temp[]` | -4 | -40 to -44 |
| no input copy (domain byte absorbed in place) | -11 | -59 to -71 |
| GT `shake256_prefixed` | 1,667 | 10,552 |

(A76 ranges: the step measured with upstream's `load64` still in place, then
with it replaced -- `hashattr_pi_memcpyload.txt`; with it replaced, O4 equals
GT.)

- **The tail loop.**  Upstream absorbs the last `(inlen + 1) mod 136` bytes
  (65 / 73 / 97 for 768 / 864 / 1152 hash_f/g) with
  `s[i/8] ^= in[i] << 8*(i%8)`: per byte `ldrb`, `ldr` of the lane, `eor`,
  `str` of the lane (disassembly), and eight consecutive bytes hit the same
  lane, so each iteration waits for the previous store.  GT copies the tail
  into a zeroed 136-byte buffer and XORs 17 whole lanes.  The same loop is
  why `hash_h` differs so much between sets: its input is 129 bytes at 768
  (all of it tail: -229 ns), 141 at 864 (5-byte tail: -14 ns), 177 at 1152
  (41 bytes: -75 ns).
- **`load64` under gcc.**  Upstream assembles each lane from eight bytes in a
  loop.  clang recognises the idiom and emits one `ldr`; gcc 14 vectorises it
  across the 17 lanes of a block into byte transposes, ~90-100 A76 cycles a
  block.  GT's `load64` is a `memcpy` into a `uint64_t` (one unaligned load
  on both compilers).
- **The input copy and its clear** (`data[0] = domain; memcpy(data + 1, ...)`
  in `symmetric.c`, then `secure_clear`) cost 10-20 ns on M2 and 80-130 A76
  cycles together: real but small.  (The earlier version of this section put
  the copy first; the measurement does not.)

## What this changes

- On M2 the arithmetic lead over Official is small: -2 to -130 ns an
  operation.  The margins quoted as "Keccak held equal, the arithmetic
  alone" (864/1152 READMEs) are 69-101% sponge on M2 and 36-69% on the A76.
- On the A76 the arithmetic is about half of the permutation-equal lead,
  -700 to -1,200 ns an operation, mostly the forward NTT and the serializers
  (P136).

## Part 3: the two fixes applied to Official (`upstream_fix/`)

Upstream has three sponges: `CE/fips202.c` (the default build on GitHub,
`ntruplus/ntruplus` main; the file last changed 2026-07-16 and still has both
forms as of 2026-09-25), `NO_CE/fips202.c`, and SUPERCOP's `fips202.c` (a third
file).  `load64` is the byte loop in all of them; the byte-by-byte tail absorb
is only in `CE/fips202.c` (SUPERCOP's copy already absorbs the tail through a
buffer).

- `CE_fips202.diff`: `load64` as one `memcpy`; the tail through a zeroed
  buffer and whole lanes, as SUPERCOP's copy does.
- `SUPERCOP_fips202.diff`: `load64` as one `memcpy`.

Output-checked (same pk / ct / ss digests as the unmodified builds, both
machines).  `build_fix.sh`, `run_fix.sh`, `fix.py`; three round-robin
sessions, ns:

| | Official as shipped | with the fix | change | GT margin before -> after |
|---|---|---|---|---|
| M2, upstream default (CE), 768 | 4,158 / 4,791 / 3,700 | 3,942 / 4,364 / 3,373 | -5.2 / -8.9 / -8.8% | -8.8 / -15.7 / -16.0% -> -3.8 / -7.5 / -7.9% |
| M2, CE, 864 | 4,551 / 5,252 / 4,140 | 4,313 / 5,009 / 4,024 | -5.2 / -4.6 / -2.8% | -9.6 / -11.7 / -9.4% -> -4.6 / -7.4 / -6.8% |
| M2, CE, 1152 | 7,106 / 6,953 / 5,484 | 6,797 / 6,552 / 5,254 | -4.3 / -5.8 / -4.2% | -9.5 / -12.1 / -10.3% -> -5.4 / -6.7 / -6.4% |
| M2, SUPERCOP's, all sets | | | 0.0 to +-0.2% | unchanged |
| A76, SUPERCOP's, 768 | 16,027 / 16,070 / 13,951 | 15,547 / 15,274 / 13,526 | -3.0 / -5.0 / -3.0% | -17.9 / -24.1 / -18.6% -> -15.4 / -20.2 / -16.1% |
| A76, SUPERCOP's, 864 | 18,390 / 19,170 / 16,951 | 17,875 / 18,323 / 16,525 | -2.8 / -4.4 / -2.5% | -18.0 / -24.0 / -18.7% -> -15.6 / -20.5 / -16.6% |
| A76, SUPERCOP's, 1152 | 28,092 / 24,582 / 21,810 | 27,447 / 23,490 / 21,229 | -2.3 / -4.4 / -2.7% | -15.0 / -22.2 / -18.3% -> -13.0 / -18.5 / -16.0% |

- On M2 the SUPERCOP file gains nothing: clang already emits one `ldr` for
  the byte loop, and its tail is already buffered.
- The CE fix on M2 is almost all the tail loop (clang), and it is largest at
  768 because 768's `hash_h` input (129 bytes) is entirely tail.
- The A76 gain is the gcc `load64` vectorisation.  A CE build compiled with gcc
  on an SHA3-capable Linux core would presumably pay both; there is no such
  machine here, so that is not measured.
- A fixed Official + CE still runs upstream's `CE/f1600.S`, which is ~11 ns a
  permutation slower than GT's (P110), so the "after" column still contains
  that permutation difference.

## Part 4: Official as GitHub main has it today (3991b2a, 2026-08-14)

The comparison is meant to be against what `ntruplus/ntruplus` main (linked
from www.ntruplus.org) ships now.  `main_snapshot/` keeps the commit and the
files that differ.

- SUPERCOP 20260831 integrates NTRU+ with `ntruplus-supercop-update.sh`
  (on the Pi), from a fixed snapshot `import/ntruplus-20260723`; for aarch64
  it copies `asm/*` and `NO_CE/*`, flattens includes and adds declassify
  annotations.  It does not fetch.
- Raw aarch64 trees, snapshot 20260723 against main: only `asm/crepmod3.s`
  (all three sets; main replaces the compare-and-add q-centering with a
  Barrett `sqdmulh` + `srshr`) and `CE/f1600.S` differ.
- Main run through the same script against SUPERCOP 20260831's leaves: **only
  `crepmod3.s` differs**, for every set.  So SUPERCOP's leaf is main's NO_CE
  build (P112's "a third fips202.c, matching neither" was wrong: it is
  NO_CE's, through the script's edits).
- Our M2 "Official + CE" used an older `CE/fips202.c`: main's adds
  `secure_clear` of `temp` and the state at the end of `shake256`, `#error`s
  without SHA3 (the empty-permutation trap is gone) and drops SHAKE128;
  `load64` and the byte-wise tail are unchanged.  `CE/f1600.S` also differs.

Rebuilt from main (`build_main.sh`: the SUPERCOP leaf with main's
`crepmod3.s`; the CE build with main's `CE/fips202.c` and `CE/f1600.S`),
output-checked, three round-robin sessions with the old builds and GT
(`run_main.sh`, `main.py`), ns:

| | Official old -> GitHub main | GT vs GitHub main |
|---|---|---|
| M2 768, NO_CE / CE | -0.0 / +0.0 / -0.2% ; +0.3 / +0.1 / +0.0% | -15.3 / -21.8 / -19.4% ; **-9.0 / -15.5 / -16.1%** |
| M2 864 | +0.0 / +0.1 / -0.2% ; +0.2 / +0.2 / +0.1% | -16.1 / -22.6 / -18.3% ; **-9.6 / -12.0 / -9.5%** |
| M2 1152 | -0.1 / -0.0 / -0.2% ; +0.1 / -0.1 / -0.2% | -16.3 / -22.0 / -18.2% ; **-9.8 / -12.0 / -10.1%** |
| A76 768, NO_CE | +0.0 / +0.0 / +0.6% | **-18.0 / -24.1 / -19.0%** |
| A76 864 | -0.0 / +0.0 / +0.4% | **-17.9 / -24.1 / -19.0%** |
| A76 1152 | +0.0 / +0.0 / +0.5% | **-15.0 / -22.2 / -18.8%** |

main's `crepmod3.s` makes Official's decapsulation 0.4-0.6% slower on the A76
(one more multiply per vector on the A76's single multiply pipe) and 0.2%
faster on M2; main's CE files cost +0.0 to +0.3% on M2.  GT's margins against
main are within 0.4 points of those against the older baselines.
