# Experiment-local benchmarks

Repository-local harnesses are diagnostic only. Formal results come from the
pinned SUPERCOP workflow and are labeled native KEM or derived polynomial.

`bench_g1c_m2_paired.c` compares the exact materialized BMScale-to-D1 boundary
with linked C2-L at identical input residency and output address. It uses 16
balanced ABBA/BAAB blocks and 96 observations per slot; the runner repeats the
binary in fresh pinned launches. These numbers cannot promote a candidate.
