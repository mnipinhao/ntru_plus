# D1-P3B14 evidence

Status: **the adjacent 24-byte `LD3` input-once decoder is rejected before
assembly.**

The exact inverse composed map and paired-input witness replay successfully.
If the two decoded q-vectors are unrealistically routed one after another, the
best retained witness has a 30-vector partial-output frontier and active-area
1180.  Treating each pair as atomic, as a real three-result `LD3` requires,
raises the output frontier to 32 vectors and active-area 632 over 27 pair
steps.  The three `LD3` source vectors and unpack/routing temporaries have not
yet been counted.

This is stronger than a marginal cost rejection: the concrete architecture
cannot satisfy the 32-register no-spill contract.  The heuristic is not an
infeasibility proof for every possible FromBytes network.  P3B11 remains the
experimental champion at 935.717 cycles and still exposes 432 lane-routing
operations per top as the main structural target.
