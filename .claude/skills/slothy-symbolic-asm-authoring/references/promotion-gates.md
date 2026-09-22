# Promotion Gates

Promotion requires all gates. Correctness pass alone is not enough.

## Required Evidence

- `kernel-contract.yml` passes.
- For replacements, `baseline-contract.yml` exists and contract comparison
  passes or approved changes are recorded.
- Static symbolic ASM checks pass.
- Slothy log or generated artifacts are parsed.
- Oracle correctness and ABI/integration tests pass.
- Full-path benchmark is improved or neutral.
- Candidate score is `promote`.

## Blocking Conditions

- Missing Slothy result: `investigate`.
- Missing full-path benchmark: `investigate`.
- Correctness failure: `reject`.
- Unapproved contract change: `reject`.
- Slothy expected cycles regress without approved parity/worse-cycle
  justification: `reject` or `investigate`.
- Full-path benchmark regression beyond threshold: `reject`.

## Contract Changes

Contract changes can be approved only explicitly. Record the changed fields,
reason, approver, and date in the candidate score and promotion report.
