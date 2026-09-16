# BaseInv shared multiplier audit and ToBytes matched-boundary measurements

2026-09-10. Production unchanged; benchmark-only diagnostic variants.

## Correction: GT BaseInv finish already shares the multiplier

The earlier explanation implied GT had not adopted SUPERCOP's denominator
precomputation sharing. That was incorrect. In generate.py finish(), dqi is
computed once outside the three-component loop and passed to every mm().
Production gt864_native_baseinv_finish.S line28 computes v8=den*qinv;
lines30,38,51 use v8 for the three numerator products. The fixed-scale candidate
retains that same sharing. No new implementation is needed for this idea.

What remains different is denominator scale correction, final centered-output
normalization and kernel organization. Neither the existing nor candidate GT
implementation should be described as recomputing dqi per component.

## Sources and boundaries

Official sources: /home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64,
the exact prior fresh-build source copy and binary hashes, not independently
verified as upstream latest. GT uses the latest tested isolated package; its
ToBytes objects are unchanged from production.

Complete boundary: read 1728 bytes in each implementation's own transform
layout, produce identical1296 wire bytes. Setup uses the same canonical wire
coefficients and each implementation's FromBytes, outside timing. Full inputs
are canonical coefficients plus q, range[3457,6913], inside both implementations'
contracts. Small inputs are centered[-1728,1728]. The two layouts must NOT be
fed the same raw coefficient-array bytes.

Both clean and instrumented paths match the original wire bytes, preserve the
input, and preserve output canaries. This focused test is not an exhaustive new
ToBytes correctness suite; the frozen binaries already passed the earlier KAT
and producer-range gates. No scheme code is modified.

## Clean whole-call PMU

Pi5 CPU3; six alternating-order processes,41 samples/process,128 calls/sample,
five warmups. Median of process medians; same prior GCC14.2 -O3 build policy.
No throttling reported. Headers/source/binary hashes are in build/evidence.json.

| Same logical serialization | Official cycles | GT cycles | GT instructions |
|---|---:|---:|---:|
| Full-range cohort | 1080.73 | 1789.48 | 3621.42 |
| Small-range cohort | 1080.78 | 1470.46 | 3386.42 |

Official has1275.42 measured instructions/call in both cohorts. Fractional
counts include amortized harness overhead. GT small saves about319 cycles
versus full in these cohorts, but remains about390 cycles slower than Official.

## GT pair / merge / wipe attribution

Diagnostic copies preserve volatile GPRs, SIMD registers and NZCV around stage
marks. Empty adjacent marks estimate overhead. Values below are estimates per
complete ToBytes, not per tile, and include each stage's loop/control overhead.

| Stage | Full cycles | Small cycles | Stage count/call |
|---|---:|---:|---:|
| Pair: routing+normalization+packing+scratch stores | ~1356 | ~1028 | 2 top groups,6 pair calls |
| Merge: scratch loads+TBL/ORR+final stores | ~383 | ~376 | 2 top groups,18 merge calls |
| Scratch wipe | ~45 | ~41 | 1 |

Some public prologue/epilogue and register erasure are outside marked regions.
Saving/restoring probe registers perturbs stack/cache/issue behavior, so adding
these estimates is not an exact reconstruction of clean whole-call cycles.
GT pair is a fused scheduled DAG: normalization cannot be separated by merely
placing another timestamp without changing its actual dataflow.

## Official normalization / packing: reliable control, rejected short probes

Initially normalization and routing/packing were marked inside each of18 loop
iterations. Subtracting empty-probe overhead produced a negative packing value.
Those estimates are invalid and are retained only as diagnostic evidence in
results.json. Do not report them as component timings or clamp them to zero.

Instead a benchmark-only copy removes the24 normalization instructions per
iteration (Barrett plus sign correction). Everything else, including input
loads, constants, routing, packing, output stores and loop structure, is retained.
It is invoked ONLY with canonical[0,q) input and compared against the original
on exactly the same array. Both must reproduce the same wire bytes.

| Matched whole-call control on canonical inputs | Cycles | Instructions |
|---|---:|---:|
| Original Official normalization+routing+packing | 1084.41 | 1275.45 |
| Diagnostic routing+packing only | 404.86 | 843.45 |
| Incremental effect of normalization | ~679.57 | 432 removed |

Incremental cycle difference is median of paired process differences, not a
standalone normalization kernel timing. It includes normalization's effect on
dependencies and issue overlap. The diagnostic variant is invalid on general
input and must never replace Official or production serialization.

This control and GT stage estimates answer different attribution questions.
Compare complete serializers directly; do NOT equate GT pair with Official
normalization or GT merge with Official packing. Both GT phases do routing and
packing work, while Official routes/packs directly to final output in one loop.

## Interpretation

1. GT finish's shared-denominator multiplication is already implemented.
2. GT ToBytes has a material extra merge boundary (~380 estimated cycles),
   involving scratch reload and final layout assembly.
3. Removing that merge cannot be assumed to save380 cycles for free: its
   required ordering/stores must be absorbed into pair's producer dataflow.
4. GT small's pair still costs~1028 cycles even without Barrett. Routing,
   canonicalization, packing and scratch stores remain substantial.
5. The next concrete experiment is a producer-to-final-byte-layout candidate,
   benchmarked as a complete ToBytes under unchanged range/canonical-output
   contracts. Do not target reduction deletion alone based on these numbers.

## Reproduction

Pi workspace: /home/pi/ntruplus-experiments/gt864-fixed-bench-20260910.5ufJSS.
Within it run pi-run.py and then pi-control.py from this directory. They link
diagnostic libraries using the existing frozen build/integrated source/objects.
Local summarize.py writes results.json from build/run-*.csv and control-*.csv.
No Slothy scheduling, production changes or new full-KEM benchmark was performed.
