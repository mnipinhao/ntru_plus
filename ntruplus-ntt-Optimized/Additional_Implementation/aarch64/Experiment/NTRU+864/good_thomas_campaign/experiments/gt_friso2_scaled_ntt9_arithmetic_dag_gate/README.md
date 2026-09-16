# M5U-CF5-D — FR-ISO2 scaled NTT9 arithmetic DAG gate

CF5-D asks whether the fixed M5R-D oriented radix-3 NTT9 topology can be
rescaled into the FR-ISO2 leaf representation cheaply enough to reopen the
complete polynomial-multiplication route.

CF5-C measured 355.036 cycles of Forward regression and showed that the
additional Algorithm-10 multiplications and their dependency schedule, rather
than table loads alone, are the primary bottleneck.  The complete-operation
ledger requires at least 184.839 cycles to be recovered from each Forward.

The algebra gate therefore requires every `(top, component)` NTT9 block to use
at most 21 modular multiplications, versus 26 in CF5-B.  This removes five per
block, or 40 over the eight blocks in a Forward.  No assembly is generated and
Slothy is not run unless this feasibility gate passes.
