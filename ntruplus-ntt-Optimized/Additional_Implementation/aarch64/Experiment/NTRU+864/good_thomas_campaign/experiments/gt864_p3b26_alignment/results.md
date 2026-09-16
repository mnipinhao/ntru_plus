# P3B26 T1 alignment / P3B27 independent ToBytes integration

Decision: accept T1 as the experimental Forward baseline; accept P3B6 as
a separately validated experimental full-KEM ToBytes replacement.
Production unchanged. No combined T1+P3B6 result is claimed.
T1 Keygen is noisy: one of three repetition medians regresses by 53.750
cycles despite the pooled gain. The Forward/component result and all
Encaps/Decaps repetitions support baseline selection; do not claim a
repeatably fixed Keygen gain. P3B6 improves all APIs in all repetitions.

Pi 5 Cortex-A76, GCC 14.2.0, -O3 -march=armv8-a+simd, portable SHAKE256.
Three repetitions, both execution orders, 41 samples/API/order; CPU 3.
Eight valid/tampered KEM cases before each process; instrumented equivalence
and cross-version public-key/ciphertext byte equality pass. No throttling.
These are PMU measurements on frozen SUPERCOP sources, not native do-part/stq.
SUPERCOP source snapshot is inherited from P3B25; upstream latest not verified.

## P3B26: T1 only

| API | baseline cycles | candidate cycles | delta | instruction delta |
|---|---:|---:|---:|---:|
| keygen | 55736.875 | 55603.000 | -133.875 | -44 |
| encaps | 47702.200 | 47581.050 | -121.150 | -44 |
| decaps | 46052.275 | 45924.675 | -127.600 | -44 |

Per-repetition cycle deltas (both orders pooled):

- Repetition 1: -192.875, -123.725, -131.875.
- Repetition 2: -278.250, -113.550, -113.750.
- Repetition 3: +53.750, -97.100, -131.175.

Actual-caller component totals (cycles per KEM, not per call):

| API | component | baseline | candidate |
|---|---|---:|---:|
| keygen | poly_ntt | 8437.954 | 8299.962 |
| keygen | poly_tobytes | 5672.955 | 5656.955 |
| encaps | poly_ntt | 8439.970 | 8311.986 |
| encaps | poly_tobytes | 3795.954 | 3788.986 |
| decaps | poly_ntt | 8440.986 | 8303.986 |
| decaps | poly_tobytes | 3799.978 | 3797.978 |

## P3B27: P3B6 ToBytes only

| API | baseline cycles | candidate cycles | delta | instruction delta |
|---|---:|---:|---:|---:|
| keygen | 55757.500 | 54718.875 | -1038.625 | -5100 |
| encaps | 47746.750 | 47023.100 | -723.650 | -3400 |
| decaps | 46059.925 | 45356.275 | -703.650 | -3400 |

Per-repetition cycle deltas (both orders pooled):

- Repetition 1: -1063.000, -745.175, -717.025.
- Repetition 2: -1048.625, -697.400, -692.975.
- Repetition 3: -959.500, -719.950, -739.450.

Actual-caller component totals (cycles per KEM, not per call):

| API | component | baseline | candidate |
|---|---|---:|---:|
| keygen | poly_ntt | 8441.486 | 8437.986 |
| keygen | poly_tobytes | 5668.979 | 4532.979 |
| encaps | poly_ntt | 8433.986 | 8431.986 |
| encaps | poly_tobytes | 3795.986 | 3039.986 |
| decaps | poly_ntt | 8439.986 | 8437.486 |
| decaps | poly_tobytes | 3794.986 | 3038.986 |

## SUPERCOP versus T1 (old ToBytes retained)

| API | baseline cycles | candidate cycles | delta | instruction delta |
|---|---:|---:|---:|---:|
| keygen | 44317.000 | 55579.375 | +11262.375 | +31756 |
| encaps | 46441.525 | 47569.850 | +1128.325 | +7622 |
| decaps | 40755.475 | 45959.475 | +5204.000 | +13834 |

Per-repetition cycle deltas (both orders pooled):

- Repetition 1: +11253.375, +1114.750, +5206.075.
- Repetition 2: +11259.500, +1133.325, +5161.525.
- Repetition 3: +11303.500, +1144.500, +5222.425.

Actual-caller component totals (cycles per KEM, not per call):

| API | component | baseline | candidate |
|---|---|---:|---:|
| keygen | poly_ntt | 7531.986 | 8298.914 |
| keygen | poly_tobytes | 3297.979 | 5655.871 |
| encaps | poly_ntt | 7531.986 | 8311.486 |
| encaps | poly_tobytes | 2203.986 | 3791.986 |
| decaps | poly_ntt | 7531.986 | 8306.914 |
| decaps | poly_tobytes | 2203.986 | 3788.986 |

## Forward diagnostic

Every timed call includes the same 1728-byte input reset. Do not label these
absolute numbers pure NTT cycles or subtract reset-only cycles as an exact
decomposition. 64 inputs in [-3,4], including all -3 and all +4: T0/T1
raw output bit equality and SUPERCOP/GT serialized output equality pass.
61 samples/order, 400 calls/sample, three repetitions.

| Variant | cycles including reset | instructions | branches |
|---|---:|---:|---:|
| gt | 4295.278 | 4687.145 | 66.032 |
| t1 | 4232.276 | 4665.145 | 68.032 |
| sc | 3853.245 | 3736.142 | 57.030 |
| reset_only | 114.730 | 236.137 | 31.030 |

T1 saves 63.002 cycles versus T0, but remains 379.032 cycles above SUPERCOP at this common boundary.

## Source and object audit

The T1 wrapper actually calls gt864_tail_layout_bank_major_inplace then
gt864_forward_six_bank_pass2_a1_t1. Tail preparation is included.
The P3B27 byte wrapper actually jumps to gt864_fr0_input_once_tobytes;
FromBytes remains gt864_fr0_cluster_transpose_frombytes.
The P3B6 target object stack accesses are limited to d8-d15 ABI saves
and the outer x29/x30 frame: no coefficient-vector spills or scratch.
Retired instruction savings are 1700 per ToBytes under this full-KEM
build, not the old isolated result of 1591; do not reuse old object counts.

## Remaining Forward gap: next algebra/range gate

SUPERCOP fuses levels 0/1/2 before its first coefficient store and uses
a raw -722 multiplication at level 0 under its [-3,4] input contract.
GT top split retains 64 vector Algorithm-10 products (four per iteration
times sixteen). Replacing only their reductions would remove 128
arithmetic instructions, not merely load encodings. This is NOT implemented.
For low,high in [-3,4], raw alpha output low-722*high lies in
[-2891,2170], beta output low+723*high in [-2172,2896]. Local int16 fit
does not prove the subsequent NTT16/one-product NTT9/M5C/M5E chain.
The next gate must verify all KEM input producers and re-close that chain
before changing the general GT kernel or claiming a cycle improvement.
The remaining roughly 929-instruction measured boundary gap also includes
Pass-2 arithmetic/routing and wrapper differences; top reduction alone
cannot explain it. No cycle attribution is inferred from instruction count.

Raw evidence, profiler details and exact hashes: build/raw/,
build/*-*.json, build/source-hashes.json. No combined candidate has been run.
