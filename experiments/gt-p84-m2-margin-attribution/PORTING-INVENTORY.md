# What 864 and 1152 still owe 768

Every entry NTRU+768 specialises, what 864/1152 call instead, and what the gap
costs.  Prices are from the P84 profiles, converted to ns per operation.

768 has no generic `poly_ntt`, `poly_tobytes`, `poly_frombytes`, `poly_basemul`
or `poly_baseinv` at all -- every entry is phase-specific.  864 and 1152 have
exactly one generic version of each and no phase-specific entry anywhere.  Their
entry sets are identical to each other.

## 1. Keygen: the CQ layout contract

768's keygen never materialises block-major order.  The forward transform writes
the CQ layout directly and every consumer downstream of it reads CQ, so the
Good-Thomas permutation is never paid.

| 768 | 864 / 1152 | what the specialisation does |
|---|---|---|
| `poly_ntt_keygen_cq` | `poly_ntt` | writes CQ directly instead of block-major |
| `poly_baseinv_keygen_cq_scaled_r` | `poly_baseinv` | consumes CQ, folds the Montgomery R scale into the output |
| `poly_basemul_keygen_cq_scaled_r` | `poly_basemul` | same, for the multiply |
| `poly_tobytes_keygen_cq` | `poly_tobytes_small`, `poly_tobytes` | packs straight out of CQ, no permutation |

**Prize:** keygen packing costs GT 372 ns at 864 and 324 ns at 1152, against
Official's 265 and 220.  **+106 ns (864), +104 ns (1152).**

## 2. Encap: lazy output and a packer that accepts it

| 768 | 864 / 1152 | what the specialisation does |
|---|---|---|
| `poly_ntt_encap_small_lazy` | `poly_ntt` | input is known ternary, so the input reduction is skipped; output is left loose in [-21050, 21050] |
| `poly_tobytes_encap_loose` | `poly_tobytes_small` | accepts that loose representation, so the separate reduction pass disappears |
| `poly_frombytes_encap` | `poly_frombytes` | checked unpack writing straight into the layout the encap transform wants |
| `poly_basemul_add_encap` | `poly_basemul_add` | a*b+c endpoint whose result is packed immediately |
| `encap_basemul_add_tobytes` (static, kem.c) | -- | fuses that multiply-add with the pack |

**Prize:** the encapsulation arithmetic deficit is the smallest of the three
operations, -19 ns at 864 and +34 ns at 1152, so this group is worth less than
the other two.  Do it after them.

## 3. Decap: the QSoA layout contract, and the one real fusion

768 keeps the ciphertext in Decap QSoA layout from unpack to repack.  The
central entry is a genuine three-way fusion; in the profile it is a single
symbol, `gt_decap_checked_ct_f_basemul_scale64_loop64`, 310 of 5058 samples.

| 768 | 864 / 1152 | what the specialisation does |
|---|---|---|
| **`poly_frombytes_basemul_decap_scale`** | `poly_frombytes` + `poly_basemul_rinv` | **fused**: checked unpack of ct and f, keeps ct in QSoA, emits the R^-1-scaled product the inverse wants |
| `poly_invntt_decap_scale` | `poly_invntt_ternary` | consumes that scaled product directly |
| `poly_ntt_decap` | `poly_ntt` | ternary input, top-split quotient exactly zero, output stays QSoA |
| `poly_frombytes_decap` | `poly_frombytes` | checked unpack into QSoA |
| `poly_basemul_decap` | `poly_basemul` | QSoA multiply |
| `poly_tobytes_decap` | `poly_tobytes_small` + `poly_tobytes_compare` | packs out of QSoA; 768 needs no separate compare entry |

**Prize:**

| | GT | Official | gap |
|---|---:|---:|---:|
| 864 decap pack/unpack | 520 | 387 | **+132** |
| 1152 decap pack/unpack | 455 | 307 | **+149** |
| 864 keygen pack/unpack | 376 | 265 | +111 |
| 1152 keygen pack/unpack | 324 | 220 | +105 |

