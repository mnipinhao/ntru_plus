# Slothy Handoff Report

## Kernel

- Name:
- Source:
- Contract:
- Target architecture:
- Target microarchitecture:
- Workflow:

## Region

- Start label:
- End label:
- Instruction count:
- Live-ins:
- Live-outs:

## Contracts

- Range contract:
- Constant contract:
- Memory contract:
- ABI/reserved-register policy:
- Constant-time assumptions:

## Static checker results

- `check-symbolic-asm.py`:
- `check-slothy-region-size.py`:
- `check-physical-reg-leaks.py`:

## Driver

- Driver file:
- Expected generated outputs:
- Files overwritten by driver:

## Post-run validation

- Compare symbolic vs allocated:
- Compare allocated vs optimized:
- Assemble:
- Reference/differential tests:
- KATs:
- Constant-time review:
- Benchmark:

## Warnings

- Slothy output is generated code, not the source of truth.
- Slothy self-check is not a scheme-level correctness proof.
- Concrete register choices may change across runs.
