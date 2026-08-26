# Results

Status: local algebra gate passed on 2026-08-26.

Command:

```sh
make check
```

Observed summary:

```text
gt864_root_gate=pass
parsed_zeta_count=288
p_root_count=288
q_root_count=32
preimages_per_q_root=[9]
legacy_leaf_set_equals_p_roots=1
grid_set_equals_p_roots=1
legacy_to_grid_bijection=1
arithmetic_crt_is_permutation=1
legacy_leaf_to_grid_sha256=a15f659eb13bf6ee173d04135e02a774ef0e90c2b153797dcecb39644eaecae5
```

Derived public field values recorded by `make print-json`:

```text
smallest_generator=7
primitive_864_root=2401
primitive_9_root=1520
Montgomery_R=3310
Montgomery_R_inverse=2775
```

Interpretation:

- proved: the current cubic-leaf roots admit the declared 9-by-32 grid;
- not proved: forward/inverse GT formulas, scale placement, ranges,
  representation cost, or performance.

No benchmark is authorized for this experiment.
