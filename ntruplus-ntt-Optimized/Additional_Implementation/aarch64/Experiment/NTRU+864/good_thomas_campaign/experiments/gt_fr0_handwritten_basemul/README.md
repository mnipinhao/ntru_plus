# B1 — FR0 handwritten BaseMul campaign

This campaign starts from the active M5C FR0 Neon intrinsics kernel and asks
whether handwritten assembly can improve Cortex-A76 widening-multiply
utilization without changing algebra, layout, scale, range, or memory ABI.

`B1-0` freezes the exact Pi 5 GCC object before any handwritten candidate.
The source remains `../gt_fr0_basemul_arithmetic/gt864_fr0_basemul.c`; generated
objects, disassembly, and raw PMU samples are gitignored under `build/`.

The fixed B1-H contract is 36 groups of three `int16x8` components, R0
operands, R1 zeta, R0 outputs, operand bound 25569, BaseMul output bound 2148,
and BaseMulAdd output bound 2205. H1/H2/H3 may change register allocation and
scheduling only. H2 is split into a sequentially unrolled `H2-U` control and a
genuinely interleaved `H2-P` candidate, so loop-amortization and software-
pipeline effects remain distinguishable.

Promotion requires correctness at isolated, alias, and full-polynomial
boundaries, no spill/stack or extra coefficient memory pass, and at least 50
BaseMul cycles saved. The preferred target is 80--100 cycles because a
handwritten kernel has higher maintenance cost than a generated schedule.

`B1-D1` is deliberately separate from H1/H2. It keeps the two early
scale-changing Montgomery reductions, retains each final cubic result as an
R0 signed-int32 accumulator, and reduces that accumulator directly with
`SQRDMULH/MLS` before narrowing. The exact static proof expands the consumer
bound from 2205 to 2911 while leaving the closed inverse maximum at 17220.
The isolated Pi 5 candidate passes correctness and object audits and saves
523.933 BaseMul cycles and 676.660 BaseMulAdd cycles. It is not Production-
linked. D1-C1 subsequently closes the executable full-polynomial consumer and
preserves a 547.594-cycle saving, so D1 is now the experimental arithmetic
baseline. Any future H1/H2 work must schedule the 57-instruction D1 DAG rather
than the obsolete 78-instruction baseline DAG.
