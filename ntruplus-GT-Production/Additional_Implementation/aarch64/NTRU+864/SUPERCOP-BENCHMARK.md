# GT864 K1 production vs frozen SUPERCOP

GT source commit: 6207939e. Hardware: Pi 5 Cortex-A76, core 3.
Linux 6.18.33+rpt-rpi-2712; GCC Debian 14.2.0-19.
Before/after throttle status: 0x0.

Baseline source: `/home/pi/supercop-20260627/crypto_kem/ntruplus864/aarch64`.
This is the installed SHAKE256 snapshot, NOT verified upstream latest.
kem.c, poly.c, ntt.s, base.s, pack.s and symmetric.c in the staged baseline
were byte-compared with that installation. hash_f calls shake256.
This is our paired PMU harness using SUPERCOP sources, not a run of SUPERCOP's
full do-part harness or compiler-selection campaign.

Measured binary paths:
- `/home/pi/ntruplus-experiments/gt864-p3b41-k1/sc.so`
  SHA256 `7ae3d62de30570939e22cba92a98eb968f4f496c24c52fd59f863b50b6c5735e`
- `/home/pi/ntruplus-experiments/gt864-production-k1-validation/NTRU+864/libgt864.so`
  SHA256 `b295d006eee1f6e496dcdaea7a31bf659e3ca13ce9cf559c814eeae036b3f302`

Both built with -O3 -std=c11 -march=armv8-a+simd -fPIC,
function/data sections, shared -Bsymbolic and --gc-sections, NO_CE SHAKE.
No new kernel or scheduler changes in this comparison.

## Method

Existing `test/paired.c` harness, six processes alternating order, 41 samples
per operation/process; 4 Keygen or 20 Encaps/Decaps calls/sample.
Deterministic benchmark RNG, identical seeds, setup outside measured boundary.
Each process runs 32 valid/tampered differential cases and 32 malformed
ciphertext cases before PMU. pk/sk/ct differences=0; return/shared-secret
checks passed. The inherited instrumentation label is not a profiler claim.

Command in the validation directory (sc.so points to baseline above):
`BASE=sc CAND=libgt864 taskset -c 3 ./paired 0` and `./paired 1`, repeated
three times each. Raw logs: evidence/supercop-paired0.log through paired5.log.
Reported values: median of six per-process medians. IPC below is the ratio
of aggregated instruction/cycle medians, not a separate counter.

| Operation | SUPERCOP cycles | GT cycles | GT cycle change |
|---|---:|---:|---:|
| Keygen | 44290.375 | 54136.500 | +22.23% |
| Encaps | 46427.450 | 46097.700 | -0.71% |
| Decaps | 40751.825 | 44445.675 | +9.06% |

| Operation | SC instructions | GT instructions | SC branches | GT branches | SC IPC | GT IPC |
|---|---:|---:|---:|---:|---:|---:|
| Keygen | 89315.75 | 120339.75 | 1184.5 | 3462.5 | 2.017 | 2.223 |
| Encaps | 120818.8 | 127692.8 | 1064.5 | 1247.5 | 2.602 | 2.770 |
| Decaps | 86643.8 | 99733.8 | 1079.5 | 1255.5 | 2.126 | 2.244 |

GT wins only Encaps on this measurement, and only slightly. It does not yet
beat this SUPERCOP baseline across the complete KEM. These are whole-operation
measurements, not fresh component profiles; they do not attribute the gap to
Forward or any single component. Code-size measurements and component profiler
results were not collected in this run.
