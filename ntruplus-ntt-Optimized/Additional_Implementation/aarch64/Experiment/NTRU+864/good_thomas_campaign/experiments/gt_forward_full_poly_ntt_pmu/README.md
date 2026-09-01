# M5P: Pi 5 complete Forward PMU hard gate

M5P benchmarks the frozen M5O complete GT864 Forward against Official Neon in
one binary on Raspberry Pi 5 / Cortex-A76.  It does not change either kernel.

Each complete repetition runs `Official -> GT` followed by `GT -> Official`.
Each order has 61 samples, each sample contains 20,000 calls, and both variants
receive 100 warm-up calls.  Three complete repetitions therefore provide 366
samples per implementation.  CPU cycles and retired instructions are read as
one Linux `perf_event` group, with kernel and hypervisor events excluded.  The
process is pinned to core 3, and any nonzero `vcgencmd get_throttled` value
invalidates the run.

The C harness is compiled with `v8` through `v15` fixed.  Official's assembly
uses those vector registers without an AAPCS save/restore sequence, so the
benchmark caller must not retain C state or floating-point conversion constants
in them across either measured call.  This changes caller allocation only and
does not add instructions inside either timed kernel.

Before timing, every process runs 64 disjoint and 64 in-place complete Forward
differentials modulo q.  Guard words surround every output and alias buffer,
and the disjoint input is checked for modification.  Candidate FR-0 positions
are interpreted through M5O's zeta-derived compile-time ABI map; no conversion
is included in the timed candidate.

`run_pi5.py` syncs an isolated source closure to
`/home/pi/ntruplus-experiments/gt864-forward-full-poly-ntt-pmu-m5p`, records
source hashes and environment, builds remotely, performs all repetitions, and
stores raw logs plus `summary.json`/`summary.md` under the ignored local build
directory.
