# Results

`make check` passes all four tracked feasible witnesses.

| top | component | vector mulmods | extra over M5R-D | deleted vs CF0 | max abs |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 26 | 8 | 1 | 19121 |
| 0 | 2 | 26 | 8 | 1 | 19427 |
| 1 | 1 | 26 | 8 | 1 | 11894 |
| 1 | 2 | 26 | 8 | 1 | 13606 |

For each case the verifier checks 16 columns and all 1296 coefficients of the
9-by-9 linear map.  Across one Forward there are eight scaled blocks, so CF1
uses 64 extra mulmods instead of CF0's 72.  That deletes eight Algorithm-10
mulmods, or 24 arithmetic instructions, per Forward without a new coefficient
memory boundary.

All four HiGHS runs stopped at the 240-second time limit.  Their assignments
are valid feasible witnesses, but the minimum possible cost remains open.
