# GT32-COMPACT-Q24-037R

037R isolates compact-Q24 execution cost from executable relocation.  It does
not edit production GT Clean and it freezes the 034 `vpaddw`/`vpminuw`
canonicalizer in all three variants.

## Causal variants

| Variant | Selected lazy-Q24 | Selected section | Later code |
|---|---|---:|---|
| A | 034 unrolled control | 5,120 B | original addresses |
| B | compact 037 body plus dead padding | 5,120 B | identical to A |
| C | compact 037 body, padding released | 1,806 B | relocated |

A and B have identical `.text` (62,935 B), `.rodata` (21,608 B), selected
section names, Q24 entry addresses, and addresses for Forward, Decode, B3,
Inverse, Keypair, Encap, and Decap.  C changes only the selected lazy-Q24
section size; complete `.text` falls to 59,607 B (`-3,328` B).  Keypair and
the code before lazy-Q24 retain their addresses, while later Encap/Decap hot
symbols move earlier by `0xce0`.

All A/B/C native SUPERCOP `try` tests and canonical 100-vector KATs pass.

## A to B: intrinsic compact-body cost

The matched local gate remains the high-resolution result: one compact lazy
Q24 call costs about `+11.5` core cycles and `+48` retired instructions.  (The
two-call micro-harness measured about `+14` core cycles, but production Encap
uses compacted lazy-Q24 once and a separate centered/high-range body once.) The formal
whole-operation campaign is too noisy to resolve that small fee.  Its robust
paired block medians (B minus A) are:

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| ASLR on | +55.750 | +43.750 | +29.750 |
| ASLR off | +4.125 | -3.000 | -26.250 |

The cross-setting inconsistency and unrelated-operation movement show that the
whole SUPERCOP caller is not a suitable estimator for a 14-cycle local effect.
No local scheduling conclusion is inferred from this table.

## B to C: footprint-release / relocation effect

Paired block medians (C minus B):

| Setting | Keypair | Encap | Decap | Negative blocks (K/E/D) |
|---|---:|---:|---:|---:|
| ASLR on | +2.000 | +136.125 | +149.875 | 8/16, 1/16, 2/16 |
| ASLR off | -0.375 | +172.250 | +135.875 | 8/16, 4/16, 4/16 |

This is the causal result.  Keypair stays near zero even though its later
P-pack address moves.  Encap and Decap regress in both ASLR settings,
including Decap even though its centered serializer and executed instructions
are unchanged.  The only relevant change is relocation of their later hot
symbols.

Therefore static-footprint release has real intrinsic value as an executable
layout variable, but **this release geometry is harmful**, not beneficial.
The earlier apparent 037 whole-image gains were placement redistribution and
cannot be credited to compact Q24 arithmetic.

## Decision

- 037 compact Q24 is not promoted.
- 036 remains the experimental Encap baseline.
- Do not search alignment or linker padding for 037.
- Proceed to 038 as an inventory/Pareto audit, not by stacking more changes.
- 039 `vzeroupper` work remains deferred until 038 fixes the hot-code shapes.

Raw campaigns and build machinery are retained in the adjacent 037 experiment:

- `../gt32_compact_q24_037/results/formal-037r-a-vs-b/manifest.json`
- `../gt32_compact_q24_037/results/formal-037r-b-vs-c/manifest.json`
- `../gt32_compact_q24_037/tools/materialize_037r.py`
- `../gt32_compact_q24_037/tools/build_fixed_supercop.sh`
