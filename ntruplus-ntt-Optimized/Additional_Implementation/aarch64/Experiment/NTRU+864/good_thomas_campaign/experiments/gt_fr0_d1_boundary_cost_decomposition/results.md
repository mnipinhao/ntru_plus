# D1-P2 results

Status: **PASS — the P1 full-KEM deficits are source-closed by the component
ledger.** All component correctness checks pass, the Pi 5 Cortex-A76 remains
unthrottled, and all three repetitions agree on the direction of every major
delta.

## Noop-adjusted primitive costs

| Diagnostic boundary | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| official → FR0 permutation | 1847.523 | 5206.996 | 874 |
| FR0 → official raw permutation | 1758.678 | 5204.996 | 873 |
| contiguous nonnegative normalization | 526.373 | 1103.996 | 118 |
| contiguous centered normalization | 782.957 | 1426.996 | 115 |
| fused FR0 → official + nonnegative | 1315.862 | 3481.996 | 117 |

The fused path is substantially cheaper than the separate raw permutation
plus normalization, but it is still a large boundary. The scalar
official-to-FR0 loop is especially poor: the generated constant map is used
through one coefficient assignment at a time, retiring about 5207
instructions and 874 branches.

## Production API deltas: GT-D1 minus Official

| API boundary | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| Forward | **-197.835** | +419 | +9 |
| raw Inverse | +2088.975 | +5076 | +62 |
| centered Inverse API | +2854.900 | +6380 | +171 |
| ToBytes bridge | +1318.990 | +3473 | +111 |
| FromBytes bridge | +2222.827 | +6928 | +867 |
| BaseInv bridge | +3952.375 | +10719 | +975 |
| D1 BaseMul | **-701.993** | -494 | +1 |
| D1 BaseMulAdd | **-694.741** | -198 | +1 |

Forward is already faster than Official even though it retires 419 more
instructions. D1 BaseMul and BaseMulAdd are also clear wins. The complete GT
loss is therefore dominated by coordinate/byte boundaries, the BaseInv
bridge, and M5E Inverse rather than Forward arithmetic.

## Exact KEM call ledger

```text
Keypair = 2F + 2BaseInv + 2BaseMul + 3ToBytes
Encaps  = 2F + 1FromBytes + 1BaseMulAdd + 2ToBytes
Decaps  = 2F + 1InverseAPI + 2BaseMul + 3FromBytes + 2ToBytes
```

| KEM | predicted gap | measured gap | residual cycles | instruction residual | branch residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keypair | 10062.064 | 9936.375 | -125.689 | 0 | 0 |
| Encaps | 3770.396 | 3776.475 | +6.079 | 0 | 0 |
| Decaps | 10361.705 | 10396.400 | +34.695 | 0 | 0 |

The exact instruction and branch closure proves that the P1 binary is
accounted for by the named APIs. The small cycle residuals are caller-context
effects, not evidence of a missing operation.
