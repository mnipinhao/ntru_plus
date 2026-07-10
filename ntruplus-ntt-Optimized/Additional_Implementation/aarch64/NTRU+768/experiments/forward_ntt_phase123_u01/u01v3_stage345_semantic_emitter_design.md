# U01v3 F01 Track E Stage345 Semantic Emitter

Status: E0 passes correctness/ABI; E1 fails correctness.  Production defaults
are unchanged.

Scope is only F01 block0+block1.  The emitter is deliberately conservative:
Stage12 block0 and block1 are computed once per row/stripe, block0 out0 values
remain live for Stage345 block0, and block1 out1 values are written to the
normal Stage12 scratch slots before current Stage345 block1 is run from
scratch.

E0 does not optimize or remap Stage345 arithmetic.  It only replaces the
current block0 Stage345 Q0..Q7 scratch loads with the established live handoff
registers.  Stage345 block1 is emitted in the current from-scratch shape to
reproduce behavior before any allocation rewrite.

The E1 gate is correctness plus ABI pass for E0.  If E0 fails, Track E stops
and no block0 allocation rewrite is attempted.

E1 is emitted only after E0 passes.  It reuses the current fixed-order SSA
allocation experiment for Stage345 block0 under Track E-owned filenames, so the
failure is isolated from shared candidates and production defaults.
