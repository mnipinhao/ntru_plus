# Y0 to Y1 input and permutation audit

Y0 forms source-u0 and source-u1 tiles separately. Each of the 48 native blocks is loaded
once for each tile family, producing 96 Pass-A loads. The second load exists solely to
derive the other qword selection (`0xa0` versus `0xf5`).

Y1 pairs those tile families. For each native block pair it:

1. loads both blocks once;
2. derives the `0xa0` compact vector;
3. destructively derives the `0xf5` vector from the retained originals;
4. keeps eight L0 values live while sharing L1/L2 factor loads.

Therefore every native address has exactly one Pass-A load: 48 loads total. The four
`vpermq` operations per logical compact pair remain necessary: two source vectors times
two distinct qword maps. Replacing them with unpack/blend chains increased instruction
count and was not used. Branch halves never cross.

Pass-A factor/qinv loads fall from 72 to 36 because paired u0/u1 tiles consume the same
L1/L2 factors while they are live. The L3/L4 table order is unchanged.
