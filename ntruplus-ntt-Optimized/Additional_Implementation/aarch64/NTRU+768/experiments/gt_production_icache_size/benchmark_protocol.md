# Warm, Mixed, And Cold Instruction-Working-Set Protocol

## Scope

The existing repeated-operation profiler is the warm baseline. New mixed and
cold diagnostics must be added to `ntruplus-ntt-Optimized/aarch64-bench`, not
to the publishable release.

## Warm

Measure keygen, encapsulation, and decapsulation independently with the current
paired/balanced harness:

```text
31 or 61 samples
2000 calls per sample
100 warmups
core 3 pinned
portable NO_CE on both GT and KPQC
```

## Mixed

Use a deterministic valid sequence:

```text
keygen -> encapsulation -> decapsulation
```

Report both the complete triplet and per-call instrumented variants. The
complete triplet is the primary measurement because per-call PMU
enable/disable overhead can dominate small differences.

Alternate GT/KPQC or candidate/baseline order across samples. Reuse identical
seeds and aligned buffers.

## Cold

Place an instruction-thrash function in the benchmark binary, in its own ELF
section, with a sequential executed span larger than the 64 KiB A76 L1I. Run
it immediately before the target operation.

Report:

```text
thrash-only control
thrash + target total
warm target
```

The total is authoritative. A derived subtraction may be shown as diagnostic,
but not as an exact isolated-kernel PMU count.

## PMU

Collect event groups in separate runs when the hardware counter limit requires
it:

```text
cycles,instructions,branch-misses
L1-icache-load-misses,stalled-cycles-frontend,stalled-cycles-backend
```

Record `time_enabled` and `time_running` if perf multiplexes an event group.

## Result Location

Each run owns one external directory:

```text
ntruplus-ntt-Optimized/aarch64-bench/results/
  gt_production_icache_size_YYYY-MM-DD/
    build.log
    environment.json
    raw/
    summary.json
    summary.md
```

Never write PMU or generated KAT output into `ntruplus-GT-Production`.
