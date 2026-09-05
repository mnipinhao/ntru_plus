# D1-P3B4 results

Status: **PASS as the new experimental production-shaped byte boundary.**

Eight deterministic Keypair/Encaps/Decaps cases are byte-identical across
Official, GT-D1 baseline and the selected-byte candidate. Valid decapsulation
succeeds; the same tampered ciphertexts return failure and identical output.
Pi5 core 3 remained unthrottled (`0x0`) through three paired repetitions in
both `ODB` and `BDO` orders.

| API | Official | GT-D1 baseline | selected bytes | candidate - baseline | candidate - Official |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keypair | 46881.000 | 56814.375 | **55672.875** | **-1141.500 (-2.01%)** | +8791.875 (+18.75%) |
| Encaps | 47037.375 | 50879.225 | **48212.325** | **-2666.900 (-5.24%)** | +1174.950 (+2.50%) |
| Decaps | 43448.950 | 53933.625 | **47645.175** | **-6288.450 (-11.66%)** | +4196.225 (+9.66%) |

Retired instructions change by -2928, -7313 and -18035 respectively. Every
individual repetition favors the candidate for all APIs.

The exact KEM call ledger predicts savings from P3B3 isolated medians:

| API | ToBytes | FromBytes | predicted saving | measured saving | residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keypair | 3 | 0 | 1213.252 | 1141.500 | +71.752 |
| Encaps | 2 | 1 | 2645.065 | 2666.900 | -21.835 |
| Decaps | 2 | 3 | 6317.525 | 6288.450 | +29.075 |

The small residuals establish that the isolated byte-boundary economics carry
through the real callers. Relocations in `kem_gt_bytes.o` point to
`gt_bytes_poly_tobytes` and `gt_bytes_poly_frombytes`, while every transform,
BaseInv and BaseMul relocation remains on `gt_d1_*`. The linked C1 FromBytes
body is stackless. R9-A uses only the expected GPR call frame and no vector
spill. This was not a stale GT-D1 byte wrapper.

The result is not a Production/SUPERCOP promotion. Encaps is now close to
Official but still 1174.950 cycles slower; Keypair and Decaps retain substantial
Forward/BaseInv/Inverse-side gaps.

## Updated component comparison against Official

The arithmetic/transform deltas below are the same Pi5 P2 measurements because
P3B4 does not change those functions. Updated ToBytes and FromBytes deltas are
P2's old bridge delta minus the P3B3 isolated saving. They are therefore a
cross-run component model, while the final API gaps are directly measured in
the P3B4 linked binary.

| One call, GT minus Official | cycles |
| --- | ---: |
| Forward | **-197.835** |
| D1 BaseMul | **-701.993** |
| D1 BaseMulAdd | **-694.741** |
| BaseInv bridge | +3952.375 |
| centered Inverse API | +2854.900 |
| selected ToBytes | +914.573 |
| selected FromBytes | +386.597 |

### Keypair = 2F + 2BaseInv + 2BaseMul + 3ToBytes

| Component | contribution to gap |
| --- | ---: |
| 2 Forward | -395.670 |
| 2 BaseInv | **+7904.750** |
| 2 BaseMul | -1403.986 |
| 3 selected ToBytes | +2743.718 |
| modeled total | +8848.812 |
| directly measured total | **+8791.875** |

### Encaps = 2F + 1FromBytes + 1BaseMulAdd + 2ToBytes

| Component | contribution to gap |
| --- | ---: |
| 2 Forward | -395.670 |
| 1 selected FromBytes | +386.597 |
| 1 BaseMulAdd | -694.741 |
| 2 selected ToBytes | +1829.145 |
| modeled total | +1125.331 |
| directly measured total | **+1174.950** |

### Decaps = 2F + 1Inverse + 2BaseMul + 3FromBytes + 2ToBytes

| Component | contribution to gap |
| --- | ---: |
| 2 Forward | -395.670 |
| 1 centered Inverse API | **+2854.900** |
| 2 BaseMul | -1403.986 |
| 3 selected FromBytes | +1159.791 |
| 2 selected ToBytes | +1829.145 |
| modeled total | +4044.180 |
| directly measured total | **+4196.225** |

The current target priority is consequently clear: Keypair is dominated by
the two BaseInv bridges; Decaps is dominated by Inverse plus the remaining byte
boundaries. Encaps has no single multi-thousand-cycle deficit and is already
within 2.50% of Official.
