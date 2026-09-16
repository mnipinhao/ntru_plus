# P3B37 — local Mac Slothy, fixed-register P3B36

Result: correctness passes; complete Forward improves only 6.656 cycles
(0.189%). Retain as an experimental scheduled candidate, not a production
promotion. This is neutral under the skill's default 1% scoring threshold.

## Method

Slothy runs locally with /Users/chenpinhao/slothy_and_ra/.venv/bin/python,
the local Slothy checkout, and neoverse_n1_experimental as an A76 proxy.
Fixed allocation, no renaming, no spills, split factor 16, overlapping
small windows, 30-second per-solver limit. Solver phase completed in 27.229 s.
The 513-instruction helper is not optimized as one monolithic solve.

The local parser requires vector MOV to be expressed as its exact ORR alias
and LDP zero offset explicitly. No arithmetic is removed. 453 instruction
positions change; all 513 instructions and arithmetic/register multiset remain.
Whole-region Slothy DFG selfcheck passes. Optional LLVM selftest was disabled;
actual executable correctness is checked separately on Pi 5.

## Same-boundary Pi 5 measurements

Three paired repetitions, both execution orders, medians of process medians.
The common input reset remains included in all Forward measurements.

| Candidate | Cycles | Instructions | Branches |
|---|---:|---:|---:|
| P3B36 original | 3524.936 | 4303.148 | 68.032 |
| P3B37 scheduled | 3518.280 | 4303.148 | 68.032 |
| Frozen SUPERCOP | 3853.233 | 3736.137 | 57.030 |

All six process comparisons improve, but the effect is small. SUPERCOP is the
unchanged campaign comparator sourced from 20260627 with SHAKE256; upstream
latest is unverified. This is not a new full-KEM timing result.

Full-KEM valid/tampered correctness (8), instrumentation equivalence and
cross-version public-key/ciphertext equality pass. Complete 2F + D1 + I versus
schoolbook (32) passes. Each benchmark process passes guard tests (256) and
serialized Forward equivalence (64). Object audit and static no-spill check
pass. Wrapper, ABI, coefficient memory boundaries and constants are unchanged.
The existing specialized input [-3,4] range contract is preserved; this does
not broaden the function to arbitrary int16 inputs.

## Evidence and reproduction

- prepare.py: contracts and fixed-register input extraction.
- optimize.py: local solver configuration.
- run_pi.py: bounded staging, executable checks, paired PMU and summary.
- build/candidate.sym.S: solver input; build/scheduled.S: allocated/scheduled output.
- build/slothy.log, environment.txt, solver-result.json: local run provenance.
- build/post-audit.json, objects.log: structural/object checks.
- build/measurement.json and forward-*.log: complete measurements.
- build/sync: exact uploaded candidate and comparator sources.

Run local scheduling with the repository venv Python and optimize.py; run
python3 run_pi.py --run --repeat --summarize for the remote checks.
Generated build artifacts are intentionally ignored by Git.

The generic skill log parser falsely recognizes “Setting timeout” as failure
and logger digits as cycle estimates. review_log.py preserves its raw output,
checks this specific false positive and records the successful full selfcheck.
No aggregate expected-cycle estimate is claimed from overlapping windows.
The score therefore remains investigate, even though execution checks pass.
P3B33, P3B36 and production remain untouched.
