# P23 — global ToBytes routing DAG search

P23 rebinds the routing search to current P18/P19 production.  The older P6-D3
reopen threshold is historical: P18 already reduced the P6-D3 4074-instruction
kernel to 2348/2128 Full/Small instructions and was promoted by P19.

This gate interns every exact P18 source rotation and three-level transpose node
across all fifteen classes.  It searches output order while modeling the 26
routing registers available beside Full-mode normalization/packing constants.
Completed output vectors are consumed immediately and are not retained.

The accepted schedule uses 61 source loads plus the exact 224 unique routing
nodes per top and peaks at 26 routing registers.  A one-output timing control
lost despite the smaller instruction count; the retained three-output Slothy
schedule restores cross-output ILP and wins both Pi 5 component boundaries and
all three full-KEM operations.  See `RESULTS.md`.  Production remains P18 until
the separate P24 promotion gate.
