# Results

Constant coverage passes with 276 distinct pairs, 18,087,936 exhaustive
signed-halfword products, and maximum fixed-product magnitude 3436.

| Candidate | Identity reductions/block | Fixed multiplies/block | Maximum node | NTT9 register model | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| R0 none | 0 | 36 | 25569 | 23 | select |
| R1 reduce s0 | 1 | 37 | 18592 | 24 | safe control |
| R2 reduce a0 | 1 | 37 | 16511 | 24 | safe control |
| R3 reduce b0+c0 | 1 | 37 | 17286 | 25 | reject register pressure |
| R4 s0+b0+c0 | 3 | 39 | 10436 | 24 | reject unnecessary work |

Every candidate is interval-safe. All have maximum multiplier DAG depth nine,
so the reductions do not improve the transform's longest multiplication chain.
R1 has twist-region ILP; R2/R3/R4 place an added dependency between radix-3
levels. R0 needs neither special identity instructions nor reciprocal-nine
placement.

The selected R0 was replayed in the compiled M5F composition test: 55 cases,
zero coefficientwise mod-q mismatches against M5B+M4, and maximum observed
output magnitude 12245. The same replay passes AddressSanitizer and
UndefinedBehaviorSanitizer with no findings.
