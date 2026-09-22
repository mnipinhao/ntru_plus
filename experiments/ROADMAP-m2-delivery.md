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
| | **GT** | **15,246** | **14,800** | **14,144** |
| | | **-17.1%** | **-22.8%** | **-16.4%** |
| 1152 | Official | 28,094 | 24,571 | 21,804 |
| | **GT** | **23,994** | **19,350** | **18,043** |
| | | **-14.6%** | **-21.2%** | **-17.2%** |

**M2 Pro (CryptoExtension), ns per operation**

| set | | keygen | encap | decap |
|---|---|---:|---:|---:|
| 768 | Official + CE | 4,164 | 4,755 | 3,697 |
| | **GT** | **3,796** | **4,075** | **3,137** |
| | | **-8.8%** | **-14.3%** | **-15.1%** |
| 864 | Official + CE | 4,554 | 5,257 | 4,143 |
| | **GT** | **4,326** | **4,988** | **4,096** |
| | | **-5.0%** | **-5.1%** | **-1.1%** |
| 1152 | Official + CE | 7,123 | 6,967 | 5,494 |
| | **GT** | **6,798** | **6,543** | **5,280** |
| | | **-4.6%** | **-6.1%** | **-3.9%** |

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
| **P90** | 1152's `cbd1` bit-sliced, `sub` and `triple` unrolled twelve a turn.  78.1 -> 48.5 (beating Official's 51.0), 55.0 -> 32.4, 49.8 -> 27.5. |

**None of it is assembly.**  Three rounds of C intrinsics matching or beating
hand-written kernels, and one replacing 808 KB of them.  The campaign's standing
assumption that speed requires assembly did not survive contact with any of
these; what mattered was the algorithm and the unroll factor.

---

## Rules that apply to every item

- **Promotion criterion: neither machine may regress.**  Cortex-A76 (Pi5,
  `pi@100.99.191.9`) and M2 Pro, both measured, before anything lands.  P88 was
  adopted at 864 and rejected at 1152 on exactly this.
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

### 1. NTRU+1152 decapsulation, pack/unpack: **+157**

The last serialization deficit anywhere.  Key generation is -7 and
encapsulation +27; decapsulation carries it all, because it is the one place
that still runs the fused `poly_tobytes_compare`.  P88 measured the swap to
pack-and-verify at -40 ns on M2 and **+79 on A76**, where the scattered narrow
loads of the expected bytes are nearly free, so the swap is blocked.

What is left is to make the compare itself cheaper.  P86 already folded its
encoding; the residue is the `load12` of the expected run.  A masked sixteen-byte
load was tried at 864 and was worse.  An untried shape: fold a pair into a
96-byte scratch and compare that contiguously, six wide loads against sixteen
narrow ones.

### 2. NTRU+768 encapsulation, pack/unpack: **+109**, key generation **+69**

768 was not touched in this round and is now the worst packer in encapsulation.
Its decapsulation is -81, so the machinery exists in the same tree -- the encap
and keygen paths simply never got it.  P86's fold is the obvious thing to try;
768's `pack.S` is hand-written assembly, which after P87 is not an argument for
leaving it alone.

### 3. NTRU+864 decapsulation, inverse transform: **+98**

Studied in P89 and mostly **not addressable**.  The two trees run identical
arithmetic; the difference is 1,728 of 6,784 dynamic instructions spent on
`umov` + `strh`.  1152's lane swap collapses those because it has four
components filling four inner lanes; 864 has three, and swapping costs eight
calls where six suffice.  Mechanically available: `str s` in the tail, worth
**6 ns**, and post-indexed `st1` in the main kernel, worth **36 ns** against a
real risk of serialising stores Slothy interleaved.  Reordering the tail ahead
of the main calls is *legal* -- they read disjoint scratch and write disjoint
halfwords, and neither reads the output -- which lifts the tail's share to 10 ns.

### 4. NTRU+864 forward transform: **+61** keygen, +32 encaps, +25 decaps

Never examined.  1152's is -25 to +47 and 768's is -45 to -5, so 864's forward
is the outlier.  Cheapest next unknown.

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
  components filling four lanes and 864 has three.
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
