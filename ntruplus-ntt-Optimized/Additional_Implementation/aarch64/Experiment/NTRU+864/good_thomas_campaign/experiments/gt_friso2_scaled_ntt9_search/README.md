# M5U-CF1: exact scaled-NTT9 fused-DAG search

This is the static arithmetic hard gate required by M5U-CF0.  It asks whether
the FR-ISO2 live-out factors can be distributed through the frozen M5R-D
paper-oriented one-product NTT9 DAG so that at least one of CF0's nine explicit
post-transform Algorithm-10 multiplications disappears per scaled block.

The experiment is default-off and is not linked to Production, Inverse, KEM,
Pi 5, or SUPERCOP.  `search_scaled_dag.py` is the exact MILP model.  The four
tracked `solution-t*c*.json` files are feasible solver witnesses for the two
top branches and the two scaled cubic components.  `verify_witnesses.py`
independently replays every witness as a finite-field linear circuit and as a
constant-specific signed-integer range DAG.

Run:

```sh
make check
```

The four searches reached their 240-second time limit.  Therefore this gate
proves existence of the 26-mulmod schedules; it does not prove that 26 is the
global minimum.
