# Correctness and audit tests

Differential, KAT, alias, range, canary, sanitizer, ABI, and constant-time gates
belong here. These gates must pass before formal timing.

`test_g1c_bmscale_inverse_d1.c` feeds the linked C2-L leaf with the qualified
terminal-major producer, then checks raw BMScale and linked inverse-distance1
bit-for-bit against an independent scalar oracle plus range and canary gates.
