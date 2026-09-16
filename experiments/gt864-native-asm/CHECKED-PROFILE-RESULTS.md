# NTRU+864 checked FromBytes / KEM rejection gate — 2026-09-08

## Scope and correctness

Production now decodes FR0 and reports any 12-bit coefficient >= 3457. The checker does not reduce invalid values modulo q. A fixed 864-coefficient unsigned maximum scan adds one 1728-byte coefficient read pass after decoding.

Encaps rejects noncanonical pk with return 1 and zero ct/ss. Decaps checks ct, then sk-f, then sk-hinv, rejecting with return 1 and zero ss. The order and RNG consumption match the selected Official implementation. This is explicit rejection, not an implicit-rejection fallback secret.

Legacy CBD/SOTP/add/crepmod3 helpers clobbered d8-d15. Six public ABI wrappers now save/restore these registers; arithmetic is unchanged. The all-position differential test exposed caller-state corruption before this fix and passes afterward. No separate six-helper ABI sentinel suite was added.

- Mac: 64 KEM round trips/tampered cases and 100 KAT cases passed.
- Pi: fresh make check, 100 byte-exact Official KAT cases; BaseInv 808 cases including failure/alias/canary/ABI/wipe; Inverse 256 inputs plus 256 R^-1 multiplication chains passed.
- Checked decoder: all 4096 uniform encodings, and q-1/q at all 864 wire positions passed.
- Rejection: 10368 pk/ct/sk-f/sk-hinv boundary cases passed, comparing status, output clearing, input preservation and RNG consumption.
- All 79 crafted noncanonical x+q ciphertext cases now agree with Official; old GT disagreed in all 79.

## Exact comparison baseline

`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64` (SHAKE256); not independently verified as upstream latest. Official sources copied without arithmetic edits. Source and binary hashes are in checked-profile-results.json.

Standalone equal-policy GCC 14.2 -O3 -march=armv8-a+simd builds, not a complete SUPERCOP compiler sweep. Pi 5 CPU3, six processes, alternating AB/BA order, 41 samples per process, 4 Keygen or 20 Encaps/Decaps calls per sample. Median of process medians. Governor ondemand; no throttling reported. RNG is the deterministic harness RNG, not OS entropy acquisition.

## Clean full-KEM PMU

| Operation | Official cycles | GT cycles | GT change |
|---|---:|---:|---:|
| keygen | 44315.12 | 51431.00 | +16.06% |
| encaps | 46423.47 | 46135.65 | -0.62% |
| decaps | 40758.60 | 44319.93 | +8.74% |

Relative to the old unchecked integrated GT, costs changed by about +13 Keygen, +471 Encaps and +1203 Decaps cycles. This includes validation, cleanup and ABI restoration, not just the maximum scan.

## Component profiler

Cycles below are per full KEM invocation, summed across calls of that component. Empty-probe overhead is subtracted. Arithmetic objects are shared with the clean build; only KEM call sites are instrumented. Instrumented/clean output equivalence passed. These are diagnostic estimates: instrumentation changes caller code, cache and register pressure, so they must not be summed as exact clean full-KEM cycles. Raw values are retained in JSON/CSV.

### keygen

| Component | Official calls | GT calls | Official cycles | GT cycles |
|---|---:|---:|---:|---:|
| BaseInv | 2 | 2 | 8368.0 | 15626.9 |
| BaseMul_R0 | 2 | 2 | 4892.0 | 4358.0 |
| CBD | 2 | 2 | 820.0 | 787.2 |
| Forward | 2 | 2 | 7555.2 | 6793.0 |
| RNG | 2 | 2 | 268.0 | 229.0 |
| SHAKE_sampling | 2 | 2 | 5524.0 | 5540.0 |
| ToBytes_full | 3 | 1 | 3336.0 | 1813.2 |
| ToBytes_small | 0 | 2 | 0.0 | 2971.4 |
| Triple | 2 | 2 | 482.0 | 481.2 |
| cleanup | 7 | 0 | 480.5 | 0.0 |
| hash_f | 1 | 1 | 13292.2 | 13235.5 |

