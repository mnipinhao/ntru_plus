# H4-M2B exact terminal-to-wire ownership search

> **Rejected by H4-M2D.** This checkpoint treated
> `serialized_coefficient` as the semantic wire key. Direct replay against
> Official physical coefficient order finds 1134 mismatches in 1152 cells.
> None of its pair-locality or staging conclusions authorizes ASM.

## Outcome

This checkpoint rebuilds the H4 serializer graph with `wire_coefficient` as
the primary key.  `official_physical_coefficient` is retained only as metadata.
This distinction resolves the first H4-M3 ASM failure:

```text
wire coefficient 0 = physical coefficient 0  = vector 20 lane 15
wire coefficient 1 = physical coefficient 16 = vector 21 lane 15
physical coefficient 1 = wire coefficient 8  = vector 20 lane 14
```

Therefore the failed ASM did not disprove M2's same-lane cross-plane model.
It disproved a helper that paired adjacent physical coefficient IDs.

## Exact graph

The generated artifact contains all 1152 cells from semantic/wire identity
through terminal hook, YMM/lane, canonical scratch cell, wire-pair role, and
final byte ownership.  It proves a bijection over both the 1152 terminal cells
and 1728 output bytes.

The 576 true wire pairs classify as:

| class | count |
| --- | ---: |
| same terminal vector | 0 |
| same lane, cross terminal vector | 576 |
| different lane, cross terminal vector | 0 |
| adjacent terminal hooks | 576 |
| same tile | 576 |

The exact pending-state replay reaches 16 wire pairs after the low endpoint
hook and returns to zero after the immediately following high endpoint hook.
The semantic minimum remains one YMM.

## Evidence correction

The following M1 results survive exact remapping:

- 576/576 adjacent-vector same-lane wire pairs;
- zero pre-pair routing;
- 16-coefficient / one-YMM semantic pending bound;
- the four terminal-lane presentation profiles.

The four-instruction primitive remains valid when applied to the two adjacent
terminal vectors:

```text
vpunpcklwd / vpunpckhwd
vpmaddwd with [1,4096]
```

The 1502-instruction Natural-Q S2 result remains a symbolic schedule estimate.
It is neither rejected nor machine-validated.  Its exact wire-keyed lowering
must be regenerated before ASM or timing.

## Zero-route store permutation

Reassigning the 72 scratch vector destination slots cannot improve Natural-Q's
512 parity-stream runs: no Natural-Q vector-pair bundle ends at a wire-pair ID
whose stride-two successor starts another bundle.  Identity storage is thus an
exact zero-route optimum for that profile.

The joint frontier is:

| presentation | terminal routes | pair routes | best pair runs after free vector-store ordering |
| --- | ---: | ---: | ---: |
| Natural-Q identity | 0 | 0 | 512 |
| bitperm xor-6 | 72 | 0 | 492 |
| bitperm 0321 xor-e | 144 | 0 | 376 |
| tile-specific serializer-sorted | 216 | 0 | 2 |

The last profile improves from 36 to two runs using a zero-route two-path
bundle-store order, but still pays 216 terminal lane routes.  It remains a
Pareto control, not the selected next schedule.

## Decision

Natural-Q is selected for the next exact schedule because it preserves the
frozen zero-route terminal and all 576 same-lane wire pairs.  No ASM or
benchmark is authorized here.

Next:

```text
canonical Natural-Q scale-1 scratch
→ wire-ID-keyed cross-vector pair32 formation
→ exact 24-bit compaction
→ 1728 bytes
```

Every generated table and lowering must use `wire_coefficient` as its primary
key.  The current H1-based H4-M3 leaf remains the correctness oracle.
