# Checkpoint G1C-M3C2: minimum repair and AVX2 set cover

M3C2 follows the negative M3C0 orientation result. It keeps the current exact
inverse factorization and evaluates four D8 input actions on the same 10,003
real-producer cases:

```text
none
reduce left
reduce right
reduce both
```

This checkpoint selects a repair shape. It does not prove that shape for every
possible producer input, choose a reduction primitive, write assembly, or
measure cycles.

## Logical result

The probe evaluates all 576 `branch × row × coefficient × D8-pair` nodes.
Thirty-seven nodes have a concrete no-repair overflow. Every one is pair 0,
physical lanes `(0,8)`, and every one is safe in the fixed corpus when either
the left input alone or the right input alone is centered. No node requires
both inputs to be reduced.

Across the complete corpus, the maximum pre-Montgomery absolute sum/difference
is:

| action | maximum |
| --- | ---: |
| none | 45,358 |
| reduce left | 31,628 |
| reduce right | 31,439 |
| reduce both | 3,456 |

The scalar logical minimum is therefore 37 reductions per inverse16 call.
This remains corpus evidence. In particular, `31,628 < 32,768` is not an
exact producer-correlated bound.

## AVX2 projection

Each affected logical node belongs to a different terminal YMM vector. Three
constant-time realizations are retained:

| realization | abstract reduction chains | routes | scope |
| --- | ---: | ---: | --- |
| selective full YMM | 37 | 0 | both halves of each affected vector |
| adjacent-row half packing | 22 | 30 | 15 packed row pairs plus 7 full vectors |
| full D4 control | 72 | 0 | all 1,152 D4 values |

The half-packing set cover uses one YMM repair chain for one selected 128-bit
half from each of two physical-adjacent rows. It minimizes chains, then routes,
then repaired halves. These are abstract scheduling units, not instruction or
cycle counts. Signed Barrett and Montgomery-by-identity remain unpriced.

Qword/lane-selective repair is not selected yet. Computing a whole YMM reducer
and blending a few lanes is dominated by the listed covers unless an actual
packing schedule demonstrates otherwise.

## Decision

M3C2 selects pair-0 one-sided repair with adjacent-row half packing as the
lowest-chain research candidate, but its safety proof is open. Assembly
remains forbidden. The next checkpoint is M3C2-P: prove the selected repair
cover against the full producer domain, or expand it conservatively where the
proof fails. M3C3 then implements/prices the full-reduction control and the two
reduction primitives before M3 C0/C1/C2 timing begins.

The machine-readable evidence is:

- `results/g1c-m3c2-repair-20260823-001/repair-observation.json`
- `generated/g1c-m3c2-repair-plan.json`
