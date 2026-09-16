# Decision

**Reject the zero-post-add common-scale B3 candidate.**

Machine-checked facts:

- all 61 scale nodes become one component when all 42 add/sub edges must be
  free;
- common-scale output requires row slope `h=0 mod 864`;
- two-constant BaseMul requires `h in {32,320,608}`;
- the conditions have no intersection;
- the valid row-independent hybrid has 18 BaseMul weights and passes all 2,592
  degree-3 basis homomorphism checks;
- its best cube-rescaled weights still violate the current direct-wide int32
  bound, so it deletes zero widening reductions;
- it costs 19 rather than 18 mulmods per NTT9 block.

The experiment adds no assembly or memory boundary.  M5R-D remains the active
GT Forward experiment and the isolated FR-ISO2 BaseMul result remains valid.

The next algebra gate should either compute the minimum post-add scale cut that
can realize row slope 32, or change the NTT9 arithmetic topology.  It must keep
the full `2F + BaseMul + I` ledger rather than optimize table cardinality alone.
