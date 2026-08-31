# Decision

Retain the stock eight-leaf SoA BaseMul ABI as the first GT consumer-layout
baseline.  Do not build Candidate B/C until the proposed NTT9 producer can be
costed against this exact shape.

Pure row/column permutations remain eligible for zero-runtime carry, provided
the BaseMul zeta table and inverse mapping are regenerated in identical
physical order.  Phase carry is outside this gate.
