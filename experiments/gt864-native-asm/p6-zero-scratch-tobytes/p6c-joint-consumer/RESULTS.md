# P6-C — joint packed-A consumer gate

P6-C passes the architectural feasibility gate. It does **not** yet replace
production ToBytes: it proves the exact packed-A producer and the worst first
row of the joint restore-A/B plus three-pair merge can coexist within the 32
Neon-register limit without coefficient scratch or lane `ST3`.

## What changed from P6-B

P6-B checked route and normalization frontiers separately. P6-C makes their
shared state concrete:

- pair 0 and pair 1 occupy 13 retained Q registers as dense byte streams;
- pair-2 A is canonicalized first and stored in an exact 108-byte, seven-Q
  12-bit representation;
- the nine pair-2 B vectors are then loaded and consumed one physical row at a
  time;
- the current merge table is used directly for pair 0 and pair 2, while the
  pair-1 indices receive a compile-time `+8` adjustment because its stream
  begins in the upper half of the overlapping `{Q0,Q1}` / `{Q1,Q2}` group;
- each loaded index vector becomes its own `TBL` destination, avoiding a
  separate index lifetime;
- each 72-byte row is emitted as four `STR Q` plus one `STR D`. Across one top,
  the target store shape is 40 `STR Q` plus one `STR D`, with no lane `ST3`.

## Exact register frontier

The original row0 infeasibility was traced to a symbolic-name discontinuity:
loads still defined `Q<A0>...Q<A6>`, while their consumers used
`V<packed0>...V<packed6>`. That created seven dead loads and seven false
live-ins. After repairing the definitions, both regions have an empty live-in
set beyond their explicit memory inputs.

| Region | Semantic instructions | Reverse-liveness peak | Slothy result | A76 modeled cycles |
|---|---:|---:|---|---:|
| canonicalize and pack pair-2 A | 179 | 26 vectors | OPTIMAL, no spill | 45 |
| normalize B0 and merge row0 | 118 | 32 vectors | OPTIMAL, no spill | 30 |

At the row0 peak, the 32 values are: 13 saved-pair vectors, seven packed-A
vectors, eight future B vectors, two pair-2 source vectors, and two merge
temporaries. Constants have already died. This is exact capacity, not spare
capacity; P6-D must not lengthen any of these lifetimes.

## Physical-register and executable checks

The allocation used `/Users/chenpinhao/slothy` with the Cortex-A76 target and
spills disabled. All 15 physical table operations meet the architectural source
group rule:

- ten TBL2 operations use overlapping consecutive groups, currently
  `{v5,v6}` and `{v6,v7}`;
- five TBL3 operations use `{v12,v13,v14}`;
- neither region contains stack memory, `x18`, `x29`, `x30`, or unresolved
  symbolic registers. `x30` is explicitly reserved because a first rerun
  assigned the scalar constant temporary to `w30`, destroying the callable
  leaf's link register; the executable oracle correctly rejected that build.

Both allocated regions assemble with Apple clang. A test-only outer wrapper
saves the callee-saved GPRs selected by allocation and `d8-d15`; this cost is
not charged once per row in the intended kernel, because the production design
will pay public ABI preservation once around the complete ToBytes call.

The physical assembly oracle passed:

- 12,288 packed-A cases, including exhaustive signed-int16 blocks and 4,096
  random vectors;
- 4,096 joint row cases against the scalar canonicalization, exact 12-bit pair
  packing, and production byte-merge mapping;
- byte-exact 72-byte output and preservation of every state item needed by
  later rows.

The independent Python model also passed 4,096 random three-pair rows, all 15
merge indices, the physical row order `[0,3,6,1,4,7,2,5,8]`, and the final
648-byte store decomposition.

## Decision and next gate

P6-C is accepted as a feasibility result. Production remains P5 ToBytes with
432-byte wiped scratch; there is no Pi 5 or full-KEM claim from this partial
kernel.

P6-D must materialize both complete full and small paths across all nine rows,
including the 28 GPR-resident D chunks, cross-row reconstruction/carry, one
outer AAPCS wrapper, and final direct stores. It must pass byte-exact complete
ToBytes tests, alias/canary/cleanup policy, no-spill allocation windows, and
only then Pi 5 paired ToBytes plus full-KEM timing.