768's decapsulation spends 145 ns there against Official's 223 -- it is 78 ns
*ahead*, because it has no separate serializer to spend it in.

`poly_tobytes_compare` was measured on its own against packing into a buffer
and running the constant-time `verify` both trees already carry, with both
sides doing the Barrett reduction:

| | `tobytes_compare` | `tobytes_full` + `verify` | |
|---|---:|---:|---|
| 864, hand-written `pack_compare.S` | 133.0 | 140.5 | **-7.5 ns, keep it** |
| 1152, C intrinsics | 166.3 | 150.4 | **+15.9 ns, a net cost** |

The idea is sound where it is written in assembly.  1152's C version loses
because it replaces two stores per block with two dependent lane loads
(`vld1_u8` + `vld1q_lane_u32`) plus an eor and an orr; a store retires into the
store buffer and a lane load does not.  Eight accumulators, to break the
144-block or-chain, made it worse still (197.1 ns), so the cost is the loads and
not the dependency.

Dropping it at 1152 is worth 16 ns, but that is a symptom.  The packer itself is
the problem: GT's `tobytes_full` is 129.1 ns against Official's `poly_tobytes`
at 78.0.  Fix section 4 first, then re-measure the compare.

## 3b. NTRU+864 only: the inverse transform never got the lane-basis rewrite

864's inverse costs 378 ns in decapsulation against Official's 239, **+140 ns**
-- the second largest deficit anywhere, and 864's alone.  1152's is 377 ns for
a third more coefficients, +43 against Official, because the lane-basis rewrite
of P64-P71 landed there and not at 864.

This is not new design work: `inverse_ntt.S`, `inverse9.S`, `inverse16.S` and
`rebase.S` at 1152 are the model, and the campaign has already paid the cost of
finding it.  The 864 equivalents are `inverse.S`, `inverse9.S`, `inverse16.S`
with no rebase pass.

## 4. NTRU+1152 only: three kernels that never got assembly

1152's `ASM_SRC` has no `add.S`, no `cbd.S` and no `pack*.S`.  768 and 864 have
all three, and so does Official.  `poly_cbd1`, `poly_triple`, `poly_sub`,
`poly_sotp_*` and the serializer are C intrinsics there, and it shows:

| | GT 1152 | Official | gap |
|---|---:|---:|---:|
| cbd1 / sotp / triple / sub, keygen | 360 | 177 | **+183** |
| cbd1 / sotp / triple / sub, decap | 207 | 149 | **+58** |

This is independent of the specialisation work and is the cheapest item on the
list to fix -- 864's `add.S`, `cbd.S` and `pack_*.S` are the model, and the
degree-4 leaves at 1152 make packing easier than at 864, not harder.

## What 864/1152 already have that 768 does not

For fair accounting: `poly_basemul_rinv` (R^-1 folded into the multiply),
`poly_invntt_ternary`, and `poly_tobytes_compare`.  The first two are real; the
third is priced above and is currently a net cost.

## Order of work, by measured prize

1. **Serialization** -- the only deficit in every column: +132 and +149 ns in
   decapsulation, +111 and +105 in key generation.  768's decap serializer is
   78 ns *ahead* of Official's, so the target is known to be reachable.  The
   mechanism is section 3: let the transform's final stage store into wire order
   so the packer needs no permutation of its own.
2. **864's inverse transform** -- +140 ns, and a port of work that already
   exists at 1152 rather than a new design (section 3b).
3. **1152's missing `add.S` / `cbd.S` / `pack*.S`** -- +183 ns in key
   generation, +58 in decapsulation, mechanical (section 4).
4. **Keygen CQ contract** -- folded into item 1; its share of the packing gap is
   the +111 and +105 above.
5. **Encap lazy/loose contract** -- smallest, -19 to +34 ns.

None of this will show on Cortex-A76.  That machine is multiply-port bound and
delivery work hides in the shadow of the mul pipe, which is why nine gates of
transform work were promoted there while the delivery path went unexamined.
