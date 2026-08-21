# Results

## 256-launch fixed-CPU gate

Each launch reports the median of 1024 paired measurements. The process is
pinned to logical CPU 1. Official and GT producers are linked into one ELF and
both call the single `hash_g` symbol at address `0x1970`.

| Mode | Official median | GT median | GT - Official | 95% bootstrap CI |
|---|---:|---:|---:|---:|
| raw | 7478 | 7478 | 0 | [0, 0] |
| mfence | 7478 | 7478 | 0 | [0, 0] |
| common copy | 7478 | 7480 | 0 | [0, 1] |

Normalization relative to raw:

| Control | Median differential effect | 95% bootstrap CI |
|---|---:|---:|
| mfence - raw | 0 | [0, 0] |
| common-copy - raw | 0 | [0, 1] |

The producer outputs and hash outputs were byte-exact before measurement.

## Interpretation

The approximately 100-cycle cumulative movement at the 050 `hash_g` frontier
is not caused by the same physical hash body running more slowly after the GT
producer. It also is not explained by an outstanding-store handoff that an
`mfence` or common-copy normalization removes.

The 050 movement must therefore be attributed outside this producer-state
handoff mechanism:

- cumulative checkpoint/caller composition;
- work attributed to the interval before the checkpoint;
- different hash virtual/code placement in the two production ELFs;
- or interaction present only in the full production prefix/exit geometry.

It is invalid to book the 050 B2-to-B3 difference as a standalone `hash_g`
component cost.

## Decision

```text
hash_g producer-state penalty: REJECTED
mfence production change:      REJECTED
common-copy production change: diagnostic only, no effect
```

The next useful gate is not another hash implementation or Q24 reducer. It is
to reconcile the 050 cumulative checkpoint accounting around B2/B3 and, if
needed, use identical hash clones in fixed slots to isolate code-address
effects. `hash_f/hash_h` data-address geometry remains a separate question.
