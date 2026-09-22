# Cost Model Checklist

Use this before trusting a Slothy cycle number.

## Repository Fit

- Prefer the repository's vendored Slothy checkout over a global install.
- Activate or use the repository virtual environment before running Slothy.
  Prefer `venv/bin/python` or `.venv/bin/python` in generated commands.
- Confirm the architecture module accepts every instruction and macro used.
- Confirm the target model matches the intended CPU.
- Confirm macro timing is not being treated as final real-instruction timing.

## Slothy Configuration

- Verify the Slothy module resolves inside the intended venv or vendored
  checkout before trusting cycle numbers.
- `allow_spills` must be false unless the stack policy and constant-time impact
  are explicitly approved.
- Reserved registers must match the ABI and platform.
- The workflow must match region size: one-pass, RA-first/window-opt, or
  macro-RA/unfold/window-opt.
- Final performance must be measured on real unfolded instructions.

## Cycle Interpretation

- Expected cycles must be parsed from the actual Slothy run log.
- Parity can be acceptable only with a written reason, such as improved
  register pressure or enabling full-path improvement elsewhere.
- A better Slothy cycle estimate is not sufficient for promotion without the
  full-path benchmark.
