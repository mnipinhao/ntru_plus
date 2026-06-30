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

## Files

| file | purpose |
| --- | --- |
| `invntt-rminus1.md` | Human-readable target contract, baseline, and window selection notes for production decap `poly_invntt_from_rminus1`. |
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

The first normal window, `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3`, has now been
run through Slothy as a benchmark-only candidate.  It improves the materialized
canonical row1-stage45 microbench from 624.673 to 616.679 cycles/call on Pi5,
but it is not a production InvNTT win because the materialized per-stripe input
is not the production cross-stripe scheduled row.

Stage123 rows remain audit/extract only until a separate stage123 contract is
written.  The post path remains out of the first pass because it includes
inverse DFT3, branchfold constants, representative-sensitive final reductions,
and final output stores.
