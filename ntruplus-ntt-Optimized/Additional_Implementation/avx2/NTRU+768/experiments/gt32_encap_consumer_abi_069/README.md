# GT32-ENCAP-CONSUMER-ABI-069

This gate tests the only scoped reopening premise left by 068: bounded
specialization between a twelve-transition shared core and a 12-KiB fully
inline body.

GT Clean is not modified.  The typed B3-terminal-to-Q24 ABI, arithmetic,
range contract and packet mapping are exactly those qualified by 068.

## Result

Clustered specialization does not break the dispatch/footprint tradeoff.
Cluster-3 and cluster-4 both lose decisively to the 032 reference and are also
slower in paired TSC than the 068 fully-inline body.

```text
typed consumer ABI:             remains correct
cluster-size sweep 2/3/4/6:     complete
cluster-3 executable:           rejected
cluster-4 executable:           rejected
full Encap:                     not run
consumer-ABI campaign:          paused for current AVX2/code-shape family
```

This is not a rejection of the mathematical consumer ABI.  It closes the
current implementation family consisting of shared, fully-inline and simply
clustered copies of the same block DAG.

## Fixed semantics

All candidates preserve the 068 contract:

- ring `Z_3457[x]/(x^768-x^384+1)`;
- general B3 R2-finalized `e=0` plus message Forward `e=0`;
- selected-executable degree bounds `[20215,20250,20285,20296]`;
- exact 768-element B3/M-to-Q24 packet-slot bijection;
- the selected full-signed-int16 Q24 reducer and canonical byte format;
- no complete ordinary 1,536-byte M-domain sum.

Each cluster contains multiple consecutive packet groups.  Its B3 block bodies
and packet consumers are inline within that cluster, while the public entry
performs only one coarse transition per cluster.  No synthetic conversion or
old-Q24 fallback is present.

## Static feasibility sweep

The generator emits cluster sizes 2, 3, 4 and 6.  Static accounting selects
cluster-3 and cluster-4 for cycle adjudication; it is not used as a performance
veto.

| blocks/cluster | transitions | total text | estimated largest cluster | dynamic instructions |
|---:|---:|---:|---:|---:|
| 2 | 6 | 12,317 B | 2,053 B | 2,362 |
| 3 | 4 | 12,167 B | 3,042 B | 2,339 |
| 4 | 3 | 12,177 B | 4,059 B | 2,336 |
| 6 | 2 | 12,101 B | 6,051 B | 2,324 |

All four shapes have:

- 992 bytes of constants;
- 48 Q24 packets;
- 288 counted routing/movement instructions;
- 36 vector scratch stores and 36 reloads;
- zero complete-M YMM stores.

The important static result is that clustering changes the maximum local body
and transition count, but not the roughly 12-KiB total unique text executed by
one complete call.

## Correctness

`make check` passes:

- generator freshness;
- exact object-level shape invariants;
- 1,000 real-Encap operand trials;
- cluster 2/3/4/6 normal equality;
- selected cluster-3/4 reversed-layout equality;
- complete canonical 1,152-byte equality against 032.

## Paired TSC gate

The benchmark uses the same ELF, pins fresh processes to CPU 1, alternates the
six invocation orders and runs 16 launches for normal and reversed physical
cluster ordering.  Negative means faster than the row reference.

| placement | comparison | median TSC | favorable launches | bootstrap 95% CI |
|---|---:|---:|---:|---:|
| normal | 032 - current | -32.50 | 16/16 | [-34.5, -31.5] |
| reversed | 032 - current | -17.75 | 16/16 | [-19.5, -16.0] |
| normal | 068 inline - 032 | +43.00 | 0/16 | [+41.5, +43.5] |
| reversed | 068 inline - 032 | +29.75 | 1/16 | [+28.0, +30.75] |
| normal | cluster-3 - 032 | +50.00 | 0/16 | [+48.25, +51.0] |
| reversed | cluster-3 - 032 | +40.75 | 1/16 | [+38.0, +42.0] |
| normal | cluster-4 - 032 | +51.75 | 0/16 | [+49.5, +53.5] |
| reversed | cluster-4 - 032 | +37.00 | 1/16 | [+35.75, +38.5] |

Cluster-3 is about +7/+11 TSC slower than fully inline; cluster-4 is about
+8.75/+7.25 TSC slower.  Neither approaches the requirement to beat 032 by
5--10 TSC before a full caller gate.

## PMU attribution

Per-call medians use 300,000 iterations and five samples on CPU 1.  Deltas in
the first table are relative to 032.

| metric | cluster-3 | cluster-4 |
|---|---:|---:|
| core cycles | +24.19 | +21.43 |
| instructions | -146.34 | -153.74 |
| L1D loads | -37.96 | -39.99 |
| L1D stores | -48.70 | -49.74 |
| branches | -8.20 | -10.23 |
| IDQ uops not delivered | +111.07 | +113.40 |
| DSB uops | -1726.23 | -1798.78 |
| MITE uops | +1537.39 | +1639.90 |
| port 5/11 uops | -35.07 | -35.23 |

Relative to 068 fully inline, clustering partially changes delivery:

| metric | cluster-3 - inline | cluster-4 - inline |
|---|---:|---:|
| core cycles | -1.63 | -4.39 |
| instructions | +6.90 | -0.50 |
| IDQ uops not delivered | -7.11 | -4.78 |
| DSB uops | +408.08 | +335.53 |
| MITE uops | -426.41 | -323.91 |

The intended mechanism is visible: bounded clusters recover some DSB delivery
and reduce MITE fallback.  The recovery is only 2--4 core cycles, while coarse
transitions/prologues remain and the invocation still traverses about 12 KiB
of unique text.  It cannot repay the 21--24 core-cycle gap to compact 032.

Again, the winner is not predicted by retired work alone: both clustered
variants retire fewer instructions, loads, stores and port-5/11 uops than 032,
but their instruction delivery is much worse.

## Decision and reopening rule

The simple clustering search class is exhausted for scope.  Do not continue
with cluster size 2 or 6, another alignment/padding sweep, or a V2 scheduling
mutation: sizes 3/4 directly test the intended 3--4 KiB middle point and remain
far outside the continuation margin.

The Encap consumer-native ABI campaign is paused.  Reopen only if a new
mechanism reduces the *total unique executed body*, not merely its partition:
for example a genuinely uniform packet microkernel with data-driven routing
that reuses one compact hot DAG without restoring complete-M traffic.  Such a
candidate must first beat 032 by at least 5--10 TSC in this island.

## Reproduction

```sh
make check
make benchmark
```

Committed evidence:

- `generated/candidate_069.s`;
- `generated/shape_sweep.json`;
- `generated/benchmark.json`;
- `generated/pmu.json`.
