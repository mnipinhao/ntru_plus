# GT32-R7-CONSUMER-ISLAND-059E

Executable consumer-island gate for the persistent symmetric R7 Encap idea.
GT Clean is unchanged.

```text
current: quartic B3 + final-store add(m) + H1 Q24
E0:      seven R7 products + R2 finalizers + H materialization + sparse K/Q24
E1:      seven e=-1 R7 products + dense mixed-scale (W product + W message)
         + one signed REDC32 + Q24
```

E1 does not form H-domain sums/differences, return the products to e=0 with
R2, or perform a 16-bit message add. Its pair data are
`[point_product(e=-1), message(e=0)]` and constants are `[W*R^2, W*R]`.

## Correctness corrections

059E is the first R7 gate to compare two genuine quartic operands through a
degree-six product against current B3. It exposed two holes in 059C/059D:

1. The selected lambda table stores `lambda*R` (e=1), not algebraic lambda.
   Interpolation must use `table*R^-1` at e=0.
2. `vpunpcklwd/hwd` are lane-local. Constant vectors follow physical lanes
   `0,1,2,3,8,9,10,11` and `4,5,6,7,12,13,14,15`.

The old tests reconstructed an already-degree-three quartic and therefore did
not exercise lambda-dependent folding. Their cost measurement remains useful,
but the product correctness claim is superseded here.

The generator proves all 3,840 product/message basis identities. The
executable passes 1,000 deterministic full-polynomial cases byte-for-byte,
including canaries. The mixed accumulator bound is 36,099,066; exhaustive
signed REDC32 output is `[-2279,2279]`.

## Result

Eight pinned-core launches:

| full 192-leaf island | median TSC | delta vs current |
| --- | ---: | ---: |
| current quartic | 493 | -- |
| E0 faithful R7 | 729 | +237 |
| E1 scale-deferred / H-elided | 889 | +398 |

PMU over 250,000 calls corroborates this: E0 costs about +381 core cycles and
+551 instructions/call; E1 costs about +632 cycles and +989 instructions/call.

E1 genuinely deletes seven R2 finalizers, H materialization, and the i16 add,
but raw-E7 lowering makes the exit dense: 56 `vpmaddwd` and 48 `vpaddd` per
block, versus E0's H-domain 16 and 8. E1 is about 161 TSC slower than E0.

## Decision

Close this specific family: centered raw E7 operands, seven pointwise
Montgomery products, and either materialized-H E0 or dense mixed-scale E1 into
the current Q24 endpoint. Reopen only if a producer-native representation
keeps the late map sparse, or if the consumer output contract changes.

```sh
make clean all
make run
perf stat -e cpu_core/cycles/,instructions ./build/bench --pmu control
perf stat -e cpu_core/cycles/,instructions ./build/bench --pmu e0
perf stat -e cpu_core/cycles/,instructions ./build/bench --pmu e1
```

