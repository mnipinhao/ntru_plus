# Decision

Pass and freeze M5A as the first handwritten fused FR-0 assembly baseline.
The experiment proves exact representatives at its declared boundary, a
stackless/no-coefficient-spill realization, a conditional range contract, and
Forward/BaseMul/inverse leaf-order closure. Production remains unchanged.

It does not prove the future NTT16 producer bound, full BaseMul arithmetic,
inverse arithmetic, KEM/KAT compatibility, or SUPERCOP performance. Those
must not be inferred from the passing microkernel gate.

The next experiment may refine instruction selection/scheduling and compose
with a real NTT16 producer only after that producer proves `|P8+tail| <= 15752`.
It should also test generated zetas in an actual FR-0 BaseMul and complete the
inverse arithmetic path before any integration or promotion decision.
