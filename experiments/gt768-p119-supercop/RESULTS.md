# P119 — SUPERCOP 20260831 run of the P118 leaf: decapsulation −1.68%, now −18.6% against Official

Native SUPERCOP timing on the Pi 5 (Cortex-A76) of three NTRU+768 leaves, using
SUPERCOP 20260831's unmodified `do-part`, `measure-anything.c` and
`crypto_kem/measure.c`:

- `official`: SUPERCOP's own `crypto_kem/ntruplus768/aarch64`;
- `gt-before`: GT production before P118 (commit `bed46cbb` tree);
- `gt-after`: GT production with P118 (commit `f36fc3a8`, branch
  `gt768-e4-inverse-integration`).

Procedure is E28's `run.py` (fresh isolated staging, native RNG initialisation,
one leaf enabled per `do-part` run), extended to three leaves and without the
profiler:

- 6 rounds, rotated order, 18 `do-part` runs on core 3;
- each GT tree passed `make check` and `scripts/export_supercop.py` in setup;
- compiler (native selection) `gcc -march=native -mtune=native -O3 -fwrapv
  -fPIC -fPIE -gdwarf-4 -Wall`, GCC 14.2.0, for every leaf;
- all endpoints `throttled=0x0`, maximum 67.0 °C;
- Official's source hashes identical before and after (`identity.json`).

## Medians of the six rounds, cycles

| | Official | GT before | GT after | after − before |
|---|---:|---:|---:|---:|
| keypair | 38,426.5 | 31,639.5 (−17.66%) | 31,646.0 (−17.65%) | +6.5 (+0.02%) |
| enc | 38,585.0 | 29,440.0 (−23.70%) | 29,442.5 (−23.69%) | +2.5 (+0.01%) |
| **dec** | **33,549.0** | **27,780.5 (−17.19%)** | **27,315.0 (−18.58%)** | **−465.5 (−1.68%)** |

Paired per-round differences, after − before:

- dec: −457, −464, −476, −465, −467, −453, **all six negative**;
- keypair: +54, +52, 0, −16, −57, −19 (noise);
- enc: −34, −20, +34, +22, +6, −14 (noise).

This agrees with P118's own harness: −498 cycles, −1.8%.  The SUPERCOP number
is slightly smaller because SUPERCOP builds with `-march=native` and its own
RNG and driver.

Medians of six rounds on one day; not a confidence interval or cross-day
stability claim.  Timing only, not a TIMECOP or constant-time certification.

## Files

- `run.py`: `run.py setup`, then `run.py measure`, on the Pi, root
  `/home/pi/gt768-p119-supercop`.  Staging, build logs and raw `.data` stay in
  the gitignored `.build/` there.
- `benchmark-summary.json`: every run with its env snapshots, metadata and data
  hash.
- `identity.json`: Official, GT and driver source hashes.
