# A1-S — fixed-T1 Slothy scheduling gate

This experiment is an existing-region replacement of the exact A1 T1
one-bank helper.  It freezes the bank-major tail ABI, M5R-D one-product
arithmetic, Algorithm-10 count, G0 ranges and FR0 outputs.  Slothy may only
allocate and schedule the unified tail/main NTT16 through transpose, twist and
two oriented NTT9 blocks.

The authoritative complete-Forward baseline is 4165.07555 Cortex-A76 cycles.
A candidate must be exact, spill-free, stack-free, preserve coefficient-memory
boundaries, and save at least 20 complete-Forward cycles to justify its
generated-code maintenance cost.

The remote endpoint timed out, after which the user explicitly authorized the
dedicated local environment `/Users/chenpinhao/slothy_and_ra/.venv`. The run
used Slothy 0.2.0 from checkout `f8462d0...`; it did not use global Python.

## Static-check note

The shared symbolic checker in the Slothy skill currently records only the
first destination of every load.  It therefore reports `tail_hi` as undefined
for the real `ldp Q<tail_lo>, Q<tail_hi>, [x1]`.  `make static` retains that
diagnostic in warnings-only mode and immediately runs a strict, LDP-aware
def/use audit over the exact 552-instruction candidate.  The candidate is not
rewritten as two `ldr` instructions for checking.

The checked-in symbolic form spells the architectural zero-offset pair load as
`[x1, #0]`.  Local Slothy 0.2.0 models the immediate-offset Q-register `ldp`
but not its `[x1]` assembly alias; both spellings encode the same instruction.

## Outcome

RA is OPTIMAL and the split-window scheduler reports full self-check OK with
552 instructions, zero spill/stack access, and no coefficient-boundary or
Algorithm-10 change. All one-bank, six-bank and full-Forward correctness tests
pass. The scheduled candidate is nevertheless rejected on Cortex-A76:
complete Forward regresses from 4165.040 to 4208.347 cycles (+43.306), while
retired instructions remain exactly 4432 in both variants. T1 bank-major is
retained; only this N1-proxy-derived schedule is rejected.

## A1-S-002 schedule-only rerun

The follow-up isolates scheduling from allocation: it retains T1's original
physical registers and lets Slothy reorder instructions only. This candidate
passes all the same static and correctness gates and improves complete Forward
from 4165.445 to 4156.983 cycles (-8.462, -0.203%). All three repetition
deltas are negative, but the gain is below the predeclared 20-cycle promotion
threshold, so current T1 remains active. See `results-rerun-002.md` for the
full evidence. Together the two runs show that the large A1-S-001 regression
came from its new register allocation; scheduling alone has a small benefit.
