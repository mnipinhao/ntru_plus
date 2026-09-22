# Scoring Policy

Candidate status must be one of:

- `reject`
- `investigate`
- `candidate`
- `promote`

## Status Definitions

`reject`: evidence shows the candidate is incorrect, violates contract,
regresses full-path benchmark beyond threshold, or cannot satisfy required
gates.

`investigate`: evidence is missing, Slothy failed or is ambiguous, benchmark is
noisy, or contract changes need review.

`candidate`: correctness passes and the candidate is plausible, but promotion
evidence is incomplete or not yet strong enough.

`promote`: all promotion gates pass.

## Cycle Policy

- Candidate Slothy expected cycles must improve over baseline.
- Parity is allowed only with a written justification.
- Worse expected cycles block promotion unless the user explicitly approves a
  broader full-path tradeoff and the full-path benchmark is neutral or better.

## Benchmark Policy

- Use full-path benchmark numbers.
- Treat neutral as within the configured threshold.
- Use median or another recorded statistic consistently for baseline and
  candidate.
- Record benchmark command, hardware, compiler flags, and input size.
