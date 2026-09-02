# Results

Status: **algebra/C-reference hard gate passed; codegen gate remains open.**

- 288 distinct cubic leaves split into two non-cube characters, 144 each.
- Exact formulas reduce the leaf moduli to `Y^3-9` and `Y^3-3`.
- 2,592 basis-pair checks prove `phi_tau(a*b)=phi_tau(a)*phi_tau(b)`.
- 48 complete 864-slot basis roundtrips have zero modulo-q mismatches.
- 32 BaseMul and BaseMulAdd cases match normalized M5C output with zero
  mismatches.
- BaseMul `out==a/b` and BaseMulAdd `out==c` alias paths have zero mismatches.
- 19 complete Forward/FR-ISO2-BaseMul/Inverse products match direct schoolbook
  multiplication modulo `x^864-x^432+1` with zero mismatches.
- The physical representation remains 864 halfwords in the same FR-0 SoA slots.
- With component-0 bound 26306 and Algorithm-10 component-1/2 bound 5185,
  every proposed direct `z0=3/9` int32 accumulator stays below 2^31.

The reference reports two explicit conversion passes.  They are evidence of
the map, not an implementation candidate, and prevent any performance or
Production claim at this stage.
