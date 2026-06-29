# Slothy Window Audit

This directory tracks Slothy-ready windows before any optimizer run happens.
It is intentionally separate from generated `.alloc.s`, `.real_alloc.s`, and
`.opt.s` artifacts.

Current scope:

- Documentation, manifest, and run tracking only.
- No Slothy run.
- No generated optimized assembly.
- No production default change.
- No arithmetic, register allocation, or instruction-order change.

## Files

| file | purpose |
| --- | --- |
| `invntt-rminus1.md` | Human-readable target contract, baseline, and window selection notes for production decap `poly_invntt_from_rminus1`. |
| `invntt-rminus1-windows.yml` | Machine-readable manifest for marker-bounded windows and rejected unsafe windows. |
| `slothy-run-tracker.md` | Human-readable run ledger. Entries stay here even for audit-only and planned runs. |
| `slothy-runs.yml` | Machine-readable run tracker for audit, planned, optimized, and promoted candidates. |

## Window Size Policy

- Prefer 70-120 instructions.
- Allow 120-150 instructions for serious runs.
- Reject windows below 40 instructions unless they isolate final-store or parser
  risk.
- Reject windows above 150 instructions unless they are explicitly marked
  split-heuristic-only.

## Current InvNTT rminus1 Decision

The existing marker-bounded row stage45 windows expand to 337 instructions each.
That is too large for a normal first pass, but `row1_stage45` is still the
best first candidate as a split-heuristic-only scheduling experiment because it
is isolated from the public ABI prologue, final branchfold post path, and
basemul-to-InvNTT boundary.

Stage123 rows remain audit/extract only until a separate stage123 contract is
written.  The post path remains out of the first pass because it includes
inverse DFT3, branchfold constants, representative-sensitive final reductions,
and final output stores.
