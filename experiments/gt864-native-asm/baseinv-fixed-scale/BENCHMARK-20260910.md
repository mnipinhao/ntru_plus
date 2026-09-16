# BaseInv fixed-scale candidate: complete BaseInv / Keygen PMU

Date: 2026-09-10. Status: measured candidate, production not modified.

## Conclusion

The arithmetic saving survives physical execution: complete successful BaseInv
is approximately 4.74% faster; cleanup-aligned Keygen is 1.42% faster. The two
BaseInv calls save approximately 2×370 cycles, consistent with Keygen's measured
739-cycle reduction. This is a measured speedup, not a Slothy cycle estimate.

## Identity and correctness

Candidate is the frozen, already-native-tested fixed-scale numerator/finish
package. Baseline is the 2026-09-09 cleanup-aligned GT production snapshot from
/home/pi/ntruplus-experiments/gt864-cleanup-20260909.bDb1rW.

Source audit asserts only gt864_native_baseinv_num.S and
gt864_native_baseinv_finish.S differ among arithmetic C/headers/assembly/Makefile.
Neither KEM cleanup nor Forward/Inverse/byte routines were changed.
All libraries were rebuilt with make -B; source manifest and source/object
hashes are archived, preventing use of a stale target binary.

- Fresh Linux build and 100 exact Official KAT cases passed.
- BaseInv 808 cases (517 success,291 failure), all zero-leaf positions,
  alias/canary/AAPCS/scratch-wipe passed.
- Inverse 256 inputs plus 256 paired BaseMul/Inverse cases passed.
- Checked decoder exhaustive values and every q-1/q position passed.
- 10368 pk/ct/sk rejection differential cases and all 79 x+q ciphertext
  counterexamples passed for both old and candidate GT.
- Profiler/clean KEM output equivalence passed.

## Complete public BaseInv (un-instrumented)

Includes public ABI wrapper, all arithmetic, failure scan and scratch wipe.
Six paired processes with alternating AB/BA order; 41 samples/process,32 calls
per sample,5 warmups; CPU3. Values are medians of process medians.

| Input | Baseline cycles | Candidate cycles | Change | Instructions saved |
|---|---:|---:|---:|---:|
| Unit element, successful | 7798.53 | 7428.20 | -4.75% | 432 |
| Ternary→Forward, successful | 7798.53 | 7429.22 | -4.74% | 432 |
| All-zero, failure | 5174.38 | 4931.02 | -4.70% | 360 |

Every process improved on every tested input. Branch counts are unchanged.
Failure skips finish, explaining why only numerator's360 instructions disappear.
The synthetic ternary input uses uniform {-1,0,1}, then 3f+1 and GT Forward;
it is a representative arithmetic workload, not the scheme's exact CBD sampler.
The separate complete KEM benchmark uses the actual scheme sampling code.
These three fixed inputs do not establish all-input timing or constant-time proof.

## Complete KEM: old GT versus candidate

Six paired processes, alternating order,41 samples/process,4 Keygen or20 other
calls/sample. Same compiler and public operation boundary, deterministic harness
RNG (not OS entropy acquisition).

| Operation | Old GT | Candidate | Change |
|---|---:|---:|---:|
| Keygen | 51924.63 | 51185.63 | -1.42% |
| Encaps | 46134.48 | 46140.40 | +0.013% |
| Decaps | 44359.95 | 44363.08 | +0.007% |

Keygen's six process deltas are -790.25,-752.50,-803.00,-722.25,-789.00,-735.25
cycles. The difference of overall medians is739 cycles; it is not the median
of these paired deltas. Keygen instructions drop864, exactly two successful
BaseInv savings. Encaps/Decaps instruction and branch counts are unchanged;
their tiny timing changes are consistent with noise, not an arithmetic regression.

## Specified Official comparison

Official: /home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64, SHAKE256.
Not independently verified as upstream latest. GCC14.2, -O3,
-march=armv8-a+simd; exact source hashes in benchmark-results.json.
This is a standalone equal-policy PMU build of those sources, not SUPERCOP's
complete compiler sweep. Governor ondemand; environment and throttling recorded.
The Official/candidate pairs are separate runs from old-GT/candidate pairs.

| Operation | Official | Candidate | Candidate difference |
|---|---:|---:|---:|
| Keygen | 44262.38 | 51154.25 | +15.57% |
| Encaps | 46427.85 | 46113.55 | -0.68% |
| Decaps | 40748.08 | 44334.00 | +8.80% |

## Keygen profiler (cycles per full Keygen)

Instrumented estimates with empty-probe overhead subtracted; not additive clean
KEM cycles. Raw values and call counts retained in benchmark-results.json.

| Component | Official | Candidate |
|---|---:|---:|
| Forward ×2 | 7555.25 | 6799.88 |
| BaseInv ×2 | 8367.75 | 14857.63 |
| BaseMul ×2 | 4892.00 | 4364.38 |
| ToBytes total ×3 | 3340.50 | 4801.13 |
| hash_f | 13282.75 | 13246.38 |
| SHAKE sampling ×2 | 5529.88 | 5559.63 |
| CBD ×2 | 826.00 | 776.88 |
| Triple ×2 | 482.13 | 481.50 |
| RNG | 268.00 | 236.00 |
| Direct KEM cleanup | 486.00 | 462.00 |

BaseInv remains the primary GT-specific Keygen deficit (~6490 cycles across
two calls), followed by ToBytes (~1461 cycles). This candidate improves the
baseline without resolving the entire Official gap. Cleanup remains enabled:
eight direct GT calls versus seven Official because GT retains h and hinv.

## Artifact locations and decision

Pi: /home/pi/ntruplus-experiments/gt864-fixed-bench-20260910.5ufJSS.
Local raw build/log/object evidence: build/pi-20260910/.
Summary: benchmark-results.json. Complete BaseInv runner: pi-baseinv-bench.py;
summary: summarize-bench.py build/pi-20260910.

Candidate is performance-positive and correctness-tested. Production promotion
is not performed by this benchmark request. Prior internal range/constant
contract differences and generic Slothy parser ambiguity remain documented in
PHYSICAL-GATE.md; no Slothy whole-kernel cycle number is claimed here.
