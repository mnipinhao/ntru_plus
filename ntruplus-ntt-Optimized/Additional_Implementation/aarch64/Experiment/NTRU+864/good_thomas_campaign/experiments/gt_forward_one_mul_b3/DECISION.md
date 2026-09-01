# Decision

**PASS — retain M5R-C as the new experimental Forward arithmetic baseline.**

The candidate satisfies the requested hard gate by deleting three, not one,
complete Algorithm-10 multiplications per NTT9 block.  It keeps M5R-B's two
independent twist loads, memory boundary, output ordering, R0 scale, and wrapper
ABI; Slothy allocates/schedules it without spill; full Forward correctness and
the A76 PMU gate pass.

The exact representative ABI is deliberately relaxed from “bit-identical to
M5R-B” to “same residue, bounded R0 representative.”  This is safe for the
existing transform-domain contract and is explicitly recorded rather than
hidden behind the modulo-q oracle.

Next hard gate: independently test the same one-product identity on the three
level-2 B3 nodes.  Their `x1-x2` operands are now bounded enough to be plausible,
but that campaign must redo the exact downstream/output range proof and may not
be folded into this result retroactively.
