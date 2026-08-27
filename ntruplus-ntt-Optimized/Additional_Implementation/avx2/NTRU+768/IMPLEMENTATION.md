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
M general BaseMul -> two-source high-range Q24 pack
```

The two-source Q24 entry adds the B3 product and message before the existing
transpose/canonicalization. The semantic sum is never a memory-resident
polynomial. The five-polynomial 8128-byte frame is intentionally retained;
frame compaction is a separate, unselected campaign.

The E0V helper lives in a page-aligned RX tail. The Encap caller retains its
qualified 611-byte input-section reservation, while pre-existing hot text and
rodata remain byte- and address-identical to the pre-E0V geometry reference.
The qualified SUPERcop builder enforces this contract automatically.

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
