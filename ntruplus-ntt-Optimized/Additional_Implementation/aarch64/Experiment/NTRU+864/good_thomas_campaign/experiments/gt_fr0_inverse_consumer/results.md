# Results

`make check` passes:

- 49 transform-domain boundary, impulse, and randomized inverse cases;
- zero direct inverse-NTT9 mismatches;
- zero modulo-q mismatches against official scalar `invntt`;
- zero normalized algebra-roundtrip mismatches;
- eight complete Forward -> M5C BaseMul -> M5D inverse products with zero
  schoolbook quotient-ring mismatches;
- zero dependency on the 32 P8 padding values.

After G0 expands the input contract to `[-2205,2205]`, the largest observed
output magnitude is 3467. The machine proof, rather than that observation,
establishes the unchanged 3696 final bound and a maximum lazy halfword
magnitude of 19845.

The algorithmic boundary is exactly two full-buffer load/store passes. The
packed alpha/beta second pass eliminates a third top-branch pass. Compiler
inspection records 160-byte and 416-byte stack frames for the two intrinsic
functions, so no stackless or performance claim is made.

Static review reports no optional AArch64 features and no secret-dependent
branches or memory access. The Neon inventory reports 11 expected cross-lane
operations: Montgomery low/high-half reconstruction, the explicit 8x8
transpose, and public top packing. Their cost remains part of the handwritten
assembly gate.
