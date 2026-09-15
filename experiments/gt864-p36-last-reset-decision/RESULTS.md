# P36 result — retain the last main high-column-8 reset

## Decision

P36 does not change production.  The removal hard gate requires a machine proof
that every current KEM producer execution reaches P8 with `abs(output) <= 5185`.
That proof did not close, so the high-column-8 `SQRDMULH; MLS` remains in P35.
This is a proof-policy decision, not a claim that no stronger future proof can
ever remove it.

## What was established

The old independent interval bound for row 6 is `2569 + 2709 = 5278`.  Exhaustive
enumeration of every signed-int16 constant congruent to the current composite
weights, plus nearby legal quotient constants, finds that `(335,3175)` and
`(120,1137)` are already minimax.  Changing the table representative therefore
does not remove the excess.

P36 then rebuilt the producer in layers:

1. Each of the 32 independent `(top,column,row6)` one-product NTT9 blocks was
   modeled with integer source coefficients and exact `SQRDMULH` quotient
   constraints.  Every min/max solve reached global optimality.
2. Those exact bounds fed a 236-variable correlation-aware CT NTT16 model.
3. A continuous-state trial appeared to reach 5187, but independent scalar
   replay disagreed; the trial was rejected as a numerical-relaxation artifact.
4. With every NTT16 state restored to integer, the 5186-feasibility query timed
   out after 300 seconds with no primal and no infeasibility certificate.

The last result proves neither reachability nor safety.  Since deletion needs a
positive safety proof, the correct hard-gate outcome is to retain the reset.

## Next work

P37 is a fresh profiler checkpoint against the selected
`/home/pi/supercop-20260831` Official package after P35.  It should refresh
full-KEM and component attribution before selecting another arithmetic DAG;
P36 should reopen only with a stronger exact solver/decomposition, not random
testing or the rejected continuous relaxation.
