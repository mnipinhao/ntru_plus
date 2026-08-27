# GT9X16-FORWARD-OPT-V2 Range Reduction Audit

## Scope

This is an explicit research side track.  The main experiment remains
`ENCAP-TAIL-ATTRIBUTION-V1`; this checkpoint does not change production ASM,
Natural-Q, T0-beta, the paper R2 DAG, or the MA2 output ABI.

The current Forward rebase is now measured rather than inferred.  Under the
normal-placement, ASLR-on fixed-common caller attribution, current GT is slower
than Official by 78.8125 cycles for `r` and 76.10416666666674 cycles for `m`.
All four placement/ASLR settings have the same direction.  That puts Forward in
the low-risk optimization range, not the cross-axis/NTT9-DAG rewrite range.

## Exact search

The 72 existing inter-layer Barrett vectors have a repeated shape:

```text
2 branches x 4 q-blocks x 9 first-layer outputs
```

The generator exhausts all `2^9 = 512` retain/remove masks.  Every mask is
checked against both current T0-beta branches, including:

- each second paper radix-3 pre-operation and intermediate;
- the existing rho/rho-inverse Montgomery operations;
- the branch-specific combined T0-beta D8/D4/D2/D1 twiddles; and
- every signed-i16 output interval through the Natural-Q boundary.

The machine Montgomery constants are consumed directly from the generated
tables; the NTT16 constants are converted from their recorded mod-q values.

## Result

Only 16 of 512 masks are safe.  The unique minimum is mask 79 in physical
register order:

```text
register order:  7  8 15 10 11  9 13 14 12
retain Barrett:  Y  Y  Y  Y  N  N  Y  N  N
```

Therefore:

```text
current:                72 Barrett vectors / Forward
minimum proved mask:    40 Barrett vectors / Forward
structural credit:     -32 Barrett vectors / Forward
Encap structural credit: -64 Barrett vectors / two Forwards
```

The retained vectors are all three inputs of the untwisted second radix-3
group, plus the `a` input of each twisted group.  The four removable vectors are
the `b/c` inputs of the two twisted groups: each is immediately consumed by an
existing Montgomery multiplication, which safely reduces the unreduced input.

The selected proof reaches a maximum absolute interval endpoint of 21333,
matching the frozen T0-beta envelope and remaining inside signed i16.  No new
reduction, routing, temporary, scale conversion, or ABI change is introduced by
the proof.

## Decision

The audit establishes strong structural credit, but it does not itself
authorize promotion or benchmark claims.  The next side-track checkpoint may
build a namespaced ASM prototype that deletes exactly the four reductions per
branch/q-block.  It must then prove canonical differential correctness, linked
`72 -> 40` reduction attribution, zero new movement/spill debt, and only then
receive short paired pricing.

Cross-axis wavefront, NTT9 DAG changes, alpha normalization redesign, and
D2/D1 routing changes remain unauthorized.  Those are only reconsidered if a
future post-reduction Forward rebase still shows substantive debt.

Generated evidence:

- `generated/gt9x16-forward-reduction-audit.json`
- `tools/generate_gt9x16_forward_reduction_audit.py`
- `tests/test_gt9x16_forward_reduction_audit.py`
