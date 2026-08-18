# GT32 P twiddle-major Keygen gate

Experiment: `GT32-P-TWIDDLE-MAJOR-KEYGEN-005`

This experiment jointly scores a compact-S5 P terminal against the complete
successful-attempt Keygen P island. Production and GT Clean are unchanged.

## Correct P baseline

The selected P Forward already leaves S4 in its packed representation:

```text
S4: 4 x 8                         32
S5: 4 x 9                         36
P_PACKED_TO_PLANES: 2 x 16       32
current terminal                 100 / tile
```

The compact twiddle-major candidate is:

```text
S4-native                         32
L4 -> TM network                  24
compact S5 table loads             2
four Montgomery butterflies       24
direct stores                       8
candidate terminal                90 / tile
```

This saves 10 instructions/tile, or 60 instructions/Forward, without changing
the four S5 Montgomery chains.

## Joint consumer result

All 48 legal compact-S5 leaf orders preserve four coefficient planes and a
degree-independent leaf permutation.

- BaseInv closes with batch/lane relabeling of `gt_native_lambda` and
  `gt_native_lambda_qinv`: zero runtime repair.
- F0 x J1 BaseMul uses the same remapped tables: zero runtime repair.
- Direct P-pack closes for all 48 candidates with one 24-instruction
  eight-packet progressive transpose per tile and no global P_TM-to-P pass.

The current SP1 pack needs 13 asymmetric half masks. Every bounded P_TM route
needs 23, so the exact incremental pack debt is 10 instructions/pack. Loads,
stores, reduction, packet arithmetic, and wire bytes are unchanged.

## Successful-Keygen economics

Using the conservative one-attempt-per-polynomial case:

```text
2 x Forward credit     2 x -60 = -120
3 x pack debt           3 x +10 =  +30
BaseInv runtime repair              0
BaseMul runtime repair              0
--------------------------------------
net                               -90 instructions
```

This lands in the predefined `1..16 instructions/pack` assembly-eligible
class. Rejection attempts are deliberately not credited.

## Decision

The generator gate passes. The next bounded executable experiment is a
P_TM Forward terminal plus a direct SP1-like P_TM pack. It must remain outside
GT Clean until exact differential tests and a whole K3-K5 benchmark pass.

## Reproduce

```sh
make check
```
