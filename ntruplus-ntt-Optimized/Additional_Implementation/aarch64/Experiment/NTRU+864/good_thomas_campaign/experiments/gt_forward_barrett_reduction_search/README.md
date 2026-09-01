# M5F-r2: Barrett reduction placement search

This default-off hard gate decides how many identity reductions the fused
Forward schedule needs before assembly. It compares R0 through R4 using the
exact 276 `(b,bprime)` pairs consumed by NTT16 twist/stages, NTT9 twist,
rho/rho2, eta/eta-inverse, and identity.

`prove_constant_coverage.py` cross-checks that set against M5F's independent
exhaustive generator and checks all 18,087,936 signed-halfword products. The
maximum result is 3436. `search_reductions.py` then exhausts each actual fixed
multiply over its incoming integer interval and propagates asymmetric bounds
through every named node for both top branches and all sixteen columns.

The intervals are sound over-approximations of reachable sets: fixed-multiply
transfer is exact for the incoming interval, while an upstream interval may
contain unreachable holes. Since R0 is already below int16 under this
over-approximation, SMT/MILP correlation refinement cannot change the safety
decision and is intentionally skipped.

Run `make check`. Generated JSON includes every node interval and the cost
fields used for the assembly decision. This gate changes no Production source.
