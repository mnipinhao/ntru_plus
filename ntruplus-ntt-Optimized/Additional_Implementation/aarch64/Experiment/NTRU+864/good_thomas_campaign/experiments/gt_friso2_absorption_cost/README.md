# M5U-B — FR-ISO2 absorption and total-cost gate

This gate asks whether M5U-A's mathematically valid two-coset basis is also a
natural implementation ABI for the complete operation

```text
Forward(a) + Forward(b) + BaseMul(/Add) + Inverse
```

It machine-checks the NTT9 row-factor conjugation, all 288 leaf
factorizations, the exact two-constant BaseMul Montgomery range/scale
schedule, and an optimistic static instruction ledger.  Run:

```sh
make check
```

The expected proof status is `reject`: that means the hard gate correctly
stops code generation.  It is not a failing test.  No Production source,
assembly, Slothy artifact, or extra coefficient memory pass is created.
