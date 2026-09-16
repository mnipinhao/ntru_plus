# Results

## Direct leaf intervals

The following values are medians of per-launch LBR call/return intervals over
128 balanced fresh processes. Deltas are promoted GT QL2 minus Official in
core cycles.

| Semantic region | Official | GT QL2 | Delta |
|---|---:|---:|---:|
| Decode public key | 172.00 | 202.00 | **+30.00** |
| CBD(r) | 118.00 | 144.50 | **+26.50** |
| r producer | 728.00 | 676.75 | **-51.25** |
| serialize r-hat | 212.00 | 257.25 | **+45.25** |
| SOTP(m) | 132.00 | 135.75 | +3.75 |
| m producer, including QL2 landing | 722.25 | 593.50 | **-128.75** |
| QL2 general BaseMul | 525.00 | 545.25 | **+20.25** |
| QL2 sum and final serializer | 259.25 | 237.00 | **-22.25** |
| descriptive mapped-leaf total | 2868.50 | 2792.00 | **-76.50** |

The mapped total is descriptive and is not subtracted from the formal
Experiment 139 Encap delta. LBR visibility, out-of-order overlap, nested work,
and whole-caller context make leaf medians non-additive.

## Stability against the pre-promotion profile

The result closely reproduces Experiment 133: r-hat serialization remains
about `+45`, Decode about `+30`, CBD about `+25`, and the QL2 producer remains
about `-130`. Promotion did not create a new component-level bottleneck.

## Optimization interpretation

The r-hat serializer is the largest positive direct leaf interval, but the
controlled serializer gate 054 measured only `+20 TSC` intrinsic GT codec
debt. Its larger production LBR interval therefore cannot all be claimed as a
serializer rewrite budget. Compact loops, constant residency, range-only
specialization, immediate producer-to-Q24 fusion, and persistent-r across the
hash barrier have already failed their respective executable gates.

The remaining ranked opportunities are:

1. r-hat serializer, only with a new operation-class deletion or a concrete
   load-dependency chain; local rescheduling has no new premise;
2. Decode, only with a new decoder/producer factorization or an asymmetric
   raw-h/normalized-r BaseMul contract;
3. QL2 BaseMul output formation, only if part of its 96-route M-to-QL2 output
   network can be absorbed without reopening the rejected QL2-native B3;
4. CBD is a measured contextual debt, but prior stack/data-placement gates
   found no actionable mechanism.

Forward(r), Forward(m)-to-QL2, and the final QL2 serializer are winners and
remain frozen. No single observed leaf debt can honestly account for the full
formal Encap deficit.
