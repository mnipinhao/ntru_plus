# GT864 P28 paired-I16 experiment

This directory is the complete, reproducible P28 experiment.  It pairs the P27
selected main-I16 banks, compacts the tail, and routes the dense raw result to
the unchanged natural ternary KEM ABI.

Run `generate.py`, `optimize-main.py`, and `optimize-tail.py` with the configured
local Slothy installation, then run `generate-route.py`.  `prepare.py` creates
isolated baseline and candidate production packages under the ignored `build/`
directory.  `oracle.c` is the exact differential oracle and `pi-bench.c` is the
isolated same-boundary PMU harness.

See [RESULTS.md](RESULTS.md) for the complete gate and rejection rationale.
