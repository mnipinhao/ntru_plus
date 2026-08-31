# Range proof

The proof starts from every signed field representative in `[-3456,3456]`, a
superset of both centered `[-1728,1728]` and canonical `[0,3456]` inputs.
It exactly models the existing top split's signed `mul`, `sqrdmulh`, and `mls`,
including the intentional low-half wrapping used by fixed-constant reduction.
Dependency between `high` and `high-fixed_alpha(high)` is preserved.

| Stage | alpha maximum | beta maximum |
| --- | ---: | ---: |
| top split | 5292 | 8450 |
| branch twist | 1845 | 1918 |
| radix-2 length 2 | 3543 | 3648 |
| radix-2 length 4 | 5266 | 5391 |
| radix-2 length 8 | 7037 | 7149 |
| radix-2 length 16 | 8871 | 8874 |

The branch twist is important: its Montgomery reduction brings the larger top
split representatives back below 1919 before additive growth begins. All
following butterfly additions/subtractions fit signed int16 without wrap. The final conservative
maximum is 8874, leaving margin `15752-8874 = 6878` for M5A.

`prove_ranges.py` performs 1,005,695 Montgomery congruence checks. The largest
absolute widened product is 13,443,950 and the largest reduction numerator is
125,698,048, both signed-int32 safe. No explicit Barrett reduction is needed.
