# Decision

Retain fixed-row eight-column batching as the primary GT transform-domain ABI.
Treat public `P9` as output-register order and public `P16` as lane order; do
not canonicalize either at runtime.

Also retain lane-dependent row rotation as a conditional extension.  It has the
same physical producer shape and can be free routing-wise, but its exact
`a_c` choices belong to the later twist/table experiment.

Retain fixed-column row-lane as a secondary candidate because it removes the
main NTT16-to-NTT9 transpose.  Its cross-lane NTT9 and row-8 repack must be
measured before comparing it with the fixed-row serializer path.

Reject only column-stream chunking before serializer microbenchmarks: nine
outputs per column cross every eight-leaf BaseMul tile boundary and destroy the
stable SIMD batch invariant.
