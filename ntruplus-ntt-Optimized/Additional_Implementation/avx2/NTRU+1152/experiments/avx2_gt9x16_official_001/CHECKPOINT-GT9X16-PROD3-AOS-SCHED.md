# GT9X16-PROD3-AOS-SCHED

## Scope and result

This checkpoint answers only whether the existing top-split AoS representation
can remain live through complete NTT9 and NTT16 distance 8/4, followed by one
exact D2/D1-to-MA2 conversion boundary.

It does not interleave the 9/16 axes, absorb twist factors, write assembly, or
run a benchmark. Official remains the performance control only.

The selected static network is `C1_live_d1_to_transpose`. Relative to the
current G0/P2-B physical realization, its complete post-top-split ledger is:

| dynamic class / forward | G0/P2-B | AoS C1 | delta |
| --- | ---: | ---: | ---: |
| data loads | 288 | 216 | -72 |
| data stores | 216 | 216 | 0 |
| routing instructions | 936 | 432 | -504 |
| Montgomery chains | 296 | 296 | 0 |
| Barrett vectors | 72 | 72 | 0 |

These are static schedule counts, not cycle estimates. Constant-memory
operands remain excluded until an actual register allocation exists.

## Step A: complete AoS NTT9

One AoS YMM contains four q cells and all four terminal coefficients:

```text
[q0j0 q0j1 q0j2 q0j3 ... q3j0 q3j1 q3j2 q3j3]
```

For a fixed branch and q block, all 16 lanes consume identical radix-3
constants. Therefore `PAPER_R2_CACHED_STREAM` applies without a lane route.
Across two branches and four q blocks:

| item | count |
| --- | ---: |
| AoS NTT9 vector streams | 8 |
| radix-3 vector butterflies | 48 |
| Montgomery chains | 80 |
| Barrett vectors | 72 |
| data loads / stores | 144 / 144 |
| routing | 0 |
| peak YMM | 15 |

The existing complete-NTT9 materialization remains: round 1 writes 72 AoS
vectors, round 2 reloads and overwrites them. Cross-axis wavefront scheduling
is explicitly deferred.

## Step B: AoS D8 and D4

After NTT9, each physical P tile owns four AoS vectors:

```text
V0=q0..q3  V1=q4..q7  V2=q8..q11  V3=q12..q15.
```

D8 consumes `(V0,V2)` and `(V1,V3)`. D4 then consumes `(V0,V1)` and
`(V2,V3)`. Both are vector-to-vector butterflies and require zero routing.
Across 18 `(branch,physical-P)` tiles, each stage uses 36 Montgomery chains.

The generated range ledger reuses the exact paper-R2 and adjusted-NTT16
representatives, not only their residues. Every recorded D8/D4/D2/D1
preoperation remains signed-i16 safe; no reduction is added.

## Step C: exact D2/D1-to-MA2 networks

### C0: materialized post-D1 control

Per tile:

```text
D2: 4 x vperm2i128
D1: 4 x vpunpck{l,h}qdq
store/reload: 4 + 4 vectors
transpose:
  4 x vpunpck{l,h}wd
  4 x vpunpck{l,h}dq
  4 x vpunpck{l,h}qdq
  4 x vpermq
```

The route total is 24 per tile, or 432 per forward, plus 72 stores and 72
reloads at the artificial D1 boundary.

### C1: live D1 into hierarchical transpose

C1 has the same arithmetic and 24 routes per tile, but the D1 sum/difference
registers directly feed the first `vpunpckwd` layer. It removes all 144 C0
boundary memory operations and needs no extra temporary array.

The generator simulates the exact AVX2 half/unpack/permute network. It proves:

- 576 distance-2 scalar lane pairs, each pairing identical `j` and q distance 2;
- 576 distance-1 scalar lane pairs, each pairing identical `j` and q distance 1;
- all 1,152 outputs land in exact MA2 coefficient planes and physical Q order.

C1 is selected.

### C2: early coefficient-plane orientation

C2 performs a hierarchical transpose immediately after D4. With contiguous
four-q input blocks the natural q order is:

```text
0,4,1,5,2,6,3,7,8,12,9,13,10,14,11,15
```

It therefore needs four additional lane-local `vpshufb` operations to reach
the frozen MA2 Q order. Reusing the already proved SoA `ROUTE2`, `ROUTE1`, and
terminal reconstruction primitives gives:

| per tile | routes |
| --- | ---: |
| hierarchical transpose and q reorder | 20 |
| SoA D2 | 8 |
| SoA D1 | 8 |
| plane reconstruction | 8 |
| total | 44 |

That is 792 routes per forward, so C2 is rejected statically.

## Step D: twist is kept independent

T0 retains the current 72 pre-twist Montgomery chains.

The existing separability proof makes both later searches legal:

```text
T1: h factor -> NTT9 constants
T2: q factor -> adjusted NTT16 constants
```

Neither is assigned credit. A candidate must prove that one multiplication is
actually removed after combined-constant, factor, scale, and range accounting.
Merely moving a multiply into the radix routine is not a chain reduction.

## Register and storage plan

- NTT9 reuses the proved peak of 15 YMM registers.
- AoS D8/D4/D2/D1 plus the C1 transpose has an explicit upper bound of 11 YMM.
- Phasewise peak is therefore 15 YMM, with a zero-spill target.
- The 2,304-byte top-split array and existing 2,304-byte output backing are
  sufficient; extra temporary storage is zero.

## Decision

The static schedule is complete and C1 is the recommended realization. The
next narrowly scoped checkpoint would be `GT9X16-PROD3-AOS-ASM0`: one
branch/one physical-P tile proving AoS paper-R2, D8/D4, and live C1 D2/D1 to
MA2 planes.

That assembly is not authorized by this checkpoint. Full-producer assembly,
twist absorption, cross-axis scheduling, performance measurement, and native
KEM remain closed.

Machine-readable evidence is in
`generated/gt9x16-prod3-aos-schedule.json`; regeneration and lane-network gates
are in `tests/test_gt9x16_prod3_aos_schedule.py`.
