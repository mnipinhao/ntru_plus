---
name: cortex-m4-lattice-polymul
description: Cortex-M4 / Armv7E-M planning and review workflow for new or materially changed lattice polynomial multiplication kernel contracts, covering scalar DSP cost modeling, modular arithmetic, transform selection, register/stack tradeoffs, memory limits, and range validation. Use when algorithm, reduction, register, stack, scratch, table, memory, range, or representation contracts are new or changing. For maintenance of an existing implementation with fixed ring and kernel contracts, use its normal repo workflow first; existing schemes are case studies only.
---

# Cortex-M4 Lattice Polynomial Multiplication

## Scope

Use this skill to design or materially change Cortex-M4 / Armv7E-M polynomial
multiplication contracts after the algebraic/ring decision is clear. Apply it
to scalar DSP kernels, embedded NTT decisions, schoolbook/Karatsuba/Toom/TMVP
choices, modular arithmetic, register and stack tradeoffs, range proofs, and
constant-time review.

## Non-goals

- Do not import AArch64 Neon lane-layout or vector-register rules.
- Do not use existing schemes as the main structure; they are case studies only.
- Do not assume transform-heavy methods beat scalar or recursive methods on
  Cortex-M4.
- Do not hide stack, scratch, flash, RAM, or table-footprint costs.
- Do not restart algebraic intake for routine maintenance when an existing repo
  already fixes the ring, transform, reduction, and representation contracts.

## Cross-skill routing

Read `../lattice-polymul-core/references/cross-skill-routing.md` when another
lattice skill also matches. If coefficient ring, polynomial modulus,
dimensions, operand ranges, output representation, or transform preconditions
are missing, route through `lattice-polymul-core` before making Cortex-M4
algorithm, arithmetic, stack, or instruction decisions. Use this platform skill
only after the algebraic/ring decision is clear.

For an existing repository implementation with fixed contracts, linked source
and object paths, tests, and benchmark targets, use the normal repo-engineering
workflow first. Return here only when the requested change alters the platform
kernel contract.

## Existing Repo Fast Path

For an existing implementation with fixed ring and transform contracts:

- inspect the linked source and object path
- identify the active compiler, flags, ABI, board, build target, and wrappers
- preserve the existing public API and representation contract
- run the existing correctness tests before and after the change
- use compiler `-fstack-usage`, linker maps, and size tools for authoritative
  stack, RAM, and flash evidence when available
- benchmark on the intended Cortex-M4 target or an explicitly accepted harness

Do not require a full new-ring or platform plan for a localized fix, audit, or
benchmark-only prototype. Route back to this skill when the change needs a new
algorithm, reduction, register/stack/scratch, table, memory, range, or ABI
contract.

## Gate Policy

Treat correctness-sensitive facts as hard gates: ring profile, modulus,
transform preconditions, C integer semantics, reduction range, representation
contract, constant-time branch and memory behavior, ABI, and bounded
stack/scratch use. Treat broad planning completeness as a soft checklist for
existing repo work; it must not block a localized prototype when the fixed
contracts and relevant correctness checks are available.

## Workflow

1. If this is existing repo work with fixed contracts, use the fast path above
   and read only the references needed for the concrete issue.
2. If algebraic intake is missing, first use
   `../lattice-polymul-core/references/new-ring-intake.md`.
3. Read `references/m4-platform-model.md` for new or changed platform contracts.
4. For algorithm cost decisions, read `references/m4-dsp-cost-model.md` and
   `references/m4-transform-selection-for-new-rings.md`.
5. For modular arithmetic, read `references/m4-mulmod-patterns.md`.
6. For register, stack, scratch, or unrolling decisions, read
   `references/m4-register-stack-tradeoff.md`.
7. For proof obligations, read `references/m4-range-proof-notes.md`.
8. Run only the static validation tools relevant to the touched source. Treat
   their findings as review prompts, not correctness proofs.
9. Use `references/case-studies/README.md` only for archetype examples.

## References to read first

- For new or materially changed Cortex-M4 contracts, start with
  `references/m4-platform-model.md`.
- Before selecting algorithms, read `references/m4-dsp-cost-model.md`.
- Before recursive, table-heavy, or unrolled implementations, read
  `references/m4-register-stack-tradeoff.md`.
- For existing repo fast-path work, read only the references needed for the
  concrete linked-source, toolchain, stack, test, or benchmark question.

## Static validation tools

Resolve and verify source paths before running a checker:

- Run `python3 scripts/check-m4-patterns.py <path>...` for conservative
  Cortex-M4 source-pattern review. It prints a capped summary by default; add
  `--verbose` for every finding or adjust `--max-per-code`.
- Run `python3 scripts/check-stack-pressure.py <path>...` to inspect local
  arrays inside function bodies and simple recursion. Treat compiler
  `-fstack-usage` output as authoritative.
- Run `sh scripts/check-secret-independent.sh <path>...` for conservative
  branch, select, and memory-access review prompts.

All tools report the number of files scanned. Missing inputs, unsupported
explicit files, unreadable inputs, or a scan of zero supported files exit with
status 2. Findings exit with status 0 by default; add `--strict` to exit with
status 1 when findings exist. These tools are triage aids and do not replace
range proofs, compiler stack reports, constant-time review, or correctness
tests.

## Validation expectations

For new or changed kernel contracts, require a scalar reference comparison,
worst-case coefficient tests, explicit 32-bit/64-bit range bounds,
stack/scratch/table accounting, constant-time branch and memory review, and
full-path Cortex-M4 benchmarks that include conversion,
transform/decomposition, target reduction, and output normalization. For
existing repo fast-path work, require the correctness, stack, code-size, and
benchmark checks relevant to the touched symbol and target.
