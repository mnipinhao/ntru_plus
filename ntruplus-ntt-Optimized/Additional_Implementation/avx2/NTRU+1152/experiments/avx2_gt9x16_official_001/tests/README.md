# Correctness and audit tests

Differential, KAT, alias, range, canary, sanitizer, ABI, and constant-time gates
belong here. These gates must pass before formal timing.

`test_g1c_bmscale_inverse_d1.c` feeds the M2 materialized control and linked
C2-L leaf with the qualified terminal-major producer, then checks raw BMScale
and both inverse-distance1 outputs bit-for-bit against an independent scalar
oracle plus range and canary gates. `test_g1c_m2_live_basis.py` checks the
source-locked live DAG, scoped eight-instruction lower bound, and retained
split-after-D1 full-inverse candidate.

`test_g1c_m3_inverse16_oracle.py` gates all four inverse physical-q maps, the
C0/C1/C2 attribution contract, independent F1/F5 accounting, and the explicit
D2 range-proof failure that currently blocks lazy M3 assembly.

`test_g1c_m3b_provenance.py` gates the D2 source classes and fixed D8
counterexample. The underlying 10,003-case probe is counterexample evidence,
not a replacement for symbolic or localized exact range proof.

`test_g1c_m3c0_orientation_search.py` gates the exhaustive zero-cost output
swap search at all three boundaries, the zero-route physical-q relabel domain,
and all sign variants of the permanent D8 counterexample. It requires M3C0 to
close without a factor-equivalent all-L/R-edge candidate before repair search.

`test_g1c_m3c2_repair_plan.py` locks the 576-node fixed-corpus action matrix,
the 37 pair-0 logical repairs, and the 22-chain/30-route adjacent-row half
set-cover result. It also requires the result to remain explicitly proof-open
and assembly-blocking.

`test_g1c_m3c2p_exact_proof.py` gates the conditional signed-i16 D8 theorem,
the rejection of one-sided repair, and the 72-vector minimum proved control.
`test_g1c_m3c3_reduction.c` exhausts all 65,536 signed-i16 inputs for both AVX2
reducers, including alias, congruence, range, and canaries.
`test_g1c_m3c3_reduction_evidence.py` locks their static leaf/constant-time
audit and the fixed nine-launch paired primitive price.

`test_inverse_ntt9_b1p.py` gates the exact Forward-R2 gauge extraction, all
729 two-radix3 cyclic orientations, the BMScale/inverse/top-split phase
placement lower bound, and the three-way B1R range shortlist.  B1P is a
symbolic design checkpoint and contains no performance claim.

`test_inverse_ntt9_b1r.py` gates the exhaustive 512 input and 32-per-variant
inter-stage reduction policies, ranks the three B1P ties by exact i16 envelope,
and requires concrete in-contract witnesses for every final Barrett and center
correction before authorizing the narrow B1 ASM deletion.
