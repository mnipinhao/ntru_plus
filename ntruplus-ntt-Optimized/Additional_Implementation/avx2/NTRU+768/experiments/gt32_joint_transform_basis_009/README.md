# GT32-JOINT-TRANSFORM-BASIS-009

This experiment changes the optimization unit from an isolated terminal
layout to the full polynomial island:

```text
Top split -> Forward_L -> BaseMul_L -> Inverse_L -> Top join
```

It does not insert an adapter back to current M or P.  Experiment number 008
was already occupied by the full-plane radix-4 gate, so this continuation is
recorded as 009.  GT Clean is not modified.

## Coverage registry

The generated artifact imports, hashes, and classifies the existing global
physical, NTT32-first/R3, full-plane radix-2/radix-4, pair/K2, Pair02, and
mixed-TMVP gates.  Covered families are controls rather than fresh search
nodes.  This prevents a new name from silently rerunning an already closed
layout or arithmetic contract.

## First new joint family

The first open candidate is a one-plane-bit Hybrid with `p0` in adjacent word
lanes and `p1` as a YMM selector.  An exact post-S1 search finds 250 legal
paths.  The best physical state is:

```text
low -> high axes: c0 q1 q3 q4 c1 q0 q2
lane axes:         c0 q1 q3 q4
YMM selector:      c1 q0 q2
```

For one N32 tile, S2..S5 cost 144 instructions, 48 shuffle uops, 32 loads,
13 live YMM, and dependency depth 22.  The progressive Clean control costs
136/40/32/15/21.  The existing top split/S1 and matching top join remain
unchanged; the physical trajectory forms Hybrid progressively and the inverse
is credited with the symmetric route.  All 128 degree/leaf basis vectors pass
exact matrix equality.

## Hybrid-native BaseMul

The selected natural arithmetic basis is:

```text
P=(a0,a1), Q=(a2,a3), A=P+x^2 Q
```

The exact split-K2 oracle gives nine variable products and three lambda
products, or 12 logical Montgomery chains instead of current B3's 19.

Hybrid makes operand formation much cheaper than the old qword-native gate:

- four `vpaddw` form `S=P+Q` for both operands and two groups;
- four `vphaddw(P,Q)` form packed P/Q pair sums;
- two `vphaddw(S0,S1)` directly pool all 16 total sums.

Thus operand formation is ten instructions, including six shuffle uops, with
no cross-group `vpermq`/`vperm2i128` compaction.  A constructive phase
allocation peaks at 14 YMM and needs no spill.

## New selective range proof

The old pair-native proof centered every input and every output.  Hybrid
allows a cheaper exact policy:

1. keep direct P/Q and their pair sums raw;
2. center only the four `S=P+Q` vectors before the pooled total;
3. center the two packed p1/q1 intermediates;
4. center only the two Q=(c2,c3) output vectors before inverse.

This reduces checkpoint sequences from 12 to 8 (36 to 24 instructions).
The raw output bounds are:

```text
[5548, 4327, 14189, 11036]
```

After centering only Q, inverse entry is:

```text
[5548, 4327, 2359, 2179]
```

The generated per-degree proof remains signed-int16 safe through the complete
inverse N32; the final conservative bounds are
`[18975,16318,12150,11746]`.

## Corrected current-B3 control

A crucial correction is that 156 instructions was a historical B3 accounting,
not the selected Clean scale-M loop.  The current
`ntruplus768_basemul_scale_m_avx2` loop is 114 instructions per 16 quartics,
including loads, stores, center, and loop control.

It also exposes why `19 -> 12 chains` overstates the executable gain:

```text
current Clean B3 vector multiply uops: 63
Hybrid lower bound:                    61
```

Current B3 hoists four qinv products and centers only c3.  Hybrid's eight
range checkpoints consume nearly all of the nominal chain saving.

## Whole-island decision

The rejection is deliberately based on the whole `2F+B+I` objective, not an
isolated BaseMul veto.  The model strongly over-favors Hybrid:

- use the best nonmonomial output sparsity floor (14 operations, versus 16
  for monomial output);
- charge its eventual three-instruction coefficient-basis repair as zero;
- charge all product routing, register moves, loads, stores, and loop control
  as zero.

Even then, the Hybrid compute floor is 105 instructions per block, so it can
credit at most 9 against the complete 114-instruction Clean B3.  Across 12
blocks that is at most 108 instructions.  The exact two-Forward plus inverse
Hybrid trajectories add 144 instructions.  Therefore:

```text
optimistic full-island delta >= +36 instructions
```

Every omitted term is nonnegative, the vector-multiply saving is only two per
block, and the pooled-sum/recombination path is not shorter.  No bounded ASM is
emitted.

This closes the one-plane-bit Hybrid plus L01 12-chain family on the selected
exact radix-2 trajectory, including the previously enumerated compact
unit-coefficient input/output bases (979 legal input bases and 289 output
bases).  It does not close arbitrary linear bases or a new top/R3 geometry.
The broader joint architecture may be reopened only by a new mechanism:
producer-generated range-safe Karatsuba operands, a basis that deletes
recombination and final repair together, a top/R3 schedule that removes a
complete six-branch materialization, or a different leaf decomposition.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/joint_transform_basis_gate.json`
