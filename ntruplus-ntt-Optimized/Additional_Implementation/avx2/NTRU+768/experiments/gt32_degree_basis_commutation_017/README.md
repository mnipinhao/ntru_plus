# GT32 degree-basis commutation gate 017

This generator-only gate tests the proposed **BaseMul-selected linear basis**
without modifying GT Clean or emitting assembly.

## Structural result

The selected incomplete transform is a 32-point leaf transform applied
independently to each quartic degree.  A quartic degree transform `T`, such as

```text
(a0+a2, a0-a2, a1+a3, a1-a3),
```

therefore commutes exactly with both Forward and inverse:

```text
(F32 x I4)(I32 x T) = (I32 x T)(F32 x I4).
```

The generator proves this modulo 3457 on all 128 degree/leaf basis vectors for
the exact selected Forward matrix and its computed inverse.  It covers the
three pair-Hadamard partitions (`01|23`, `02|13`, `03|12`) and every signed
output-row permutation in that family.

Commutation means the basis change is **movable**, not free.  In the current
decomposition, NTT32 butterflies mix the 32-leaf axis; they do not produce
`a0 +/- a2` or other quartic-degree forms.  The selected
`FR_PACKED_TO_BM_REGS` terminal contains 12 routing instructions and zero
degree add/sub instructions.  The inverse entry likewise begins by recovering
leaf topology and then applies inverse leaf butterflies independently to each
degree.  It does not consume a pair-Hadamard degree basis for free.

## Optimistic executable floor

For a pair-Hadamard basis, each of four output degree rows needs one vector
add/sub per 16-leaf block.  With two BaseMul inputs and one inverse-side undo:

```text
two Forward/input formations:  2 * 4 * 12 = 96
inverse-side T^-1 undo:             4 * 12 = 48
------------------------------------------------
optimistic boundary floor:                   144 instructions
```

This deliberately charges zero for inverse-2 scaling, routing, loads, stores,
loop control, range repair, and code delivery.  Gate 009's already optimistic
maximum BaseMul credit is only 108 instructions over the polynomial, with
vector multiply uops changing only from 63 to 61 per block.  The minimum
whole-island delta is therefore still `+36` instructions before omitted costs.

## Decision

No assembly is emitted.  This closes the specific mechanism that current
Forward final butterflies or current inverse first butterflies can absorb
pair-Hadamard quartic-degree forms for free.  It does **not** claim that every
arbitrary bilinear basis is exhausted.

Reopen only when at least one boundary transform actually disappears because
an upstream producer natively emits the forms or a downstream consumer accepts
them, when a new basis deletes more multiply/reduction uops than its explicit
formation floor, or when the decomposition changes so a transform butterfly
really mixes the quartic-degree axis.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/degree_basis_commutation_gate.json`
