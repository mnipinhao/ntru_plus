# NTRU+864 stock Neon layout and consumer ABI gate

## Bounded question

What physical leaf layout does the linked stock Neon Forward NTT actually
store, and what exact layout do `poly_basemul` and `poly_basemul_add` consume?

This is M1/M2 contract reconstruction.  It does not claim that a GT NTT16 or
NTT9 implementation already exists: the only new-path code at this point is
the separate LD3 top-split prototype.

## Resulting physical ABI

The stock Forward NTT finishes in 96-byte chunks.  Each chunk contains two
48-byte SoA tiles.  For tile `g` and lane `l`, physical leaf `8*g+l` is stored
at:

```text
j=0 coefficient: 24*g + 0  + l
j=1 coefficient: 24*g + 8  + l
j=2 coefficient: 24*g + 16 + l
```

`poly_basemul` loads those three vectors as `v4`, `v5`, and `v6` for its first
operand, and `v7`, `v8`, and `v9` for its second operand.  The lane-matched
`zetas_mul` vector selects the modulus `X^3-z` for the same eight leaves.
`poly_basemul_add` loads its addend in the identical three-vector SoA shape.

Thus the stock BaseMul consumer already prefers the proposed high-level ABI:

```text
register/component = j
lane               = leaf
```

It does not consume leaf-major AoS triples with `LD3`.

## Logical mapping

`analyze_layout.py` maps all 288 physical leaf slots to:

```text
(top branch, GT row, top-local GT column, coefficient plane j)
```

using the exact stock Montgomery zeta table.  The declared 2-by-9-by-16 grid
uses primitive-864-root exponents congruent to 1 modulo 6 for `alpha` and 5
modulo 6 for `beta`.  The script also verifies that BaseMul consumes stock
leaf roots in alternating eight-root positive/negative vector groups.

## Design consequence

The future GT NTT9 should preferentially store SoA tile-8 output directly.
Row and column permutations may be carried without runtime correction only if
the BaseMul zeta lanes and inverse consumer use the same physical slot map.
That statement is now a concrete table-remapping obligation, not an assumption.

## Run

```sh
make check
```

No Candidate B/C serializer, cycle result, or Production path is included.
