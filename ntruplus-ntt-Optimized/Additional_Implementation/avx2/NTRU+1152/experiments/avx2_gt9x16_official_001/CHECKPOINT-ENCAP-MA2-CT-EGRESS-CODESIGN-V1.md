# ENCAP-MA2-CT-EGRESS-CODESIGN-V1

This checkpoint maps H4 from the linked H3 machine object. It writes no H4
assembly. The input cut is each live `H3_TERMINAL_C`; the output contract is
the exact 1728 ciphertext bytes after one `inv4`, canonicalization to
`[0,3456]`, and 12-bit packing.

## Machine def/use gate

The linked straight-line H3 object is disassembled and replayed backwards
using exact YMM definitions and uses. This replaces symbolic lifetime
annotations at the terminal boundary.

```text
linked peak YMM:                 16
terminal stores recovered:      72
minimum free YMM at a terminal: 3
zero-slack terminal hooks:       0
```

The earlier tile-level `16/16` peak is real, but it does not occur at a
terminal hook. Every live `c_j` hook has room for at least one temporary, so
H4-A terminal `inv4` plus sign canonicalization is feasible without a spill in
principle. An exact instruction schedule is still required before ASM.

## Exact byte ownership

The map joins all 72 terminal vectors and 1,152 lanes to the Official pack
oracle. Every one of the 576 true 12-bit coefficient pairs spans two MA2
vectors, confirming that a single-vector serializer is impossible. In actual
H3 terminal order, however, pair endpoints arrive in adjacent waves:

```text
maximum pending pairs:          16
maximum pending coefficients:   16
i16 storage lower bound:         1 YMM
```

This corrects the overly pessimistic idea that four complete `c_j` vectors
must remain live. A coefficient-plane streaming H4-B with one pending-pair
vector is structurally plausible. The next map must price exact normalization,
pair join, pack transpose, and byte-store routes against the three-register
minimum slack; it may not assume the one-YMM lower bound is achievable.

The authorized continuation is an H4 exact schedule search. MA2 arithmetic,
Natural-Q ownership, scale, reduction policy, and serializer byte semantics
remain frozen, and no H4 ASM is generated here.
