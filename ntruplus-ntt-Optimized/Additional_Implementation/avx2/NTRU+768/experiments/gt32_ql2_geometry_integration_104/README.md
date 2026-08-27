# GT32-QL2-GEOMETRY-INTEGRATION-104

This gate integrates the three executable QL2 kernels qualified by experiment
103 without changing their arithmetic or the production caller contract.

The control and candidate both contain the existing page-aligned E0V tail and
the same deterministic page-aligned QL2 RX cluster.  Their 611-byte Encap input
sections are equal-sized; only the Encap caller machine bytes differ.  All
other shared text/rodata symbols must retain identical addresses, sizes, and
machine bytes.

The production source tree is not modified by this experiment.

`make benchmark` runs the primary formal campaign.  Two retained independent
confirmation campaigns resolve its system-wide outliers; `RESULTS.md` records
the complete qualification decision.  QL2 gives a repeatable production Encap
win, but promotion is deferred because a small ASLR-off Decap collateral
regression reproduces.
