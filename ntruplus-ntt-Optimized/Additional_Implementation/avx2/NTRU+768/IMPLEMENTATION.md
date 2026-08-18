# Selected implementation

This export resolves every experimental selector at source level.

## Key generation

```text
CBD -> triple -> shared frontend -> P Forward (F0)
    -> P/J1 BaseInv
    -> P F0-by-J1 BaseMul
    -> P SP1 Q24 pack
```

The selected batch-inverse tree is hand-written AVX2. No P-to-M conversion is
performed.

## Encapsulation

```text
public-key bytes -> Q24 unpack M
r,m coefficient producers -> shared frontend -> M Forward
M general BaseMul -> standalone add(m) -> high-range Q24 pack
```

The standalone add is intentional in this snapshot: the B3-final-store-add
probe is not part of the formally selected whole-image implementation.

## Decapsulation

```text
three serialized polynomials -> shared Q24 unpack3 M
scale B3 -> M inverse core -> inverse tail -> crepmod3
message Forward -> general B3 -> centered Q24 recovered-r pack
derived-r Forward -> native M modulo-q equality
```

The final verification does not serialize a second 1152-byte polynomial.
The recovered-r serialization remains because `hash_g` consumes canonical
bytes.

## Frozen boundaries

N5, B3, and I1 local arithmetic are frozen. Reopening requires deletion of a
complete materialization, reduction, multiply, or shuffle chain; a changed
typed consumer contract; or a different ISA/microarchitecture.
