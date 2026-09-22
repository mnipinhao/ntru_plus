# Iteration Policy

Each iteration must have a hypothesis, changed artifact list, and gate result.

## Rules

- Return to the earliest state affected by the change.
- If the instruction DAG changes, regenerate symbolic assembly and rerun static
  checks.
- If ABI, memory, range, constants, or outputs change, update contracts and
  require explicit approval for replacement mode.
- If only Slothy configuration changes, rerun Slothy and parse the new result.
- If benchmark results are noisy, rerun the full-path benchmark before changing
  code.

## Stop Conditions

- Promote when all gates pass.
- Reject when correctness or contract preservation fails without a viable fix.
- Investigate when external evidence is missing.
- Keep candidate when evidence is promising but not promotion-ready.
