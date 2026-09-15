# GT864 P28-S fixed-allocation timing experiment

P28-S asks whether Cortex-A76 timing scheduling alone can rescue the rejected
P28 paired inverse consumer.  It keeps P28's exact arithmetic, physical
register allocation, layout, memory boundaries, masks and public ABI.

Run `prepare.py`, then invoke `optimize.py` separately with `main`, `tail`, and
`route`.  `verify_multiset.py` proves that the three scheduled files retain the
exact executable instruction multisets.  `prepare-integration.py` creates
isolated production, P28 and P28-S packages under ignored `build/`.
`pi-bench.c` is the isolated PMU harness, and `summarize.py` summarizes the
ignored raw Pi 5 CSV files under `pi-run/`.

The Slothy driver uses `/Users/chenpinhao/slothy`, fixed physical allocation,
two split-heuristic regions for main and tail, and 108 per-output route
windows.  The local Cortex-A76 target did not provide timing entries for the
already parsed `vins_d` instruction.  The driver locally assigns the same
vector-pipe class, throughput 1 and latency 2 used by the neighboring
`mov_vtov_d`/lane-insert model; the Slothy checkout is not modified, and Pi 5
PMU timing remains authoritative.

See [RESULTS.md](RESULTS.md) for the rejected promotion gate and measurements.
