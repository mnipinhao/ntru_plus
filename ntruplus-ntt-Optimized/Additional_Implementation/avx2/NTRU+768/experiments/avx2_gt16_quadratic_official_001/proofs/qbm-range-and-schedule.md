# QBM range and schedule proof

Fused split deliberately keeps `a0 +/- s*a2` lazy in `[-3456,3456]`; this
removes six centered-correction instructions per vector while staying inside
signed int16.  Weighted right-operand lanes are reduced to `[-1728,1728]`.
Consequently:

```text
|c0 accumulator| <= 2*3456*1728 = 11943936
|c1 accumulator| <= 2*3456*3456 = 23887872
```

Both are strictly inside signed int32 and exclude the `-32768 * -32768`
special case.

For a signed accumulator `x`, let signed `m` be the low word of
`x*q^-1 mod 2^16`.  Then `x-m*q` is divisible by `2^16`, and the fixed AVX2
sequence is:

```text
vpmullw qinv
vpand    low-word-mask
vpmaddwd [q,0,...]
vpsubd
vpsrad   16
```

Exhausting all 65,536 low words and both legal extreme high-word quotients
proves the output interval `[-2092,2093]` over the complete accumulator range.
It fits int16 and carries Montgomery scale `R^-1`.

The selected per-vector schedule is two loads, four weighted-operand
instructions, one pair swap, two `vpmaddwd`, two five-instruction reducers, two
pack/order instructions, and one store: 22 instructions.  It uses at most 11
YMM registers.  The postmultiply control costs 31 instructions/vector; the
dual asymmetric ABI costs 19 in QBM plus five producer/precompute instructions
and expands one operand by 1,536 bytes, so neither wins the complete boundary.
