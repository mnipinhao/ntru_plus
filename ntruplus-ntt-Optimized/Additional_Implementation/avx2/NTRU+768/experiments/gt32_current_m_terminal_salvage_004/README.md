# GT32 current-M terminal salvage

Experiment: `GT32-CURRENT-M-TERMINAL-SALVAGE-004`

This generator-only experiment asks whether the S4-native/compact-S5 result
from 002 can be returned directly to the exact current M ABI. GT Clean,
Q24, B3, callers, and production symbols are unchanged.

## Baseline

Per tile:

```text
S4                 40
S5                 36
PACKED_TO_PLANES   32
total             108
```

Assembly eligibility was fixed at `<=100 instructions/tile`; `<=96` was the
ideal target.

## A — S4-native plus existing S5

An exact BFS proves that each S4-native SUM/DIFF pair still needs two paired
physical operations to become the current S5 low/high operands:

```text
2 x vperm2i128
2 x vpunpck{l,h}qdq
= 4 instructions/pair
```

Across four pairs this is 16 instructions/tile—the same combined physical
work currently split between S4 repair and S5 input formation.

The only static saving is that the S5 difference can target the now-dead input
register directly, eliminating one final `vmovdqa` per pair:

```text
S4-native                    32
S4N -> existing S5 operands  16
S5 arithmetic/direct dest    24
PACKED_TO_PLANES/stores       32
total                        104
```

This is a real `-4/tile`, or `-24 instructions/Forward`, but it does not meet
the promotion margin.

## B — PACKED4 / QPAIR02 ownership

The alternate pair ownership does not remove either required physical
dimension: S4-native half ownership and S5 qword ownership. It realizes the
same 16-instruction operand route and the same four direct-destination move
deletions. Best total remains 104/tile.

## C — compact S5 to exact current M

For all 48 legal 24-instruction compact-S5 terminal orders, the generator
searches the exact postroute back to current M:

| Postroute cost/tile | Terminal orders |
|---:|---:|
| 24 | 4 |
| 32 | 20 |
| 40 | 24 |

The best sequential exact-M compact path is therefore:

```text
S4-native                    32
L4N -> compact L/H           24
constant loads                2
S5 arithmetic                24
exact-current-M postroute    24
stores                         8
total                        114
```

It loses statically to both production and A/B.

## Decision

```text
Best exact-current-M result: 104/tile
Saving:                      4/tile = 24/Forward
Assembly threshold:          <=100/tile
Decision:                    stop before assembly
```

This closes the straightforward current-M salvage schedules, not every
possible nonuniform cross-pair schedule. Reopen only if a joint schedule can
remove at least four additional instructions/tile, a consumer absorbs the
remaining deposit, or the output ABI changes.

## Reproduce

```sh
make check
```

