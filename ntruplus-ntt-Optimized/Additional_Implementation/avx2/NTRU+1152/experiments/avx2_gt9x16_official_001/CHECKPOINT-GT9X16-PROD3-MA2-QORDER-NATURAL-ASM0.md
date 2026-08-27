# GT9X16-PROD3-MA2-QORDER-NATURAL-ASM0

This checkpoint realizes the C1-natural-Q ABI as namespaced, aligned AVX2
machine objects.  The current-Q producer and H1 remain untouched controls.
T0, the MA2 arithmetic DAG, scale, reductions, and serializer bit semantics
are frozen.

The candidate consists of:

- a PROD3 producer that retains the C1 transpose's natural physical-q order;
- a resident-h formation and lane-wise MA2 whose lambda tables are reindexed
  offline (zero runtime lambda shuffles); and
- an H1 reconstruction generated from the exact natural-Q ownership schedule.

Correctness is closed in four independent layers.  For every physical plane,
the natural producer is the raw, representative-exact Q permutation of the
current producer.  Resident h is checked against its exact source-position
oracle.  Current and natural MA2 plane outputs satisfy raw lane equivariance.
Finally, current and natural H1 produce identical 1728-byte outputs.  The test
covers zero, alternating boundary input, and 255 deterministic random small
caller inputs; every invocation compares all 1152 physical cells.

The linked caller-weighted audit uses two producers, one resident-h/MA2 path,
and one H1.  Natural minus current is exactly `-192` routing instructions and
`+16` data loads.  Data stores, `vpmullw`, `vpmulhw`, and Barrett
`vpmulhrsw` counts are unchanged.  All six entries are 32-byte aligned; all
new constants use `.p2align 5`; and the linked objects have no calls, branches,
stack references, vector spills, or internal `vzeroupper`.

This is a correctness and structural qualification only.  It does not claim
that `-192 routes + 16 loads` is a cycle win.  The next authorized checkpoint
is a SUPERCOP-derived caller-shaped current-Q versus natural-Q paired pricing
campaign.  Native KEM remains unauthorized until that arbitration is complete.
