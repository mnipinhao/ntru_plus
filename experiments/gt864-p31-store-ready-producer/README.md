# GT864 P31 store-ready producer DAG

P31 is an experimental inverse-to-ternary candidate.  It keeps P29's exact
mathematics and natural output ABI, but removes the standalone three-bank main
route.  Pair2 consumes bank0 and emits rows 0--3; pair1 consumes a dense stream
of retained normalized bank2 high halves and emits rows 4--7.  Both output
paths use full-vector `ST3.4h`; there is no lane `ST3` and no coefficient spill.

The candidate passed correctness but failed timing: it is 343.508 cycles
slower than P29 and 418.617 cycles slower than production for the complete
inverse-to-ternary boundary.  It is rejected and production remains unchanged.
See `RESULTS.md` for the full audit and `kernel-contract.yml` for the scratch
and wrapper register contract.
