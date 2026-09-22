# Optimization Modes

Select one mode before creating output files.

## `new_symbolic_kernel`

Use when no optimized region exists and the task is to create a Slothy-ready
symbolic candidate from a known contract.

Required artifacts:

- `kernel-contract.yml`
- `instruction-dag.yml`
- `candidate.sym.S`
- Slothy driver
- `candidate-contract.yml`

Allowed final status before Slothy: `investigate`.

## `existing_region_replacement`

Use when replacing part of an existing optimized function.

Required artifacts:

- `baseline-region.S`
- `baseline-contract.yml`
- `kernel-contract.yml`
- `instruction-dag.yml`
- `candidate.sym.S`
- `candidate-contract.yml`
- baseline and candidate full-path benchmark records

Hard rule: preserve the exact baseline region contract unless explicit approval
records each contract change.

## `new_kernel_baseline_then_iterate`

Use when designing a new kernel where no optimized implementation exists yet.
Create a simple correct baseline first, integrate it into the full path, then
iterate symbolic candidates against that baseline.

Required artifacts:

- baseline C or simple assembly implementation
- `baseline-contract.yml`
- oracle and full-path benchmark for the baseline
- candidate artifacts from `new_symbolic_kernel`

## `oracle_scaffold_only`

Use when the repository lacks correctness infrastructure. Produce only oracle,
contract, and benchmark scaffolding. Do not generate candidate `.S`.

Required artifacts:

- oracle plan or scaffold
- `kernel-contract.yml`
- benchmark plan
- iteration file with blocked state

## `post_slothy_review`

Use when Slothy output or generated artifacts are supplied by the user or
collected from an authorized run.

Required artifacts:

- symbolic source or candidate contract
- Slothy log or generated files
- parsed Slothy result
- correctness and benchmark evidence before promotion

Do not backfill a promotion decision from Slothy output alone.
