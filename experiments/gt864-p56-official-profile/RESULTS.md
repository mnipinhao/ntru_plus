# P56 results

P56 compares exact committed P55 production (`9941d3bc`) with the selected
SUPERCOP 20260831 NTRU+864 AArch64 source on the same Pi 5. The Official source
hashes match `OFFICIAL-BASELINE.json`; this snapshot is not independently
verified as the latest upstream revision.

Correctness and measurement gates passed:

- fresh GT 64-case valid/tampered KEM test;
- exact GT KAT SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`;
- six cross-implementation processes, each with 100 exact transcripts and 100
  tampered ciphertexts;
- twelve instrumentation-equivalence processes;
- 252 clean observations per implementation and KEM operation;
- 126 observations per instrumented component;
- Pi 5 core 3, GCC 14.2, `throttled=0x0` before and after.

## Authoritative clean full-KEM result

| operation | selected Official | GT P55 | GT delta | GT improvement | Official / GT instructions |
|---|---:|---:|---:|---:|---:|
| Keygen | 44305.250 | 39097.875 | -5207.375 | 11.75% | 89316 / 78061 |
| Encaps | 46370.725 | 36636.275 | -9734.450 | 20.99% | 120822.2 / 90188.2 |
| Decaps | 40769.125 | 35383.250 | -5385.875 | 13.21% | 86634.2 / 76454.2 |

Cycle deltas use `GT - Official`; negative is faster. Clean full-KEM medians are
authoritative. Instrumented component medians below are diagnostic.

## Matched-boundary interpretation

- Keygen `hash_f`: 13274.625 → 9187.000 cycles, a 4087.625-cycle GT win.
  Forward saves 733.125 cycles and two-call BaseInv saves 165.000. GT's mixed
  one-Full/two-Small serializers total 3386.250 versus Official's three Full
  calls at 3316.750, leaving only about a 69.5-cycle diagnostic serializer gap.
- Encaps `hash_f`: 13295.025 → 9183.025, a 4112.000-cycle GT win. Official
  `ToBytes_full + hash_g` totals 16784.850 cycles; GT
  `Full_to_hash_g + ToBytes_small` totals 12509.025, a 4275.825-cycle fused
  serialization/hash win. GT also saves 740.950 in Forward and 727.100 in
  BaseMulAdd.
- Decaps `hash_g`: 14553.100 → 10094.700, a 4458.400-cycle GT win. Forward
  saves 737.225, R0 BaseMul saves 257.000 and three FromBytes calls save
  116.375. The remaining diagnostic deficits are small: GT fused
  Inverse-to-ternary is 4759.050 versus Official Inverse+Crepmod3 at 4603.300
  (+155.750), while the complete re-encryption serialization/compare aggregate
  is about +58.4 cycles. R-inverse BaseMul is effectively tied (+4 cycles).

The current next optimization target remains Inverse-to-ternary, but its
remaining selected-Official deficit is now only about 156 diagnostic cycles;
new work should require an arithmetic or routing DAG with a credible complete-
Decaps gain rather than another representation-only rewrite.
