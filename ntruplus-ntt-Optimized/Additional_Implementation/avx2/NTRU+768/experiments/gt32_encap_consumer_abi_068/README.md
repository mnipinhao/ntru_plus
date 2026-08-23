# GT32-ENCAP-CONSUMER-ABI-068

This experiment asks whether the B3 terminal representation can become a
Q24-consumer-native packet state, eliminating the complete ordinary M-domain
sum that remains in experiment 032.

GT Clean is not modified.  The experiment is a directional architecture gate,
not a production or full-Encap promotion gate.

## Result

The typed mapping and arithmetic are correct, but both tested executable
retirement shapes lose to the 032 reference:

```text
current:    B3 -> full M -> poly_add -> full M sum -> Q24
032:        B3 finalizer + m -> full M sum -> Q24
068:        B3 finalizer + m -> packet state -> Q24 bytes
                                      (no complete M sum)
```

The shared-core 068 shape loses by 48--49 TSC to 032.  A second, fully inline
mutation removes the twelve call/return trips and cuts the loss to 28--31 TSC,
but still loses decisively.  No full Encap run was made because the
predeclared island continuation gate failed.

Decision:

```text
mapping / typed ABI:                       PASS
shared-core direct retirement:            REJECTED
fully-inline direct retirement:           REJECTED
whole B3-to-Q24 consumer-ABI family:       OPEN only with a new shape premise
032 B3-final-store add(m):                 remains the local reference champion
GT Clean production:                      unchanged
```

## Exact packet mapping

`tools/generate_mapping.py` derives the mapping from the selected `pack.s`
routing rather than maintaining a handwritten permutation.  For the selected
M layout:

```text
block = tile*2 + q4
tile  = 2*k3 + branch
lane bits [0,1,2,3] carry logical Q bits [2,3,0,1]
logical k32 = bitreverse5(Q)
```

All 768 source words map bijectively to the 768 serialized coefficient slots.
Each group of four Q24 packets depends on exactly one 128-byte B3 block.  The
twelve execution groups retire blocks in this order:

```text
0, 1, 9, 8, 4, 5, 11, 10, 6, 7, 3, 2
```

The complete row-level oracle is committed as `generated/mapping.csv`; the
typed group metadata and derivation are in `generated/mapping.json`.

## Six-column seam contract

| Column | Contract |
|---|---|
| ring | `Z_3457[x]/(x^768-x^384+1)` |
| representation | general B3 R2-finalized `e=0` plus message Forward `e=0` |
| layout | four M degree-plane YMMs for one 16-leaf block at retirement |
| scale | `e=0` |
| bound | per degree `[20215, 20250, 20285, 20296]`; maximum 20296 |
| consumer | the exact reducer/packetizer for 48 canonical Q24 packets |

The bound comes from the selected-executable proof in 032.  The selected
`v=9` Q24 reducer was exhaustively qualified over the full signed-int16 domain
by 032R.  This experiment does not restore the stale 12699 range assumption
and does not add a reduction checkpoint.

## Implemented shapes

### V1: shared B3 block core

Each Q24 group calls a reusable block core that performs the current B3
arithmetic, R2 finalization, message addition, M-to-packet transpose, reduction
and packing.  It never stores or reloads a complete M sum.

This keeps static code at 4,342 bytes, but dynamically executes twelve direct
call/return pairs and repeatedly crosses between the packet body and shared
core.

### V2: fully inline block retirement

The plausible mode-preserving mutation inlines all twelve block computations
in packet order.  It eliminates the call/return dispatch and pointer setup at
each group.  It also avoids a complete M sum, but grows the active symbol to
12,034 bytes.

Both variants use only the existing 96-byte raw B3 `c0/c1/c2` scratch.  Neither
stores a full 1,536-byte result polynomial.

Relative to 032, the direct packet retirement deletes at least:

- 48 final-sum YMM stores;
- 48 Q24 input YMM loads;
- 3,072 bytes of vector traffic.

