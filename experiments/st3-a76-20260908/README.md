# Cortex-A76 store microbenchmark (Pi 5)

Experiment ID: `st3-a76-20260908`

## Host and method

- Host: Raspberry Pi 5, Cortex-A76 r4p1, four cores
- Kernel: Linux `6.18.33+rpt-rpi-2712`
- Compiler: GCC `14.2.0`
- PMU: Linux perf `6.18.33`
- CPU policy: boost disabled, maximum frequency 2.4 GHz
- Affinity: `taskset -c 3`
- Samples: `perf stat -r 11 -e cycles,instructions`
- Working allocation: 16 KiB, prefaulted and best-effort `mlock`
- Inner footprint: at most 1536 bytes, rewound after each unrolled loop
- Work per process: 10,000,000 logical 48-byte output groups
- Store sources are register-resident; each assembly loop is warmed before the
  measured invocation.

The reported `perf stat -r` central value is the mean. The percentage printed
by perf is its run-to-run variability measure.

## Results

The U=32 result is used for the main comparison. Store-instruction counts below
exclude loop/control and process instructions; cycles are the process PMU count,
whose fixed overhead is negligible at these iteration counts.

| sequence for 48 bytes | store instructions / 48B | cycles / store instruction | cycles / 48B | perf variability |
|---|---:|---:|---:|---:|
| `st3 {v0.8h-v2.8h}` | 1 | 3.2816 | 3.2816 | 0.18% |
| eight `st3 {v0.h-v2.h}[lane]` | 8 | 2.0163 | 16.1305 | 0.01% |
| 24 `st1 {vN.h}[lane]` | 24 | 1.0723 | 25.7351 | 0.00% |
| three `str qN` | 3 | 1.0416 | 3.1249 | 0.61% |

The equal-work lane result is directly measured as an eight-lane sequence; it
is not computed by assuming eight isolated lane-store latencies.

### Unroll convergence

| sequence | U=8 cycles/48B | U=16 cycles/48B | U=32 cycles/48B |
|---|---:|---:|---:|
| full `ST3` | 3.2620 | 3.2748 | 3.2816 |
| lane `ST3` x8 | 16.1865 | 16.1367 | 16.1305 |
| lane `ST1` x24 | 25.6776 | 25.6944 | 25.7351 |
| `STR Q` x3 | 3.1767 | 3.2030 | 3.1249 |

The U=8/16/32 sweep shows that loop branch and rewind overhead do not explain
the instruction-family ranking.

## Representative U=32 PMU check

This was a separate seven-repeat run with
`cycles,instructions,stall_backend,l1d_cache_refill_wr`.

| sequence | cycles / 48B | backend stalls | L1D write refills |
|---|---:|---:|---:|
| full `ST3` | 3.2824 | 1,805,188 | 777 |
| lane `ST3` x8 | 16.1352 | 182,257 | 803 |
| lane `ST1` x24 | 25.7351 | 219,953 | 797 |
| `STR Q` x3 | 3.1250 | 898,871 | 792 |

The roughly 800 L1D write refills over 10,000,000 repeated 48-byte groups are
consistent with an L1-resident microbenchmark, not a DRAM bandwidth benchmark.
`stall_backend` is recorded as supporting evidence but is not by itself a
pipeline attribution: the event counts stall cycles, not a uniquely identified
store-pipeline cause.

## Reproduction shape

The benchmark sources and binaries were temporary artifacts under
`/tmp/st3-a76-20260908` on both the development host and Pi 5. The key command
for each case was:

```sh
perf stat -x, -r 11 -e cycles,instructions \
  taskset -c 3 ./st3_bench TEST OUTER_ITERATIONS
```

Each assembly function used U=8, 16, or 32 copies of its 48-byte sequence,
post-indexed addresses, a pointer rewind, `subs`, and `b.ne`. `OUTER_ITERATIONS`
was selected so every case performed 10,000,000 48-byte sequences.

## Decision

For an NTRU+ layout that permits all choices, prefer three full-vector `STR Q`
stores or one full-vector `ST3`; they are close, with `STR Q` about 4.8% lower
in this isolated test. Do not model lane `ST3` as three cycles per instruction:
the measured reciprocal throughput is about 2.02 cycles/instruction. However,
serializing 48 bytes with eight lane `ST3` instructions costs about 4.91 times
one full `ST3`, while 24 lane `ST1` instructions cost about 7.84 times one full
`ST3`.

Classification: `accept` as Cortex-A76 microarchitectural evidence. This does
not replace an end-to-end NTRU+ benchmark when choosing a transpose-plus-full-
store implementation, because the required transpose instructions and live-
register pressure are absent here.
