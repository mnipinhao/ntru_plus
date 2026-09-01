# Results

M5K passes its bounded two-block register-pressure and scheduling gate.

- Exact structure: 333 real instructions, 144 coordinates, eighteen uniquely
  defined outputs, and no first-block output redefinition in block two.
- Exact inherited bounds: NTT16 9342, fixed multiplication 3436, complete
  NTT9 28568, zero unsafe signed-halfword nodes.
- Fixed tail: the first emitted `v16` occurrence is the post-first-NTT9 capture;
  the register may only be reused after that dependency.
- Remote RA: Slothy 0.2.2, OPTIMAL in 31.46 seconds, selfcheck OK, spills
  forbidden.
- Remote scheduling: `split_heuristic_full:OK!`, 83 expected N1-proxy cycles.
- Register set: exactly `v0-v7,v16-v31`; no `v8-v15`.
- Memory/flow: 32 public `ldr qN,[x3],#16`; no coefficient memory, store,
  stack, branch, or spill.
- Local assembly: allocated and scheduled artifacts both pass.

The 83-cycle number is proxy metadata for this extracted one-bank region, not
a Raspberry Pi 5 or full-Forward performance result.
