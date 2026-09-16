# M5U-CF5-E — B3–BaseMul leaf-basis co-design

This default-off algebra experiment tests whether the NTT9 B3 butterflies can
remain common-scale add/sub islands while a geometric degree-3 basis moves the
remaining row-dependent work to BaseMul.

The candidate family is

`D_u = diag(1,u,u^2)`, with leaf modulus `Y^3 - z/u^3`.

The first gate forbids every post-add scale transition.  It then asks whether
the resulting BaseMul weights retain the direct-wide arithmetic benefit that
made FR-ISO2 attractive.  No assembly, Slothy, Pi timing, or Production link is
allowed in this experiment.
