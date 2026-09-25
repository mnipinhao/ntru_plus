# Roadmap — closing NTRU+864 and NTRU+1152's M2 gap

Living document.  Started 2026-09-21 from P83 (corrected M2 baseline) and P84
(attribution); rewritten 2026-09-22 after P86 through P90 landed; tables and
the item list brought up to date 2026-09-23 after P123-P131; the current
margins, against GitHub main, and the landings since are 2026-09-25 (P132-P138).

## Current margins (P138, 2026-09-25)

**Supersedes the tables in "Where things stand" below**, which are kept for
their method notes and history.  GT at main a6524aea.  Official is the
published implementation, `github.com/ntruplus/ntruplus` main 3991b2a: its
default build (SHA3, `CE/`) on M2, its `NO_CE` build on the A76.  SUPERCOP
20260831's leaves are that `NO_CE` build from a 2026-07-23 snapshot and differ
from main only in `crepmod3.s` (main's is 0.4-0.6% slower in decapsulation on
the A76).  One session per machine for all three sets, every build
output-checked; `experiments/gt-p138-unified-margins/`.

| GT vs Official (keygen / encaps / decaps) | M2 Pro, default build | Cortex-A76, `NO_CE` | M2, permutation equal | A76, permutation equal |
|---|---|---|---|---|
| 768 | -9.0 / -15.5 / -16.1% | -18.0 / -24.1 / -19.0% | -5.1 / -11.7 / -12.8% | -10.2 / -13.4 / -11.7% |
| 864 | -9.6 / -12.0 / -9.5% | -17.9 / -24.1 / -19.0% | -6.1 / -6.8 / -5.8% | -10.7 / -12.8 / -10.9% |
| 1152 | -9.8 / -12.0 / -10.1% | -15.0 / -22.2 / -18.8% | -6.1 / -6.9 / -6.6% | -7.7 / -10.6 / -10.6% |

**"Keccak held equal" is not the arithmetic alone.**  It holds the permutation
equal and leaves each side its own sponge.  A build of GT's arithmetic with
Official's sponge splits it: GT's sponge is 69-101% of the permutation-equal
margin on M2 and 36-69% on the A76; the arithmetic is +2 to -130 ns an
operation on M2 and -684 to -1,216 ns on the A76 (matching P136's component
sums, so the KEM glue is small).  The sponge difference is two things in
upstream's C: `CE/fips202.c` absorbs the final partial block byte by byte into
the state in memory (the M2 part), and every upstream `load64` is a byte loop
that gcc vectorises into byte shuffles (the A76 part).  With both fixed,
Official is 4-9% faster on M2 (default build) and 2-5% on the A76, and GT's
M2 margins against the default build fall to -3.8 to -7.9%
(`upstream_fix/`).  Not reported upstream; the user will cover it in their
report.

**P139 (2026-09-25)** adds what a report needs (`experiments/gt-p139-report-data/`):

- SUPERCOP 20260831 on the Pi 5 for all three sets, against SUPERCOP's leaf
  and main's: GT -17.1 / -24.1 / -18.7% (768), -17.0 / -24.1 / -18.7% (864),
  -12.5 / -22.2 / -18.1% (1152); key generation as the mean of 576 samples,
  because 1152's retries make its median unstable (-12.5% or -17.2% by
  median, depending on the round mix).
- Code size: linked KEM text 87.5 / 48.4 / 48.5 KB against Official's 19.2 /
  22.8 / 20.9 KB; executed per operation 22-45 KB against 7.5-12.2 KB.  Fully
  cold (caches flushed before each operation), GT keeps -6 to -13% on
  encapsulation, -2 to -5% on decapsulation, and 768's key generation is
  **+3.3%** behind.
- 768's component table; its M2 deficits are the codec and
  `poly_basemul_add_encap`.

## Where things stand

Rebuilt in one session, every binary of a table with the same compiler, each GT
tree carrying **its own Makefile `CFLAGS`**; RNG reseeded before every timed
batch; min of 401 x 300 under the clock gate, median of three sessions.  All
three sets pass their full gate suite at these revisions.  864 and 1152 rows
are P129 (2026-09-23, GT at cf397cc4, every build output-checked); 768 rows
are P108.  P130 and P131 landed after these tables; their effect on the 864
decapsulation cell is in the note under the Keccak-equal M2 table.

**Cortex-A76 (Raspberry Pi 5), ns per operation.  Neither side has FEAT_SHA3.**

