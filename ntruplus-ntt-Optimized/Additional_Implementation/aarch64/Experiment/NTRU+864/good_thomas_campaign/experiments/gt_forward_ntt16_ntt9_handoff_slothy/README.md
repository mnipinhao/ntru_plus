# M5J: NTT16-to-NTT9 physical handoff hard gate

This experiment closes the boundary left open by M5I. It starts from the real
M5F NTT16 producer shape rather than assuming nine consumer-ready vectors:
sixteen column vectors hold rows `s=0..7`, and two tail vectors hold `s=8`.

Two 24-instruction `trn1`/`trn2` networks transpose the two 8-column blocks.
The first becomes nine row vectors for columns 0..7. The second becomes eight
held row vectors; its ninth row is fixed in `v16` and remains live without an
instruction. This is an ABI constraint, not a free symbolic value: reserving
`v16` makes Slothy account for its pressure and proves that no candidate
instruction destroys it.

Rows 1..8 of the current block then use Algorithm 10 fixed multiplication:
two public 16-byte table loads followed by `sqrdmulh`, `mul`, and `mls`.
The 16 loads are a conservative symbolic-model form of eight potential `ldp`
pairs. They read 256 public bytes and do not create coefficient traffic. The
result immediately enters the complete 102-instruction M5I oriented NTT9.

The whole region is 190 real instructions:

- 48 transpose instructions;
- 16 public constant loads;
- 24 twist arithmetic instructions;
- 102 complete-NTT9 instructions.

The 16 loads plus 24 arithmetic instructions are eight five-instruction
twists. The machine mnemonic total is exactly 190.
`prove_handoff.py` checks all 144 coordinates, all 256 table pairs over the
four top/block families, and imports the M5G exact range result: NTT16 maximum
9342, fixed-product maximum 3436, and complete-NTT9 maximum 28568.

The formal remote run used host `fedora`, Slothy 0.2.2, and checkout
`d636d638d06b370d1acc5774ca31c9572d3d2e6f`. RA-only is OPTIMAL in 9.12
seconds with order preserved and spills forbidden. The second fresh Slothy
instance schedules the allocated real instructions and ends with
`split_heuristic_full:OK!` at 47 expected N1-proxy cycles.

Both returned artifacts use exactly `v0-v7,v17-v31`. They never use
ABI-forbidden `v8-v15` or fixed held-tail `v16`; only public pointer `x3`
appears as a GPR. There are no stores, stack operations, branches, or spill
instructions. Both files assemble locally as Armv8-A Neon.

This proves one physical producer-to-consumer block handoff without a
coefficient memory boundary. It does not yet consume the second NTT9 block,
link a full Forward implementation, or provide Raspberry Pi 5/SUPERCOP data.
