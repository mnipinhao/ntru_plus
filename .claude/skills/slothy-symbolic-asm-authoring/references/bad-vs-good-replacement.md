# Bad vs Good Replacement

## Bad

Create a standalone ABI `.S` kernel, validate it with a C oracle, then splice
it into an existing optimized function.

Why this is bad:

- Standalone ABI hides the existing function's live-in/live-out contract.
- The C oracle may not cover pointer increments, packed layout, clobbers, or
  surrounding instruction dependencies.
- Slothy cycles for the standalone kernel do not prove full-path improvement.
- Splicing can silently break stack, constant-time, or memory-order contracts.

## Good

Extract the exact baseline region contract, preserve it, generate a symbolic
candidate for the same region, run Slothy, compare cycles and full-path
benchmark, then promote only if gates pass.

Required proof:

- Baseline region is extracted and recorded.
- Candidate contract preserves the baseline contract or approved changes.
- Slothy result is parsed.
- Oracle correctness passes in the integrated path.
- Full-path benchmark is improved or neutral.
