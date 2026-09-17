# GT32 Encap persistent QL2 gate (134)

This gate asks whether QL2 can become the persistent Encap presentation on
both inputs of general BaseMul, rather than remaining only the convergence
presentation introduced by experiments 102--104.

Production GT Clean is not modified.

## Exact structural result

QL2 is a qword-local AoS layout:

```text
one qword = [c0,c1,c2,c3] of one quartic leaf
four qwords/YMM, four YMM/group, twelve groups
```

It is therefore compatible with the *kind* of qword-local `vpmaddwd` BaseMul
already implemented by `GT32-AOS-DOT-REDC16-001`.  A scalar permutation
oracle passes all 64 impulses and 1,000 random quartic products modulo 3457.

If Decode(h), Forward(r), r serialization, general BaseMul and final Q24 all
keep QL2 at their shared boundaries, the executed boundary-routing ledger is:

```text
current 104:             48 routes/group
persistent QL2 target:   12 routes/group
delta:                  -36 routes/group
12 groups:             -432 routes/Encap
```

This is a real operation-class-deletion premise.  It is larger than the
single-r persistent-T experiment 101 and, crucially, requires a native
BaseMul rather than converting QL2 back to coefficient planes at entry.

## Mandatory scale correction

The old qword-local R1-U kernel cannot be reused unchanged:

```text
old R1-U:       e=0 x e=0 -> e=-1   (inverse consumer)
Encap general:  e=0 x e=0 -> e=0    (Q24 consumer)
```

The first executable candidate must include the general-B3 `Mont(R^2)`
finish after REDC16.  The constructive lowering adds 48 Montgomery chains,
four instructions per output vector, or 192 dynamic instructions.  The old
kernel uses 15 YMM and the finish can reuse dead temporaries, so zero spill is
still plausible; this is not yet a cycle claim.

Consequently the old R1-U `-49..-52 TSC` result is **not** credited to Encap.
Likewise, `-432 routes` is not converted into cycles.  The native BaseMul's
blend/shuffle/reduction DAG must be measured.

## Decision

```yaml
GT32-ENCAP-PERSISTENT-QL2-134:
  mapping: PASS
  scalar_product_oracle: PASS
  operation_class_deletion: 432 boundary routes per Encap
  old_R1U_direct_reuse: REJECTED_WRONG_SCALE
  conversion_based_variant: CLOSED_BY_101_CLASS
  decision: PASS_TO_EXECUTABLE_135
  production_modified: false
```

Gate 135 is deliberately local and matched:

```text
control:   M x M -> QL2 general B3
candidate: QL2 x QL2 -> qword-local dot/REDC16 -> Mont(R^2) -> QL2
```

It must use same-ELF paired Normal/Reversed placement and report TSC, core
cycles, retired instructions, multiplier pressure and port 5/11.  More
instructions are not a rejection criterion.  Full Encap integration is only
eligible if the measured native-B3 cost leaves credible repayment for the
432-route producer/serializer deletion.

Reproduce with:

```sh
make check
```

The machine-readable artifact is `generated/persistent-ql2-gate.json`.
