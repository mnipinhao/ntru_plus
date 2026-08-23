# GT32-LATE-SOA-067 — Decap production-image promotion gate

This experiment asks only whether the Decap caller improvement qualified by
066 survives a production-shaped GT Clean image.  It does not modify GT Clean
production sources and it does not change Late-SoA arithmetic.

## Immutable evidence entering this gate

```text
065 FULL_ARITHMETIC_CHAIN_PASS    about -67 TSC
066 AFFECTED_CALLER_PASS          about -10 TSC
067 PRODUCTION_IMAGE              measured here
```

The superseded Encap proposal remains:

```text
NOT_RUN — caller graph incompatible with the 065 B3-to-inverse seam
```

## Production-shaped construction

The production `decap.c` is compiled twice in the same PIE ELF:

- Control renames only `ntruplus768_dec_impl`.
- Candidate renames that entry and redirects exactly two call targets:
  `ntruplus768_basemul_scale_m_avx2` to the 066-qualified fused B3/post-I1
  body, and `ntruplus768_invntt_m_avx2` to the existing inverse remainder.

Consequently the caller frame, decode, validation, inverse tail, crepmod3,
recovered-message/r path, hashes, native final verification, failure mask,
cleanup, and return convention all come from the same production source.
The executable also retains and executes production Keypair and Encap during
setup, and links every selected GT Clean C/ASM object with the captured
SUPERcop compiler profile.

The complete 066 seam object is reused verbatim.  No code-size pruning,
constant relocation, padding search, scheduling change, decoder change, or
new fusion is allowed in 067.

## Measurements

- Primary: full-Decap same-ELF alternating paired TSC, pinned to CPU 1.
- Placements: Normal and Reversed production-object link order.
- Robustness target: both medians and bootstrap upper bounds below zero;
  `28/32` favorable launches is the predeclared near-all-launch promotion
  target.
- Attribution: core cycles, instructions, loads, stores, IDQ not-delivered,
  ELF hashes, section sizes, and selected symbol addresses.

PMU does not independently veto a paired-TSC pass, but a conflicting large
core-cycle/frontend regression marks the result fragile.

## Correctness

The production-shaped binary must pass valid and invalid/malformed Decap
differential tests.  Both KAT variants must reproduce the immutable response:

```text
bytes:  948402
SHA256: 22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

Final measurements and the promotion decision are recorded in `RESULTS.md`
and `STATUS.yml`.

## Decision

The promotion gate fails in both production-shaped placements:

```text
Normal:   +57.715 TSC, 95% CI [+53.014, +66.817]
Reversed: +11.086 TSC, 95% CI [ +0.229, +19.966]
```

Therefore `Late-SoA × current GT Clean Decap production image` is
`CLOSED_FOR_SCOPE`.  The 065 arithmetic pass and 066 affected-caller pass
remain valid, but GT Clean production is unchanged.