Symmetric about SHA3, *not* about assembly: GT compiles `keccakf1600.S`, 230
hand-written instructions, while Official has only its 621-line portable C --
upstream wrote no non-SHA3 assembly Keccak.  A real result, but not a
Good-Thomas one, and its size inside these margins is unmeasured (P112).

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official | 16,025 | 16,068 | 13,942 |
| | **GT** | **13,135** | **12,263** | **11,551** |
| | | **-18.0%** | **-23.7%** | **-17.1%** |
| 864 | Official | 18,389 | 19,188 | 16,948 |
| | **GT** | **15,216** | **14,811** | **14,205** |
| | | **-17.3%** | **-22.8%** | **-16.2%** |
| 1152 | Official | 28,102 | 24,581 | 21,819 |
| | **GT** | **24,077** | **19,347** | **18,139** |
| | | **-14.3%** | **-21.3%** | **-16.9%** |

**Cortex-A76 with the Keccak held equal** -- Official's sponge calling GT's
scalar permutation (P129).  This removes the 1.27x permutation advantage below:

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 864 | Official + GT's Keccak | 16,897 | 16,710 | 15,457 |
| | **GT** | **15,216** | **14,811** | **14,205** |
| | | **-9.9%** | **-11.4%** | **-8.1%** |
| 1152 | Official + GT's Keccak | 25,863 | 21,395 | 19,893 |
| | **GT** | **24,077** | **19,347** | **18,139** |
| | | **-6.9%** | **-9.6%** | **-8.8%** |

**M2 Pro, against Official + CryptoExtension.**

**This is upstream's default build, not a baseline we constructed** (P112).
`ntruplus/ntruplus` `main` sets `HAS_SHAKE256_ASM := 1` and compiles
`CE/f1600.S` with `-march=armv8.2-a+sha3`; 864 and 1152 symlink to 768's copy.
SUPERCOP's tarball is the stripped variant -- no `f1600.S`, and
`SUPPORTS_SHAKE256_ASM` never defined.  So this table is the honest headline.
The measurement copy of `CE/f1600.S` carries the AAPCS64 save/restore upstream omits.

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official + CE | 4,159 | 4,751 | 3,702 |
| | **GT** | **3,795** | **4,081** | **3,138** |
| | | **-8.8%** | **-14.1%** | **-15.2%** |
| 864 | Official + CE | 4,545 | 5,254 | 4,146 |
| | **GT** | **4,153** | **4,683** | **3,871** |
| | | **-8.6%** | **-10.9%** | **-6.6%** |
| 1152 | Official + CE | 7,115 | 6,953 | 5,486 |
| | **GT** | **6,440** | **6,129** | **4,959** |
| | | **-9.5%** | **-11.9%** | **-9.6%** |

**M2 Pro, against Official exactly as SUPERCOP has it** -- portable Keccak,
because SUPERCOP's copy dropped the SHA3 path that upstream builds by default:

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official | 4,479 | 5,152 | 3,863 |
| | **GT** | **3,795** | **4,081** | **3,138** |
| | | **-15.3%** | **-20.8%** | **-18.8%** |
| 864 | Official | 4,905 | 5,988 | 4,604 |
| | **GT** | **4,153** | **4,683** | **3,871** |
| | | **-15.3%** | **-21.8%** | **-15.9%** |
| 1152 | Official | 7,680 | 7,838 | 6,023 |
| | **GT** | **6,440** | **6,129** | **4,959** |
| | | **-16.1%** | **-21.8%** | **-17.7%** |

**M2 Pro, with the Keccak held byte-identical** -- Official's own `CE/fips202.c`
sponge linked against GT's permutation.  The strictest of the three, P114.

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official + GT's Keccak | 4,025 | 4,520 | 3,580 |
| | **GT** | **3,796** | **4,080** | **3,139** |
| | | **-5.7%** | **-9.7%** | **-12.3%** |
| 864 | Official + GT's Keccak | 4,380 | 4,979 | 3,988 |
| | **GT** | **4,153** | **4,683** | **3,871** |
| | | **-5.2%** | **-5.9%** | **-2.9%** |
| 1152 | Official + GT's Keccak | 6,858 | 6,571 | 5,265 |
| | **GT** | **6,440** | **6,129** | **4,959** |
| | | **-6.1%** | **-6.7%** | **-5.8%** |

GT wins all nine with the symmetric primitive removed from the question.  The
thinnest cell is 864 decapsulation at -2.9% -- the same cell P111 found carrying
the worst inverse; P127 found GT's 864 decapsulation *arithmetic* ~60 ns behind
Official's on M2, the lead coming from the rest.  **P130 moved that cell to
-4.2%** (and 864 decapsulation against Official + CE to -7.8%, A76
Keccak-equal to -9.4%), re-measured in P129's harness against the same
Official builds.

