# M5U-CF5-C — FR-ISO2 scaled-consumer cost decomposition

This is a benchmark-and-understand gate, not a new arithmetic candidate.
FR-ISO2, the 345-instruction NTT16 producer, returned Slothy allocations,
two-load/two-store Forward boundary, range, and output layout are frozen.

The gate compares each scaled CF5-B bank with the same `(top,component)` input
processed by the 569-instruction M5R-D FR0 bank.  Generated isolated functions
retain exact instruction order and the same eighteen output stores.  Their
only purpose is to attribute the already measured full-Forward delta.

The route threshold is 184.839 cycles that must be removed from each complete
CF5-B Forward before FR-ISO2 can optimistically break even after two Forwards
and the measured BaseMul saving, assuming zero Inverse penalty.
