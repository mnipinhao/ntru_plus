---
name: aarch64-neon-lattice-polymul
description: AArch64 Armv8-A and Armv9-A Advanced SIMD / Neon planning and review workflow for new or materially changed lattice polynomial multiplication kernel contracts, covering feature policy, cost modeling, modular multiplication, layouts, instruction selection, and range validation. Use when layout, instruction, table, memory, range, or representation contracts are new or changing. For maintenance of an existing implementation with fixed contracts, use its normal repo workflow first; for existing NTRU+768 GT production work, use ntruplus-gt-kernel-engineering.
---

# AArch64 Neon Lattice Polynomial Multiplication

## Trigger conditions

Use this skill when the user asks Codex to design or materially change a
lattice polynomial multiplication kernel contract for AArch64 Armv8-A or
Armv9-A Advanced SIMD / Neon.

Use it for Neon NTTs, incomplete NTTs, modular multiplication kernels,
coefficient layouts, table layouts, transform selection, range proofs, and
constant-time review for new rings, new parameter sets, or new kernel
contracts.

## Non-goals

- Do not use SVE, SVE2, or SME unless the user explicitly requests those
  targets.
- Do not import Cortex-M4 scalar DSP tradeoffs as Neon layout rules.
- Do not organize guidance around existing schemes; they are examples only.
- Do not copy scheme-specific root tables, cutoffs, constants, or reductions.
- Do not over-schedule manually when the user wants Slothy. Stop after
  instruction selection and layout planning.
- Do not block existing repo engineering work that already has fixed scheme
  context, linked asm, correctness tests, and benchmark targets.

## Cross-skill routing

Read `../lattice-polymul-core/references/cross-skill-routing.md` when another
lattice skill also matches. If coefficient ring, polynomial modulus,
dimensions, operand ranges, output representation, or transform preconditions
are missing, route back to `lattice-polymul-core` before making Neon layout or
instruction decisions. Use this skill only after the algebraic/ring decision is
clear.

For existing NTRU+768 GT production work in this workspace, route to
`ntruplus-gt-kernel-engineering` first.

## Existing Repo Fast Path

If the task targets an existing implementation with fixed ring/transform
contracts, linked source/object paths, tests, and benchmark targets, do not
restart algebraic intake or require a full platform plan. Use normal
repo-engineering steps instead:

- inspect the linked source and object path
- identify the active build flags and wrappers
- create benchmark-only prototypes when requested
- assemble, run correctness tests, and run PMU/benchmarks before making
  performance claims

Only route back to this skill when the change needs a new Neon layout,
instruction selection, range contract, table layout, or memory contract.

## Gate Policy

Treat correctness-sensitive facts as hard gates: ring profile, modulus,
transform preconditions, reduction range, representation contract,
constant-time memory access, and output byte contract. Treat planning
completeness as a soft checklist for existing repo work; it should guide the
audit but not prevent a benchmark-only prototype.

## Slothy boundary

When the user wants Slothy, stop after:

- instruction selection
- coefficient layout
- table layout
- range contract
- constant contract
- memory contract
- reserved-register constraints

Do not manually schedule beyond this point. Do not emit physical-register
candidate assembly here. Read the local handoff reference, then hand off to the
single canonical `slothy-symbolic-asm-authoring` skill.

## Workflow

1. If this is an existing repo engineering task with fixed contracts, use the
   existing repo fast path above and read only the references needed for the
   specific issue.
2. If algebraic intake is missing, first use the core skill's
   `../lattice-polymul-core/references/new-ring-intake.md`.
3. Read `references/armv8-v9-neon-platform-model.md` and
   `references/arm-feature-policy.md`.
4. For performance decisions, read `references/neon-cost-model.md` and
   `references/neon-layout-and-permutation.md`.
5. For arithmetic kernels, read `references/neon-mulmod-patterns.md` and
   `references/neon-range-proof-notes.md`.
6. For transform choices, read
   `references/neon-transform-selection-for-new-rings.md`.
7. When the user wants Slothy, produce a clean kernel contract with instruction
   selection, layout, range contract, constant contract, memory contract, and
   reserved-register constraints. Read `references/slothy-handoff.md`, then
   hand off to the canonical `slothy-symbolic-asm-authoring` skill. Let that
   skill load and apply its own references.
8. Run only the static validation tools relevant to the touched source or
   contract. Treat their findings as review prompts, not correctness proofs.
9. Use `references/case-studies/README.md` only for archetype examples.

## References to read first

- For new or materially changed Neon kernel contracts, read
  `references/armv8-v9-neon-platform-model.md`.
- Then read `references/arm-feature-policy.md` to keep the target Neon-only.
- For new performance-sensitive kernel designs, also read
  `references/neon-cost-model.md` before proposing code structure.
- For existing repo fast-path work, read only the references needed to answer
  the concrete linked-source, wrapper, test, or benchmark question.

## Static validation tools

Resolve and verify source paths before running a checker:

- Run `python3 scripts/check-aarch64-feature-usage.py <path>...` to identify
  optional or out-of-scope ISA features.
- Run `python3 scripts/check-neon-patterns.py <path>...` to inventory layout,
  narrowing, and multiply-high patterns. It prints a capped summary by default;
  add `--verbose` for every finding or adjust `--max-per-code`.
- Run `sh scripts/check-secret-independent.sh <path>...` for conservative
  branch, select, and memory-access review prompts.

All tools report the number of files scanned. Missing inputs, unsupported
explicit files, unreadable inputs, or a scan of zero supported files exit with
status 2. Findings exit with status 0 by default; add `--strict` to exit with
status 1 when findings exist. These tools are triage aids and do not replace
range proofs, constant-time review, assembly inspection, or correctness tests.

## Validation expectations

For new or changed kernel contracts, require proof of root/transform
preconditions, lane range bounds, representation-map correctness, constant-time
memory and branch behavior, and full-path benchmarks that include conversions,
table access, target reduction, and caller workload. For existing repo
fast-path work, require only the correctness and benchmark checks relevant to
the touched symbol/path. Inspect generated assembly when correctness or timing
depends on exact instruction selection.