**Output check (P129).**  Upstream's `CE/fips202.c` calls `f1600` only under
`__ARM_FEATURE_CRYPTO` and otherwise has an *empty* permutation body.
`-march=armv8.2-a+sha3` alone does not define it under Apple clang: such a
build hashes nothing, times at half of GT, and still passes an
encaps/decaps selftest.  Use `+crypto+sha3`, and check the bytes
(`experiments/gt-p129-current-margins/check_out.sh`).  Of each total margin over SUPERCOP's Official, 22-61% is
SHA3 instructions, a uniform 20-22% is our Keccak kernel being 7.3% faster than
upstream's, and 19-60% is the arithmetic.

The gap between the second and third tables is the Keccak backend.  All are true, but
they answer different questions.  **For a claim about Good-Thomas, quote the
third.**  For the implementation against upstream's default build, the first.
The SUPERCOP one only as the figure a reviewer downloading the tarball would
reproduce.

## Why 768 led on M2: it had a different Keccak  (P109, P110)

Permutation **counts** are identical between GT and Official for every set and
operation, and Keccak is 48-73% of each -- almost the same share for all three
sets, so dilution was never it.  The contestable remainder was 2-6x better at
768, and it traced to the hashing: GT 768 spent **152.8 ns a permutation against
864's 164.8 and 1152's 164.1**, in one process with every symbol renamed, so not
layout.

`shake256_prefixed` is character-identical in the three trees.  What differed was
the permutation itself:

