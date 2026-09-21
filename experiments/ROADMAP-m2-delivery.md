# Roadmap — closing NTRU+864 and NTRU+1152's M2 gap

Living document.  Started 2026-09-21 from P83 (corrected M2 baseline) and P84
(attribution).  Supersedes P82, which is withdrawn.

## Where things stand

Against Official + CE at the **SUPERCOP revision**, on M2 Pro, ns per operation:

| set | keygen | encaps | decaps |
|---|---:|---:|---:|
| **768** | **-8.8%** | **-14.3%** | **-15.3%** |
| **864** | **-2.2%** | **-4.2%** | +0.2% |
| **1152** | **-1.2%** | **-4.5%** | **-2.3%** |

On A76 (cycles, taskset-pinned, unaffected by any of this) GT leads by 12-25%
on all nine numbers.

Splitting the M2 margin by relinking Official's arithmetic against GT's
`keccakf1600_v84a.S`: **the whole margin is the Keccak backend**, which all
three sets share.  Outside it 768 is ahead by 10-98 ns and 864/1152 are behind
in five of their six numbers.  GT's own sponge structure adds nothing on top of
the permutation.

Where 864/1152's arithmetic goes, per role, decapsulation, ns (`basemul` and
`crepmod3` summed because GT folds the mod-3 step into the multiply):

| role | 768 | 864 | 1152 |
|---|---:|---:|---:|
| pack / unpack | **-78** | **+132** | **+149** |
| invNTT | -14 | **+140** | +43 |
| NTT | -42 | -32 | +37 |
| basemul + crepmod3 | +45 | -7 | -72 |
| sotp / cbd / add | +29 | +19 | +58 |
| memory / clear | -64 | -85 | -116 |
| **non-Keccak** | **-126** | **+124** | **+46** |

and key generation:

| role | 768 | 864 | 1152 |
|---|---:|---:|---:|
| pack / unpack | +46 | +111 | +105 |
| NTT | +18 | +39 | +74 |
| baseinv | -10 | -22 | +20 |
| basemul + crepmod3 | -35 | -38 | -104 |
| sotp / cbd / add | +13 | +2 | **+183** |
| memory / clear | +14 | -38 | -68 |
| **non-Keccak** | **+57** | **+53** | **+193** |

and encapsulation:

| role | 768 | 864 | 1152 |
|---|---:|---:|---:|
| pack / unpack | **+109** | **+116** | **+102** |
| NTT | -42 | +34 | +9 |
| basemul | +17 | -23 | -59 |
| sotp / cbd / add | +6 | -8 | **+83** |
| memory / clear | -78 | -86 | -88 |
| **non-Keccak** | **+5** | **-5** | **+4** |

All three are at parity in encapsulation once Keccak is aligned.  Serialization
is about 110 ns behind in every one of them -- **768 included** -- and is
cancelled by GT's cheaper zeroization and transform rather than by anything the
encap lazy/loose contract does.

**Attribution numbers come from a different regime than the promotion numbers.**
The profiles run one operation back to back, which is not how P83 measures; each
build reports its own ns/op from inside that loop, and the role shares are
converted with it.  Use P83's round-robin harness for any promotion decision and
the profiles only for where the time goes.

---

## Rules that apply to every item

- **Promotion criterion: neither machine may regress.**  A change lands only
  when both Cortex-A76 (Pi5, `pi@100.99.191.9`) and M2 Pro are measured and
  neither is worse.
- **M2 measurements use `experiments/gt-p83-m2-supercop-baseline/perop3.c`.**
  Never a fresh timing macro.  It warms up for three seconds, carries a clock
  witness and gates on it.  A fresh thread on this machine sits in the E-cluster
  band for tens of milliseconds; a harness without that warm-up measures the
  ramp, which is how P82 inverted.
- **The Official baseline is SUPERCOP's**, fetched from the Pi5 at
  `~/supercop-20260831/crypto_kem/ntruplus*/aarch64`.  The vendored
  `ntruplus-ntt-Optimized/Additional_Implementation/aarch64` tree is an older,
  slower revision.
- **Keep the timing path integer.**  Upstream's `CE/f1600.S` and `asm/pack.s`
  (`poly_tobytes`) both clobber `v8-v15` without saving them; a harness holding
  a double there reads back `-inf`.
