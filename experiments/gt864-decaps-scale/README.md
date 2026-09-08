# Decaps scale gate (default-off)

This is the algebraic prerequisite to a new Inverse DAG, NOT a new hand-written
Inverse arithmetic implementation. Existing I9/I16 assembly is reused with
regenerated terminal scale constants. No production source is changed.

Only the first Decaps BaseMul/Inverse pair in the copied kem.c changes.
Keygen's two BaseMuls, Encaps BaseMul-add and Decaps second BaseMul are unchanged.
Both first-Decaps operands come from FromBytes, range [0,4095].

Input/output physical leaf layout and roots stay FR0. BaseMul replaces each
terminal signed-wide R0 Barrett reduction by REDC: output is R^-1.
Inverse I9 and I16 stages are unchanged. Each existing I16 terminal scale b
becomes center(b*R mod q), and bhat is regenerated. Linearity compensates the
pending R^-1 factor before inverse top split; no extra coefficient pass.

Bounds: cross0 <=2*4095^2; REDC cross0 <=2241 in magnitude. Final cubic
accumulators <=3*4095^2 (also encloses zeta-weighted terms). REDC result
<=2497, narrower than the existing M5E input contract 3023. All REDC
numerators fit int32. Internal inverse stages unchanged; new terminal
constant bounds must be checked before promotion, not inferred from equality.

This candidate changes representation, so a random test is not a complete
range/constant-time proof. Keep experimental until a source-tied inverse
range closure and linked-object audit are complete. No Slothy run here.

Pi5/GCC14.2.0: 512 FromBytes-range differential products passed R^-1 relation
and exact centered inverse equality. Six paired full-KEM processes passed
valid/tampered/malformed equality. Median of process medians:
Decaps 44441.625 -> 44072.700 (-368.925 cycles, -0.83%).
Keygen 54121.125 -> 54126.125; Encaps 46089.150 -> 46100.225 (unchanged callers).
Keep as experimental scale candidate, not production; this does not yet
replace the I9/I16 arithmetic or solve the larger Inverse routing gap.