| | instructions | M2 Pro |
|---|---:|---:|
| **GT 768** (mlkem-native's hybrid routine) | **122** | **147.30 ns** |
| GT 864 / GT 1152 (written for them) | 146 | 158.33 |
| upstream CE `f1600` | — | 158.32 |

All byte-identical on the same state.  Recomputed against 147.3, the three
wrappers cost +4.9, +6.5 and +5.8 ns a permutation -- **equally good; the whole
difference was the permutation.**

Copied into both trees (`97ef2d6b`), gates including 864's `test_keccak_v84a`
(100,003 states, `d8-d15` preserved).  **Every M2 margin for 864 and 1152 roughly
doubled**; Cortex-A76 has no FEAT_SHA3, the file compiles away there and is
unchanged.  For scale: the transform work of this session -- a paired inverse, an
`ST3` widening and a packed tail, three landings with Slothy runs and full gate
suites -- moved 864's decapsulation from -1.1% to -2.5%.  The file copy moved it
to -6.8%.  See `experiments/gt-p110-keccak-swap/`.

## Why the two machines differ, and where the ceiling is  (P91)

**The Keccak permutation is issued the same number of times by both sides** --
768: 13/21/12, 864: 14/24/14, 1152: 21.4/32/19 -- and it is **the same speed on
M2**: 158.2 ns for upstream's `CE/f1600.S` against 158.4 for GT's
`keccakf1600_v84a.S`.  On A76, where neither has FEAT_SHA3, Official has
portable C at 493.1 ns and GT hand-written scalar assembly at 386.7, **1.27x**.

That 27%, applied to the 48-73% of every operation the permutation occupies, is
worth 13-20% of the total on A76 and **exactly nothing on M2**.  It is the whole
reason the A76 margins are three to fifteen times the M2 ones, and none of it is
Good-Thomas work.

What is left to compete over on M2, and how much of it each set takes:

| set/op | perm share | Official rest | GT rest | GT ahead | margin | ceiling | realised |
|---|---:|---:|---:|---:|---:|---:|---:|
| 768 keygen | 49% | 2106 | 1738 | 17% | -8.8% | -51% | 17% |
| 768 encap | 70% | 1431 | 751 | **48%** | -14.3% | -30% | 48% |
| 768 decap | 51% | 1797 | 1237 | 31% | -15.1% | -49% | 31% |
| 864 keygen | 49% | 2338 | 2110 | 10% | -5.0% | -51% | 10% |
| 864 encap | 72% | 1458 | 1189 | 18% | -5.1% | -28% | 18% |
| **864 decap** | 53% | 1927 | 1880 | **2%** | -1.1% | -47% | **2%** |
| 1152 keygen | 48% | 3735 | 3410 | 9% | -4.6% | -52% | 9% |
| 1152 encap | 73% | 1901 | 1477 | 22% | -6.1% | -27% | 22% |
| 1152 decap | 55% | 2486 | 2272 | 9% | -3.9% | -45% | 9% |

Encapsulation cannot beat -27 to -30% on M2 however good the arithmetic gets.
**864's decapsulation is the outlier**: 2% ahead on its contestable part where
768 manages 31%.

## What landed

| | |
|---|---|
| **P137** | 1152 decoder with two-register `tbl` (`unpack.S`, generated): the first transpose level and the byte expansion in one `tbl` per block pair, 40 SIMD ops a pair against 48; two-register `tbl` costs one `trn` on both machines.  Per call M2 70.0 -> 54.6 ns, A76 612 -> 479 cycles (Official 54.6 / 486).  SUPERCOP: decapsulation **-1.01%**, encapsulation -0.33%; M2 decapsulation -0.91%.  `export_supercop.py` now checks its lists against the Makefile (the first SUPERCOP run linked without `unpack.S`). |
| **P136** | Component table on the current trees (no code change).  P128's tool charged Official a `poly` copy before every in-place `poly_ntt`/`poly_triple`; its kem.c copies once, in decapsulation.  Corrected, M2 arithmetic is 864 -39 / -39 / -40 ns, 1152 -113 / -8.5 / -25; the forward NTT is +12-13 ns a call on M2 (as P100/P105), -360 to -430 cycles on the A76. |
| **P135** | 768 `poly_frombytes_encap` (NTRU+768 tree, noted here for completeness): each half of each block-major output vector is six contiguous bytes, so no transpose.  Per call M2 65.5 -> 37.9 ns, A76 503 -> 324 cycles; SUPERCOP encapsulation -0.55%. |
| **P134** | 864/1152 `reduce_canon`: Barrett, then `add` + `umin` instead of a sign mask and a second `mls` -- one multiply fewer.  A76 -0.4 to -0.54% on every operation, M2 4-11 ns. |
| **P133** | 864 `frombytes` as the inverse of the run-based serializer: one 16-byte load and one `tbl` per nine-byte run, a 6-of-8 transpose, one op per vector.  Per call M2 73.8 -> 55.4 ns, A76 640 -> 498 cycles; decapsulation -1.5% M2, -1.3% A76. |
| **P132** | 864/1152 cleanup as 768's P121: Slothy listings stripped, `.L` labels, one `C_SYM` spelling, dead code removed, comments describe code, READMEs rewritten.  Code bytes unchanged where not deleted. |
| **P131** | 1152 `tobytes`: P130's store scheme on twelve-byte blocks.  On M2 backward stores and the forward-maximal order both cost ~9 ns of decapsulation, so the shipped order has 66 of 144 blocks in one store: A76 keygen / encaps / decaps **-0.44 / -0.34 / -0.39%**, M2 unchanged.  1152 `frombytes` already had the 16-byte load. |
| **P130** | 864 overheads around unchanged arithmetic: `frombytes` one 16-byte load per 12-byte group (was 8-byte + scalar + lane insert; the group at byte 636 loads the 16 bytes ending at its last byte, ASan-checked); the first product's 36 tiles in one call (constants set once); `tobytes` one 16-byte store for 113 of 144 nine-byte runs where the extra bytes land in a neighbour written later (order generated and byte-simulated), 288 stores -> 175.  M2 keygen / encaps / decaps **-0.55 / -0.45 / -1.28%**, A76 **-0.87 / -0.83 / -1.29%**. |
| **P128** | 1152 `baseinv`'s C chains: `fqmul` takes the Montgomery quotient from `mul`, as Official's does, not from `uzp1` of the widened product -- one permute fewer on each step of a ~40-step serial chain.  `baseinv` M2 550 -> 517 ns (Official 532).  Key generation **-90 ns on M2 (-1.44%)**, +195 cycles on A76 (+0.36%): rule 2. |
| **P126** | 1152's `p65_rebase` folded into `basemul_rinv`: two halves per iteration, `trn2` replaces the narrowing `uzp2`, `zip` finishes the transpose.  Decapsulation **-18.5 ns on M2 (-0.37%)**, A76 unchanged: the A76 splits permutes over both vector pipes at dispatch even when V0 is saturated (16 `smull` + 16 `zip` = 23 cycles, not 16), so the saved pass is paid back in basemul.  `check-inplace` and `rebase.S` gone. |
| **P124** | 864/1152 pass SUPERCOP TIMECOP (`-O`..`-Os`, `TIMECOP=256`); Official fails on `poly_fqinv_batch`.  Decaps key-decode status and keygen's retry declassified; 864 baseinv branch-free, 1152 keeps a declassified early exit (29% of its candidates are non-invertible).  Inverse scratch KEM-owned and cleared.  Timing neutral. |
| **P86** | 1152's serializer folded the way Official folds: `sli`/`ushr` on the pre-transpose lanes instead of a transpose and per-lane `tbl`.  `tobytes_full` 129.2 -> 98.0, `tobytes_small` 92.9 -> 65.4, `frombytes` 79.8 -> 70.9. |
| **P87** | 864's serializer in six-vector groups, nine bytes a run, six coefficients folded into five halfwords.  `tobytes_full` 123.7 -> 97.2, `tobytes_small` 114.1 -> 69.7.  **564 KB of assembly deleted.** |
| **P88** | 864 re-encrypts into `buf3`'s tail and verifies instead of the fused compare.  **244 KB more assembly deleted.**  Not adopted at 1152: A76 regresses 86 ns there. |
| **P88 at 1152** | The fused `poly_tobytes_compare` becomes a re-encrypt into `buf3`'s tail plus `verify`, the arrangement 864 already had.  Decapsulation **-48 ns on M2 (-0.91%)**, +86 on A76 (+0.48%).  Blocked by the old criterion at -40/+79, landed under rule 2.  `gt864-p101-p29-landed` has the rule. |
| **P107** | 864's inverse tail normalises **six values a vector, not three**: `j = 8` gives one `(t, side)` only its three components, so the six-instruction normalisation ran on three of eight lanes -- 32 calls for 96 values, 2.00 instructions per value against `crepmod3`'s 0.75.  One `MOV V.d[1], V.d[0]` packs the high side into lanes 4..6 and one normalisation covers both; the store path is unchanged.  850 instructions become 738, A76 502 cycles become 430 and M2 139 become 119.  Decapsulation **-31 ns on A76 and -7 on M2**, so it lands under rule 1.  `gt864-p107-tail-packed`. |
| **P106** | 864's inverse route stores one `ST3.8H` a group instead of two `ST3.4H`: the eight-lane components are `c0 = (A.lo\|D.lo)`, `c1 = (A.hi\|D.hi)`, `c2 = C`, so two `ZIP .2D` replace three `EXT`.  Substituting plain stores prices the interleave at **136 cycles on A76 and 33 on M2** -- A76 charges four times what M2 does.  Decapsulation **-18 ns on A76 and -5 on M2**, both machines.  `gt864-p106-p29-a76`. |
| **P29** | 864's inverse: three paired main calls, a direct tail and a full-vector `ST3.4h` route folding the ternary reduction in.  Store µops 972 -> 224, retired instructions 5,362 -> 4,320.  Decapsulation **-38 ns on M2 (-0.93%)**, +118 on A76 (+0.83%); 864's thinnest margin goes -1.1% -> **-2.1%**.  First change under rule 2, and the campaign's first assembly change.  `gt864-p101-p29-landed`. |
| **P90** | 1152's `cbd1` bit-sliced, `sub` and `triple` unrolled twelve a turn.  78.1 -> 48.5 (beating Official's 51.0), 55.0 -> 32.4, 49.8 -> 27.5. |

