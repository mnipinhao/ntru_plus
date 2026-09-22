# Existing Optimized Region Mode

Use this for replacing an optimized region inside a function that already has
ABI scaffolding, layout decisions, and performance-sensitive integration.

## Required Workflow

1. Locate the exact region labels or source span.
2. Extract the region with `scripts/extract-slothy-region.py`.
3. Create `baseline-contract.yml` from the extracted region.
4. Create `kernel-contract.yml` for the intended replacement.
5. Build `instruction-dag.yml` for the same region semantics.
6. Generate `candidate.sym.S` only after both contracts pass.
7. Run static checks and contract comparison.
8. Execute Slothy when authorized under repository policy, or hand off the
   exact command; collect traceable output before continuing.
9. Parse Slothy output, run oracle correctness, and benchmark the full path.
10. Promote only if all gates pass.

## Preserved Contract Items

- Function ABI and live-in/live-out registers.
- Stack and callee-save policy.
- Pointer increments, post-increments, and memory order.
- Alignment and aliasing assumptions.
- Constant representation and load source.
- Coefficient ranges before and after the region.
- Constant-time branch and address behavior.
- Integration path and benchmark command.

## Failure Modes

- Standalone ABI kernels hide live-out and clobber requirements.
- C-only oracles miss integration pointer movement and layout contracts.
- Cycle improvements on extracted code can disappear after full integration.
- Slothy output can be correct for a standalone function but invalid as a
  splice into a larger optimized routine.
