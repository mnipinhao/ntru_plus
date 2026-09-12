# P22 result — two-output SSA main-I16 butterflies

P22 tested whether the current P13-B main inverse NTT16 could replace every
three-instruction held-left butterfly

```
ORR tmp,left,left
ADD left,left,right
SUB right,tmp,right
```

with two SSA outputs:

```
ADD sum,left,right
SUB diff,left,right
```

All roots, reductions, tables, scales, bounds, loads, stores and public ABIs
remain unchanged.  Production revision
`15c326183f592044fbc67071d9459af86ce104e4` is the frozen baseline.

## Static, mathematical and Slothy gates

- 32 `ORR` instructions are deleted per call: 667 to 635 region instructions.
- The Python oracle passes 544 boundary/random cases with exact signed-int16
  outputs and all 128 exact store addresses.  Input/intermediate/output bounds
  remain 2617/21397/4454.
- Local Slothy uses `/Users/chenpinhao/slothy`, Cortex-A76, spills disabled.
  Functional RA is `OPTIMAL`; all timing windows self-check.
- The A76 model changes from 166 to 158 cycles per call.
- Native Pi 5 testing passes 4096 exact, in-place alias, AAPCS callee-save and
  1792-byte scratch-wipe cases.  Both packages pass `test_kem`, identical
  100-case KAT and byte-identical malformed-ciphertext transcripts.

The initial direct probe failure was a harness error: the inherited P13 test
passed the obsolete `gt864_inverse16_tail_scale_barrett` table after production
had moved to `gt864_p13b_tail`.  The current-table probe passes and the stale
failure is not attributed to P22.

## Pi 5 timing

CPU 3, Cortex-A76 PMU, six balanced processes, unthrottled.  The dedicated
main-I16 harness was compiled at `-O2`; GCC 14.2 incorrectly optimized its PMU
measurement to all-zero results at `-O3`, while `-O0/-O1/-O2` all produced live
counters.  The measured assembly kernels are unchanged.

| Boundary | Baseline cycles | Scheduled cycles | Paired-median delta | Instructions delta |
|---|---:|---:|---:|---:|
| main-I16 ×6 | 2129.531 | 2092.344 | -37.203 | -192 |
| complete Inverse-to-ternary | 4895.516 | 4900.485 | +5.610 | -192 |
| complete Decaps | 40137.150 | 40162.050 | +21.775 | -192 |

The direct boundary improves in all 366/366 pairs; its paired cycle IQR is
[-37.203,-37.187].  However, complete Inverse regresses in 365/366 pairs with
paired IQR [4.750,6.766], and Decaps regresses in 173/186 pairs with paired IQR
[11.512,32.287].  Keygen and Encaps retire exactly zero changed instructions.

The RA-only control is decisively worse: complete Inverse-to-ternary changes
4897.797 to 5084.204 cycles (+186.407), and Decaps changes 40121.850 to
40321.150 (+199.300), despite the same -192 instructions.

## Decision

P22 is rejected.  It proves that deleting held-value copies is locally useful,
but the available schedules do not improve the actual consumer boundary.  No
production source is changed.  The next active item is P23, the ToBytes
coordinate-to-wire routing search, which must first satisfy P6's static reopen
threshold before any new Slothy or Pi 5 campaign.
