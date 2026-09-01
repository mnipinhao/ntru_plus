# Register and memory budget

This is an instruction-selection budget, not a claim about current compiler
allocation.

## Pass 1

Inverse NTT9 arithmetic needs nine live row/state vectors, two modulus vectors,
one current public constant, four widening-Montgomery scratch vectors, and at
most six destructively reused radix-3 temporaries: 22 live vectors. The
transpose phase needs eight state plus eight transpose temporaries and the
separate `s=8` vector: 17. These phases do not peak simultaneously.

## Pass 2

Packed-top inverse NTT16 needs 16 state vectors, two modulus vectors, one
current constant, four widening-Montgomery scratch vectors, and one butterfly
temporary: 24. Scaling, top recombination, and stores consume completed `t`
vectors destructively. Packing alpha/beta into vector halves is what avoids a
32-state-vector top-branch peak.

The tail uses the same 16-vector schedule with six live lanes. No extra
register bank is needed.

## Compiler reality

The current `-O3` intrinsic build allocates 160 stack bytes for pass 1 and 416
bytes for pass 2. Therefore the C is an executable arithmetic/layout reference,
not the final kernel. A handwritten assembly gate must demonstrate the above
destructive schedule, inspect spills, and measure its scalar scatter/store
cost before any performance claim.
