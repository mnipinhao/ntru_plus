# Decision

**PASS M5U-A and retain FR-ISO2 as the primary leaf-representation candidate.**

FR-0 remains the physical layout, but its algebraic basis changes from 288
lane-dependent `X^3-z_leaf` polynomial bases to two branch-normalized bases.
The exact homomorphism and complete-product oracle pass, so the representation
is suitable for a bounded implementation search.

Do not connect the reference conversions to Production and do not benchmark
them.  The next hard gate is M5U-B: derive exact Forward and Inverse fused
constant DAGs plus a two-constant BaseMul Montgomery schedule.  It must remove
both conversion passes, preserve 2-load/2-store transform boundaries, prove
the new M5R-D consumer ranges, and show an instruction-count reduction across
Forward + BaseMul + Inverse before any assembly or Slothy work.

BaseMulAdd must be included in M5U-B.  BaseInv and canonical serialization are
recorded as Production veto consumers even if their assembly is deferred.
