# Roadmap — closing NTRU+864 and NTRU+1152's M2 gap

Living document.  Started 2026-09-21 from P83 (corrected M2 baseline) and P84
(attribution); rewritten 2026-09-22 after P86 through P90 landed.

## Where things stand

Both machines, all binaries per machine built in one session, RNG reseeded
before every timed batch, clock-gated harness:

**Cortex-A76 (Raspberry Pi 5, no CryptoExtension), ns per operation**

| set | | keygen | encap | decap |
|---|---|---:|---:|---:|
| 768 | Official | 16,003 | 16,044 | 13,939 |
| | **GT** | **13,124** | **12,257** | **11,549** |
| | | **-18.0%** | **-23.6%** | **-17.1%** |
| 864 | Official | 18,387 | 19,171 | 16,925 |
| | **GT** | **15,258** | **14,808** | **14,268** |
| | | **-17.0%** | **-22.8%** | **-15.7%** |
| 1152 | Official | 28,094 | 24,571 | 21,804 |
| | **GT** | **24,337** | **19,360** | **18,198** |
| | | **-13.4%** | **-21.2%** | **-16.5%** |

**M2 Pro (CryptoExtension), ns per operation**

| set | | keygen | encap | decap |
|---|---|---:|---:|---:|
| 768 | Official + CE | 4,164 | 4,755 | 3,697 |
| | **GT** | **3,796** | **4,075** | **3,137** |
| | | **-8.8%** | **-14.3%** | **-15.1%** |
| 864 | Official + CE | 4,554 | 5,257 | 4,143 |
| | **GT** | **4,340** | **4,987** | **4,055** |
| | | **-4.7%** | **-5.1%** | **-2.1%** |
| 1152 | Official + CE | 7,123 | 6,967 | 5,494 |
| | **GT** | **6,958** | **6,541** | **5,241** |
| | | **-2.3%** | **-6.1%** | **-4.6%** |

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
| **P86** | 1152's serializer folded the way Official folds: `sli`/`ushr` on the pre-transpose lanes instead of a transpose and per-lane `tbl`.  `tobytes_full` 129.2 -> 98.0, `tobytes_small` 92.9 -> 65.4, `frombytes` 79.8 -> 70.9. |
| **P87** | 864's serializer in six-vector groups, nine bytes a run, six coefficients folded into five halfwords.  `tobytes_full` 123.7 -> 97.2, `tobytes_small` 114.1 -> 69.7.  **564 KB of assembly deleted.** |
| **P88** | 864 re-encrypts into `buf3`'s tail and verifies instead of the fused compare.  **244 KB more assembly deleted.**  Not adopted at 1152: A76 regresses 86 ns there. |
| **P88 at 1152** | The fused `poly_tobytes_compare` becomes a re-encrypt into `buf3`'s tail plus `verify`, the arrangement 864 already had.  Decapsulation **-51 ns on M2 (-0.96%)**, +93 on A76 (+0.51%).  Blocked by the old criterion at -40/+79, landed under rule 2.  `gt864-p101-p29-landed` has the rule. |
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
- **Both sides of a KEM-level comparison must be built in the same session with
  the same flags.**  Rebuilding unchanged source moved 1152 keygen by 66 ns on
  its own; a delta under about 70 ns is layout noise until it survives a rebuild.
- **The Official baseline is SUPERCOP's**, from the Pi5 at
  `~/supercop-20260831/crypto_kem/ntruplus*/aarch64`, not the vendored tree.
- **Keep the timing path integer.**  `CE/f1600.S` and `asm/pack.s` both clobber
  `v8-v15` without saving them.
- Gates before promotion: `make check`, KAT, `check_release.py`,
  `check_zeroization.py`, `check_inplace.py`, the manifest, the ABI test and the
  SUPERCOP leaf check.  A change to decapsulation's rejection path also needs a
  negative differential test -- KAT vectors are all valid ciphertexts.

---

## What is left, by measured prize

Per-role deficits as they stand, GT minus Official, ns, Keccak aligned.

### 1. NTRU+1152 unpack: **measured, structural, closed**

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
`poly_tobytes_keygen_cq`, 1.32x, called three times, +177 of the +185.  It has
545 instructions and 210 transpose-class, and it has not been analysed.

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

### 3. NTRU+864 decapsulation, inverse transform: **landed, +68 remains**

P29 took the +106 gap against Official down by 38 ns on M2.  What is left is
**+68 ns**, and it is no longer a store problem: the region now issues 224 store
µops against Official's 220.

The one thing left on this kernel is P29's own next gate.  Its IPC on A76 is
**1.41 against the old path's 1.93**, which is why it costs 300 cycles there
while retiring 1,042 fewer instructions.  Break-even needs **1.56, 11% more**;
at production's issue width those 4,320 instructions would take 2,234 cycles and
beat the old path on *both* machines, turning the +0.83% A76 cost into a gain.
That is a producer/consumer dependency question -- do not reschedule P29 or
optimise only its stores -- and both symbolic sources are on disk in
`gt864-p28-paired-i16/candidate-main.sym.S` and
`gt864-p29-direct-st3/candidate-main-route.sym.S`.

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

### 5. NTRU+1152 decapsulation, forward transform: **+47**

Keygen is +21 and encapsulation -25, so this is decapsulation-specific.

### 6. NTRU+864 key generation, baseinv: **+33**

1152's is -50.

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

- **Report the two upstream AAPCS64 violations?**  `CE/f1600.S` and
  `poly_tobytes` in `asm/pack.s` write `v8-v15` with no save/restore.  Outputs
  are unaffected; a C caller holding a double is silently corrupted.
- **864's inverse driver** has a "tail padding" clear writing to `sp + 1536`
  where the scratch has been caller-owned in `x25` since P80.  Looks like dead
  code; tests pass either way.  Worth a look.
- **Re-measure the campaign's older component tables.**  Anything from a
  sequential `#define TIME` harness carries P82's fault.
- **The two `backup-*-20260912` branches** hold 90 unique experiment records.
