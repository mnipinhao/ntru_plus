# GT9X16-PROD3-ENCAP

## Scope and caller correction

This checkpoint installs the persistent-AoS producer and native MA2 path in
the real NTRU+1152 encapsulation caller.  It freezes top-split arithmetic,
PROD3, MA2, inverse-four, serializer, twist, and code organization.

The real caller exposes one semantic edge that the preceding ciphertext
island did not price: the sampled polynomial `r` is serialized in its Official
NTT representation and hashed before SOTP creates `m`.  The candidate must
therefore produce both the MA2-native representation and the exact Official
serialized bytes:

```text
poly_cbd1(r)
-> top split -> PROD3 persistent AoS -> MA2-native r planes
                                  \
                                   -> inverse physical projection
                                      -> generic F0
                                      -> Official order
                                      -> remove scale 4
                                      -> poly_tobytes -> hash_g

poly_sotp_encode(m)
-> top split -> PROD3 persistent AoS -> MA2-native m planes

(r planes, m planes, resident h) -> unchanged native MA2 -> ciphertext
```

The bridge reuses the existing `r` and `m` polynomial objects as scratch.  It
adds no polynomial-sized allocation.  The inverse physical projection is a
32-byte-aligned, branchless AVX2 leaf containing 72 aligned loads, 72 aligned
stores, and 72 `vperm2i128` instructions.  It preserves signed 16-bit
representatives exactly; scale removal happens only after conversion to
Official order.

## Correctness

The hash-edge differential compares all 1,728 serialized bytes with Official
`poly_ntt` plus `poly_tobytes`.  It passes zero, alternating inputs, all 2,304
signed impulses, 4,099 random-small inputs, input immutability, canaries, and
ASan/UBSan.

The complete repository `make check` and `make sanitize` gates pass.  A
100-case NIST KAT replay is byte-exact with the frozen NTRU+1152 response:

| artifact | SHA-256 |
| --- | --- |
| request | `36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa` |
| response | `2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3` |

This covers candidate key generation, encapsulation, decapsulation, and exact
API output semantics under deterministic KAT seeds.

## Native SUPERCOP result

The pinned pristine baseline is SUPERCOP 20260627.  Both implementations were
installed under distinct names in the disposable campaign and measured on
CPU 1 of the Intel Core Ultra 7 155H with the performance governor and turbo
disabled.  Each operation has 864 observations from nine fresh processes.
SUPERCOP selected its normal best compiler recipe independently: native O3
for Official and native O2 for the candidate.

| operation | Official StQ2 | candidate StQ2 | candidate - Official |
| --- | ---: | ---: | ---: |
| keypair | 34898.4861 | **34141.5741** | -756.9120 (-2.17%) |
| enc | **43059.2778** | 44557.9769 | +1498.6991 (+3.48%) |
| dec | 30550.0972 | **30352.3565** | -197.7407 (-0.65%) |

The headline `enc_cycles` gate fails.  Keypair and decapsulation movement is
not treated as a candidate win because those operations were not changed;
their deltas are placement/compiler side effects to retain as controls.

## Fixed-common paired ELF

Official and candidate were rebuilt with the same SUPERCOP O3GC recipe.  The
formal replay uses 16 paired ABBA blocks per setting, 64 fresh launches and 96
observations per KEM operation per launch.  Positive values mean the candidate
is slower.

| setting | mean paired `enc_cycles` delta | bootstrap 95% CI |
| --- | ---: | ---: |
| normal, ASLR off | +1986.73 | [+1935.57, +2038.35] |
| normal, ASLR on | +1892.85 | [+1804.47, +1977.63] |
| reversed, ASLR off | +2125.25 | [+2082.37, +2164.89] |
| reversed, ASLR on | +1956.93 | [+1846.40, +2040.10] |

All 64 block deltas are positive.  The regression therefore remains after
removing native compiler-selection differences and is directionally invariant
under ASLR and archive placement.

The fixed normal ELFs have 44,951 bytes of Official `.text` and 139,223 bytes
of candidate `.text`.  This installed experiment still retains several
historical assembly bodies in the linked sections, including generic MA2 and
standalone PROD3 branch symbols.  That footprint is a real property of this
experiment ELF, but it does not explain away the result: reversed placement
and ASLR controls preserve a roughly 1.9--2.1k-cycle encapsulation regression.
Dead-body cleanup is not authorized as a performance rescue before caller
attribution.

## Interpretation and decision

The approximately 432-cycle persistent-AoS ciphertext-island win remains
valid.  Native encapsulation nevertheless loses by approximately 1,499 cycles,
and fixed-common paired replay loses by approximately 1,893--2,125 cycles.
The island and native results do not have identical boundaries, so they must
not be arithmetically added as one performance estimator.

The main newly exposed candidate-only edge is recovery of Official serialized
`r` for `hash_g` and SOTP.  This makes the present architecture a dual-output
producer, whereas the preceding island stopped at MA2-native planes.  The
correct next checkpoint is therefore caller attribution at that exact fanout:

```text
Official control:
  coefficient r -> Official NTT state + exact hash bytes

candidate:
  coefficient r -> PROD3 MA2 planes + exact same hash bytes
```

PROD3, MA2, twist, top split, and the 72 final packing permutations remain
frozen.  The candidate is retained as a research implementation but is not
promoted to clean production.
