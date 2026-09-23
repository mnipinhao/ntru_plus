# NTRU+768: true-y CT physical replay and two-schedule comparison

This is the next decision gate after the [mixed-gauge tail screen](ntruplus768-mixed-gauge-decision.md). It repairs the physical selective-Barrett control and compares it against mixed gauge at the same BaseMulScale input → Official coefficient output boundary. Both use the true `y=x⁴` twisted CT factor map and the unchanged materialized Official ABI. This gate produces a **complete conservative macro schedule**, not a linked full inverse or measured cycles.

## Why the old control disagreed with Official

The earlier replay chose `ξ = min(leaf set)` and one global `ζ₃₂`. That is valid for an abstract cyclic inverse, but not for the loaded AVX2 order. A physical stage-6 pair can hold `(22, −22)` in one lane and the reversed numerical order in another. The node root is the first **physical upper-child** leaf. At every higher butterfly the actual generator is

```text
ξ = upper-child ξ
ζ = lower-child ξ / upper-child ξ (mod 3457)
twiddle(k) = ζ^(−k)
```

The generator checks that `ζ` has order `2n`, `ζ²` agrees with both child generators, and the two child owner sets are disjoint. It follows the same four route networks as the linked inverse. This fixes the old 21-mismatch witness without adding an output adapter or changing the factor map. The prior stage-5 claim of **10** mixed constant-vector profiles was an artifact of the wrong root choice; the physical schedule has **2** at that stage.

The selective control now replays 101 compiled BaseMulScale outputs, including the old canonical witness, with zero residue mismatches against the linked Official inverse and byte-exact linked `crepmod3`. Its final scale is `R/192 = 2646 (mod q)`; mixed gauge uses `R/48 = 213`. The actual physical mixed-gauge route independently passes the same 101-case inverse/consumer differential. Thus the two sides finally have the same semantic and physical comparison boundary.

## Range closure

The inputs use the proved 768 BaseMulScale cell intervals, not four copies of ±7644. Both schedules include a full-vector `y³²` untwist, even where a lane's factor is one, because that operation is also a representative reduction. The factored radix-3/trinomial tail is the same arithmetic topology with different final-scale constants.

| Maximum absolute bound | Selective Barrett | Mixed gauge |
| --- | ---: | ---: |
| Radix-2 output | 24,856 | 29,708 |
| After mandatory untwist | 2,336 | 2,507 |
| Top pre-operation | 6,907 | 6,703 |
| Final coefficient output | 1,879 | 1,747 |

The selective schedule greedily repairs **12 vector operands entering stage 4 and 12 entering stage 3**. It is a valid complete schedule under these intervals; greedy selection is not a minimality proof. No signed-i16 pre-operation in either modeled schedule exceeds range.

## Matched register, constant and dependency ledger

The comparison uses the same explicit schedule policy: for each radix-2 stage and eight-vector packet, load two butterfly pairs, complete pair 0 and pair 1, route their four outputs, and store back into the existing 1,536-byte buffer. Stage 2 needs no route. The untwist, radix-3 and level-0 phases are separately materialized into that same backing. This makes the whole traversal executable without a new polynomial-sized temporary or cross-function live register requirement; it intentionally does **not** assert that such materialization is fast.

| Per inverse, conservative schedule | Selective Barrett | Mixed gauge |
| --- | ---: | ---: |
| Prefix Montgomery vector operations | 78 | 96 |
| Prefix Barrett vector repairs | 24 | 0 |
| Full/mixed-lane qhalf vector pairs | 0 / 0 | 24 / 24 |
| Common untwist + top Montgomery | 168 | 168 |
| Common top Barrett | 16 | 16 |
| **Total modeled Montgomery / Barrett vectors** | **246 / 40** | **264 / 16** |
| Distinct nonidentity prefix twiddle-vector profiles | 11 | 14 |
| Minimum paired-word prefix table footprint | 704 B | 896 B |
| Prefix paired-word loads, cached within packet / reloaded per multiply | 144 / 156 | 168 / 192 |
| Same conservative data loads / stores, all phases | 384 / 384 | 384 / 384 |
| Same inherited radix-2 route vector pairs | 96 | 96 |

Each twiddle profile needs a constant word and Montgomery companion. The footprint and paired-word load figures are model bounds under the stated packet caching policy, **not** linked `.rodata` bytes or measured load uops. Both sides additionally need the same 48 distinct `y³²` untwist vectors (minimum 3,072 B of paired words); the final-scale words differ. Shared q/v constants, qhalf masks/bias and instruction encoding are not hidden inside the profile count.

The conservative register plan holds four live data vectors per route group. After pair 0, two outputs wait while pair 1 executes. The isolated linked mixed pair used nine YMM names; allowing ten per pair including constant temporaries gives a 12-YMM macro budget with the two pending outputs. The route step holds four outputs plus two temporaries; the tail triplet is budgeted at 12. This is a **bounded macro allocation**. Exact operand def/use, XMM/YMM aliases and spill freedom for the complete linked inverse remain unproved.

The dependency graph is also reported as structural layers, not a latency or cycle model. Through stage 2, the longest selected prefix path has 13 layers for selective repair (up to four Montgomery and one Barrett macro) and 14 for mixed gauge (up to four Montgomery and two qhalf macros). The common untwist → radix-3 → level-0 dependency follows both. Mixed gauge replaces repairs with modular-half dependencies and extra constant multiplication; simply counting 24 fewer Barrett vectors therefore cannot establish a shorter critical path.

## Decision

The repaired selective schedule is now a legitimate control. Under the *same* conservative materialization and routing policy, mixed gauge has no clear structural advantage: it trades 24 prefix Barrett vectors for 18 additional prefix Montgomery vectors, 48 qhalf vector-pair operations, 24 more lower-bound paired twiddle loads and three additional twiddle profiles. The dependency-layer comparison is likewise not favorable to mixed gauge. This **does not prove** selective is faster on AVX2; operation latency, caching and packet interleave still require a linked object and cycles.

If one implementation prototype is opened next, selective repair is the better first choice. It should be realized as a **compact eight-vector packet body**, not the 384-load/384-store conservative schedule used to close this comparison. The gate for serious pricing remains exact linked ≤16-YMM allocation, constant operands, no spill, correctness and full Decap cycles against caller-lazy Official GS. Mixed gauge remains a research control unless a new mechanism removes its qhalf/constant cost or shortens an actual linked dependency chain.

Reproduce from the experiment directory:

```sh
python3 tools/research_physical_true_twist_replay.py
python3 tools/research_mixed_gauge_vector_schedule.py
python3 tools/research_mixed_gauge_full_tail.py
python3 tools/research_true_twist_selective_repair.py
python3 tools/research_true_twist_schedule_comparison.py
```

Machine-readable ledgers are `results/yang-true-y-twist-{selective-repair,mixed-gauge-full-tail,mixed-gauge-vector-schedule,two-schedules}-20260923.json`. No full inverse ASM, Decap cycle benchmark, Native SUPERCOP candidate or clean-production change is claimed.