**None of it is assembly.**  Three rounds of C intrinsics matching or beating
hand-written kernels, and one replacing 808 KB of them.  The campaign's standing
assumption that speed requires assembly did not survive contact with any of
these; what mattered was the algorithm and the unroll factor.

---

## Rules that apply to every item

- **Promotion criterion**, as amended 2026-09-22.  Both machines measured
  before anything lands -- Cortex-A76 (Pi5, `pi@100.99.191.9`) and M2 Pro.  A
  change may land when **either**:
  1. neither machine regresses at the operation level, **or**
  2. the regression is **at most 1%** on one machine *and* the other machine's
     gain, in percent of that operation, is **strictly larger** than it.

  Rule 2 exists because the two machines value the same work differently by a
  factor of six (P96: on A76 adding a store costs 5.9x what removing one saves,
  because the removed ones hide in the multiply-port shadow).  Holding to rule 1
  alone rejects every store-path redesign on the machine where stores are free,
  which is what happened to P28 and P29 (P98).  It is an explicit exception with
  a measured bound, not a case-by-case judgement: a change that regresses A76 by
  more than 1%, or by more than it gains on M2, still does not land.

  P88 was adopted at 864 and rejected at 1152 under rule 1 and stays that way.
- **Reseed the RNG before every timed batch.**  Key generation rejects and
  retries, and the spread between the cheapest and dearest single key generation
  on one stream is 11x.  Without reseeding, two builds do not measure the same
  work.  `experiments/gt-p91-m2-margin-ceiling/rb2.c`.
- **Check the profiler attributed everything.**  `sample` emits `???` rows for
  assembly without `.size`; that was 46-71% of the samples, and all of the
  permutation, in any profile of a build linking upstream `CE/f1600.S`.
  `roles2.py` now refuses to return below 98% attribution.
- **M2 measurements use `experiments/gt-p83-m2-supercop-baseline/perop3.c`.**  It
  warms up for three seconds, carries a clock witness and gates on it.  A fresh
  thread on this part sits in the E-cluster band for tens of milliseconds.
