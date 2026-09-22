---
name: slothy-symbolic-asm-authoring
description: Hard-gated Slothy optimization-loop orchestrator for AArch64 Neon symbolic assembly. Use when Codex must plan a kernel optimization mode, extract or create kernel/baseline contracts, select the instruction DAG and layout, author symbolic assembly and Slothy drivers, parse Slothy results supplied by the user, score correctness and full-path benchmark evidence, and decide reject/investigate/candidate/promote for new kernels or existing optimized-region replacements.
---

# Slothy Symbolic ASM Optimization Orchestrator

## Core Principle

Codex is not the final scheduler.

Codex selects the optimization mode, instruction DAG, data layout, symbolic
assembly, oracle, Slothy driver, scoring scripts, and iteration plan. Slothy
performs scheduling, register allocation, and software pipelining. Promotion
requires correctness, contract preservation, a Slothy result, and a full-path
benchmark.

## Hard Gates

- Do not generate a candidate `.S` file until `kernel-contract.yml` exists and
  passes `scripts/check-kernel-contract.py`.
- For `existing_region_replacement`, do not generate a candidate `.S` file
  until `baseline-contract.yml` exists and the exact baseline region has been
  extracted.
- Require a real Slothy run by the user or authorized Codex. Do not claim a
  candidate is schedulable, allocated, or optimized until traceable Slothy
  output or generated artifacts have been collected for the current inputs.
  The legacy state key `Slothy_run_by_user` names this evidence gate; it does
  not require the user to execute the command personally.
- Before any Slothy command, identify and use the repository virtual
  environment. Prefer `venv/bin/python` or `.venv/bin/python`; do not use a
  global `python`, `slothy`, or `slothy-cli` unless the repo has no local venv
  and the user explicitly accepts that fallback.
- Correctness alone is insufficient. A promotable candidate must preserve the
  contract, pass oracle correctness, include a parsed Slothy result, and improve
  or remain neutral on the full-path benchmark.
- Contract changes require explicit approval before a candidate can be promoted.
- Candidate status must be exactly one of `reject`, `investigate`,
  `candidate`, or `promote`.

## Optimization Modes

Select exactly one mode before creating artifacts:

- `new_symbolic_kernel`
- `existing_region_replacement`
- `new_kernel_baseline_then_iterate`
- `oracle_scaffold_only`
- `post_slothy_review`

Read `references/optimization-modes.md` for mode preconditions and artifacts.

## Mandatory State Machine

Follow this state sequence without skipping gates:

`repo_probe -> baseline_contract -> kernel_contract -> instruction_dag -> symbolic_asm -> static_checks -> Slothy_run_by_user -> parse_slothy_result -> oracle_correctness -> full_path_benchmark -> score_candidate -> promotion_decision -> iteration_or_promote`

Read `references/optimization-state-machine.md` before starting and keep an
iteration record from `assets/optimization-iteration-template.yml`.

## Required References

Read only the files needed for the selected mode, but always read the state
machine and promotion gates:

- `references/optimization-state-machine.md`: mandatory state order and gates.
- `references/optimization-modes.md`: mode selection and allowed outputs.
- `references/kernel-contract.md`: kernel, baseline, and candidate contract
  requirements.
- `references/existing-optimized-region-mode.md`: exact-region replacement
  workflow and anti-splice rule.
- `references/new-kernel-baseline-mode.md`: baseline-first workflow for new
  kernels.
- `references/instruction-dag.md`: instruction DAG selection and traceability.
- `references/symbolic-asm-authoring.md`: symbolic source rules.
- `references/cost-model-checklist.md`: Slothy/model/cycle sanity checks.
- `references/pattern-library.md`: how to use bundled symbolic fragments.
- `references/promotion-gates.md`: correctness, Slothy, benchmark, and
  contract gates.
- `references/scoring-policy.md`: candidate scoring and status policy.
- `references/iteration-policy.md`: iteration loop rules.
- `references/bad-vs-good-replacement.md`: explicit bad/good region
  replacement rule.
- `references/post-slothy-review.md`: review flow after Slothy artifacts exist.

Legacy references in this skill remain supplemental. Prefer the required
references above for gated optimization work.

## Assets

- `assets/kernel-contract-template.yml`
- `assets/baseline-contract-template.yml`
- `assets/instruction-dag-template.yml`
- `assets/candidate-contract-template.yml`
- `assets/candidate-score-template.yml`
- `assets/optimization-iteration-template.yml`
- `assets/promotion-report-template.yml`
- `assets/slothy-driver-template.py`
- `assets/patterns/*.sym.S`

Pattern fragments are examples, not candidates. Do not copy a fragment into a
candidate `.S` file until the active `kernel-contract.yml` and, for existing
regions, `baseline-contract.yml` exist.

## Scripts

Use scripts as gates, not as advisory lint:

- `scripts/probe-slothy-repo.sh`
- `scripts/extract-slothy-region.py`
- `scripts/extract-asm-cost.py`
- `scripts/check-kernel-contract.py`
- `scripts/compare-kernel-contract.py`
- `scripts/check-symbolic-asm.py`
- `scripts/check-physical-reg-leaks.py`
- `scripts/parse-slothy-log.py`
- `scripts/score-candidate.py`
- `scripts/check-promotion-readiness.py`

Run static gates before executing or handing off Slothy. Commands must use the
repo venv interpreter, for example `venv/bin/python optimize.py` or
`.venv/bin/python optimize.py`. Follow the repository execution/remote policy;
when execution is authorized and access is available, run and collect the output
without requiring a personal user handoff. Run scoring and promotion gates only
after actual Slothy output, correctness output, and full-path benchmark evidence
are available and bound to the candidate.

## Promotion Policy

Promote only when all are true:

- Oracle correctness passes.
- Contract preservation passes, or approved contract changes are recorded.
- Slothy emits a result and expected cycles improve, or parity is explicitly
  justified.
- Full-path benchmark improves, or remains neutral within the recorded
  threshold.
- Candidate score is `promote`.

If any evidence is missing, use `investigate`. If correctness fails, contract
preservation fails without approval, or full-path performance regresses beyond
threshold, use `reject`.
