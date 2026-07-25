# GT Production Instruction-Working-Set Audit

Date: 2026-07-24

## Boundary

This directory owns all code-size and instruction-cache analysis for the
publishable GT release:

```text
ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768
```

The release remains source-only. Do not put benchmark harnesses, generated
binaries, PMU logs, Slothy artifacts, candidate assembly, or result files in
that directory.

Development artifacts belong here. Raw benchmark output belongs under:

```text
ntruplus-ntt-Optimized/aarch64-bench/results/
  gt_production_icache_size_<date>/
```

## Current Evidence

The section-GC release has about 80.7 KiB of `.text`, compared with about
19.8 KiB for KPQC final. Cortex-A76 has a 64 KiB L1 instruction cache, but
whole-binary size is not the performance contract: keygen, encapsulation, and
decapsulation execute different subsets of the linked text.

Existing Pi 5 evidence:

```text
section GC text reduction: about 14.1 KiB
decapsulation L1I misses:   about 10.09 -> 3.79 per measured call
balanced full-KEM cycles:   effectively neutral
```

This means static-size reduction is useful, but the selected warm KEM paths
are not consistently frontend-bound.

## Measurement Matrix

Every candidate must be compared in the same binary or in balanced AB/BA
replacement binaries:

| Mode | Purpose |
| --- | --- |
| `warm` | Repeated keygen, encapsulation, or decapsulation |
| `mixed` | Keygen -> encapsulation -> decapsulation working-set turnover |
| `cold` | Target call after an external instruction-thrash step |

Required counters:

```text
cycles
instructions
L1I refill/miss
frontend stalls
backend stalls
branch misses
```

Required metadata:

```text
ELF .text bytes
allocated bytes
largest text symbols/regions
symbol address mod 32/mod 64
compiler and flags
release manifest hash
```

Cold measurements must report the instruction-thrash control separately.
Do not subtract one noisy median from another and present it as an exact kernel
cycle count.

## Candidate Policy

Optimization order:

1. Remove unreachable code through section ownership and linker GC.
2. Remove exact duplicate implementations.
3. Compact low-gain, high-text expansion.
4. Rework serialization kernels that are both large and slower than KPQC.
5. Compact forward/inverse arithmetic only with hardware evidence.

The forward NTT and rminus1 inverse are performance-critical. Code-size
reduction alone is not enough to replace them.

Promotion gate:

```text
warm full-KEM regression <= 0.5%
mixed/cold result is stable
text reduction >= 2 KiB, unless cycles improve independently
correctness/KAT/ABI pass
production source closure pass
```

## Files

```text
release_boundary_policy.json
candidate_registry.json
audit_release_boundary.py
analyze_elf_text.py
analyze_serialization_duplication.py
bench_full_kem_variants_pmu.c
bench_serialization_candidates_pmu.c
generate_serialization_candidates.py
benchmark_protocol.md
serialization_candidate_abi_sentinel.S
serialization_endpoint_audit.md
serialization_endpoint_inventory.json
test_serialization_candidates.c
results/README.md
```

Generate and test the first serialization size candidates:

```sh
make -B test_gt_serialization_icache_candidates
```

Run the release boundary audit from this directory:

```sh
python3 audit_release_boundary.py
```

Analyze a Pi 5 ELF without writing into the release:

```sh
python3 analyze_elf_text.py \
  --elf /tmp/gt-production-kem-dec \
  --output-dir ../../../../../aarch64-bench/results/gt_production_icache_size_manual
```
