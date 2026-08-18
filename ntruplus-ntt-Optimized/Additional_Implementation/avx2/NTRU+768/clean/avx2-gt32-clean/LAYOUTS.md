# Typed polynomial representations

The wire format and public KEM semantics are exactly the NTRU+768 format.
M and P only describe internal physical coordinates.

## M

M is the persistent private coefficient-plane SoA layout used by Encap and
Decap.  Each 16-lane YMM contains one quartic degree plane for sixteen leaves.
The Q24 unpacker deposits directly into M; B3 consumes M without a global
transpose; the inverse core and the typed M packers also consume it directly.

## P

P is the key-generation physical placement.  It retains coefficient planes
but uses the leaf order selected for the P Forward, J1 BaseInv, F0-by-J1
product, and SP1 Q24 serializer.  P is not converted to M during Keygen.

## Montgomery exponent

`e` records representation scale modulo `q=3457`:

- Forward terminal values are `e=0` (`F0`).
- J1 BaseInv output is `e=1`.
- `F0 x J1` returns `e=0`.
- Scale BaseMul creates the inverse-input `e=-1` contract.
- General BaseMul preserves `e=0`.

These exponents are part of the function type.  Calling a generic-looking
operation on J1 data is invalid even if the arrays have the same C type.

## Q24 GT-native codec

Q24 consumes or produces 24-byte packets containing sixteen 12-bit
coefficients.  A packet corresponds to four quartics and one TILE4 vector.
The codec fuses serialization, canonical reduction/checking, GT leaf mapping,
and the M/P physical deposit or gather.  It does not materialize the Official
intermediate coefficient layout.
