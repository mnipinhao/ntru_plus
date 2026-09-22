# Optimization State Machine

Use this state machine for every optimization task. Do not generate or promote
candidate assembly from an untracked state.

## States

1. `repo_probe`
   - Run `scripts/probe-slothy-repo.sh`.
   - Record Slothy location, target model, existing optimize drivers, tests,
     benchmarks, source files, and region labels.
   - Record the venv interpreter used for Slothy, such as `venv/bin/python` or
     `.venv/bin/python`.
   - Exit gate: repository facts are recorded in the iteration file.

2. `baseline_contract`
   - Required for `existing_region_replacement` and
     `new_kernel_baseline_then_iterate`.
   - Extract the exact baseline region with
     `scripts/extract-slothy-region.py`.
   - Record ABI, live-in/live-out, memory, constants, ranges, clobbers, and
     measured baseline cost.
   - Exit gate: `baseline-contract.yml` exists and is not placeholder-only.

3. `kernel_contract`
   - Create or update `kernel-contract.yml` from
     `assets/kernel-contract-template.yml`.
   - Run `scripts/check-kernel-contract.py kernel-contract.yml`.
   - Exit gate: required contract fields pass.

4. `instruction_dag`
   - Create `instruction-dag.yml` from `assets/instruction-dag-template.yml`.
   - Every instruction must trace to the contract and every output must trace to
     a dependency chain.
   - Exit gate: DAG has named inputs, outputs, constants, memory accesses, and
     ordering constraints.

5. `symbolic_asm`
   - Generate symbolic `.S` only after the previous gates.
   - Preserve the DAG and contract; do not hand-schedule final physical
     registers.
   - Exit gate: symbolic file, driver, and candidate contract exist.

6. `static_checks`
   - Run `check-symbolic-asm.py --candidate --kernel-contract kernel-contract.yml`.
   - Run `check-physical-reg-leaks.py` with the contract.
   - For existing regions, run
     `compare-kernel-contract.py baseline-contract.yml candidate-contract.yml`.
   - Exit gate: all checks exit zero, or the candidate is `reject`.

7. `Slothy_run_by_user`
   - Retain this legacy key for existing iteration records. The actor may be
     the user or authorized Codex; the gate is real execution evidence.
   - Execute the exact venv-based command under the repository execution policy
     when authorized and access is available; otherwise provide the command
     and expected generated files for handoff.
   - Prefer `venv/bin/python optimize.py ...` or
     `.venv/bin/python optimize.py ...`; do not hand off a global `python`,
     `slothy`, or `slothy-cli` command unless no repo venv exists and the user
     approves the fallback.
   - Stop before claiming scheduling/allocation success.
   - Exit gate: a real Slothy log or generated artifacts are collected and
     traceable to the current inputs, driver, model, and command.

8. `parse_slothy_result`
   - Run `scripts/parse-slothy-log.py` on the supplied log.
   - Record expected cycles, status, output files, and solver warnings.
   - Exit gate: Slothy result is `pass` or the candidate is `investigate`.

9. `oracle_correctness`
   - Run or request the oracle, differential tests, KATs, and ABI checks.
   - Exit gate: correctness is pass/fail/unknown in candidate score.

10. `full_path_benchmark`
    - Benchmark the real integration path, not only a standalone harness.
    - Exit gate: baseline and candidate benchmark numbers are recorded.

11. `score_candidate`
    - Run `scripts/score-candidate.py candidate-score.yml`.
    - Exit gate: status is one of `reject`, `investigate`, `candidate`,
      `promote`.

12. `promotion_decision`
    - Run `scripts/check-promotion-readiness.py`.
    - Exit gate: promotion report is complete or candidate returns to iteration.

13. `iteration_or_promote`
    - If `promote`, generate `promotion-report.yml` and state the changed
      files.
    - Otherwise record the next hypothesis and return to the earliest affected
      state.

## Non-Skippable Gates

- `kernel_contract` precedes all candidate `.S` generation.
- `baseline_contract` precedes candidate `.S` generation for existing optimized
  regions.
- `Slothy_run_by_user` precedes cycle-based scoring.
- `full_path_benchmark` precedes promotion.
