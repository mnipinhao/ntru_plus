# Decision

M5E-r1 passes and replaces the initial M5E implementation as the handwritten
inverse assembly baseline for FR-0, still default-off and outside Production.

The result closes the immediate M5D uncertainty: packed alpha/beta state fits
in caller-saved vector registers, the complete inverse preserves the intended
two-load/two-store algorithmic boundary, and component-strided natural output
can be emitted without a top scratch or coefficient spill. Algorithm-10 fixed
Barrett multiplication is exhaustively checked and the entire candidate is
coefficientwise congruent to M5D. Because representatives change, M5D's 3696
exact-output bound is replaced by M5E-r1's independently proved 6888 bound.

The remaining trade-off is scalar store pressure. Code size falls from 10,744
to 7,292 bytes, while the local combined median-of-medians falls from 919.750
to 545.354 ns. Before Production consideration, target PMU and full-path
measurements must still price instruction-cache and store behavior.
The next hard gate is handwritten forward NTT16 producer/composition, preserving
M5B arithmetic/range and the campaign's two-load/two-store objective. Full
Forward oracle, KEM/KAT, source closure, target attribution, and SUPERCOP remain
later promotion gates.
