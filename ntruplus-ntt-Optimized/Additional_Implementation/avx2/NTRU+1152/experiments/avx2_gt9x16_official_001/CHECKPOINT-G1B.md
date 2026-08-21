# Checkpoint G1B: F1 producer-tail price

G1B measures the real F1 producer tail, not a standalone layout converter. Both
variants execute the same R2 plus adjusted-D1 arithmetic as F0. F0 stores the
persistent pair representation; F1 reconstructs the four terminal coefficient
vectors and stores terminal-major output directly from the D1 tail.

The combined function keeps the already-materialized 576-byte R2 seam. Its ABI
uses distinct R2 scratch and terminal-major output pointers because the sparse
terminal-major destination cannot also hold the contiguous R2 intermediate.
This checkpoint does not alter R2 or D1 arithmetic.

## Correctness and static audit

F1-B0 is the clean reconstruction upper bound. F1-B1 schedules reconstruction
inside the final row-pair tail. Both pass 10,003 boundary/random cases over all
1,152 cells, preserve transform scale 4, and pass output canaries. Aliasing is
not applicable across the two distinct output layouts.

| Variant | Instructions | text bytes | routing incl. blends | stores | peak live YMM | frame/spills/calls |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| F0 D1 persistent | 847 | 3,734 | 108 | 54 | 15 | 0/0/0 |
| F1-B0 terminal-major | 886 | 3,923 | 144 | 54 | 15 | 0/0/0 |
| F1-B1 fused terminal-major | 886 | 3,923 | 144 | 54 | 15 | 0/0/0 |

The S/D name describes physical q-lane parity packing. F1 reconstruction is
word interleave plus 128-bit-half composition; it is not an algebraic
`a+b`/`a-b` transform and therefore does not change the scale contract.

## Paired diagnostic result

The same ELF, compiler flags, resident input, CPU pinning, 16 balanced blocks,
and 96 observations per slot were used for nine fresh launches.

| Comparison | median left | median right | right-left | direction |
| --- | ---: | ---: | ---: | --- |
| F0 → F1-B0 | 684.0 | 744.0 | +60.5 cycles | 9/9 slower |
| F0 → F1-B1 | 683.5 | 742.0 | +58.5 cycles | 9/9 slower |
| F1-B0 → F1-B1 | 745.0 | 742.0 | -3.0 cycles | 9/9 faster |

The result is `high-producer-tax` and repository-local diagnostic evidence
only. The debt matrix records +58.5 cycles for B1, +60.5 as the B0 clean upper
bound, and leaves consumer credit and net delta null.

F1 is neither selected nor rejected here. F0 remains the control until G2 can
price complete consumer paths.

