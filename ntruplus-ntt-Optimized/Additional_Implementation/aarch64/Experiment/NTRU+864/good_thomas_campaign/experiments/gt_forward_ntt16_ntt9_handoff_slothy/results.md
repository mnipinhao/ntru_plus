# Results

M5J passes its bounded physical-ABI gate.

- Exact coordinate map: 144/144 producer coordinates reach the intended row
  vector and lane; mapping SHA-256 is
  `973e60ce41f3de3c97f9869b9376132a62d51bb8cec015ae4fe407e10635f806`.
- Twist tables: 256 pairs checked across two top branches and two column
  blocks; all belong to M5F's exhaustive Algorithm-10 constant set.
- Exact inherited bounds: NTT16 9342, fixed multiplication 3436, complete
  NTT9 28568, zero unsafe signed-halfword nodes.
- Region: 190 real instructions and zero physical vector tokens in source.
- Remote RA: Slothy 0.2.2, OPTIMAL, selfcheck OK, spills forbidden.
- Remote scheduling: `split_heuristic_full:OK!`, 47 expected N1-proxy cycles.
- Emitted register set: exactly `v0-v7,v17-v31`; no use of `v8-v16`.
- Memory/flow: 16 public `ldr qN,[x3],#16`; no coefficient memory, store,
  stack, branch, or extra GPR instruction.
- Local assembly: allocated and scheduled artifacts both pass the AArch64
  assembler.

The 47-cycle number is model metadata for this extracted boundary, not a Pi 5
or full-Forward performance result.
