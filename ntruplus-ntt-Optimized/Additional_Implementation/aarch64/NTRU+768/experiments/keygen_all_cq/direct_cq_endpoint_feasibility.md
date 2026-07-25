# Direct-CQ Stage345 Endpoint Feasibility

This is a correctness-first, default-off gate. It analyzes the active
production Stage345 schedule without changing arithmetic, reduction, or
register allocation.

## Hard contract

- Four BPQ Q outputs form one CQ group.
- An output overwritten before the fourth Q is ready must be parked in a
  vector register untouched for the entire interval.
- The transpose uses four dead vector temporaries. One dead input from each
  input pair receives the first-level `trn2`; no live input is overwritten.
- No spill/reload, recomputation, or arithmetic/reduction change is allowed.

## Result

`feasible_no_spill: true`
`failed_groups: []`
`total_parking_moves: 9`

| CQ group | row | block.group | parking moves | CQ inputs | transpose temps | gate |
|---:|---:|---:|---:|---|---|---|
| 0 | 0 | 0.0 | 2 | q28, q29, q2, q18 | q5, q8, q22, q25 | pass |
| 1 | 0 | 0.1 | 0 | q14, q1, q26, q4 | q2, q3, q5, q8 | pass |
| 2 | 0 | 1.0 | 0 | q17, q2, q9, q1 | q10, q14, q18, q20 | pass |
| 3 | 0 | 1.1 | 0 | q6, q3, q5, q4 | q1, q2, q8, q9 | pass |
| 4 | 0 | 2.0 | 1 | q2, q9, q10, q19 | q3, q4, q5, q6 | pass |
| 5 | 0 | 2.1 | 0 | q11, q14, q1, q28 | q2, q3, q4, q5 | pass |
| 6 | 0 | 3.0 | 0 | q9, q2, q10, q19 | q4, q5, q7, q8 | pass |
| 7 | 0 | 3.1 | 0 | q12, q14, q1, q3 | q2, q4, q5, q6 | pass |
| 8 | 1 | 0.0 | 2 | q28, q29, q2, q18 | q5, q8, q22, q25 | pass |
| 9 | 1 | 0.1 | 0 | q14, q1, q26, q4 | q2, q3, q5, q8 | pass |
| 10 | 1 | 1.0 | 0 | q17, q2, q9, q1 | q10, q14, q18, q20 | pass |
| 11 | 1 | 1.1 | 0 | q6, q3, q5, q4 | q1, q2, q8, q9 | pass |
| 12 | 1 | 2.0 | 1 | q2, q9, q10, q19 | q3, q4, q5, q6 | pass |
| 13 | 1 | 2.1 | 0 | q11, q14, q1, q28 | q2, q3, q4, q5 | pass |
| 14 | 1 | 3.0 | 0 | q9, q2, q10, q19 | q4, q5, q7, q8 | pass |
| 15 | 1 | 3.1 | 0 | q12, q14, q1, q3 | q2, q4, q5, q6 | pass |
| 16 | 2 | 0.0 | 2 | q28, q29, q2, q18 | q5, q8, q22, q25 | pass |
| 17 | 2 | 0.1 | 0 | q14, q1, q26, q4 | q2, q3, q5, q8 | pass |
| 18 | 2 | 1.0 | 0 | q17, q2, q9, q1 | q10, q14, q18, q20 | pass |
| 19 | 2 | 1.1 | 0 | q6, q3, q5, q4 | q1, q2, q8, q9 | pass |
| 20 | 2 | 2.0 | 1 | q2, q9, q10, q19 | q3, q4, q5, q6 | pass |
| 21 | 2 | 2.1 | 0 | q11, q14, q1, q28 | q2, q3, q4, q5 | pass |
| 22 | 2 | 3.0 | 0 | q9, q2, q10, q19 | q4, q5, q7, q8 | pass |
| 23 | 2 | 3.1 | 0 | q12, q14, q1, q3 | q2, q4, q5, q6 | pass |

The JSON artifact records every output-ready line, intervening clobber,
parking assignment, completion live set, and temporary-register pool.
