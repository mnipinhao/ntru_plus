# ToBytes timing gate — 2026-09-08

**Decision: keep experimental; positive complete-boundary performance result.**
Production is unchanged. This is a comparison against frozen GT `opt.so`, not a
new Official/SUPERCOP run. Repository base: `22ba499e4f8d59e182f08ec8463b54cf82842b4e`
plus the recorded experimental changes and artifact hashes below.

## Complete ToBytes

Cycles are the median of six process medians; each process has 41 samples with
128 calls/sample and five discarded warmup batches. Each row is its own paired
comparison, so baseline values differ slightly across rows.

| Comparison | Baseline cycles | Candidate cycles | Change |
| --- | ---: | ---: | ---: |
| Frozen P3B12 serializer -> scheduled full | 1854.203 | 1795.668 | -3.157% |
| Frozen P3B12 serializer -> scheduled small | 1854.641 | 1467.953 | -20.850% |
| Scheduled full -> scheduled small | 1795.903 | 1466.883 | -18.321% |
| Allocated full -> scheduled full | 1849.407 | 1795.746 | -2.901% |
| Allocated small -> scheduled small | 1487.696 | 1470.168 | -1.178% |

All six process deltas are negative for every comparison. The benchmark invokes
the whole public serializer: routing, normalization, packing, byte scratch,
merge, public ABI save/restore and scratch wipe are inside the measured call.
Both implementations receive the identical deterministic [-3023,3023] input.
Full-int16 correctness is tested separately; cycles for every possible input
distribution are not claimed.

Complete-call retired instructions are approximately 4474.461 old, 3621.461
new full, 3386.461 new small, including harness overhead. Full -> small saves
235 retired instructions here: 228 core instructions plus seven public-wrapper
unconditional branches (one entry branch and six pair-return branches).
The all-full C adapter adds another branch at selected call sites, so the
full-KEM all-full -> selected difference is 236 instructions per small call.

The new byte scratch still uses 648 bytes, allocates/wipes 656 bytes, and adds
2592 bytes of byte-scratch traffic. Measurements show the complete implementation
offsets those costs versus the frozen serializer; they do not isolate a causal
cycle cost for scratch, TBL or stores individually. IPC is lower than the old
serializer even though total cycles improve; fewer instructions alone would
not have established this result.

## Full KEM — frozen GT versus scheduled selected entry

Other arithmetic objects are the unchanged frozen native opt candidate.
Four proven D1 output sites use small, three Forward output sites use full.

| Operation | Frozen cycles | Candidate cycles | Saved cycles | Change |
| --- | ---: | ---: | ---: | ---: |
| Keygen | 52226.625 | 51330.750 | 895.875 | -1.715% |
| Encaps | 46107.300 | 45637.400 | 469.900 | -1.019% |
| Decaps | 43580.175 | 43032.825 | 547.350 | -1.256% |

Six process paired cycle deltas:

- Keygen: -910.50, -911.25, -908.00, -870.25, -880.25, -890.50.
- Encaps: -496.60, -455.10, -483.65, -435.65, -456.60, -466.50.
- Decaps: -577.10, -537.90, -547.75, -550.55, -527.35, -549.10.

## Attribution controls

| Full-KEM comparison | Keygen saved | Encaps saved | Decaps saved |
| --- | ---: | ---: | ---: |
| Frozen -> scheduled all-full | 213.750 | 97.200 | 213.850 |
| Scheduled all-full -> selected | 664.750 | 358.975 | 308.500 |
| Allocated selected -> scheduled selected | 95.625 | 76.575 | 68.950 |

These are separate paired runs, not quantities that must sum exactly. The
largest incremental gain comes from the small-input specialization, with a
smaller repeatable gain from scheduling. Keygen saves two small calls; Encaps
and Decaps each save one. Full-KEM measurements include the retained full entry.

## Correctness and Slothy

- Local Slothy entry `/Users/chenpinhao/slothy`, venv
  `/Users/chenpinhao/slothy_and_ra/.venv/bin/python`, target Cortex-A76.
- Mode continues `new_symbolic_kernel`. Timing only: frozen allocation,
  no renaming/spills, bounded split windows (factor 8, stepsize 0.05), 30-second
  solve timeout. No new arithmetic/range/layout changes.
- Full, small and merge all emitted concrete `.opt.S` and ended in
  `split_heuristic_full:OK!`; ELF assembly and no-spill audits passed.
- The generic skill log parser reports intermediate infeasible/timeouts as
  failure. Reviewed final status is pass; `bytes-slothy-review.json` records the
  discrepancy. No whole-kernel cycle estimate is fabricated from window minima.
- Scheduled Mac and Pi5 native tests pass 66048 full cases, 7425 small cases,
  512 shared-domain differentials, exact bytes, input immutability, AAPCS,
  canaries and 656-byte scratch wipe.
- Frozen/all-full/selected full-KEM differential tests pass, including exact
  pk/sk/ct equality, 32 valid/tampered cases and 32 malformed ciphertext cases.
  This is differential testing, not an additional official KAT campaign.
- Slothy emulator selftest remains disabled; real native execution is used.

## Measurement provenance and limits

Host: `pi@100.99.191.9`, Cortex-A76 CPU3 affinity. GCC 14.2.0,
`-O3 -march=armv8-a+simd`. Six processes alternate AB/BA order. Full KEM uses
41 samples/process, four Keygen calls or 20 Encaps/Decaps calls per sample,
the frozen harness and deterministic matching seeds. Counters are user-space
cycles, instructions, branches; no PMU overhead subtraction. No cold-cache or
cache-event attribution is claimed. Governor remained `ondemand`; no global
host settings were changed. Throttle flags were zero before and after,
temperature 59.3 -> 62.0 C. Small full-KEM effects should still be rechecked at
publication/promotion time rather than extrapolated to every workload.

Raw CSVs are gitignored under `build/bytes-timing/`, with a remote copy in
`/home/pi/ntruplus-experiments/gt864-native-timing-20260908.X8u5QV/experiments/gt864-native-asm/build/bytes-timing`.
Persistent summaries: `bytes-timing-results.json`, `bytes-timing-environment.json`.

Scheduled source SHA256:

- full: `e338e9b411ea5842b085bb2592868c0a7519341434b91c77314da910ecf685a0`
- small: `b6607bf08d8e9aec1521c1db08fea5088adcf51b03ce3c203f603ae04cb4bfd1`
- merge: `dd26d4040759fb49c57662ebcf257834c79633b0812d84ad1fd2bd44c50c88fc`

Reproduce local scheduling with `optimize.py <tobytes_block|tobytes_small|tobytes_merge>
--timing-only` using the venv/PYTHONPATH above, then native tests with
`integration/build_bytes.py --scheduled`. In the existing isolated Pi workspace,
`python3 experiments/gt864-native-asm/pi-bytes-timing.py` rebuilds the new ToBytes
objects, reruns correctness and measures against the preserved binaries.
Summarize with `summarize-bytes-timing.py build/bytes-timing`.

## Next decision

The performance hypothesis passes. Keep the proven caller specialization and
scheduled cores as the experimental candidate. Production integration still
requires its separate publication/KAT and security review; no production
replacement or commit is made by this timing gate.
