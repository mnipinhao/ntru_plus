# P15 — P9 fixed-DAG timing schedule

P15 keeps the production P9 ToBytes coordinate map, input-once loads,
normalization, byte packing, stores, and GCC 14.2 physical register allocation.
It schedules bounded completion windows with the Cortex-A76 Slothy model.

The experiment is successful only if the exact full and small public ToBytes
boundaries both improve on Pi 5 without changing the instruction multiset,
memory accesses, scratch, register allocation, or output bytes.

Run order:

```sh
python3 prepare.py
PYTHONPATH=/Users/chenpinhao/slothy \
  /Users/chenpinhao/slothy_and_ra/.venv/bin/python optimize.py
python3 run_pi5.py
```

`--reuse-existing` audits an already generated mode before scheduling any
missing mode.  It exists only to resume an interrupted multi-mode run; a clean
reproduction omits it.

Result: the combined gate is rejected.  Full improves by 76.555 cycles, while
small regresses by 1.586 cycles.  See `RESULTS.md` and `pi-results.json`.
