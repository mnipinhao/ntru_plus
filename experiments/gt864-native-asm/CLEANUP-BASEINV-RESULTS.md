# Keygen cleanup alignment and BaseInv decomposition — 2026-09-09

## Outcome

Keygen cleanup is now implemented in production. Forward, BaseInv arithmetic,
Inverse, ToBytes and FromBytes are unchanged. This is a baseline-correction and
diagnostic gate, not an arithmetic optimization promotion.

The dominant BaseInv work is numerator/denominator generation and finish,
not field inversion or scratch wiping.

## Keygen cleanup contract

The source oracle is the selected SUPERCOP 20260831 aarch64/kem.c. Its sampling
workspace belongs to the outer Keygen function and is reused across f/g retries.
GT now follows that ownership: a 216-byte buffer is fully overwritten on each
SHAKE sampling attempt, then explicitly cleared on Keygen exit. No early-return
path was added. BaseInv failure still triggers the same retry and RNG sequence.

Cleared objects: coins (32), sampling buffer (216), f/finv/g/ginv (4×1728), and
both h/hinv (2×1728). GT retains two product temporaries while Official reuses
one: GT therefore has eight direct clear calls versus Official's seven.
This aligns Keygen-owned secret-memory coverage, not identical stack size or
all internal/register erasure policies across both implementations.

Linux uses explicit_bzero, Darwin memset_s, through gt864_secure_clear.h.
Runtime KEM profiler observes eight clear calls; linked KEM disassembly is
archived. A separate post-return Keygen stack-memory sentinel test was not run.

## Correctness

- Mac: 64 KEM round trips/tampered ciphertext cases and 100 KAT cases passed.
- Pi fresh source builds and source manifests passed for baseline and candidate.
- 100 Official KAT cases are byte identical; SHA256 remains
  0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c.
- BaseInv 808 cases: 517 success, 291 failure, all 288 zero-leaf positions,
  alias/canary/ABI/scratch-wipe tests passed.
- Inverse 256 inputs and 256 paired multiplication chains passed.
- All 4096 uniform FromBytes values and q-1/q at every coefficient passed.
- 10368 rejection boundary differential cases and 79 noncanonical ciphertext
  counterexamples passed against Official. Both old and new GT reject them.
- Stage-profiler versus clean KEM output equivalence passed before measuring.

The initial isolated upload omitted the Inverse C oracle directory; the test
stopped at compilation before timing. The existing oracle was copied into the
isolated directory, and the entire gate was rerun successfully.

## Clean full-KEM benchmark

Exact Official path: /home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64.
SHAKE256, not independently verified as upstream latest. Standalone same-policy
GCC 14.2 -O3 -march=armv8-a+simd build, not SUPERCOP's compiler sweep.
Pi5 CPU3, six alternating AB/BA processes, 41 samples each, median of process
medians; deterministic harness RNG. Raw environment and hashes are in JSON.

| Operation | Official cycles | GT cycles | GT difference |
|---|---:|---:|---:|
| Keygen | 44320.38 | 51885.25 | +17.07% |
| Encaps | 46450.33 | 46135.40 | -0.68% |
| Decaps | 40748.45 | 44351.15 | +8.84% |

Paired against the previous checked GT, Keygen increased from 51432.88 to
51888.13 cycles (+455.25, +0.89%). Encaps/Decaps instruction counts are unchanged;
their tiny timing movements are not optimization gains or regressions established
by this gate. Direct Keygen cleanup profiler estimates are 459 GT vs 486 Official
cycles, but these are instrumented estimates and cannot substitute for clean PMU.

## BaseInv stage profiler

Each figure below is per **one BaseInv call**; Keygen normally calls it twice.
Marks are placed at whole-stage boundaries in a diagnostic copy of the public
wrapper. They preserve all volatile GPR/SIMD state before calling the PMU reader.
Core objects are unchanged. Adjacent empty marks measure about 140 cycles of
overhead, subtracted per stage. Cache/stack effects remain: these are approximate
attribution estimates, not exact additive full-function cycles.

| Stage | Work per successful BaseInv | Adjusted cycles |
|---|---|---:|
| Numerator / denominator | 36 eight-leaf tiles | 4572 |
| Prefix | 11 calls × 3 vector chains | 277 |
| Failure scan | all 24 terminal lanes | 32 |
| Field inversion | combine 3 vectors, exponentiate, split | 393 |
| Recovery | 11 reverse steps × 3 vector chains | 538 |
| Finish | 36 eight-leaf tiles | 1813 |
| Scratch wipe | 1200 bytes, 75 fixed stores | 79 |

Public prologue/epilogue, final vector-register erasure and some pointer setup
are outside those marked intervals. No benefit is inferred from subtracting
this table from an independently instrumented whole BaseInv measurement.

## Source findings and next hard gate

1. Numerator first converts all three input vectors with REDC(input×867),
   then computes the cubic adjugate and denominator. Across 36 tiles this is
   108 input conversion multiplications. They are representation/range operations,
   not established redundant operations; do not delete them by modular identity.
2. Finish converts each denominator inverse with REDC(den×1), applies it to
   three numerator vectors, and centers the three results. That is 36 denominator
   scale corrections plus 108 final products and their output normalizations.
3. Both implementations already use hierarchical batching: three prefix chains,
   one combined eight-lane inversion, then recovery. GT is not doing 288 separate
   exponentiations. Its current exponent generator is a 12-bit binary chain
   starting from oneR; Official uses a 15-multiplication addition chain. This is
   a valid later target, but the measured field-inversion budget is only ~393 cycles.
4. The priority is a BaseInv numerator/finish **scale and range ledger** against
   Official: preserve FR0 input/output and failure semantics, identify which
   conversions or normalizations can be absorbed or weakened, then prove exact
   roots/scales/bounds before editing the DAG. Keep BaseInv→BaseMul boundaries.
5. Do not optimize away the new cleanup to recover its ~455 Keygen cycles.

## Evidence and reproduction

Production change: ntruplus-GT-Production/Additional_Implementation/aarch64/
NTRU+864/kem.c and its source manifest.

Pi workspace: /home/pi/ntruplus-experiments/gt864-cleanup-20260909.bDb1rW.
Local raw evidence: experiments/gt864-native-asm/build/cleanup-20260909/.
Machine-readable full/component/stage results: cleanup-baseinv-results.json.

Runners: pi-integrated.py --checked, pi-profile.py, pi-baseinv-stages.py.
Summarizer: summarize-cleanup.py build/cleanup-20260909.
The isolated package needs the existing old/ baseline and gt864-decaps-scale C
oracle; stage instrumentation is never linked into the production library.
