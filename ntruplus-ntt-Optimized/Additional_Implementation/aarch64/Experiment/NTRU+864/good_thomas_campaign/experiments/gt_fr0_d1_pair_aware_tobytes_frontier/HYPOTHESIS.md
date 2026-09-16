# D1-P3B13 pair-aware ToBytes frontier hypothesis

P3B9 showed that an already adjacent pair of normalized q-vectors can be
packed faster by `pack16` than by two independent `pack8` calls.  This gate
asks whether the exact P3B6 input-once schedule can be reordered so each
adjacent serialized output pair remains in registers until both vectors are
complete, without the P3B10 coefficient scratch boundary.

The fixed contracts are the P3B6 composed map, exact signed-int16
normalization, 1296 output bytes, one load per FR0 input q-vector, no
coefficient scratch, and no spill.  A candidate is viable only if its paired
output frontier plus source, normalization and pack temporaries fits in the 32
architectural vector registers.

This is a feasibility gate, not an optimality proof or a cycle benchmark.
