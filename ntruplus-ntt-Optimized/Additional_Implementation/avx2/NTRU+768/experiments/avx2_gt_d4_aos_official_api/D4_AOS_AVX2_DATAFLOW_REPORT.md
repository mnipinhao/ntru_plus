# d4AoS AVX2 dataflow report

The proved d4 representation is physically realizable: the prototype passes direct AVX2 F/I/B differentials, uses no Official or SoA kernel, has no scalar coefficient hot loop, no whole-array conversion, and no unsanitized YMM spill. The compact branch-paired terminal store is structurally better than the inherited SoA transpose.

But the only fully proved AVX2 dataflow evaluates all 96 roots for each of 48 vectors. It is correct but categorically noncompetitive. A new factorized 32×3 blocking must prove exact stage-order tables, CROSS-YMM partner traffic, immediate DFT3-to-terminal handoff, and total 2F+B+I cost before any handwritten inverse ASM is authorized.