- Every change must pass the tree's own gates before it is measured for
  promotion: `make check`, KAT, `check_release.py`, `check_zeroization.py`,
  `check_inplace.py`, the manifest, the ABI test (d8-d15 preserved) and the
  SUPERCOP leaf check.

---

## Item 0 — profile encapsulation  *(done, 2026-09-21)*

Result is in the tables above.  Two things came out of it.

**Serialization is behind in encapsulation for all three sets, 768 included,
by about 110 ns.**  768's advantage is confined to decapsulation.  Whatever
`poly_ntt_encap_small_lazy` and `poly_tobytes_encap_loose` buy, it is not a
packing win, so item 5 should not be expected to deliver one either.

**1152's `sotp/cbd/add` is +83 ns here**, against +149 in key generation and
+27 in decapsulation, confirming item 3 across all three operations.

It also found and fixed a conversion fault: role shares had been multiplied by
per-operation times from the round-robin harness, a different regime from the
profiling loop.  `spin.c` now measures and prints its own ns/op and the shares
are converted with that.  The corrected attribution is what the tables above
carry.

---

## Item 1 — serialization  *(gate 1b measured 2026-09-21; deferred behind item 3)*

See `experiments/gt-p85-gate1b-wire-order/`.  Three things were settled.

**The permutation is an 8xL transpose, L the leaf degree** -- 3 at 864, 4 at
1152 -- not the 8x8 an early reading suggested.  864's degree-3 runs are 6 bytes
and never align; 1152's degree-4 runs are one `str d`.  **1152 is the easier
target, not 864.**

**The cost moves rather than doubles.**  A transform final stage storing
transposed and scattered costs +33 ns per forward pass over 1152 coefficients
against four contiguous `str q`.  With the NTT-domain layout equal to wire
order, decapsulation's serializers give back 109 ns of packing and 79 of
unpacking against about 99 paid by two forward transforms and one inverse:
**about -89 ns, 1.6% of the operation.**

**It is still not next.**  `ntt9.S` leaves its live values 64 slots apart, so the
four consecutive vectors the transpose needs are not co-resident; this is a
change to the bank schedule, not to store addressing.  The file is 872 lines of Slothy-scheduled
assembly marked "do not edit"; its generator *is* on disk, at
`experiments/gt1152-p04-forward-8bank/generate_ntt9.py`, contrary to what P85
first recorded -- but the binding obstacle was always the bank schedule, not the
generator.

Revisit after item 3, with the packer's real cost known, and only if the
schedule can be regenerated rather than hand-edited.

---

## Item 2 — NTRU+864's inverse transform

**Prize:** +140 ns in decapsulation, the second largest deficit anywhere, and
864's alone.  864's inverse costs 378 ns for 864 coefficients; 1152's costs
377 ns for a third more, at +43 against Official.

**Why the difference:** the lane-basis rewrite of P64-P71 landed at 1152 and
never at 864.  1152 has `inverse_ntt.S` with a `p65_rebase` pass putting
(component, half) in the lanes, plus `inverse9.S` and `inverse16.S` built for
that basis.  864 has `inverse.S`, `inverse9.S`, `inverse16.S` and no rebase.

This is a port of work that already exists, not a new design.  The 1152 lane
basis is `new(j,t,c,h) = j*128 + t*8 + (c + 4h)`; 864's decomposition is
2 x 9 x 16 against 1152's 4 x 288, so the mapping has to be re-derived, but the
method and the kernels are there.

**Studied 2026-09-21, and the premise is false** -- see
`experiments/gt864-p89-inverse-study/`.  The two trees run identical arithmetic;
the whole +143 ns is 1,728 of 6,784 dynamic instructions spent on `umov` +
`strh`.  1152's lane swap collapses those into `str d` because it has four
components filling four inner lanes.  864 has three: swapping costs eight calls
where six suffice, and the extra calls exceed what the stores save.  Same
obstacle as P87's serializer, now having blocked two ports.

What is available is mechanical: `str s` for the tail, whose lanes are already
contiguous, and post-indexed `st1 {v.h}[l], [xT], #6` for the main kernel, whose
four lanes are three halfwords apart.  About -10%, 419 -> 376 ns, 43 of the 143.
Both files are Slothy-scheduled and the post-indexed address register serialises
stores the scheduler interleaved, so the tail is the safer half.

---

## Item 3 — NTRU+1152's missing assembly

