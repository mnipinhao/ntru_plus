# NTRU+

Use this reference for NTRU+ scheme-aware optimization planning.

NTRU+ is NTRU-based, but treat it as its own NTT-friendly NTRU-like variant. Do
not assume classic NTRU, NTRU Prime, or NTTRU behavior.

## Source priority

1. Current NTRU+ specification and implementation.
2. Current NTRU+ repository commit.
3. NTRU+ paper.
4. `../families/ntru-like.md`.
5. Core and platform skills.

## Required extraction

- NTRU+ version.
- Repository URL and commit.
- Parameter set.
- `n`.
- `q`.
- `f(x)`.
- Ring notation.
- Modulus shape.
- NTT structure.
- Transform length.
- Root and zeta tables.
- Coefficient representation.
- Reference C polynomial multiplication path.
- KAT or test-vector path.
- Benchmark harness path.

## Known orientation facts

Use these only as orientation until current spec/repo facts are extracted:

- Phase source notes describe NTRU+ as NTRU-like and NTT-friendly.
- The cited plan describes paper-version rings of the form
  `Rq = Z_q[x]/<f(x)>` with `f(x) = x^n - x^(n/2) + 1`.
- The cited plan mentions paper-version parameter examples such as
  `n = 576, 768, 864, 1152` and `q = 3457`.

Do not hard-code these values into a kernel plan without confirming the current
specification and implementation.

## Ring-profile fields

```yaml
scheme_id: ntruplus
variant_family: ntru-like
spec_version:
repo_commit:
parameter_set:

ring:
  coefficient_ring: Z_q
  q:
  q_bits:
  polynomial_modulus:
  degree:
  modulus_shape:
  transform_length:
  roots_of_unity:
  coefficient_representation:

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

hot_operations:
  - poly_mul
  - ntt
  - intt
  - pointwise_mul
  - encode_decode_related_arithmetic

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

- Input representation.
- Output representation.
- Coefficient bounds before and after.
- Twiddle or constant source.
- Memory layout.
- Whether the kernel is a full transform, partial transform, pointwise product,
  or leaf kernel.
- Whether a Slothy symbolic region is appropriate.

For kernel ordering, read
`../roadmaps/ntruplus-kernel-roadmap.md`.

## Slothy handoff conditions

Only hand off to `slothy-symbolic-asm-authoring` after:

- Instruction selection is fixed.
- AArch64 Neon layout is fixed.
- Memory contract is fixed.
- Constant contract is fixed.
- Range contract is fixed.
- Region is small enough or split into a workflow A/B/C plan.

## Validation checklist

- Verify current NTRU+ spec and repo commit.
- Verify ring parameters from source, not from family assumptions.
- Verify NTT tables and coefficient representation against reference code.
- Verify KAT path before any assembly work.
- Verify new symbolic kernels against reference C before benchmarking.

## Common mistakes

- Assuming NTRU+ uses classic NTRU's ring.
- Assuming NTRU+ uses NTRU Prime's trinomial ring.
- Treating paper-version parameters as current without checking.
- Starting platform or Slothy work before producing `ring-profile.yml`,
  `operation-dag.yml`, and `kernel-requirements.yml`, or before the selected
  platform skill produces its kernel contract.
