# Post-Slothy Review

Use when the user supplies or authorized Codex collects Slothy logs, `.alloc.S`, `.real_alloc.S`, `.opt.S`,
or similar generated artifacts.

## Review Order

1. Confirm the Slothy log came from the repo venv command, not an accidental
   global install.
2. Parse the Slothy log with `scripts/parse-slothy-log.py`.
3. Compare symbolic source to allocation output.
4. Compare allocation output to optimized output.
5. Confirm generated code uses concrete registers and no forbidden physical
   registers.
6. Confirm memory accesses, live-outs, constants, and range comments still
   match the candidate contract.
7. Assemble and run oracle correctness.
8. Run full-path benchmark.
9. Score the candidate.

## Do Not

- Treat symbolic names inside comments as emitted registers.
- Expect physical register numbers to be stable across solver runs.
- Edit generated `.opt.S` as the source of truth unless the task is explicitly
  a one-off review patch.
- Promote from Slothy cycles alone.
