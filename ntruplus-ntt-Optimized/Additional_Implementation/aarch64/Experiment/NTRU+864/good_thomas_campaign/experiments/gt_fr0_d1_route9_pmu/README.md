# D1-P3B1 — coordinate route9 machine shootout

This benchmark-only experiment compares four implementations at exactly the
same FR0/Official coordinate boundary: the current generated scalar map, a
factorized scalar control, R9-A transpose/repair, and R9-B three-bank TBL.
Forward and reverse are separate symbols and are timed separately.

`generate_tables.py` imports the authoritative P3A coordinate map and emits
compile-time public tables. `test_route9.c` checks all 864 tagged positions,
128 random vectors per direction, and both vector round trips. `run_pi5.py`
builds one binary, pins it to Cortex-A76 core 3, runs three bidirectional-order
PMU repetitions, checks throttling, and archives size, symbols and disassembly.
`audit_results.py` enforces the result and no-vector-spill gates.

Run the archived-result audit with:

```sh
make audit
```

This does not implement ToBytes/FromBytes, BaseInv, Inverse, KEM or Production.
The winning coordinate network is an input to P3B2, where the target becomes
the composed pre/post-shuffle byte order rather than exact Official vectors.
