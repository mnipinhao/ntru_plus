# K1 production integration evidence

## Current promotion gate — 2026-09-10

The production-linked 84/37 BaseInv and pair+merge ToBytes promotion passed:

- local Apple arm64: 47 exact Makefile-selected objects, 64 KEM
  round-trips/tampered rejections and 100 KAT cases;
- Pi 5 Linux/GCC 14.2: manifest, assembly/link, the same KEM/KAT gate, and 808
  BaseInv success/failure/alias/canary/AAPCS/scratch-wipe cases;
- malformed transcript: 417216 bytes, SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`;
- KAT `.rsp`: SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.

Six-process AB/BA paired PMU on Pi 5, core 3, ondemand governor, 62 C:

| Operation | SUPERCOP 20260831 Official | GT production | Delta |
|---|---:|---:|---:|
| Keygen | 44330.875 | 47226.875 | +6.53% |
| Encaps | 46413.375 | 46007.625 | -0.87% |
| Decaps | 40772.875 | 44191.300 | +8.38% |

The comparison source is
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`; independent latest
upstream provenance remains unverified.  Raw evidence is retained under
`experiments/gt864-native-asm/baseinv-tobytes-next-model/production-promotion-results/`.

The remainder of this document records historical K1 integration evidence.

Historical K1 evidence below. Latest sequential native integration and unchanged
ToBytes validation: [NATIVE-INTEGRATION.md](NATIVE-INTEGRATION.md). Linux testing
now passes. The 2026-09-08 checked-decoder gate closes the previously observed
Official noncanonical-input rejection gap: 10368 boundary differential cases
and all 79 x+q counterexamples pass. See experiments/gt864-native-asm/
CHECKED-PROFILE-RESULTS.md in the parent repository for fresh PMU and profiler.
Do not reuse historical numbers below as current performance.
The 2026-09-09 gate additionally aligns Keygen-owned secret cleanup; all above
correctness gates pass again. CLEANUP-BASEINV-RESULTS.md supersedes the earlier
checked-decoder report's missing-Keygen-cleanup limitation and performance baseline.

Host: pi@100.99.191.9, Linux AArch64, GCC Debian 14.2.0-19.
Remote directory: /home/pi/ntruplus-experiments/gt864-production-k1-validation/NTRU+864.
Reference: /home/pi/ntruplus-experiments/gt864-p3b41-k1/raw.so.

## Correctness and selection

- `make -j4 check`: imported manifest passed, assembler/linker passed,
  64 valid KEM round trips and tampered ciphertext tests passed, KAT generated.
- `test/paired.c`: 32 deterministic valid/tampered cases, byte-identical
  pk/sk/ct and shared secrets; 32 malformed ciphertext cases returned equal
  status and output against original K1. Repeated in all six PMU processes.
  The inherited instrumentation-equivalence label is not a profiler test here:
  both handles deliberately point to the uninstrumented implementation.
- KAT generator linked separately against original K1: entire .rsp matched.
  SHA256 PQCkemKAT_2624.rsp:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Full object byte comparisons passed for gt864_forward_six_bank.o,
  gt864_forward_poly_ntt.o, gt864_poly_api.o, gt864_fr0_basemul_d1.o,
  gt864_fr0_inverse9_block.o, cluster_transpose_frombytes.o.
  This compares complete objects, including function sections, not empty .text.
- kem-normal.o relocations select gt_d1_poly_ntt at all KEM Forward calls,
  gt_d1 BaseMul/Inverse/BaseInv and p3b12_candidate byte adapters.
- Library SHA256:
  `b295d006eee1f6e496dcdaea7a31bf659e3ca13ce9cf559c814eeae036b3f302`.

## Paired PMU integration check

Core 3; six processes, alternating order, 41 samples/process; 4 Keygen or
20 Encaps/Decaps calls per sample. Numbers below are median of six process
medians. Raw cycles/instructions/branches are in evidence/paired0..5.log.

| Operation | Original K1 cycles | Package cycles |
|---|---:|---:|
| Keygen | 54274.250 | 54154.000 |
| Encaps | 46085.150 | 46095.425 |
| Decaps | 44430.875 | 44424.675 |

No new speedup is claimed. Small sub-percent variation, especially the
order-dependent Keygen split, does not establish an arithmetic improvement.
Encaps differs by +0.022%; Decaps by -0.014%. The identical core objects and
these results support integration parity, not a new optimization result.

This comparison is against original K1, NOT a fresh Official comparison.
The existing Official reference remains SUPERCOP 20260627 SHAKE256 and has
not been verified to be upstream's latest version.

## Scope and limitations

KEM-only producer/consumer range evidence is inherited from P3B40 and the
tested P3B41 K1 lowering; it is archived, not independently re-solved here.
The imported source hash manifest binds the unchanged implementation.
The wrapper object is unchanged (including d8–d15 preservation); a new
standalone ABI-sentinel test was not run. No generic polynomial multiply gate.
Linux/GCC is the validated build; Darwin and CE hash builds are not claimed.
Internal compatibility/helper symbols are retained for faithful integration;
only crypto_kem_* is a supported public API. Name/dead-helper cleanup remains
a separate mechanical gate, not part of this arithmetic promotion.
## P1 BaseInv addition-chain promotion — 2026-09-10

The production `binv_inverse3` uses 21 widening Montgomery multiplications and
157 instructions, versus P0's 28 and 208.  Local Cortex-A76 Slothy scheduling
completed with no spill and an expected 283 cycles.

Mac and Pi 5 passed the 100-case KAT, 64 KEM round trips, tampered rejection,
and the linked 808-case BaseInv test including every zero-leaf position, exact
aliasing, canaries, AAPCS preservation, and scratch wipe.  The Pi 5 malformed
transcript remained exactly 417,216 bytes with SHA-256
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
Six paired Pi 5 repetitions measured BaseInv success at 5469.860 cycles versus
5561.656 and Keygen at 46995.250 versus 47172.250.

## P3-A complete inverse centering — 2026-09-10

The production Inverse now calls one constant-resident `center864` kernel in
place of 27 `center32` calls.  The closed input bound remains `abs <= 6912` and
the exact output remains natural-order centered R0 with `abs <= 1728`.
Exhaustive scalar coverage of the producer range, 4,096 random vectors and
memory canaries passed locally.  On Pi 5, both isolated P2/P3-A packages passed
manifest validation, `test_kem`, 100-case KAT, 256 exact Inverse comparisons,
256 exact-alias comparisons, and six repetitions of valid/tampered KEM tests.
Paired PMU measured -235 instructions, -52 branches, and -212.859 cycles per
Inverse; complete Decaps inherited the same exact static-event reduction and
-212.275 cycles.
