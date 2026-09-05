# Range and scale proof

G0 `gt_m5rd_fr0_range_chain_closure` supersedes the historical M5B/M5A input
chain for the current M5R-D assembly. Replaying the exact constant-specific
`9342` Algorithm-10 producer through both levels of M5R-D one-product B3 gives
FR-0 union `[-25569,25566]`; the symmetric M5C consumer contract is therefore
`[-25569,25569]`.

| Accumulator | Conservative interval |
| --- | ---: |
| one variable product | ±653,773,761 |
| two variable products | ±1,307,547,522 |
| three variable products | ±1,961,321,283 |
| coefficient 0 after zeta term | ±691,238,529 |
| coefficient 1 after zeta term | ±1,327,773,762 |

Every accumulator fits signed int32. After the second Montgomery reduction,
the three R-minus-1 bounds are respectively 12276, 21989, and 31656. Final
RSQ conversion returns normal-R0 BaseMul outputs bounded by 2148. Including an
R0 addend in the combined final reduction gives BaseMulAdd bound 2205.

The implementation intentionally uses low-half wrap to construct the
Montgomery quotient. `prove_ranges.py` exhausts all 65,536 possible low halves
for the `-qinv/add` identity; no variable product or accumulator wraps int32.