**Prize:** +183 ns in key generation, +58 in decapsulation.

1152's `ASM_SRC` has no `add.S`, no `cbd.S` and no `pack*.S`.  768 and 864 have
all three and so does Official, so `poly_cbd1`, `poly_triple`, `poly_sub`,
`poly_sotp_encode`, `poly_sotp_decode` and the whole serializer are C
intrinsics there.

Mechanical: 864's `add.S`, `cbd.S`, `pack_small.S`, `pack_full.S` and
`pack_compare.S` are the model.  1152's degree-4 leaves make packing *easier*
than 864's degree-3 ones -- four coefficients land on a 12-byte boundary every
time, where 864's three-coefficient leaves are 4.5 wire bytes and never aligned,
which is why `pack_full_top` needs 54 `tbl` and 24 `ext` to route them.

Overlaps item 1c: write the packer for the wire-order contract directly rather
than porting 864's current shape and then moving the transpose out again.

**Done when:** 1152's `sotp/cbd/add` role is at or below Official's, both
machines.

---

## Item 4 — revisit `poly_tobytes_compare` at 1152

Measured against packing into a buffer and running the constant-time `verify`
both trees already carry, with both sides doing the Barrett reduction:

| | `tobytes_compare` | `tobytes_full` + `verify` | |
|---|---:|---:|---|
| 864, hand-written `pack_compare.S` | 133.0 | 140.5 | -7.5 ns, keep |
| 1152, C intrinsics | 166.3 | 150.4 | **+15.9 ns, a net cost** |

1152's C version replaces two stores per block with two dependent lane loads
(`vld1_u8` + `vld1q_lane_u32`) plus an eor and an orr.  Eight accumulators, to
break the 144-block or-chain, made it worse (197.1 ns), so the cost is the loads
and not the dependency.

Do **not** act on this before item 3.  The packer itself is the problem --
GT's `tobytes_full` is 129.1 ns against Official's `poly_tobytes` at 78.0 --
and once it is assembly the compare may well win the way 864's does.

---

## Item 5 — the encap lazy/loose contract

768 has `poly_ntt_encap_small_lazy` (ternary input, input reduction skipped,
output left loose in [-21050, 21050]) and `poly_tobytes_encap_loose` (a packer
that accepts that representation, so the separate reduction pass disappears),
plus `poly_frombytes_encap` and `poly_basemul_add_encap`, and a static
`encap_basemul_add_tobytes` fusing the multiply-add with the pack.

864/1152 use generic `poly_ntt`, `poly_tobytes_small`, `poly_frombytes`,
`poly_basemul_add`.

Priced only at the operation level so far: -19 ns at 864, +34 at 1152.  Item 0
is what makes this schedulable.

---

## Item 6 — the forward transform

864 keygen +39, 1152 keygen +74, 1152 decap +37.  Small, and partly an artefact
of item 1 if the transpose moves in.  Re-measure after item 1, not before.

---

## Deliberately not doing

- **Specialising `tobytes` on its `full` parameter.**  clang outlines the
  2,186-instruction body and passes `full` as a runtime argument; forcing
  `always_inline` is worth 6 ns on M2 for +61% object text (9,924 -> 15,964
  bytes).  Bad trade against A76's 64 KB L1I.
- **The single 16-byte store in 1152's `store12`.**  110.3 ns against 123.0, but
  it corrupts 71 of 144 blocks in pair order; address order would fix it and
  needs eight pairs live at once, which is not reachable.
- **The GPR tail store in 1152's `store12`.**  Measured neutral (123.0 vs
  123.0).  The `memcpy` form is still worth taking on its own as a
  strict-aliasing fix, independent of performance.

## Open questions, not scheduled

- **Report the two upstream AAPCS64 violations?**  `CE/f1600.S` and
  `poly_tobytes` in `asm/pack.s` both write `v8-v15` with no save/restore.
  Outputs are bit-identical, so nothing is wrong today; a C caller holding a
  double across the call is silently corrupted.  User's decision.
- **Re-measure the campaign's older component tables.**  Anything produced with
  a sequential `#define TIME` harness carries P82's fault.  The harness that
  produced the `basemul_rinv` / `basemul_scale` component table is no longer on
  disk.
- **The two `backup-*-20260912` branches** hold 90 unique experiment-record
  files.  Deferred by the user.
