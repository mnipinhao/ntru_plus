# GT32 Compact Q24 037

037 starts from the selected experimental 036 Encap architecture.  It freezes
the qualified 034 Q24 canonicalizer and changes only the serializer code shape.
GT Clean is not edited.

## Shape audit

The twelve four-packet groups have the serialized-order route sequence:

```text
A A B C D D E D A A B C_tail
```

There is no exact global U2, U3, or U4 period.  An earlier experiment already
covered the obvious class-major descriptor solution: C1 grouped the same route
classes into six table-driven loops, but out-of-order stores forced safe tails
and scalar descriptor dependencies.  It cost about +70 core cycles for the two
Encap packs.

037A instead preserves serialized order and dispatches directly to five local
fixed-immediate helpers.  It has no descriptor loads and no variable permutes.
Only the shared C helper uses the safe fourth-packet tail, allowing the interior
C group and final object tail to share one body.

## Local gate

- Control symbol cage: 5,120 bytes.
- 037A active symbol: 1,806 bytes (`-3,314`, `-64.7%`).
- Exhaustive `[-12699,12699]` differential: pass.
- Guard-page final-packet test: pass.

Median candidate-minus-control values across four launches:

| Placement | One Q24 core | One Q24 TSC | Two Q24 core | Two Q24 TSC |
|---|---:|---:|---:|---:|
| Normal | +11.743 | +7.318 | +14.575 | +9.039 |
| Reversed | +11.280 | +7.077 | +13.434 | +8.439 |

One pack retires 48 additional instructions; two packs retire 96 additional
instructions.  This is a real local entry fee, but it is much smaller than C1
and much smaller than the whole-Encap delivery effect demonstrated by 036.
Therefore 037A continues to a release-padding whole-KEM gate.

## Promotion rule

037 is not production-promoted by the local result.  The independent export
must pass KAT and the fixed-ELF SUPERcop Keypair/Encap/Decap comparison.  A
whole-Encap win cannot override a material regression in the other two
operations; the final decision remains operation-aware.

## KAT and native SUPERcop build

The independent `avx2-gt32-clean-compact-q24-037` export passed all four native
SUPERCOP compiler profiles.  Its 100-vector NIST-style KAT is byte-exact with
the canonical NTRU+768 request and response:

```text
PQCkemKAT_2336.req  36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
PQCkemKAT_2336.rsp  22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

The formal fixed ELF uses the same O3/PIE/section-GC recipe as 036.  Its
selected Q24 symbol is 1,806 bytes and its complete `.text` is 59,351 bytes,
versus 62,935 bytes for 036 (`-3,584` bytes).

## Formal fixed-ELF whole-operation gate

The campaign used CPU 1, 16 paired blocks, odd ABBA/even BAAB order, 64 fresh
process launches per ASLR setting, and at least 96 SUPERCOP observations per
operation per launch.  The table reports the robust paired block median in
cycles; negative means the candidate is faster.

### 037 minus 036 (causal compact-Q24 gate)

| Setting | Keypair | Encap | Decap | Negative blocks (K/E/D) |
|---|---:|---:|---:|---:|
| ASLR on | -179.500 | -179.625 | -45.375 | 13/16, 11/16, 8/16 |
| ASLR off | -48.125 | -12.500 | -17.125 | 10/16, 8/16, 9/16 |

Several blocks entered a system/runtime mode that displaced all operations by
roughly 4,000--6,000 cycles.  Consequently the bootstrap *mean* is not a valid
estimate of the small 037 effect.  More importantly, Keypair and Decap move by
the same order as Encap even though they do not execute the replaced serializer.
That is direct evidence that the apparent whole-image movement is not a clean
Q24 runtime credit.  The stable ASLR-off Encap estimate is only -12.5 cycles
with 8/16 negative blocks, while the local two-pack cost is +8.4--9.0 TSC.

### 037 minus Official Main

| Setting | Keypair | Encap | Decap | Negative blocks (K/E/D) |
|---|---:|---:|---:|---:|
| ASLR on | -345.750 | +307.625 | -23.750 | 11/16, 2/16, 12/16 |
| ASLR off | -256.375 | +289.125 | -1.500 | 14/16, 1/16, 8/16 |

The operation-level conclusion is stable despite the contaminated outlier
blocks: GT wins Keypair, loses Encap by about 1%, and Decap is in the parity
band.  Therefore 037 does not globally beat Official and does not satisfy the
operation-aware promotion rule.

## Decision

037 is closed as an informative compact-code negative control.  It proves that
the five fixed-immediate helpers can remove 64.7% of the active Q24 symbol, but
the extra local work and whole-image delivery variance prevent a stable Encap
promotion.  036 remains the selected experimental Encap baseline.  Production
GT Clean remains unchanged.
