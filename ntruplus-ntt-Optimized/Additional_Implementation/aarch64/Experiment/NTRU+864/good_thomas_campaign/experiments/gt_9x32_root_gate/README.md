# NTRU+864 GT 9-by-32 root gate

## Question

Does the exact NTRU+864 cubic-leaf root set used by the current reference admit
a 9-by-32 algebraic grid suitable for the first scalar Good-Thomas experiment?

This experiment does not claim that a conventional twiddle-free 288-point DFT
implements the NTRU+864 transform. It proves only the root topology required
before deriving the forward and inverse transform.

## Why this is first

The current ring is

```text
Z_3457[x] / (x^864 - x^432 + 1).
```

With `y = x^3`, every polynomial is

```text
A0(y) + x*A1(y) + x^2*A2(y)
```

over

```text
P(y) = y^288 - y^144 + 1.
```

The proposed factorization follows from

```text
P(y) = Q(y^9),  Q(z) = z^32 - z^16 + 1.
```

Therefore the candidate grid must have 32 valid `z` columns and exactly nine
`y` roots above each column. Merely observing `288 = 9 * 32` is insufficient.

## Inputs

- Production-authoritative scalar zeta table:
  `Reference_Implementation/NTRU+864/ntt.c`.
- `q = 3457`, `n = 864`, cubic leaf degree `d = 3`.
- Montgomery radius `R = 2^16 mod q` used only to decode the checked-in table.

## Checker

`gt864_root_model.py` independently:

1. parses all 288 Montgomery-form zetas from the reference source;
2. reconstructs the 288 leaf labels used by `poly_basemul` and
   `poly_baseinv`, namely `zetas[144+i]` and its negative;
3. enumerates every field root of `P(y)` and compares the exact sets;
4. derives a primitive 864th root from the smallest field generator;
5. constructs 32 roots of `Q(z)` and nine preimages over each root;
6. checks that the resulting 9-by-32 grid equals the current leaf-root set;
7. constructs a bijection from current leaf order to `(row, column)` and
   hashes that mapping for reproducibility;
8. separately checks that the campaign's arithmetic CRT formula is a
   permutation of `0..287`. It does not equate that permutation with the leaf
   map without a later transform proof.

Run from this directory:

```sh
make check
make print-json
```

Or run every current campaign gate:

```sh
make -C ../.. check
```

## Gate

Pass requires all of the following:

- exactly 288 parsed zetas;
- exactly 288 distinct roots of `P`;
- exact equality between the current leaf labels and all roots of `P`;
- exactly 32 distinct roots of `Q`;
- exactly nine preimages per `Q` root;
- a bijective 9-by-32 root grid;
- a bijective current-leaf-order to GT-grid mapping;
- a bijective arithmetic CRT index map.

Passing this gate permits a direct scalar evaluation/interpolation experiment.
It does not permit Neon implementation or performance measurement.

## Production isolation

No Production Makefile includes this directory. The checker reads the scalar
reference source but builds and links no NTRU+864 object.
