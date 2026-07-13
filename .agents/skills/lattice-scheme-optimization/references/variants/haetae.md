# HAETAE

Use this reference for HAETAE scheme-aware optimization planning.

HAETAE is Dilithium-like in its module-lattice / Fiat-Shamir-with-aborts
structure, but it is not Dilithium.

## Source priority

1. Current HAETAE specification and implementation.
2. Current HAETAE repository commit or submission package.
3. HAETAE paper.
4. `../families/dilithium-like.md`.
5. Core and platform skills.

## Required extraction

- Parameter set: HAETAE-120, HAETAE-180, or HAETAE-260 if the current spec uses
  these names; otherwise record the current naming exactly.
- Repository URL and commit.
- `q`.
- Ring `R`.
- Polynomial modulus.
- Matrix dimensions `k` and `l`.
- NTT and inverse NTT tables.
- High/low-bit decomposition behavior.
- Challenge multiplication path.
- Signature encoding constraints.
- Verification product paths.
- Reference tests and KAT paths.

## Known orientation facts

Use these only as orientation until current spec/repo facts are extracted:

- Phase source notes describe HAETAE as module-lattice and Dilithium-like.
- The cited plan states that HAETAE uses the working polynomial ring
  `R = Z[x]/(x^256 + 1)` across security levels.
- The cited plan states that HAETAE uses `q = 64513`, with `q = 1 mod 512`,
  allowing full NTT splitting, and that `q` fits in 16 bits.
- The cited plan notes that a shared optimized NTT path matters because the
  modulus is constant across parameter sets.

Do not hard-code these values into a kernel plan without confirming the current
specification and implementation.

## Ring-profile fields

```yaml
scheme_id: haetae
variant_family: dilithium-like
spec_version:
repo_commit:
parameter_set: HAETAE-120 | HAETAE-180 | HAETAE-260

ring:
  coefficient_ring: Z_q
  q:
  q_bits:
  polynomial_modulus:
  degree:
  ntt_condition:
  coefficient_storage:
  arithmetic_width:

representations:
  input:
  internal:
  output:
  canonical_or_bounded:

ranges:
  operand_a:
  operand_b:
  known_intermediates: []
  output:

module:
  k:
  l:
  decomposition_constants:

hot_operations:
  - ntt
  - intt
  - matrix_vector_mul
  - challenge_mul
  - highbits_lowbits_related_arithmetic
  - verification_products

target_requirements:
  candidate_architectures: []
  selected_platform_skill:

validation:
  reference_c:
  kats:
  differential_tests:
  benchmark_harness:
```

## Operation DAG focus

For each hot kernel, extract:

- Whether the kernel is NTT, inverse NTT, matrix-vector multiplication,
  challenge multiplication, decomposition arithmetic, or verification logic.
- Input and output representation.
- Coefficient bounds before and after.
- Accumulation depth.
- Twiddle or decomposition constant source.
- Public vs secret memory access.
- Whether the operation is shared across parameter sets.

For kernel ordering, read
`../roadmaps/haetae-kernel-roadmap.md`.

## Slothy handoff conditions

Only hand off to `slothy-symbolic-asm-authoring` after:

- Instruction selection is fixed by the AArch64 Neon plan.
- Matrix/vector or NTT fragment boundaries are fixed.
- Range bounds are known for `q`, reductions, and decomposition arithmetic.
- Constants and table order are fixed.
- Region is small enough or mapped to workflow A/B/C.

## Validation checklist

- Verify current HAETAE spec and repo commit.
- Verify `q`, ring, and parameter-set dimensions from source.
- Verify NTT table order against reference implementation.
- Verify high/low-bit decomposition behavior separately from NTT arithmetic.
- Verify KAT path before any assembly work.
- Verify symbolic kernels against reference C before benchmarking.

## Common mistakes

- Treating HAETAE as Dilithium.
- Reusing Dilithium `q`, zeta tables, decomposition constants, or packing.
- Optimizing NTT without tracking matrix-vector and challenge multiplication
  caller constraints.
- Assuming 16-bit storage implies 16-bit intermediate arithmetic is sufficient.
- Starting platform or Slothy work before producing `ring-profile.yml`,
  `operation-dag.yml`, and `kernel-requirements.yml`, or before the selected
  platform skill produces its kernel contract.