It retains the 48 message loads/adds, the Q24 reduction and pack arithmetic,
and the 144-instruction four-plane transpose network.

## Correctness

`make check` passes:

- exact 768-slot mapping bijection;
- generator freshness checks;
- 1,000 deterministic real-Encap operand trials;
- control, 032, V1 and V2 byte-exact equality;
- normal and reversed implementations;
- static proof that V1/V2 have no complete-M output stores.

The executable endpoint is the complete canonical 1,152-byte Q24 stream, not
an internal modulo-q checkpoint.

## Paired TSC result

The directional gate pins fresh processes to CPU 1, alternates invocation
order, and uses 16 launches for each independently emitted normal/reversed
body.  Negative means the row candidate is faster.

| placement | comparison | median TSC | favorable launches | bootstrap 95% CI |
|---|---:|---:|---:|---:|
| normal | 032 - current | -19.75 | 16/16 | [-24.0, -17.5] |
| reversed | 032 - current | -22.25 | 16/16 | [-24.0, -19.0] |
| normal | V1 shared - 032 | +48.50 | 0/16 | [+47.5, +51.0] |
| reversed | V1 shared - 032 | +49.25 | 0/16 | [+47.0, +51.5] |
| normal | V2 inline - 032 | +27.50 | 1/16 | [+26.5, +30.0] |
| reversed | V2 inline - 032 | +30.50 | 0/16 | [+27.5, +33.5] |

Thus V2 is only about +7.8/+8.3 TSC slower than the original current path,
but it does not beat the stronger and already-qualified 032 reference.

## PMU attribution

The table reports per-call medians and deltas relative to 032.  The PMU run is
300,000 iterations per sample and five samples on CPU 1.

| metric | 032 | V1 shared delta | V2 inline delta |
|---|---:|---:|---:|
| core cycles | 804.00 | +20.18 | +5.21 |
| instructions | 2498.81 | -125.67 | -150.04 |
| L1D loads | 553.92 | -30.53 | -42.61 |
| L1D stores | 187.30 | -39.73 | -51.88 |
| branches | 19.39 | +9.00 | -15.25 |
| IDQ uops not delivered | 10.69 | +81.03 | +117.06 |
| DSB uops | 2500.30 | -66.38 | -2138.39 |
| MITE uops | 50.64 | -48.68 | +1971.71 |
| port 5/11 uops | 586.99 | -22.94 | -38.41 |

V1 proves that the deleted memory and arithmetic work is outweighed by
frontend starvation from the twelve shared-core transitions.  V2 removes that
dispatch cost, but its 12-KiB active body is delivered predominantly through
MITE and remains frontend-starved.  The loss is therefore not predicted by
retired instruction count: V2 retires about 150 fewer instructions and uses
about 43/52 fewer loads/stores than 032, yet takes more cycles.

## Scope and reopening rule

068 closes only these two direct-retirement implementations:

1. a compact packet body that repeatedly calls a distant shared B3 core;
2. a fully unrolled packet-order B3/Q24 body.

It does not prove that a B3-to-Q24 consumer ABI is universally impossible.
Reopen only with a new mechanism that breaks the observed dispatch/footprint
tradeoff—for example, a compact uniform packet consumer that can reuse a hot
block body without twelve long-range transitions and without materializing a
complete M polynomial.  Alignment, padding, register-allocation, or another
equivalent scheduling sweep is not a sufficient new premise.

Experiment 069 subsequently tests the bounded 3/4-block clustering premise.
It recovers only 2--4 core cycles of frontend delivery versus fully inline and
remains 21--24 core cycles slower than 032.  The shared/full-inline search
class described here is therefore exhausted; use 069 for the campaign-level
pause and reopening rule.

## Reproduction

```sh
make check
make benchmark
```

Evidence is stored in:

- `generated/mapping.json` and `generated/mapping.csv`;
- `generated/candidate_068.s`;
- `generated/benchmark.json`;
- `generated/pmu.json`;
- `generated/static_audit.json`.
