# P21 — current-production Inverse-to-ternary decomposition

P21 is a measurement/selection gate. It does not change the production kernel.
It re-runs the P7-B0 style Pi 5 decomposition against the current P13-B,
P13-C, P8 and P7-C1 production path after P20 identified the matched Decaps
inverse boundary as the largest remaining positive cycle gap.

Measured boundaries are the twelve-call inverse9 aggregate, six-call main I16
aggregate, tail I16, raw-to-ternary consumer, complete Inverse-to-ternary, and
diagnostic no-store main/tail controls. The latter are optimistic scatter-cost
ceilings, not implementable candidates.

Result: passed. The six-call main I16 aggregate is now the largest measured
stage, including after removing its diagnostic scatter instructions. P22 must
therefore attack the main-I16 arithmetic/dependency DAG; terminal scatter is
not selected. See `RESULTS.md`.

```sh
python3 run_pi5.py
```
