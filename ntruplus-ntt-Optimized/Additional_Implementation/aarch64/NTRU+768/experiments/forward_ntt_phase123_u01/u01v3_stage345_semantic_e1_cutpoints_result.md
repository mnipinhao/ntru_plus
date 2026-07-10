# U01v3 Track E E1 Fine Cutpoints

Status: generated and run on Pi5. This is a diagnostic for old E1, not E1v2.

Cutpoints:

```text
stage3_entry: after 0 executable Stage345 block0 instructions
after_first_butterfly_group: after 16 executable Stage345 block0 instructions
after_first_reduction_group: after 32 executable Stage345 block0 instructions
after_twiddle_multiply_group: after 48 executable Stage345 block0 instructions
after_second_reduction_group: after 56 executable Stage345 block0 instructions
stage3_exit: after 64 executable Stage345 block0 instructions
```

Observed semantic-pair first diff:

```text
row: 0
cutpoint: after_first_butterfly_group
semantic_value: v15_q8
lane: 0
e0_reg: q8
e1_reg: q8
e0_value: -995
e1_value: 1451
final_mismatches: 144
```
