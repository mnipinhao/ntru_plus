# Results

`make check` passes 75 boundary, impulse, centered-random, and wide-range
randomized cases. Neon output is
exactly equal to a scalar mirror of the same reduction schedule and equals the
direct 32-term evaluation modulo 3457. There are zero mismatches.

The machine proof covers the wider `[-3456,3456]` input contract and proves a
maximum of 8874 at every NTT16 output and intermediate halfword. M5A permits
15752, so the top-split/NTT16 producer needs zero additional Barrett reductions.
The randomized test observed maximum 7593; this observation is not the proof.

Compiler inspection is deliberately separate. This build uses a 352-byte stack
frame for the 16-vector array and saved state, so this experiment makes no
two-load/two-store or performance claim. It freezes the arithmetic, constants,
natural-column ordering, and range contract for later handwritten assembly.
