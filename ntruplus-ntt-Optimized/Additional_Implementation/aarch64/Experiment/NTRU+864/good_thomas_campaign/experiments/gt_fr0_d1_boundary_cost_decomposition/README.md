# D1-P2 — production boundary cost decomposition

This fixed-contract benchmark decomposes the D1-P1 GT-versus-Official KEM
gap. It uses the exact P1 wrapper source under a diagnostic-only compile flag;
no transform, layout, range, memory, or ISA contract changes.

Measured paired boundaries are raw coordinate permutations, nonnegative and
centered reductions, fused FR0-to-stock conversion, Forward, raw and centered
Inverse, serializer, deserializer and stock-BaseInv bridge. The resulting API
deltas are multiplied by the exact stock KEM call counts and reconciled with
the D1-P1 Keypair, Encaps and Decaps PMU gaps.