### encaps

| Component | Official calls | GT calls | Official cycles | GT cycles |
|---|---:|---:|---:|---:|
| BaseMulAdd | 1 | 1 | 2903.5 | 2174.0 |
| CBD | 1 | 1 | 413.0 | 402.2 |
| Forward | 2 | 2 | 7547.0 | 6804.6 |
| FromBytes_checked | 1 | 1 | 754.0 | 901.8 |
| RNG | 1 | 1 | 380.2 | 360.3 |
| SOTP_encode | 1 | 1 | 422.0 | 409.2 |
| ToBytes_full | 2 | 1 | 2225.0 | 1821.5 |
| ToBytes_small | 0 | 1 | 0.0 | 1489.6 |
| cleanup | 5 | 6 | 297.0 | 295.6 |
| hash_f | 1 | 1 | 13297.9 | 13242.8 |
| hash_g | 1 | 1 | 14596.6 | 14484.2 |
| hash_h | 1 | 1 | 4068.6 | 4042.7 |

### decaps

| Component | Official calls | GT calls | Official cycles | GT cycles |
|---|---:|---:|---:|---:|
| BaseMul_R0 | 1 | 1 | 2445.0 | 2181.0 |
| BaseMul_Rinv | 1 | 1 | 1768.0 | 1765.6 |
| CBD | 1 | 1 | 402.0 | 391.9 |
| Crepmod3 | 1 | 1 | 484.0 | 468.0 |
| Forward | 2 | 2 | 7546.0 | 6810.3 |
| FromBytes_checked | 3 | 3 | 2270.0 | 2709.5 |
| Inverse | 1 | 1 | 4138.0 | 7263.4 |
| SOTP_decode | 1 | 1 | 409.0 | 390.5 |
| Sub | 1 | 1 | 222.5 | 210.6 |
| ToBytes_full | 2 | 1 | 2220.0 | 1815.8 |
| ToBytes_small | 0 | 1 | 0.0 | 1493.3 |
| cleanup | 8 | 11 | 544.0 | 652.7 |
| hash_g | 1 | 1 | 14586.5 | 14485.1 |
| hash_h | 1 | 1 | 4064.8 | 4040.4 |

## Interpretation and limitations

- Keygen: BaseInv is the largest GT-specific deficit (~7259 cycles across two calls). ToBytes total is ~4785 versus ~3336. Forward and D1 multiplication recover part of the gap.
- Decaps: Inverse is the largest deficit (~3125 cycles). ToBytes total adds ~1089 and three checked FromBytes calls add ~440 relative to Official. The R^-1 BaseMul alone is essentially tied.
- Encaps: Forward and BaseMulAdd gains narrowly offset the more expensive byte boundaries. A 0.62% full-KEM lead is small and should not be treated as a broad performance win.
- Next priorities: BaseInv, Inverse, then ToBytes routing/scratch. Integrate validity aggregation into the existing FromBytes producer later to remove its extra coefficient scan without changing rejection.
- Cleanup policy is not fully equal: Official Keygen has seven directly profiled clear calls, current GT Keygen has none. This turn closes decoding/rejection, not all secret-erasure parity. Hash-internal clearing is inside hash timings. KAT/rejection success is not a proof of constant-time behavior.

## Reproduction / artifacts

Pi workspace: `/home/pi/ntruplus-experiments/gt864-checked-profile-20260908.jbWPzF`.
Run `pi-integrated.py --checked` then `pi-profile.py` inside that isolated source package (requires its frozen old/ baseline). Local evidence: `build/checked-profile/`; summarization: `summarize-checked-profile.py build/checked-profile`. Production source changes are in byte_api.c, gt864_frombytes.h, kem.c, gt864_secure_clear.h, gt864_support_abi.S and Makefile.
