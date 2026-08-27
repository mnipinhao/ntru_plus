# ENCAP-TAIL-ATTRIBUTION-V1 Map

The `+605.4`-cycle cumulative tail debt is now assigned three nested,
caller-shaped boundaries with both producers outside the timed region.

```text
T0: resident h preparation
T1: T0 + multiply/add arithmetic
T2: T1 + ciphertext serialization
```

Official T0 is a no-op wrapper because decoded public-key `h` is already in
Official's consumer representation.  GT T0 is the frozen
`project_h_natural_q`.  Official T1 is `poly_basemul + poly_add`; GT T1 is the
frozen cumulative Natural-Q scale-4 MA2.  T2 adds `poly_tobytes` or Direct H1,
respectively.

The reported components must be derived from cumulative paired deltas:

```text
h projection       = delta(T0)
MA2 increment      = delta(T1) - delta(T0)
serializer         = delta(T2) - delta(T1)
total tail         = delta(T2)
```

This avoids inventing a new preprojected-h MA2 kernel and guarantees that the
three components telescope back to the measured tail.  It also keeps the exact
production-shaped MA2 schedule intact.

The next checkpoint is the SUPERCOP-derived fixed-common measure source and
byte-exact/canonical preflight for these boundaries, followed by nine-launch
normal/reversed and ASLR-on/off pricing.  No arithmetic ASM is authorized by
this map.
