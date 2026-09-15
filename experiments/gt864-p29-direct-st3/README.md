# GT864 P29 equal-half paired direct-ST3 experiment

P29 replaces P28-S's standalone 216-`TBL2`/216-mask-load route.  It pairs
equal row halves, preserves the P28-S one-product main arithmetic, and emits
natural ternary output with full-vector `ST3.4h` for rows 0--7 plus exact
six-byte scalar tail stores for row 8.

`audit.py` proves the coordinate map and exhaustive raw-to-ternary range.
`generate.py` emits the two symbolic kernels.  `optimize.py` runs bounded local
Slothy allocation from `/Users/chenpinhao/slothy`; the checked-in `.alloc.S`
files are the actual allocated assembly.  `oracle.c` checks C/assembly identity,
and `prepare-integration.py` creates ignored production, P28-S, and P29 packages.
`summarize.py` reduces ignored Pi 5 paired-PMU CSV files to `results.json`.

P29 is rejected for production.  See [RESULTS.md](RESULTS.md).
