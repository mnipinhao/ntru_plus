# Forward frontend DCE + Slothy

This is an exact-region replacement experiment for the current production
G1R123+S2 forward NTT.  The U01/G1 generation chain currently takes each
Phase123 iteration from the source-order symbolic input.

Each 160-instruction body ends with four pointer updates whose values are never
read: the next iteration reconstructs all pointers from fixed bases, and the
last iteration has no pointer consumer.  The candidate removes those four
instructions and asks Slothy to schedule the remaining 156 instructions.

The arithmetic, reductions, input loads, twelve output stores, and output
addresses are frozen.  No spills are allowed.  `fixed` preserves physical
vector allocation; `rename` lets Slothy rename vector temporaries while all
GPRs and `v0` remain fixed.

The fixed-register candidate is now the production frontend. All three operand
permutation classes contain 156 instructions and have N1 expected 39 cycles.
The rename candidate remains an experiment because it was slower on Pi 5.

Promotion evidence:

- `poly_ntt` differential mismatches: 0
- ABI sentinel mask: `0x0`
- canonical GT/KPQC KAT SHA-256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`
- direct Pi 5 `poly_ntt`: 2659 -> 2612 median cycles
- canonical full KEM, source-order -> fixed Slothy frontend:
  encap 38290 -> 38212; decap 33700 -> 33569 median cycles

The N1 estimate is retained only as solver evidence; all performance decisions
above use Cortex-A76 PMU measurements.
