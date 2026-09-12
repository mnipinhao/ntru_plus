# P8 GT864 vs selected Official — 2026-09-12

GT frozen revision: `766cc844`. Official source: `/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.
Both use SHAKE256. This is a fresh common-harness comparison of that SUPERCOP source, not the SUPERCOP do-part aggregate report. Upstream-latest status remains unverified.

## Clean full-KEM PMU

| Operation | Official cycles | GT cycles | GT minus Official | GT change | Official / GT instructions |
|---|---:|---:|---:|---:|---:|
| keygen | 44298.125 | 46384.500 | +2086.375 | +4.71% | 89328.0 / 99097.0 |
| encaps | 46447.775 | 45769.400 | -678.375 | -1.46% | 120822.2 / 125572.2 |
| decaps | 40762.775 | 41348.650 | +585.875 | +1.44% | 86648.2 / 96898.2 |

252 clean observations per implementation/operation, six balanced AB/BA processes. Clean end-to-end values decide wins; profiling instrumentation is not included in this table.

## Complete call-site profiler

Cycles below are median net cycles per whole KEM operation, not per call. Parentheses give calls/operation. Measured read-pair overhead is subtracted per call. A dash means no separate call, not a zero-cost operation. Component medians do not necessarily sum to clean totals.
P8 combines inverse and ternary; compare GT Inverse_to_ternary against Official Inverse + Crepmod3. Compare all ToBytes variants together.

### keygen

| Component | Official cycles (calls) | GT cycles (calls) |
|---|---:|---:|
| BaseInv | 8361.125 (2) | 10398.000 (2) |
| BaseMul_R0 | 4882.000 (2) | 4349.000 (2) |
| CBD | 815.750 (2) | 766.625 (2) |
| Forward | 7534.000 (2) | 6784.000 (2) |
| RNG | 284.000 (2) | 223.000 (2) |
| SHAKE_sampling | 5527.750 (2) | 5536.750 (2) |
| ToBytes_full | 3327.000 (3) | 1774.875 (1) |
| ToBytes_small | — | 2774.750 (2) |
| Triple | 483.250 (2) | 469.250 (2) |
| cleanup | 474.000 (7) | 372.000 (7) |
| hash_f | 13269.625 (1) | 13233.250 (1) |

ToBytes total (sum of group medians): Official **3327.000**, GT **4549.625**, gap **+1222.625** cycles.

### encaps

| Component | Official cycles (calls) | GT cycles (calls) |
|---|---:|---:|
| BaseMulAdd | 2900.000 (1) | 2170.000 (1) |
| CBD | 410.050 (1) | 382.000 (1) |
| Forward | 7535.000 (2) | 6782.150 (2) |
| FromBytes_checked | 751.000 (1) | 723.050 (1) |
| RNG | 384.000 (1) | 352.000 (1) |
| SOTP_encode | 423.300 (1) | 401.950 (1) |
| ToBytes_full | 2216.000 (2) | 1777.850 (1) |
| ToBytes_small | — | 1384.200 (1) |
| cleanup | 283.000 (5) | 215.000 (5) |
| hash_f | 13276.525 (1) | 13242.475 (1) |
| hash_g | 14570.350 (1) | 14487.000 (1) |
| hash_h | 4059.475 (1) | 4037.150 (1) |

ToBytes total (sum of group medians): Official **2216.000**, GT **3162.050**, gap **+946.050** cycles.

### decaps

| Component | Official cycles (calls) | GT cycles (calls) |
|---|---:|---:|
| BaseMul_R0 | 2440.000 (1) | 2174.000 (1) |
| BaseMul_Rinv | 1762.000 (1) | 1761.950 (1) |
| CBD | 400.725 (1) | 375.725 (1) |
| Crepmod3 | 488.000 (1) | — |
| Forward | 7534.000 (2) | 6793.200 (2) |
| FromBytes_checked | 2262.375 (3) | 2165.125 (3) |
| Inverse | 4132.000 (1) | — |
| Inverse_to_ternary | — | 5446.050 (1) |
| SOTP_decode | 406.000 (1) | 383.000 (1) |
| Sub | 219.000 (1) | 204.000 (1) |
| ToBytes_full | 2213.000 (2) | 1777.525 (1) |
| ToBytes_small | — | 1388.000 (1) |
| cleanup | 538.000 (8) | 451.500 (8) |
| hash_g | 14558.950 (1) | 14478.800 (1) |
| hash_h | 4056.500 (1) | 4033.650 (1) |

ToBytes total (sum of group medians): Official **2213.000**, GT **3165.525**, gap **+952.525** cycles.
Inverse + ternary: Official **4620.000**, GT **5446.050**, gap **+826.050** cycles.

## Interpretation / work ledger

- Keygen: BaseInv costs GT an extra2036.875 cycles across two calls; aggregate ToBytes adds1222.625. Forward saves750 and R0 BaseMul saves533. P10 BaseInv remains important.
- Encaps: ToBytes adds946.050 cycles; Forward saves752.850 and BaseMulAdd saves730. GT wins overall despite its routing cost.
- Decaps: ToBytes adds952.525 and inverse+ternary adds826.050. Forward saves740.800, R0 BaseMul saves266, checked FromBytes saves97.250; R^-1 BaseMul is effectively tied.
- Keep P9 ToBytes routing search next because it affects all three operations; keep P10 BaseInv queued. Do not reopen rejected P6 without its static savings gate. P8 is complete, not pending.
- Inverse still has a real residual gap, but it is no longer the previously measured +2896-cycle single-component gap. Any further inverse experiment must preserve the P8 combined boundary and be separately scoped.
- Hashing dominates absolute Encaps/Decaps time, but implementations share the backend and measured hash gaps are small. It is not the main GT-specific regression.

## Provenance and validation

- Pi5 Cortex-A76 core3; GCC14.2; both use -O3 -march=armv8-a+simd, PIC and identical link policy. Builds are fresh in `/home/pi/ntruplus-official-profile-p8-20260912`; source SUPERCOP tree is not modified.
- Official kem.c/symmetric.c/api.h hashes match the previously selected baseline exactly. Full copied-tree and binary hashes, source/object lists and environment are in results.json.
- GT manifest-check, 64 KEM/tamper cases and100-case KAT digest pass: `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Six clean processes each compare100 byte-exact cross-implementation KEM transcripts and100 tampered ciphertexts. All12 instrumented-versus-clean equivalence tests pass.
- Clean:42 samples/process, inner counts4/20/20 for Keygen/Encaps/Decaps, five warmup samples. Profile:21 samples/process, same inner counts, three warmup samples;126 observations per group.
- Governor ondemand; temperature60.9→63.1C; throttling remains0x0; no competing benchmark observed. PMU excludes kernel/hypervisor time.
- Both harnesses provide the same deterministic RNG for reproducibility, not an OS entropy source. RNG call-site differences are instrumentation/compiler effects, not an entropy-service speed comparison.
- Cleanup rows count KEM-level secure_clear only; internal assembly scratch/register clearing is included in each kernel. Matching call counts alone does not prove identical global cleanup policy.
- Raw CSV, generated profiled source and build logs remain under ignored raw/ and build/, also retained in the isolated Pi directory. No production algorithm or priorities were silently changed.

## Reproduce

Run prepare.py locally to freeze GT766cc844, upload this directory without build/raw, then run pi_run.py on the Pi. The runner refuses existing output directories, checks Official hashes and GT manifest/KAT, and runs the six clean/profile rounds. Run summarize.py followed by report.py after collecting raw/ and build/environment.json.
