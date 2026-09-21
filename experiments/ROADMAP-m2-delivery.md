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

Encapsulation has not been profiled; only its totals are known (-19 ns at 864,
+34 at 1152).  That is item 0 below.

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

## Item 0 — profile encapsulation  *(prerequisite, cheap)*

Encapsulation is the only operation not yet attributed.  Sample
`spin_{off,gt}{768,864,1152} 1` the way P84 did for ops 0 and 2, and fill in the
role table.  Without it, item 5 is unpriced and there may be a deficit hiding
there that outranks item 4.

**Done when:** the encapsulation role table exists alongside the other two in
`experiments/gt-p84-m2-margin-attribution/RESULTS.md`.

---

## Item 1 — serialization  *(largest, present in every column)*

**Prize:** 864 decap +132, 1152 decap +149, 864 keygen +111, 1152 keygen +105.
768's decap serializer is 78 ns *ahead* of Official's, so the target is known to
be reachable.

**What is actually wrong.**  Good-Thomas scatters the coefficients and the wire
order is fixed by the specification, so a permutation between them is
unavoidable.  It can be paid three ways: a separate pass over memory, register
shuffles inside the serializer, or the addressing of a kernel that was going to
touch the data anyway.  864 and 1152 pay it the second way; 768 pays it the
third and therefore pays nothing.

Evidence: 768's `poly_frombytes_decap` and `poly_tobytes_decap` are sequential
loops, 66 instructions and **18 permutation instructions per 64 coefficients** --
exactly Official's 18, which is what 12-bit bit-packing costs on its own.  The
scatter lives in the decap forward transform's stores: 72 of them in the row0
block, 72 distinct immediate offsets spanning 0..1528.  864's `pack_small.S` is
1029 instructions of which **772 are permutation**, 57 per 64 coefficients,
fully unrolled with no loop.

**The permutation, extracted empirically** (feed value = index, decode the wire
fields):

- 864: GT slot `v*8 + t`  ->  wire `perm[t] * 48 + v`, `perm = [0,3,6,1,4,7,2,5]`
- 1152: same shape, stride 64

So eight consecutive GT vectors, transposed 8x8 (24 `trn`), give eight vectors
each holding eight **wire-contiguous** coefficients.  The permutation *is* that
transpose.  The minimum is therefore 24 permutation instructions per 64
coefficients against the 57 that 864 spends and the 18 Official spends.

**Plan.**

1. **1a.** Move the 8x8 transpose out of the serializer and into the final stage
   of the transform that feeds it, so the serializer becomes sequential.  Do 864
   first: its `ntt9.S` final stage already stores `str q` at 16-byte steps, so
   the change is the store addressing plus a transpose the stage can absorb.
2. **1b.** Check the cost actually moved rather than doubled.  Adding 24 `trn`
   per 64 coefficients to the transform costs about 23 ns at 864 on M2; the
   serializer must give up more than that.  If it does not, stop and say so --
   this is the measurement that decides whether the whole item is real.
3. **1c.** Repeat at 1152, where it merges with item 3 (there is no packer
   assembly to move the work out of yet).
4. **1d.** The same contract covers key generation; 768's `poly_ntt_keygen_cq` /
   `poly_tobytes_keygen_cq` pair is the model.  The +111 and +105 are its share.

**Risk:** scattered `str d` stores are half the width of `st1` quads, so the
transform pays store-port pressure.  On A76 this hides in the mul-port shadow;
on M2 it does not.  1b is the gate.

**Done when:** 864 and 1152 decap pack/unpack is at or below Official's, both
machines measured, no regression.

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

**Done when:** 864's decap invNTT is within Official's 239 ns, both machines,
no regression.

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
