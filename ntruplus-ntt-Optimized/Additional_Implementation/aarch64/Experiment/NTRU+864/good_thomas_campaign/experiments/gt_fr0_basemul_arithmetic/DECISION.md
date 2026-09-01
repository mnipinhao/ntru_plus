# Decision

Pass and freeze M5C as the FR-0 BaseMul/BaseMulAdd arithmetic contract. The
generated zeta order is not merely a root-set hypothesis: it is consumed by a
working 36-tile Neon implementation, matches official leaf roots through a
proved permutation, passes exact and canonical arithmetic, supports aliases,
and stays within signed int32/R0 output bounds.

Production remains unchanged. This result does not close BaseInv or inverse
transform arithmetic, and it does not establish performance. The next bounded
hard gate is the matching inverse permutation and inverse arithmetic path.
