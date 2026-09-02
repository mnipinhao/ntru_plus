# Hypothesis

Two block-specific instantiations of one CF1 scaled-NTT9 witness can share one
register-only region with:

- block 0 operating on GT columns 0 through 7;
- block 1 operating on GT columns 8 through 15;
- block 0's nine outputs live and unchanged through all of block 1;
- eighteen distinct final output registers;
- no preservation copy, spill, stack access, coefficient load/store, or new
  memory boundary.

Each block must use independently generated lane constants.  Reusing the
columns-0-through-7 vectors for columns 8 through 15 would be mathematically
wrong whenever the witness factor has a nonzero column coefficient.

The gate is register and composition feasibility only.  It does not include
the NTT16 producer, output stores, linked Forward oracle, Cortex-A76 timing, or
SUPERCOP.
