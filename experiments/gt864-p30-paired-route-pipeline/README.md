# GT864 P30 adjacent-record route pipeline

P30 is a timing-only successor to P29.  It keeps the exact 873-instruction
route, 96 scratch-Q loads, 64 full-vector `ST3.4h` stores, arithmetic, layout,
ranges, ABI, and public pointer sequence.  The only intended change is exposing
two adjacent `(top,t)` records in each of 16 Slothy windows instead of using 32
single-record windows.

`generate.py` derives the symbolic source from P29.  `optimize.py` uses
`/Users/chenpinhao/slothy` and the Cortex-A76 target with every concrete GPR
reserved.  `verify.py` checks the instruction, load-offset, pointer-store,
full-ST3, and no-spill contract.  `prepare-integration.py` makes ignored
production/P29/P30 packages, and `summarize.py` reduces ignored Pi 5 PMU CSVs.

P30 is rejected. See [RESULTS.md](RESULTS.md).
