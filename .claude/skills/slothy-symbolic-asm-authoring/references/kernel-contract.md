# Kernel Contract

The contract is the source of truth for candidate generation and promotion.

## Contract Files

- `kernel-contract.yml`: intended operation, ABI, data layout, memory,
  constants, ranges, constant-time policy, Slothy workflow, and validation path.
- `baseline-contract.yml`: exact behavior and integration contract of the
  baseline region or baseline kernel.
- `candidate-contract.yml`: the candidate's claimed contract after symbolic
  authoring and after Slothy output review.

## Required Fields

At minimum, a promotion-capable contract records:

- mode and candidate status.
- kernel id, name, source path, target architecture, target microarchitecture.
- Slothy workflow and region start/end labels.
- ABI inputs, outputs, clobbers, concrete GPRs, fixed vector registers, and
  reserved registers.
- instruction DAG file and layout assumptions.
- memory loads, stores, alignment, aliasing, public-offset policy.
- constants, representation, modulus, and reduction method.
- input, intermediate, and output ranges.
- constant-time assumptions and secret/public input split.
- oracle command, test command, and full-path benchmark command.

## Generation Rule

Do not create `candidate.sym.S` from a prose description. First create
`kernel-contract.yml`, run `scripts/check-kernel-contract.py`, and resolve
errors.

For existing optimized regions, first create `baseline-contract.yml` from the
exact source region. The candidate may only replace that same region contract.

## Contract Preservation

Run `scripts/compare-kernel-contract.py baseline-contract.yml candidate-contract.yml`
for replacements. Differences in ABI, memory, range, constant-time, or outputs
block promotion unless the user explicitly approves them and the approval is
recorded in the candidate score and promotion report.
