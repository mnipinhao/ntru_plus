# P84 — on M2 the margin is the Keccak backend, and what 864/1152 give back is delivery

P83 established the corrected M2 numbers.  This asks where they come from, and
why NTRU+768's margin is three to seven times the other two.

## The Keccak backend is almost the whole margin

Three builds per parameter set, measured with P83's gated harness: Official
arithmetic with upstream's CE Keccak, the same Official arithmetic relinked
against GT's `fips202.c` + `keccakf1600_v84a.S`, and GT.  The middle build
splits the margin in two.

| set | op | GT - Official | of which Keccak | of which arithmetic |
|---|---|---:|---:|---:|
| 768 | keygen | -367 | -357 | -10 |
| 768 | encaps | -677 | -633 | -44 |
| 768 | decaps | -564 | -466 | -98 |
| 864 | keygen | -119 | -174 | **+55** |
| 864 | encaps | -209 | -190 | -19 |
| 864 | decaps | +14 | -75 | **+89** |
| 1152 | keygen | -59 | -157 | **+98** |
| 1152 | encaps | -319 | -353 | **+34** |
| 1152 | decaps | -123 | -195 | **+72** |

Every set's win is the permutation backend, which all three share.  Outside it,
768 is ahead by 10-98 ns and 864/1152 are *behind* in five of their six numbers.

GT's own sponge structure adds nothing on top of the backend: with the same
f1600, Keccak time is 1804 vs 1832 ns at 768, 2308 vs 2273 at 864, 3064 vs 3090
at 1152 -- neutral within the noise.  It is the permutation, not the plumbing.

## Where the arithmetic goes

`sample` at 1 kHz against a spinning build, self-time from its
"Sort by top of stack" section, with `<deduplicated_symbol>` resolved back to
real symbols through `nm` and local labels mapped to their enclosing global.
Sample shares are converted to ns using P83's per-operation times.

The roles cannot be compared one by one, because 768 has fused several of them:
its decapsulation runs a single
`gt_decap_checked_ct_f_basemul_scale64_loop64`, worth 310 of 5058 samples,
that does what Official splits between `loop_frombytes` and `looptop_scale`.
Grouping into a delivery path (pack/unpack + basemul + crepmod3) and a
transform (NTT + invNTT + baseinv) is invariant to that fusion.

| set/op | delivery Off | delivery GT | diff | transform Off | transform GT | diff | rest diff |
|---|---:|---:|---:|---:|---:|---:|---:|
| 768 keygen | 453 | 464 | +11 | 1071 | 1079 | +8 | +38 |
| 768 decaps | 540 | 507 | **-34** | 617 | 561 | -56 | -36 |
| 864 keygen | 556 | 628 | +73 | 1198 | 1215 | +17 | -37 |
| 864 decaps | 709 | 834 | **+125** | 713 | 821 | +107 | -109 |
| 1152 keygen | 704 | 705 | +1 | 2124 | 2218 | +95 | +97 |
| 1152 decaps | 814 | 891 | **+77** | 960 | 1040 | +80 | -111 |

**The Good-Thomas transform is not the differentiator on M2.**  In
decapsulation 768's is 56 ns ahead of Official's; 864's and 1152's are 107 and
80 behind, and per role that is the inverse, not the forward.

**Delivery is the other half.**  768's is 34 ns ahead, 864's 125 behind and
1152's 77 behind.

Per role, in decapsulation, with `basemul` and `crepmod3` added together
because GT folds the mod-3 step into the multiply:

| role | 768 | 864 | 1152 |
|---|---:|---:|---:|
| pack / unpack | **-78** | **+132** | **+149** |
| invNTT | -14 | **+140** | +43 |
| NTT | -42 | -32 | +37 |
| basemul + crepmod3 | +45 | -7 | -72 |
| sotp / cbd / add | +29 | +19 | +58 |
| memory / clear | -64 | -85 | -116 |
| **non-Keccak** | **-126** | **+124** | **+46** |

and in key generation:

| role | 768 | 864 | 1152 |
|---|---:|---:|---:|
| pack / unpack | +46 | +111 | +105 |
| NTT | +18 | +39 | +74 |
| baseinv | -10 | -22 | +20 |
| basemul + crepmod3 | -35 | -38 | -104 |
| sotp / cbd / add | +13 | +2 | **+183** |
| memory / clear | +14 | -38 | -68 |
| **non-Keccak** | **+57** | **+53** | **+193** |

Serialization is the one deficit present in every column: +105 to +149 for 864
and 1152, against -78 for 768's decapsulation.  864's inverse transform is the
second, at +140, and it is 864's alone -- 1152's is +43 because the lane-basis
rewrite of P64-P71 already landed there.  1152's third is the kernels it never
got in assembly.

### A correction

The first version of this record put `packed_i9` and `p65_rebase` in the
delivery and forward-transform buckets on the strength of their names.  Both are
inverse-transform internals: `packed_i9` is the radix-9 inverse leaf and
`p65_rebase` is the lane-basis rebase inside `inverse_ntt.S`.  Corrected, 864's
decap delivery gap falls from 237 ns to 125 and its transform gap rises from
-4 to +107; 1152's falls from 215 to 77 and rises from -58 to +80.  The
conclusion that serialization is the consistent deficit survives; the claim that
the transform was a win for all three does not.

## Why

Good-Thomas scatters the coefficients, so serialization has to carry a
permutation that Official's layout does not need.  Measured on its own, GT
1152's `tobytes` is 129 ns against Official's 78.

768 answered that by fusing the permutation into the operations either side of
it and specialising every entry by phase.  Its `kem.c` calls
`poly_ntt_keygen_cq`, `poly_tobytes_keygen_cq`,
`poly_basemul_keygen_cq_scaled_r`, `poly_baseinv_keygen_cq_scaled_r`,
`poly_ntt_encap_small_lazy`, `poly_tobytes_encap_loose`, `poly_frombytes_encap`,
`poly_basemul_add_encap`, `poly_ntt_decap`,
`poly_frombytes_basemul_decap_scale`, `poly_invntt_decap_scale` and
`poly_tobytes_decap` -- about fifteen phase-specific entries.

864's and 1152's `kem.c` call `poly_ntt` six times, `poly_tobytes_small` four
times, `poly_frombytes` four times, `poly_basemul` three times and
`poly_baseinv` twice.  Generic entries, no fusion, plus a `poly_tobytes_compare`
of their own.  The call *counts* are identical; the specialisation is not.

## What this says for the campaign

The remaining M2 work on 864 and 1152 is not in the transform.  It is porting
768's fusion and phase specialisation -- above all
`poly_frombytes_basemul_decap_scale`, which is where 768's decapsulation buys
its delivery win.  On A76 this will not show, for the reason the campaign has
met before: the machine is multiply-port bound and the delivery work hides in
the shadow.

## Reproducing

```
# build spin_{off,gt}{768,864,1152} as in P83, adding -g
./spin_<bin> <op> &          # op: 0 keygen, 1 encaps, 2 decaps
sample $! 6 1 -f profiles/<bin>.<op>.txt
python3 roles2.py
```
