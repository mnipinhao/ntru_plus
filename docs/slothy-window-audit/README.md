# Slothy Window Audit

This directory tracks Slothy-ready windows, campaign results, and current-best
benchmark-only candidates.  It is intentionally separate from production
promotion decisions.

Current scope:

- Documentation, manifest, run tracking, and benchmark-only generated
  candidates.
- No production default change.
- No arithmetic, register allocation, or instruction-order change in production
  sources unless a later task explicitly promotes a candidate.

## Promotion Policy

Small source-order local Slothy windows are no longer considered sufficient
promotion evidence for these production kernels.

A Slothy candidate must pass all of the following before it can be considered a
real optimization candidate:

1. Correctness against the relevant standalone and KEM/full-path differential.
2. Pi5 PMU against the correct benchmark-only or production baseline.
3. Reproducibility, or at least non-regression on a repeat run.

Slothy model cycles are useful for scheduling diagnostics, but they are not
promotion evidence by themselves.

Recent negative examples:

- InvNTT Stage45 canonical stripes: Slothy reported `OPTIMAL` and selfcheck OK,
  correctness passed, but the PMU win was not reproducible and the all-four
  scaling candidate regressed.  The route is stopped.
- Generic/rminus1 basemul one-loop: Slothy reported `OPTIMAL` and correctness
  passed, but Pi5 PMU regressed.  The source-order one-loop route is rejected.

## Files

| file | purpose |
| --- | --- |
| `invntt-rminus1.md` | Human-readable target contract, baseline, and window selection notes for production decap `poly_invntt_from_rminus1`. |
| `forward-ntt-production-contract.md` | Production Forward NTT entrypoint, layout contract, caller audit, and Slothy readiness decision. |
| `invntt-rminus1-windows.yml` | Machine-readable manifest for marker-bounded windows and rejected unsafe windows. |
| `slothy-run-tracker.md` | Human-readable run ledger. Entries stay here even for audit-only and planned runs. |
| `slothy-runs.yml` | Machine-readable run tracker for audit, planned, optimized, and promoted candidates. |
| `slothy-targets.yml` | Global target-level tracker across InvNTT, NTT, basemul, polyinv, and stopped targets. |
| `slothy-best.yml` | Current best benchmark-only Slothy candidates and their PMU/correctness status. |
| `slothy-campaigns.md` | Campaign-level summaries, including discarded candidate summaries. |

## Window Size Policy

- Prefer 70-120 instructions.
- Allow 120-150 instructions for serious runs.
- Reject windows below 40 instructions unless they isolate final-store or parser
  risk.
- Reject windows above 150 instructions unless they are explicitly marked
  split-heuristic-only.

## Current InvNTT rminus1 Decision

The existing marker-bounded row stage45 windows expand to 337 instructions each,
which is too large for a normal first pass.  `row1_stage45` remains useful as a
row-level split-heuristic stress test, but the normal first candidates are now
stripe-pair subwindows derived from the canonical stage45 stripe macro.

The first normal window, `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3`, initially showed
a small benchmark-only microbench win.  The follow-up scaling campaign built an
all-four row1 stripe candidate and retested the path; correctness passed, but
the all-four candidate regressed from 543.266 to 625.327 cycles/call.  The
production-scheduled 337-instruction row1 Stage45 stress attempt also failed in
the Slothy parser on `adr x3, invntt32_stage45_consts`.

Current decision: stop the canonical row1 Stage45 stripe route for now.  Do not
extend it to row0/row2 unless a new production-row contract or parser/model fix
changes the evaluation target.

Stage123 rows remain audit/extract only until a separate stage123 contract is
written.  The post path remains out of the first pass because it includes
inverse DFT3, branchfold constants, representative-sensitive final reductions,
and final output stores.
