# Whole-caller delivery attribution and benchmark policy

## What Normal and Reversed mean

They are not two algorithms and do not use different inputs.  They are two
links of the same sources with the link inputs reversed:

- **Normal:** benchmark and GT32 objects are presented to the linker first;
  Official objects follow.
- **Reversed:** Official objects are presented first; benchmark and GT32
  objects follow.

This changes `.text` addresses, relative distance, alignment and front-end
set mapping.  It does not change the arithmetic, polynomial layout, constants
or KEM semantics.  For example, the Q24 body moves from `0x26b40` to
`0x16860`, the B3-to-M body from `0x161a0` to `0x2e1e0`, and the global
inverse from `0x8ea0` to `0x3c340`.

Normal/Reversed are therefore an attribution stress test, not two candidates
that a production selector may choose between.  A result that wins only one
placement is evidence of an address/code-layout-sensitive delivery problem.

## Why the whole-caller result changes

The opt-in global-inverse edge performs less intrinsic work in both links:

| delta per complete decapsulation | Normal | Reversed |
| --- | ---: | ---: |
| retired instructions | -261.000 | -261.000 |
| retired loads | -40.999 | -40.999 |
| retired stores | -42.000 | -42.000 |

The reduction is structural.  B3 emits the internal M layout and the new
inverse consumes M directly, progressively returning to the existing AoS T9
entry.  The old B3-to-AoS plus I1 boundary is not executed.

This intrinsic saving is not delivered identically after linking.  A paired
front-end PMU gate found very different decoded-uop delivery mixtures:

| candidate minus current, per call | Normal | Reversed |
| --- | ---: | ---: |
| `idq.dsb_uops` | +2940.084 | +634.658 |
| `idq.mite_uops` | -678.510 | +134.509 |
| `idq_uops_not_delivered.core` | -380.307 | -202.340 |

By contrast, measured `icache_data.stalls` and completed iTLB walks differ by
far below one event per call.  The evidence therefore does **not** support a
classic L1I-miss or iTLB-miss explanation.  It supports a broader instruction
front-end delivery attribution: reversing the link remaps the Q24, B3,
inverse, T9, caller and shared KEM/hash code and changes how the decoded-uop
cache (DSB) and legacy decode path (MITE) supply the caller.

This does not uniquely prove one particular DSB set collision.  The proven
facts are narrower:

1. arithmetic and memory-work savings are stable;
2. hot-code addresses and adjacency change substantially;
3. the DSB/MITE delivery mix changes substantially;
4. ordinary L1I/iTLB miss counts are too small to explain the difference;
5. full-caller cycle delivery consequently changes with link layout.

The 100k paired diagnostic gate reflects this: the new edge saves 176.994
core cycles/call in Normal but 49.445 in Reversed relative to the current Q24
GT caller, even though both retire the same 261 fewer instructions.

## Why decapsulation can beat Official

The global-inverse candidate combines already qualified GT-native boundaries
with a cheaper first-product consumer edge:

```text
Q24 GT-unpack(c,f)
  -> private SoA B3 producing M
  -> global inverse consuming M
  -> existing T9 / crepmod3
  -> existing GT-native recovered-r and check packing
```

This removes about 261 instructions, 41 loads and 42 stores from the current
GT decapsulation.  In a favorable whole-binary layout those savings are large
enough to pay the remaining GT-vs-Official boundary/critical-path debt.  The
100k diagnostic comparison therefore records `-89.297` TSC/call versus
Official in Reversed.

It is not yet correct to say that GT decapsulation unconditionally beats
Official.  The same source is `+33.689` TSC/call behind Official in Normal.
The precise statement is:

> GT32 now has enough intrinsic decapsulation work reduction to beat Official
> in a favorable code layout, but has not demonstrated a placement-stable
> production win.

## Required benchmark method from this point forward

Formal KEM performance claims must use the method in
`/home/nuc/supercop-20260627`, specifically `crypto_kem/measure.c` and the
selected `cpucycles` implementation.

On this host, the existing SUPERcop result records:

```text
cpucycles_implementation default-perfevent
cpucycles_persecond 4500000000
```

The required procedure is:

1. Build Official and the opt-in GT candidate as separate SUPERcop
   implementations with the same compiler flags and dependency set.
2. Use aligned allocations as SUPERcop does.
3. For each operation and each loop, collect 33 consecutive `cpucycles()`
   timestamps around 33 executions and form the 32 adjacent single-operation
   differences.
4. Report SUPERcop's stabilized second quartile (`stq2_longlong`) and retain
   the encoded raw deviations.
5. Benchmark `keypair`, `enc` and `dec` separately through the public KEM API.
6. Preserve randombytes accounting and correctness checks.
7. Treat PMU region counters as attribution only, not as the headline KEM
   benchmark.

The old Normal/Reversed, batched-100k, paired AB/BA harness remains useful for
diagnosing code-layout sensitivity.  It is no longer the promotion benchmark
and its TSC values must not be mixed with SUPERcop cycle results.
