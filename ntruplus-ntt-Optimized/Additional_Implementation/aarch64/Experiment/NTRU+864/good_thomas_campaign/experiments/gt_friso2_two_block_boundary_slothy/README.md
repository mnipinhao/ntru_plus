# M5U-CF3 — FR-ISO2 two-block boundary composition

This experiment composes the two eight-column scaled NTT9 blocks belonging to
one fixed `(top, component)` bank.  Unlike CF2, all eighteen inputs enter one
symbolic region and all eighteen outputs are simultaneous live-outs.  Slothy
must therefore preserve block 0's nine results throughout block 1.

The four regions are deliberately medium-sized: 308 instructions for top 0
and 276 for top 1.  No complete 600-plus-instruction Forward bank is submitted
to one solver invocation.

```sh
make static-check
make audit
```

The hard gate passes for all four cases.  See `REGISTER_FLOW.md` for the exact
boundary and `results.md` for the evidence limits.
