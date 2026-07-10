# Stage345 Block0 Rename Validation

Status: generated for Track E; production default unchanged.

The validator rebuilds Stage345 block0 as SSA values and checks the physical-register rewrite independently of the handwritten E1 asm.

Key finding: the old E1 allocator enforced `mls same_as old_dest` too late. E1v2 uses a same-as-first allocator, so destructive NEON ops are colored before unrelated temps can occupy that physical register.

Observed E1 localization anchor:

```text
row0 stage3_exit q1 lane0: e0=0 e1=911
```

Validation summary:

```text
old_e1_violations: 8
e1v2_violations: 0
e1v2_same_as_constraints: 20
e1v2_same_as_interference_count: 0
old_e1_q1_stage3_exit: v53_q24
e1v2_q1_stage3_exit: v53_q24
fine_cutpoint_first_diff: after_first_butterfly_group v15_q8 lane0
```

Frozen allocator invariant for follow-up candidates:

```text
1. Destructive instructions such as mls must resolve same_as before greedy coloring.
2. same_as_interference_count must be 0.
3. Any candidate with same_as interference is rejected before ASM emission.
```

A raw physical `q1` diff is not by itself the bug because E1 renames registers. The actionable bug is an invalid rename contract: every use must read the renamed producer's color, destructive ops must keep the old destination color, and block1 live-ins must not be written by Stage345 block0.
