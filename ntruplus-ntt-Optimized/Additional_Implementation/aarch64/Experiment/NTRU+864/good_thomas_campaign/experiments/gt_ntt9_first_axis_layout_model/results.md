# Results

`make check` passes the exact model, but the NTT9-first candidate fails the
hard gate.

- All 864 P8 coordinates and 864 FR-ISO2 output coordinates are bijective.
- Current P8 can expose two lane-wise NTT9 blocks with 288 total transpose
  instructions, unchanged from NTT16-first, and a 26-register peak.
- NTT9 outputs directly form nine NTT16 `lo/hi` pairs; no extra coefficient
  boundary is needed for the physical layout alone.
- The required `theta^(6*c*s)` phase is free only for column 0.  Columns 1--15
  conjugate to dense 81/81 matrices and have no NTT9 row-rotation solution.
- The phase-free lower bound merely ties CF5-A at 4726 instructions; it cannot
  satisfy the strict-below gate.  The direct dense fallback estimates 8218.
- Canonical CRT packing needs 54 simultaneous output vectors, six natural
  input reads, an extra full-buffer pass, or 864 lane stores.  Its maximally
  optimistic scatter bound is still 5190 instructions.

Decision: reject NTT9-first and retain NTT16-first for CF5-B.