- **A KEM-level comparison must use the Makefile's own `CFLAGS`, and both sides
  must be built in the same session.**  1152's are
  `-O3 -std=c11 -D_DEFAULT_SOURCE -DNTRUPLUS1152_ASM_{BASEMUL_RINV,BASEINV_NUM,BASEINV_FINISH}`;
  a hand-written `cc -O3` drops the three `-D` and silently selects the C
  fallbacks in `inverse.c`, which inflated key generation by 165 ns and
  decapsulation by 47 on M2.  The A/B delta survived, the absolute numbers did
  not.  Rebuilding unchanged source moved 1152 keygen by 66 ns on
  its own; a delta under about 70 ns is layout noise until it survives a rebuild.
- **The Official baseline is SUPERCOP's**, from the Pi5 at
  `~/supercop-20260831/crypto_kem/ntruplus*/aarch64`, not the vendored tree.
- **Keep the timing path integer.**  `CE/f1600.S` and `asm/pack.s` both clobber
  `v8-v15` without saving them.
- Gates before promotion: `make check`, KAT, `check_release.py`,
  `check_zeroization.py`, the manifest, the ABI test and the
  SUPERCOP leaf check.  A change to decapsulation's rejection path also needs a
  negative differential test -- KAT vectors are all valid ciphertexts.

---

## What is left, by measured prize

Per-role deficits as they stand, GT minus Official, ns, Keccak aligned.

### 1. NTRU+1152 unpack: **measured, structural, closed**

