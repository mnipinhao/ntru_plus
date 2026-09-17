# Experiment 145 results

## ASLR-off formal SUPERcop-style comparison

GT minus Official; 16 paired blocks on CPU 1:

| Operation | Official Q2 | GT Q2 | Paired mean delta | 95% CI | Favorable blocks |
|---|---:|---:|---:|---:|---:|
| Keypair | 21441.35 | 21240.38 | **-204.27** | **[-217.33,-190.49]** | 16/16 |
| Encap | 28060.95 | 28200.42 | **+130.34** | **[+114.82,+144.46]** | 0/16 |
| Decap | 19272.55 | 19262.54 | **-12.51** | **[-25.98,-1.82]** | 11/16 |

This independently reproduces the ASLR-off Experiment 144 result. Keypair and
Decap are faster; Encap remains about 130 paired core cycles slower.

## LBR Encap component profile

The same fixed ELFs were profiled in 128 balanced, ASLR-disabled fresh
processes. Values are medians of per-launch direct-leaf LBR intervals. They
are descriptive and must not be added to reconstruct full Encap.

| Semantic region | Official | GT | GT - Official |
|---|---:|---:|---:|
| Decode public key | 172.50 | 206.00 | **+33.50** |
| CBD(r) | 118.00 | 142.00 | **+24.00** |
| r producer | 724.25 | 677.00 | **-47.25** |
| r serializer | 211.50 | 246.00 | **+34.50** |
| hash-input copy | 22.00 | 0.00 | **-22.00** |
| SOTP(m) | 130.75 | 136.00 | +5.25 |
| m producer / QL2 landing | 721.00 | 596.75 | **-124.25** |
| BaseMul | 524.00 | 536.00 | +12.00 |
| sum + ciphertext serializer | 259.00 | 248.00 | **-11.00** |

Direct-r-hash therefore has a visible mechanism: the Official hash-input copy
costs about 22 core cycles and is absent from GT. The remaining GT serializer
body is still about 34.5 cycles slower than Official, so the net serialization
boundary is not yet intrinsically superior.

The two Forward producer regions remain strong winners. Decode and CBD remain
medium debts, while BaseMul is now only a small direct-leaf debt. The mapped
leaf picture is more favorable than the complete caller result; out-of-order
overlap, nested work, unobserved intervals, and executable delivery prevent
assigning the approximately 130-cycle whole-operation deficit to any single
leaf or to a sum of these medians.

## LBR Decap component profile

This uses the same 128 balanced, ASLR-disabled fresh processes and fixed ELFs.
The values are again medians of per-launch direct-leaf LBR intervals and are
not an additive decomposition of full Decap.

There are 64 launches per implementation. Early/middle leaves have 64 launch
observations. Late leaves have 19--57 observations because the finite LBR
stack does not always retain every earlier return; their medians are therefore
lower-confidence attribution, not formal component benchmarks.

| Semantic region | Official | GT | GT - Official |
|---|---:|---:|---:|
| Three decoders | 446.00 | 541.00 | **+95.00** |
| First/scale BaseMul | 424.00 | 429.00 | +5.00 |
| Inverse through crepmod3 | 966.00 | 941.50 | **-24.50** |
| Recovered-polynomial Forward | 800.00 | 696.00 | **-104.00** |
| Polynomial subtraction | 25.00 | 25.00 | 0.00 |
| Second/general BaseMul | 511.00 | 509.25 | -1.75 |
| Recovered-r serializer | 225.00 | 208.00 | **-17.00** |
| SOTP decode | 152.00 | 136.00 | **-16.00** |
| Derived-r generation | 838.00 | 769.75 | **-68.25** |
| Visible final-check leaf | 211.00 | 109.00 | **-102.00** |

The final row is intentionally asymmetric: Official's 211 cycles cover its
second serializer, while GT's 109 cycles cover its native-domain comparison.
Official then performs an inline byte-comparison loop that LBR cannot isolate,
so this row *understates* the Official final-check cost and is not used as an
exact standalone delta.

The actionable result is that Decap's two BaseMul sites are already at parity:
`+5.0` and `-1.75` cycles. GT's clearest remaining leaf debt is decode3 at
about `+95` cycles. GT recovers that debt through the transform paths,
inverse-to-mod3, serialization/SOTP, and native final verification.

The visible leaf deltas are much more favorable than the formal full-Decap
delta of `-12.51` cycles. That discrepancy is evidence of a large non-additive
caller residual (hash wrappers, inline glue/verification, overlap, LBR
coverage, and code delivery), not a new component that can be assigned by
subtracting medians. Therefore the profiler does not claim that the listed
wins sum to the whole-operation result.

## Decision

`ASLR_OFF_BASELINE_CONFIRMED_R_SERIALIZER_COPY_CLOSED`

- Future formal benchmarks use ASLR disabled only.
- Direct-r-hash remains production-selected.
- The removed copy is closed and must not be counted as future headroom.
- Reopening the serializer requires a new codec operation-class deletion or a
  measured dependency premise, not another copy/materialization proposal.
