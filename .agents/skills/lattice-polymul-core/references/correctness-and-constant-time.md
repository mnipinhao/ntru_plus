# Correctness and Constant-Time

Use this reference to validate that an optimized polynomial multiplication
implementation matches the target ring and preserves side-channel constraints.

## Correctness map

For each implementation, document:

- Canonical input representation.
- Internal representation.
- Forward map from input to internal representation.
- Internal multiplication or operation.
- Inverse map or reconstruction.
- Final target reduction.
- Output representation.

This map is required for transforms, incomplete transforms, coefficient
switching, auxiliary polynomial embeddings, cached transformed operands,
transposed/TMVP formulations, and recursive matrix algorithms.

## Reference implementation

Keep or write a simple reference that:

- Implements the exact target quotient ring.
- Uses clear integer types or big integers when needed.
- Prioritizes correctness over speed.
- Exposes the same output convention expected from optimized code.

Use it for boundary tests, randomized tests, and differential validation.

## Constant-time checklist

- No secret-dependent branches.
- No secret-dependent table indices.
- No secret-dependent memory addresses.
- No value-dependent loops in reductions.
- No compiler-dependent signed overflow.
- No conditional correction that compiles to branchy secret-dependent code
  unless audited.
- No precomputed representation that leaks secret-dependent access patterns.

## Representation invariants

For every non-canonical representation, state:

- Which values are allowed.
- Whether values are canonical or bounded.
- Whether values are centered or unsigned.
- Whether the representation is in transform domain.
- Whether callers may mix it with canonical values.
- Which function converts it back.

## Benchmark integrity

When comparing strategies:

- Benchmark the full operation path.
- Include conversions and precomputations, or state amortization.
- Include target reduction.
- Include matrix/vector caller work when relevant.
- Exclude unrelated protocol work when comparing multiplication kernels.
- Report compiler, flags, platform, clock methodology, and input distribution.

## Validation checklist

- Prove representation maps compose to the target operation.
- Compare optimized output to reference output on boundary inputs.
- Compare optimized output to reference output on randomized inputs.
- Run tests for every representation conversion.
- Audit constant-time behavior for secret-dependent inputs.
- Re-run validation whenever parameters, compiler flags, or target ISA change.

## Do not do this

- Do not treat random testing as proof of embedding correctness.
- Do not assume a mathematically fixed transform is constant-time in code.
- Do not compare protocol-level cycle counts when evaluating multiplication
  kernels.
- Do not let API callers confuse canonical and transformed operands.
