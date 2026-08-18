# F32X3 fused-terminal register plan

During compact DFT3, `ymm0..2` hold Y0/Y1/Y2, `ymm3..4` the shared omega chain, and
`ymm5..7` raw D0/D1/D2. `ymm11` is q, `ymm12` the Barrett reciprocal, and `ymm13/14`
omega qinv/factor.

Terminal consumption is sequential: D0 in `ymm5` while D1/D2 remain in `ymm6/7`, then
D1 while D2 remains, then D2. For each value, `ymm2` holds the half swap, `ymm0` the
Montgomery low/correction temporary, `ymm3` the P contribution, `ymm4` the Q
contribution, and `ymm8` the immediate Barrett temporary. Destructive reuse releases the
consumed D register after its four stores.

GPR allocation is `r8=direct-table cursor`, `rdx=offset cursor`, `r10=output`,
`rsi=post-L4 state cursor`, and `ecx=16-group loop count`. Peak use is 15 YMM registers.
Release disassembly has no call and no YMM spill. The aligned 1,536-byte stack object is
the explicitly permitted semantic post-L4 transform state, not spill storage.
