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
r coefficient producer -> shared frontend -> M Forward -> r-hat bytes
m coefficient producer -> shared frontend -> QL2 Forward
M general BaseMul -> QL2 product
QL2 product + message -> QL2 two-source Q24 pack
```

The two-source Q24 entry adds the B3 product and message after both producers
have absorbed two Q24 routing layers. Dynamic convergence routing is reduced
from 288 to 144 operations. The semantic sum is never a memory-resident
polynomial. The coefficient-producer lifetime reuses the final message slot
after the frontend returns, giving four polynomial slots and a 6592-byte
Encap frame without changing the B3 output alias contract.

The old E0V helper remains in its page-aligned RX tail as a geometry anchor.
The three QL2 kernels occupy a second deterministic page-aligned RX tail. The
Encap caller retains its qualified 611-byte input-section reservation, while
86 pre-existing symbols and rodata remain byte- and address-identical between
the E0V and QL2 images. The qualified SUPERcop builder enforces this contract.

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
