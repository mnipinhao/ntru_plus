# M5U-B1 — isolated two-constant BaseMul cycle gate

This experiment measures the cycle value of deleting two intermediate widening
Montgomery reductions from each FR-ISO2 cubic tile.  It compares two kernels
under exactly the same `z0=9/3` representation so the primary difference is the
reduction DAG, not Forward conversion or lane-dependent FR0 zeta loading.

Local correctness and range gate:

```sh
make check
```

Returned Pi 5 evidence audit, after an authorized `python3 run_pi5.py` run:

```sh
make remote-audit
```

The direct-wide candidate wins the isolated gate.  This is not a complete
FR-ISO2 transform-ABI, full multiplication, Production, or SUPERCOP claim.
