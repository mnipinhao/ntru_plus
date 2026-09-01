# Range and scale proof

M5B proves NTT16 output at most 8874. Replaying the exact M5A FR-0 schedule
with that interval gives BaseMul operand union `[-24437,24438]`; the symmetric
consumer contract is therefore `[-24438,24438]`.

| Accumulator | Conservative interval |
| --- | ---: |
| one variable product | ±597,215,844 |
| two variable products | ±1,194,431,688 |
| three variable products | ±1,791,647,532 |
| coefficient 0 after zeta term | ±631,698,084 |
| coefficient 1 after zeta term | ±1,213,166,664 |

Every accumulator fits signed int32. After the second Montgomery reduction,
the three R-minus-1 bounds are respectively 11368, 20240, and 29067. Final
RSQ conversion returns normal-R0 BaseMul outputs bounded by 2114. Including an
R0 addend in the combined final reduction gives BaseMulAdd bound 2168.

The implementation intentionally uses low-half wrap to construct the
Montgomery quotient. `prove_ranges.py` exhausts all 65,536 possible low halves
for the `-qinv/add` identity; no variable product or accumulator wraps int32.
