# D1-P3B24: P3B23 full-KEM closure

Run `python3 run_pi5.py`. Reuses P3B12's frozen source manifest, Official,
correctness harness, flags and three-way PMU harness. Both GT variants use
the same r9_to ToBytes and arithmetic. Only FromBytes differs: P3B11 versus
P3B23. Generated wrappers and Makefile are under build/config.

Hypothesis: one FromBytes substitution saves about 282 cycles in Encaps and
three save about 845 in Decaps. Require valid/tampered KEM equivalence,
0/1/3 FromBytes relocation ledger, and consistent paired PMU improvement.
Production promotion is not required to run this experiment.
