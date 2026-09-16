# M5U-CF5-F — small-weight leaf-basis Pareto search

This default-off algebra experiment compares the existing FR-ISO2 row slope
`H=32` with the signed-small-weight slopes `H={176,464,752}`.

For `u=kappa*theta^(2*column+H*row)`, the residual cubic BaseMul weight is
`z'=z/u^3`, whose row exponent is `K=96-3H mod 864`.  `H=32` gives `K=0`
and weights `{9,3}`.  The other three slopes give `K=432` and weights
`{+9,-9,+3,-3}`.

The gate checks the exact leaf algebra and signed direct-wide BaseMul first,
then searches the frozen oriented NTT9 topology.  No assembly, Slothy, Pi 5
timing, or Production link is allowed until a complete-operation static ledger
has a viable Forward witness.
