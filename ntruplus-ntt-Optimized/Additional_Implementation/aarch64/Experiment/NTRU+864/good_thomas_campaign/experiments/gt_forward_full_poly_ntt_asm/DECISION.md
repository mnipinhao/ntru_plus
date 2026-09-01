# M5O decision

The full Good-Thomas Forward composition gate passes.  Freeze the exact
top-split -> P8 -> M5N -> FR-0 path as the first complete experimental Forward
candidate.

The strongest evidence is the 864-basis differential against the actual
Official Neon Forward after a zeta-derived, machine-checked output
permutation.  That test validates the entire linear transform, including top
split, twist placement, NTT16, oriented NTT9, scale, sign, leaf identity, and
physical layout modulo q.  Random and boundary cases additionally exercise
the proven lazy arithmetic ranges.

Do not add a runtime conversion to Official layout: FR-0 is the intended
transform-domain ABI for the matching GT BaseMul and inverse path.  Also do not
promote this symbol into Production yet.  The next hard gate is target timing:
measure this complete Forward candidate and Official under the same harness,
first with Pi 5 PMU/instruction evidence and then with the frozen SUPERCOP
methodology.  If code-footprint or call overhead loses materially, revisit the
producer/pass-2 boundary or shared-helper expansion, not the proven algebra.