**Reopened and landed by P137 (2026-09-24).**  The transpose stays, but a
two-register `tbl` (one `trn`'s cost on both machines) does its first level
and the byte expansion together, 40 SIMD ops a pair against 48; per call M2
70.0 -> 54.6 ns and A76 612 -> 479 cycles, both now at or under Official.  The
analysis below was right that the permutation cannot be removed; it priced
the permutation's cost too high.

The profiler's +157 was wrong; the compare it blamed is gone (`ecb6d5e1`), and
what remained was one kernel, `poly_frombytes`, at 1.29 on M2 and 1.27 on A76
(P102).  P103 found the work: **432 of its 473 excess instructions are one
`transpose8` per pair over eighteen pairs -- 91%.**  Everything else in the call
accounts for 41.

The transpose is not reducible.  Six of its eight output rows are used but the
last stage still needs all eight intermediates, so a six-row variant saves 2 of
24; and it cannot move to the store side because it feeds `unfold4`, not memory
-- transposing is what makes the 3-halfword-to-4-coefficient unfold
lane-parallel across eight wires.  **This is the Good-Thomas permutation in the
unpack direction, 0.375 instructions per coefficient, the same price the inverse
pays in stores.**

What was available landed (`8cc42ff8`): the range check is a tree rather than a
loop, because below `-O3` gcc spilled all eight vectors and reloaded them to
fold them -- 1,156 cycles a call at `-O2` against 876, and a 256-byte stack
frame.  At this Makefile's `-O3` it is 10 cycles; the value is insurance for
SUPERCOP's own flags.  A full unroll of the pair loop was tried and is **+70% on
M2**.

Removing the transpose means not needing the permutation, which is the same open
question the inverse leaves.  See `experiments/gt1152-p103-frombytes/`.

### 2. NTRU+768: **+53 key generation, +18 encapsulation** -- measured, and it is `tobytes_keygen_cq`

P104 timed it directly.  The profiler's +109 on encapsulation was a **fusion
accounting error**: `tobytes_encap_loose` is 1.89x Official because it absorbs
the reduction `poly_ntt_encap_small_lazy` skips, and that NTT wins 107 cycles a
call **twice**.  Counting both sides, the trade is a net win of 48 cycles and
encapsulation's whole kernel deficit is **+63 cycles (+18 ns)**, not +109.

| operation | GT | Official | difference |
|---|---:|---:|---:|
| key generation | 864 | 679 | **+185 (+52.8 ns)** |
| encapsulation | 1,801 | 1,738 | +63 (+18.1 ns) |
| decapsulation | 1,909 | 1,924 | -15 (-4.3 ns) |

**Key generation is the larger half now**, and it is one kernel:
`poly_tobytes_keygen_cq`, 1.32x, called three times, +177 of the +185.  P104
opened it.

| per call | instructions |
|---|---:|
| GT `tobytes_keygen_cq` | **1,220** |
| Official `poly_tobytes` | 808 |
| GT `tobytes_decap` | 809 (= Official's shape) |

**GT's fold-and-store core is better than Official's** -- 675 instructions
against 808, 56 per 64 coefficients against 67.  The whole +412 is the
permutation wrapper: 192 data loads, 24 index loads, 96 two-source `TBL`, 96
`UZP`, 48 `MOV`.  Index reuse is already optimal (24 loads for 96 `TBL`), and
two-source `TBL` is the right choice -- P97 measured three-source at +21% on A76.

What is reachable is the **96 duplicate data loads** (`TBL` pairs are `(g,g+4)`
so each vector's second use falls in a different pack-core call) and the 48
`MOV`: about **18 ns of the 51**.  The other 33 ns is the 96 `TBL` and 96 `UZP`,
which is the permutation itself -- the same answer 1152's unpack and 864's
inverse gave.

`frombytes_encap` is 1.79x and worth +103 on encapsulation.  P104 derived its
permutation: every 4-lane half is one element position from **four consecutive
12-byte blocks**, i.e. 48 contiguous bytes, which `LD3` de-interleaves on the
load unit -- 1152 cannot do this because its eight wires are scattered.  But the
two halves of an output vector always come from **different** quads (0 of 96
share one) and the pairing graph is two components of twelve quads, so a single
pass cannot hold a component.  That forces 192 narrow `STR D` where the data
needs 96, and the estimate falls to about **-33 cycles**, not the -67 that
1152's rate suggested.  **The store budget decides again.**

`poly_tobytes_encap`, 427 instructions, is dead code -- encapsulation calls
`encap_basemul_add_tobytes`.  768 is the last set whose codec is hand-written
assembly (`pack.S`, 73 KB, 2,232 instructions); 864's and 1152's were replaced
by C intrinsics in P87/P86 and the C won.  See
`experiments/gt768-p104-item2-measured/`.

### 3. NTRU+864 decapsulation, inverse transform: **landed, +52 remains, closed (P127)**

P127 re-priced what is left by knockout.  Per callee (M2 / A76): packed_i9
120 ns / 1,670, invntt16_paired 135 / 1,980, tail 33 / 417, route 52 / 500;
on M2 the paired kernel sits exactly on its SIMD-op bound.  Upper bounds:
deleting packed_i9's 192 lane stores -10 ns / -237 cycles, deleting p28_main's
`ext`/lane inserts -12 ns / 0.  Together at most ~0.5% of decapsulation before
the replacement permutes, so **not pursued**.  Running decapsulation in
Official's layout (768's route) is out too: GT's forward NTT and basemul lead
by ~1,200 A76 cycles there.  The remaining gap is the three-component
structure itself.  The history below is kept.


P29 took the +106 gap against Official down by 38 ns on M2.  What is left is
**+68 ns**, and it is no longer a store problem: the region now issues 224 store
µops against Official's 220.

P106 took P29's A76 cost apart and the IPC story was wrong.  Per component:
**the paired kernel is a 34-cycle win**; the regression is **+180 in the tail and
+148 in the route**.  Its low IPC is a consequence of doing the same arithmetic
in 37% fewer instructions, not a stall.  The GPR parking P28 uses to avoid
spilling was tested and is not the cause either -- replacing it with stack
spills changes A76 by 4 cycles and backend stalls not at all.

Both halves are now fixed and landed.

| 864 decapsulation | pre-P29 | P29 | + route (P106) | + tail (P107) |
|---|---:|---:|---:|---:|
| M2 Pro | 4,093 | 4,055 | 4,045 | **4,041 (-1.27%)** |
| Cortex-A76 | 14,149 | 14,266 | 14,248 | **14,211 (+0.44%)** |

P29's A76 cost is down from +117 ns to **+62** and its M2 gain up from -38 to
**-52**.  Per component on A76 the paired main is **-34**, the route **+95** and
the tail **+108**.

What remains is not a defect in either: the route's +95 is the `ST3` premium A76
charges over plain stores (80 cycles, measured by substitution), and the tail's
+108 is that the old tail did not normalise at all -- 738 instructions against
592 for the same 96 values, now at `crepmod3`'s density.  **Both are the price
of producing natural order directly instead of scattering with 768 `STRH` and
sweeping afterwards, and on M2 that price is negative.**

### 4. NTRU+864 forward transform: **+26** every operation -- examined, closed

P100 measured it.  Both sides call `poly_ntt` exactly twice in every operation
and neither specialises it at 864, so three different figures for one function
was the tell: they came from the sampling profiler.  In place against in place,
GT is **850 cycles a call against Official's 804 on M2 and 3,376 against 3,740
on A76** -- +26.4 ns an operation on M2, a 304 ns cushion on A76.

**There is no lever.**  GT's forward is within 17% of Official on store µops
(257 against 220, where one full output pass is 108), already has better IPC
than Official on *both* machines (M2 4.77 against 4.34, A76 1.20 against 0.93),
and its 563 extra instructions are spread across four classes with no dominant
term.  Smallest item on this list, not the cheapest.

P100 also fixed the unit: **a store costs per 16 bytes, not per instruction.**
The same 1,024 bytes written as 64 `STR Q`, 32 `ST1 {2}`, 21 `ST1 {3}` or 16
`ST1 {4}` all take 31.8 cycles on M2.  Merging stores into wider forms buys
nothing; `invntt16`'s 128 `STRH` per call are expensive because each occupies a
whole 16-byte µop to move two bytes.  Counted that way the inverse writes the
864 coefficients **10.7 times over against Official's 2.0**, and that excess
(+932 µops, +466 cycles) is larger than the inverse's entire +375-cycle gap.
See `experiments/gt864-p100-forward-and-store-uops/`.

### 5. NTRU+1152 forward transform: **decapsulation is a GT win** -- closed

| operation | M2 | A76 |
|---|---:|---:|
| key generation | +23.4 ns | **-361 ns** |
| encapsulation | +23.4 ns | **-361 ns** |
| **decapsulation** | **-9.7 ns** | **-425 ns** |

The roadmap said +21 / -25 / +47.  Decapsulation is a **win of 10 ns**, for the
reason item 4 had: Official pays a `poly` copy there (`f = m;`) that GT's
out-of-place form avoids.  What is real is +23 on key generation and
encapsulation, the same generic in-place forward gap 864 shows, which P100 found
has no concentrated lever.  P105.

### 6. NTRU+864 key generation, baseinv: **a GT win** -- closed

| `poly_baseinv`, one call | GT | Official | ratio |
|---|---:|---:|---:|
| M2 Pro | 1,334 | 1,349 | **0.99** |
| Cortex-A76 | 3,979 | 4,157 | **0.96** |

Key generation calls it twice: **-8.6 ns on M2 and -148 on A76**, not the +33
the roadmap carried.  P105.

### The profiler's record, now complete

| item | profiler | measured | |
|---|---:|---:|---|
| 1. 1152 unpack | +157 | +54 | 3x over |
| 2. 768 encapsulation | +109 | +18 | 6x over, fusion accounting |
| 2. 768 key generation | +69 | +53 | |
| 4. 864 forward | +61 / +32 / +25 | +26 uniform | wrong shape |
| 5. 1152 forward | +21 / -25 / +47 | +23 / +23 / -10 | two signs wrong |
| 6. 864 baseinv | +33 | **-8.6** | sign wrong |
| 3. 864 inverse | +106 | **+106** | correct, and the only one timed directly |

**Six of seven were wrong, and the one that was right was never sampled.**  Two
faults compounded: the sampler's own 5% disagreement on a 2,000 ns bucket
(P91), and harnesses that gave one side a `poly` copy the real code does not pay
-- or removed one it does.  Nothing goes on this list again without a direct
timing, and every comparison is checked against `kem.c`'s aliasing first.

---

## Deliberately not doing

- **The wire-order transform contract** (old item 1).  Gate 1b measured it at
  about -89 ns for 1152 decapsulation, but `ntt9.S` never holds the four
  consecutive vectors the transpose needs -- they sit 64 slots apart -- so it is
  a change to the bank schedule, not to store addressing.  See
  `experiments/gt-p85-gate1b-wire-order/`.  The generators *are* on disk under
  `experiments/`, contrary to what P85 first said; the schedule was always the
  binding obstacle.
- **Porting 1152's lane basis to 864's inverse.**  P89: it depends on four
  components filling four lanes and 864 has three.  P95's mixed-axis variant
  gets around that and P96 still kills it: it relocates stores rather than
  removing them.  See `experiments/gt864-p96-inverse-store-budget/`.
- **Specialising `tobytes` on its `full` parameter.**  6 ns for +61% object text.
- **The single 16-byte store in 1152's `store12`.**  Corrupts 71 of 144 blocks
  in pair order; address order needs eight pairs live.
- **The GPR tail store.**  Measured neutral.  The `memcpy` form is still worth
  taking as a strict-aliasing fix.

## Open questions, not scheduled

- ~~Report the two upstream AAPCS64 violations?~~  Fixed upstream: GitHub
  main 3991b2a's `CE/f1600.S` and `asm/pack.s` (768, 1152) save and restore
  d8-d15; 864's `pack.s` does not use v8-v15.  Only our old vendored copies had
  them (checked 2026-09-25).
- ~~864's inverse "tail padding"~~ -- answered by P125's range proof: the 32
  never-written scratch halfwords the transform reads never reach an output.
- ~~Re-measure the campaign's older component tables.~~  Done: P136 (864,
  1152, which also found P128's tool charging Official a copy) and P139 (768).
- **The two `backup-*-20260912` branches** hold 90 unique experiment records.
