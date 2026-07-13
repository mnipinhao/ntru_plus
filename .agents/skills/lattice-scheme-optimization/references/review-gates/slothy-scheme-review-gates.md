# Slothy Scheme Review Gates

Use these gates after each Codex output in the NTRU+ / HAETAE / Slothy symbolic
workflow.

## Gate 1: Profile gate

### When to use

Use after `ring-profile.yml` or scheme extraction output.

### Checks

- NTRU+ parameters are extracted from current spec/repo, not only paper memory.
- HAETAE uses current source facts for `q`, ring, and actual parameter set.
- NTRU+ is not treated as classic NTRU.
- NTRU+ is not treated as NTRU Prime or NTTRU.
- HAETAE is not treated as Dilithium.
- Repo URL, commit, and parameter set are recorded.

### Fail conditions

- Missing repo commit.
- Paper constants treated as current implementation facts.
- NTTRU appears as an active target.
- Dilithium constants imported into HAETAE without source proof.

## Gate 2: Kernel contract gate

### When to use

Use after `operation-dag.yml`, `kernel-requirements.yml`, or a platform-owned
kernel contract.

### Checks

- The operation DAG covers one operation or coherent kernel family.
- Exact input representation is stated.
- Exact output representation is stated.
- Coefficient range before and after is stated.
- Constants and zeta order are stated.
- Memory and constant-time requirements are stated.
- Reference C oracle or reference relation is stated.
- Target platform route is stated.
- If a platform contract exists, instruction selection, ABI, live-ins,
  live-outs, memory contract, and reserved-register policy are stated.
- If Slothy is requested, the platform kernel is small enough for the selected
  Slothy workflow.

### Fail conditions

- One giant scheme-wide operation DAG.
- No coefficient range.
- No reference oracle.
- Platform instructions or physical-register policy placed in
  `kernel-requirements.yml`.
- Missing live-out list in a platform contract.
- Instruction selection changes after platform planning without updating the
  contract.

## Gate 3: Symbolic assembly gate

### When to use

Use after symbolic `.S` and driver draft are produced.

### Checks

- Only symbolic temporaries are used.
- Physical registers appear only for ABI inputs/outputs or explicit reserved
  registers.
- No secret-dependent branch.
- No secret-dependent load/store address.
- No unnecessary physical register allocation.
- No over-scheduling.
- Instruction selection is platform-appropriate.
- Slothy start/end labels match the driver.
- Static checker warnings are reviewed.

### Fail conditions

- Physical `v0..v31` or `q0..q31` used as ordinary temps.
- Missing live-in/live-out comments.
- Missing range comments.
- Branch inside region without public-control justification.
- Driver labels mismatch source labels.

## Gate 4: Post-Slothy gate

### When to use

Use after the user runs Slothy and provides generated output.

### Checks

- Slothy output preserves ABI.
- Slothy output does not clobber reserved registers.
- Slothy self-check or dataflow check passed.
- Generated `.alloc.S`, `.real_alloc.S`, and `.opt.S` stages match selected
  workflow expectations.
- Differential tests pass.
- KATs pass if scheme-level tests are available.
- Benchmark improves the intended operation without hiding conversion or wrapper
  cost.

### Fail conditions

- Generated output fails assembly.
- Reserved register is clobbered.
- Differential tests fail.
- Benchmark is reported before correctness.
- Performance comparison excludes required conversion, wrapper, or reduction
  costs.

## Gate report shape

Use this shape when reporting gate results:

```text
Gate:
Result: pass | fail | needs-info
Blocking issues:
- ...
Warnings:
- ...
Required fixes:
- ...
Next allowed step:
- ...
```
