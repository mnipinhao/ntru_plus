# D1-P3B16 route9-pair plus byte-pack hypothesis

Observation: every stock `shuffle2` block serializes six component vectors and
its coefficient pairs are exactly stream pairs `(0,1)`, `(2,3)`, `(4,5)` at
the same lane.  This looks suitable for paired normalization and 12-bit pack.

Hypothesis: two route9 streams can be consumed as a pair and their results can
feed byte packing before all six Official-layout vectors are materialized.

Fixed constraints: exact composed map, one load per FR0 input q-vector, no
coefficient/byte scratch, 32 vector registers, identical 1296 bytes and fixed
public flow.  The gate fails if complete route9 fanout or packed-byte state
cannot be consumed before exceeding the register budget.
