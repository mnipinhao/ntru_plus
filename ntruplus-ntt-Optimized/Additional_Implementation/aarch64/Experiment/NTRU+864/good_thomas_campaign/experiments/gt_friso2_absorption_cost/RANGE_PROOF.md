# M5U-B range and scale proof

Inputs use the M5R-D/M5U-A split bound: component 0 is at most 26306 and
components 1/2 are strictly below the Algorithm-10 envelope 5185.

The direct `z0=9/3` cubic accumulators are formed in signed 32-bit lanes.  The
machine proof checks every symbolic worst-case sum and verifies the largest is
1,175,921,686, below 2^31.  It then applies the exact signed `-qinv/add`
Montgomery envelope, verifies the R^-1 representatives fit signed halfwords,
and checks both the BaseMul `RSQ` finish and BaseMulAdd `RSQ + c*R` finish.

Scale ledger:

```text
R0 inputs * R0 inputs, integer z0 -> wide R0 accumulator
Montgomery reduction             -> R^-1 halfword
multiply by RSQ=R^2              -> wide R1
Montgomery reduction             -> R0 halfword
BaseMulAdd: add c(R0)*R inside the final wide R1 accumulator
```

No narrowing precedes a proven reduction.  This proves the arithmetic DAG,
not a register allocation or cycle result.
