# K1 production integration evidence

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
