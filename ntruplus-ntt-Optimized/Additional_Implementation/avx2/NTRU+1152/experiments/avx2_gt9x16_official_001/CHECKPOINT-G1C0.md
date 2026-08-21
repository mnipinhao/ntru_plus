# Checkpoint G1C0: inverse-sink audit before prototypes

G1C0 prevents a misleading BMScale benchmark. Official NTRU+1152 BMScale
already stores four terminal coefficient vectors at offsets 0, 32, 64, and 96
in each 128-byte block, and Official inverse level 6 consumes two adjacent
blocks with eight loads. It continues directly into level 5 without
materializing the seam. Therefore a C1 store-order-only candidate has no
standalone-converter credit against the Official control.

The generated source-locked audit is
`generated/g1c-inverse-sink-audit.json`. It records the inverse level-6 shape:
four sums, four differences, four Montgomery difference chains, four Barrett
sum reductions, and 16 word-routing instructions.

## BaseInv algebraic closure

The BaseInv path preserves the Official two-phase lifecycle:

1. `poly_baseinv_1` emits four adjugate vectors and one denominator vector for
   each of 18 blocks.
2. `fqinv_batch` inverts the complete `den[18]` array.
3. `poly_baseinv_2` applies denominators with sign pattern `+,-,+,-`.
4. Failure zeroes the output, and both paths clear `den[18]`.

For a uniform component gauge `g`, adjugate degree is 3, denominator degree is
4, and the final BaseInv output gauge is `g^-1`. The current identity-gauge
control therefore needs no component correction. For the scale-1/4, R0
BaseInv output, the direct inverse scalar normalization is:

```text
4 * 288^-1 * R mod 3457 = 142
```

This closes scalar normalization only. It does not close the adjusted inverse
level-6 component/twiddle map or its range proof.

## Prototype gate

- G1C-M C0 is the Official zero-conversion control.
- C1 is not built because store order alone has no credit to recover.
- C2 requires a generated adjusted inverse level-6 oracle and range proof
  before assembly is authorized.
- G1C-I has scalar normalization and `den[18]` lifetime closure, but also waits
  for the adjusted inverse head.

Cycles remain null. G1B debt and G1C credit must not be added; G2 will compare
linked complete paths.
