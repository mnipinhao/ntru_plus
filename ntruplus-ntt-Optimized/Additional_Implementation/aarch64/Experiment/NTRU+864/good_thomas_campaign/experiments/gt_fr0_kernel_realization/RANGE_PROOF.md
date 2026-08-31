# Range proof

`prove_ranges.py` models the exact signed-integer instruction schedule, not
only field congruence. It requires every halfword add/sub to remain in int16;
therefore the assembly does not depend on wraparound.

For all 244 public constants used by the candidate, every possible int16 input
was exhaustively checked against the widening Montgomery reduction: 15,990,784
congruence checks. The largest absolute 32-bit product is 56,426,496 and the
largest reduction numerator is 169,410,560, both within signed int32.

The maximum symmetric producer contract proved by interval propagation is:

```text
every P8+tail input coefficient x satisfies |x| <= 15752
```

At that bound the largest halfword intermediate is 32767. Bound 15753 fails:
`level2.group0.out0` can reach 32768. Centered input `[-1728,1728]` reaches at
most 15833; `[-3456,3456]` reaches at most 17939.

This is a conditional interface proof. It does not claim that the future
NTT16 producer already meets the contract. That producer must independently
prove its actual P8+tail output lies in `[-15752,15752]` before fusion.
