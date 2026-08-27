# 099 — current GT Clean versus Official

Fresh direct comparison of production baseline `b2a4bea` and frozen NTRU+768
Official AVX2.  Both are native SUPERcop `measure.c` PIE executables compiled
with the same GCC flags and measured on CPU 1 with ASLR enabled.

Protocol: 16 balanced blocks, alternating `O/G/G/O` and `G/O/O/G`; 32 fresh
process launches per implementation; 96 native observations per operation per
launch; SUPERcop stabilized Q2 is the primary absolute cycle estimate.
