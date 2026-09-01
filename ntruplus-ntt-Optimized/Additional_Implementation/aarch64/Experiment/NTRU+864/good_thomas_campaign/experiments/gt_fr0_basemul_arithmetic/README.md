# M5C: FR-0 BaseMul arithmetic closure

This default-off experiment answers one bounded question: can the fixed-row
FR-0 transform-domain ABI directly support correct NTRU+864 BaseMul and
BaseMulAdd arithmetic with its generated branch-specific zeta table?

Each of 36 physical tiles is:

```text
offset = 24*group
a0 = a[offset+0..7]
a1 = a[offset+8..15]
a2 = a[offset+16..23]
zeta = gt864_fr0_zetas_mul[group][lane]
```

Each lane independently multiplies in `Z_3457[X]/(X^3-zeta)`. Inputs,
addends, and outputs are normal `R0`; zeta is Montgomery `R1`. The implementation
uses widening int32 accumulators and the official two-step Montgomery/RSQ scale
schedule. Run `make check` for table-map, range, exact-schedule, canonical
cubic, and alias gates. Production remains untouched.
