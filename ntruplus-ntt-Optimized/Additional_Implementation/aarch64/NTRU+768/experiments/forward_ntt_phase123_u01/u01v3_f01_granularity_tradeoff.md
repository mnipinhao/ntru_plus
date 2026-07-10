# U01v3 F01 Granularity Tradeoff

Date: 2026-07-09

Status: Track G model-only result.  Production default is unchanged.
No S2/S4 mixing, no twiddle1 lazy-reduction change, no Slothy, and no
Track E combination are used here.

## Scope

Only the F01 block0+block1 boundary is modeled:

```text
Stage12 block0 Q0..Q7
Stage12 block1 Q8..Q15
Stage345 block0 final scatter
Stage345 block1 final scatter
```

The instruction deltas below are relative to G0a, the current
F0-like shared-prefix shape where block0 is fused and block1 remains
behind the row-scratch boundary.

## Candidate Matrix

| id | candidate | extra arithmetic | extra loads | extra stores | max live vector regs | removed scratch ops | net instruction delta | status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| G0a | current_shared_prefix | 0 | 0 | 0 | 8 | 0 | +0 | baseline |
| G0b | delayed_block1_prefix_checkpoint | 24 | 48 | 48 | 8 | 48 | +69 | stop |
| G0c | partial_shared_prefix_q9_q21 | 0 | 18 | 18 | 10 | 48 | -9 | stop |
| G0d | recompute_small_prefix | 24 | 48 | 48 | 8 | 48 | +69 | stop |

## Interpretation

### G0a current_shared_prefix

Existing F0-like shared-prefix shape: block0 is register-handoff fused, while block1 remains behind the row-scratch boundary.

Reason: This is the comparison baseline.  It is already correctness-safe and measured at the F0 envelope, but it does not remove block1 scratch traffic.

### G0b delayed_block1_prefix_checkpoint

Produce block0, checkpoint two out1-producing prefixes per stripe, run Stage345 block0, then form block1 directly in Stage345 block1 consumer registers.

Reason: No raw q reloads, but the replacement is two prefix stores plus two prefix loads per stripe.  Net instruction estimate is positive and memory checkpointing becomes the primary mechanism.

### G0c partial_shared_prefix_q9_q21

Use q9 plus q21 as the only no-rewrite block0 survivors, and preserve the remaining block1 live-ins through memory.

Reason: The theoretical best case is only a small negative instruction delta, requires a new producer liveness contract for q9/q21, and still relies on six memory-preserved vectors per row.  That is too weak after the measured B8/Bmin result matched F0.

### G0d recompute_small_prefix

After Stage345 block0, recompute only the small prefix needed for block1.  Under the no-raw-q-reload rule, this collapses to the same two-vector prefix checkpoint as G0b; allowing raw reloads would duplicate Stage12 input loads and is disallowed.

Reason: With raw q reloads forbidden, recomputation needs saved prefixes and has the same cost as G0b.  With raw q reloads allowed, it would violate Track G's G1 rule and repeat the known negative two-pass shape.

## Stop Decision

G0 status: `negative`.
G1 status: `not_emitted`.

No modeled Track G candidate clears the plausibility bar under the first-wave constraints.  The only negative-delta option is a six-vector memory-preservation variant with a small estimated gain and a dependency on a new q9/q21 producer liveness contract; the delayed/recompute shapes are clearly positive instruction deltas.

No G1 delayed-block1 assembly or test artifact was emitted, because
the model does not show a plausible first-wave Track G win.
