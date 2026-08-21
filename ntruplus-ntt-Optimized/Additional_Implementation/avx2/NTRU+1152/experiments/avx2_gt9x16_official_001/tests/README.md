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
