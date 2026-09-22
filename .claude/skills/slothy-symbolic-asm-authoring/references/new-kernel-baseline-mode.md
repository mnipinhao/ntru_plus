# New Kernel Baseline Mode

Use this when no optimized kernel exists. Build the correctness and benchmark
path before optimizing.

## Required Workflow

1. Write `kernel-contract.yml`.
2. Create a simple baseline implementation that is easy to audit.
3. Run oracle correctness against the baseline.
4. Integrate the baseline into the full path.
5. Benchmark the baseline in the full path.
6. Record `baseline-contract.yml`.
7. Create `instruction-dag.yml`.
8. Generate symbolic candidate and Slothy driver.
9. Run the normal Slothy, correctness, benchmark, and scoring gates.

## Baseline Requirements

- Prefer clarity over speed.
- Use the same public API and data layout planned for the optimized candidate.
- Record benchmark noise, command, hardware, compiler flags, and input sizes.
- Do not promote a candidate against a microbenchmark-only baseline.

## When To Stop

If oracle correctness or full-path benchmarking does not exist yet, switch to
`oracle_scaffold_only`. Do not generate candidate assembly.
