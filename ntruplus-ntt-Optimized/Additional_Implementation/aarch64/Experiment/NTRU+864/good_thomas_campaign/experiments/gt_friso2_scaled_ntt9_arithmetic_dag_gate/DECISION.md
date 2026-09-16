# Decision

CF5-D is closed as **hard gate not passed**.

- Proven: all four inherited 26-mulmod witnesses remain exact, range-safe
  upper bounds for the fixed oriented NTT9 topology.
- Measured input: at least 184.839 cycles must be recovered per Forward before
  FR-ISO2 can break even with M5R-D under the optimistic zero-Inverse-penalty
  ledger.
- Required candidate: at most 21 mulmods in every scaled NTT9 block.
- Observed: neither exact encoding produced such a witness within four bounded
  300-second searches; neither produced an infeasibility certificate.
- Consequence: no assembly, remote Slothy allocation, or Pi 5 benchmark was
  run, because there is no candidate arithmetic DAG to schedule or measure.

M5R-D remains the experimental Forward champion.  Reopening FR-ISO2 requires a
new NTT9 arithmetic topology, not another schedule of the existing graph.
