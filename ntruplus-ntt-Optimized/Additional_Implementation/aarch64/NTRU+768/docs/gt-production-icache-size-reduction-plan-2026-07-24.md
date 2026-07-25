# GT Production Instruction-Cache And Code-Size Plan

Date: 2026-07-24

## Decision

Treat code size as an explicit production constraint, but do not require the
entire linked KEM binary to fit in the 64 KiB Cortex-A76 L1I. Promotion depends
on the per-operation instruction working set and Pi 5 PMU, not static
instruction count alone.

The publishable release remains source-only. All experiments, PMU output,
Slothy artifacts, code-size reports, and candidate implementations live in:

```text
experiments/gt_production_icache_size/
ntruplus-ntt-Optimized/aarch64-bench/results/
```

## Baseline

```text
KPQC final .text:       19,757 bytes
GT release .text:       80,673 bytes
GT/KPQC ratio:          4.08x
A76 L1I nominal size:   64 KiB
```

The whole GT binary is larger than L1I, but keygen, encapsulation, and
decapsulation do not execute every linked function. OS code does not reserve a
fixed portion of L1I; interrupts and context switches evict lines only when
other code executes.

## Existing Hardware Evidence

Section GC removed about 14.1 KiB and reduced measured decapsulation L1I misses
from about 10.09 to 3.79 per repeated call. Balanced full-KEM cycles remained
effectively neutral. The current warm workload is therefore not consistently
frontend-bound.

The compact decapsulation verify endpoint saves 9,088 bytes versus the fully
unrolled F2 backend. F2 is about 112 cycles faster in full decapsulation, so
compact F1 remains the general release choice.

## Audit Order

1. Verify section ownership and linker-GC reachability.
2. Identify exact duplicate tables, wrappers, and endpoint bodies.
3. Audit canonical pack/unpack, which are both large and slower than KPQC.
4. Audit duplication across keygen-specific pack endpoints.
5. Preserve forward NTT and rminus1 inverse unless a compact candidate passes
   warm, mixed, and cold hardware gates.

## Promotion Gate

```text
correctness, ABI, deterministic KAT: pass
release source closure:              pass
warm full-KEM regression:            <= 0.5%
mixed/cold evidence:                 stable
text reduction:                      >= 2 KiB
```

A candidate that improves cycles may use a smaller text threshold. A candidate
that only reduces L1I misses but does not improve cycles remains a size-first
change and must not be described as an A76 speedup.
