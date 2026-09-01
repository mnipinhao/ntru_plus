# Decision

M5E passes. Retain this implementation as the first handwritten inverse
assembly baseline for FR-0, still default-off and outside Production.

The result closes the immediate M5D uncertainty: packed alpha/beta state fits
in caller-saved vector registers, the complete inverse preserves the intended
two-load/two-store algorithmic boundary, and component-strided natural output
can be emitted without a top scratch or coefficient spill. Exact differential
testing inherits M5D's previously proved official inverse, range, roundtrip,
and full-product properties by transitivity; M5E does not replace those oracles.

The accepted trade-off is substantial code size and scalar store pressure.
Before Production consideration, target PMU measurements must determine
whether the 10,744-byte fully unrolled inverse harms instruction-cache behavior.
The next hard gate is handwritten forward NTT16 producer/composition, preserving
M5B arithmetic/range and the campaign's two-load/two-store objective. Full
Forward oracle, KEM/KAT, source closure, target attribution, and SUPERCOP remain
later promotion gates.
