# GT32-COMPACT-FRONTEND-036R

036R separates the compact frontend's executed schedule from the executable
relocation caused by releasing its unused bytes.  Production GT Clean is not
modified.  The 034 Q24 canonicalizer and every component other than `ntt.s`
are frozen across all variants.

## Causal variants

| Variant | Executed frontend | Reserved frontend | Later hot symbols |
|---|---|---:|---|
| A | original wide body | 3,917 B | original addresses |
| B | compact `U3 x 2 + U2` body | 3,917 B (dead padding) | identical to A |
| C | same compact body as B | 2,472 B | relocated earlier |

A and B have identical 64,087-byte `.text` sections.  Their frontend entry,
Forward kernels, Q24 bodies, BaseInv, B3, inverse, and KEM entry points have
identical addresses.  C releases the padding: `.text` becomes 62,679 bytes
(`-1,408` B after section alignment), and all hot symbols following the
frontend move earlier by `0x5a0` (`1,440` B).  The frontend entry and KEM API
stubs retain their addresses.

All three variants pass the native SUPERCOP build/try path and the canonical
100-vector KAT byte-for-byte:

```text
req 36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
rsp 22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

## A to B: intrinsic compact schedule

The prior matched local cage remains the high-resolution measurement:

| Placement | Frontend | Forward | 2 x Forward |
|---|---:|---:|---:|
| Normal | -0.431 | +0.267 | +0.647 |
| Reversed | -0.486 | +0.292 | +0.356 |

The fixed-ELF paired block medians (B minus A) are consistent with an effect
too small for whole-operation timing:

| Setting | Keypair | Encap | Decap | Negative blocks (K/E/D) |
|---|---:|---:|---:|---:|
| ASLR on | +8.250 | +4.250 | +8.625 | 7/16, 7/16, 5/16 |
| ASLR off | +15.375 | +12.375 | -6.750 | 5/16, 5/16, 9/16 |

Large system outliers make arithmetic means unsuitable here.  Neither the
local gate nor these paired medians show a meaningful compact-frontend
execution win.  The compact schedule is therefore not the mechanism behind
the old whole-image Encap result.

## B to C: padding release and relocation

Paired block medians (C minus B):

| Setting | Keypair | Encap | Decap | Negative blocks (K/E/D) |
|---|---:|---:|---:|---:|
| ASLR on | +17.250 | -97.000 | -141.250 | 7/16, 11/16, 13/16 |
| ASLR off | -11.125 | -196.500 | -165.250 | 9/16, 14/16, 14/16 |

The same executed compact body becomes much faster for Encap and Decap only
after its reserved bytes are released.  Keypair stays near zero.  This is an
operation-specific executable-delivery effect, not a frontend arithmetic or
dependency-schedule improvement.  Its magnitude and even its distribution
depend on the surrounding linked image, so it cannot be treated as a portable
credit for compacting arbitrary symbols.

## Decision

- Reclassify 036: its compact active schedule is locally neutral; the observed
  whole-image benefit came from the resulting relocation geometry.
- Keep 036 as an executable-delivery reference and exact-image Encap candidate,
  not as an intrinsic frontend champion.
- Do not stack further frontend loop/unroll variants or search magic padding.
- 038 must use equal-size cages for every active-body candidate, then measure
  footprint release separately.
- Candidate emission in 038 may resume only for shapes that can show intrinsic
  local value before relocation credit is considered.

Raw results are under `results/formal-036r-a-vs-b` and
`results/formal-036r-b-vs-c`; the three canonical KAT records are under
`results/kat-{a,b,c}`.
