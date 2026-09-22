# Slothy Validation After Run

Use this reference after the user or authorized Codex runs Slothy and collects
traceable output under the repository execution policy.

## Rule: Inspect each generated stage according to workflow

### When to use

Use when `.alloc.s`, `.real_alloc.s`, `.opt.s`, or equivalent files exist.

### Preconditions

- User has run Slothy or a Slothy driver.
- Generated files are available.

### Authoring pattern

- Small workflow: compare symbolic source to `.opt.s`.
- Medium workflow: compare `.sym.S` to `.alloc.s`, then `.alloc.s` to `.opt.s`.
- Macro workflow: compare `.sym.S` to `.alloc.s`, `.alloc.s` to
  `.real_alloc.s`, and `.real_alloc.s` to `.opt.s`.

### Range/correctness requirements

- Generated code must preserve the instruction DAG, memory contract, and
  live-outs.

### Validation checklist

- Confirm emitted instructions use concrete architectural registers.
- Ignore symbolic names only when they appear in Slothy comments.
- Confirm expected reordering only occurs in scheduling passes.
- Confirm generated files correspond to the intended driver.

### Common mistakes

- Reading comments as emitted code.
- Treating concrete register numbers as byte-stable.
- Comparing only final `.opt.s` and skipping `.alloc.s` inspection.

## Rule: Assemble and test before benchmarking

### When to use

Use after generated assembly is inspected.

### Preconditions

- Toolchain and test harness are available.

### Authoring pattern

- Assemble generated output.
- Link into the kernel test harness.
- Run reference or differential tests.
- Run scheme KATs if applicable.
- Benchmark only after correctness passes.

### Range/correctness requirements

- Tests must cover boundary coefficient ranges, not only sampled protocol
  distributions.

### Validation checklist

- Assembler accepts generated code.
- ABI and clobbers are correct.
- Reference tests pass.
- Constant-time review passes for secret-dependent inputs.
- Benchmark report records generated artifact and driver revision.

### Common mistakes

- Benchmarking before functional tests.
- Forgetting ABI clobber validation.
- Assuming Slothy self-check covers range correctness.

## Rule: Triage failures from dataflow first

### When to use

Use when Slothy rejects input or generated code fails tests.

### Preconditions

- Failure log or bad generated artifact exists.

### Authoring pattern

- Unknown instruction: inspect target model support.
- Unsatisfiable allocation: reduce live ranges, split region, or reserve fewer
  registers only if safe.
- Wrong output: inspect undefined symbolic names, accidental reuse, tied
  operands, and macro hidden constraints.
- Slow solver: move from one-pass to RA-first/window-opt, then macro workflow.

### Range/correctness requirements

- Do not weaken reserved-register or clobber policy merely to satisfy the
  solver unless ABI safety is revalidated.

### Validation checklist

- Re-run static checkers.
- Re-run Slothy on the smallest failing region.
- Re-run correctness tests after any fix.

### Common mistakes

- Blaming Slothy before checking symbolic source.
- Allowing spills without deciding stack and constant-time policy.
- Fixing generated output rather than symbolic source or driver.
