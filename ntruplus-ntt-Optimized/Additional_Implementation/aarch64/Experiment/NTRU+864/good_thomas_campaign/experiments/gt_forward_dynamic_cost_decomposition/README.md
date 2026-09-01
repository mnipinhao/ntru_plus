# M5Q: GT864 Forward dynamic-cost decomposition

M5Q is an `understand` gate over the frozen M5O implementation.  It changes no
kernel instruction.  `analyze_assembly.py` reconstructs the exact dynamic path,
aligns all 633 symbolic one-bank instructions with the order-preserving Slothy
allocated artifact, and recovers every symbolic vector value's physical
register and lifetime.

The static ledger must total 4,825 instructions inside the GT symbols.  M5P
measured 4,832 instructions per call, so the remaining seven are the common C
measurement loop/call overhead.  Official measured 4,035 under the same
harness, hence its kernel is 4,028 and the exact GT excess is 797.

The Pi 5 component harness separately measures top split and pass 2 with the
same perf-event cycles/instructions group.  Component cycles are diagnostic,
because isolated cache state is not identical to immediate producer-consumer
composition; retired instructions must match the static ledger exactly after
common harness subtraction.
