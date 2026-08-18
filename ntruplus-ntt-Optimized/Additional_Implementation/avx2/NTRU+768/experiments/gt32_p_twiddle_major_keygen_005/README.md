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

## Corrected joint consumer result

All 48 legal compact-S5 leaf orders preserve four coefficient planes and a
degree-independent leaf permutation.

- BaseInv closes with batch/lane relabeling of `gt_native_lambda` and
  `gt_native_lambda_qinv`: zero runtime repair.
- F0 x J1 BaseMul uses the same remapped tables: zero runtime repair.
- None of the 48 candidates closes the existing 24-instruction/tile direct
  P-pack route.

The exact P_TM-to-P adapter distribution is:

```text
2 candidates      48 instructions / polynomial
8 candidates      96 instructions / polynomial
22 candidates    144 instructions / polynomial
16 candidates    192 instructions / polynomial
```

The best adapter is one 2-instruction qword-unpack operation per degree and
tile: `2 x 4 degrees x 6 tiles = 48`. The uniform direct route family also
cannot add less than its next 8-instruction/tile layer, which is the same
48-instruction/polynomial lower bound.

## Successful-Keygen economics

Using the conservative one-attempt-per-polynomial case:

```text
2 x Forward credit     2 x -60 = -120
3 x pack debt           3 x +48 = +144
BaseInv runtime repair              0
BaseMul runtime repair              0
--------------------------------------
net                               +24 instructions
```

This lands in the predefined `>=40 instructions/pack` hard-stop class.
Rejection attempts are deliberately not credited.

## Executable audit and model correction

The first generator revision reused experiment 002's pre-S4 M token state and
incorrectly reported a 10-instruction pack debt. A diagnostic Forward emitted
from that model failed the exact differential at trial 0.

The P path is different: `P_MONT_HALF_PACKED` performs its half selection
inside S4. The corrected search therefore starts from the exact post-S4 packed
P tokens. The diagnostic assembly was removed; no performance benchmark was
run after the corrected static gate stopped the candidate.

## Decision

The gate hard-stops before assembly. Current production P remains selected and
P-suffix remains the local reference oracle. Reopen only if a new nonuniform
packet atom closes P_TM with less than 40 instructions/pack, or if a different
consumer contract removes the complete adapter.

## Reproduce

```sh
make check
```
