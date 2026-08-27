# Results

## Seam audit

The current B3 DAG saturates all 16 YMM registers.  Its first three quartic
outputs are therefore written to the output buffer while the fourth is still
being computed; the W+D QL2 formation then reloads those three vectors.
Completely eliminating B3 scratch traffic is not a legal local mutation.

Both 105 variants retain those necessary three-vector scratch stores/reloads,
but delete the four final QL2 stores and four later serializer reloads per
tile: 48 final stores and 48 reloads per Encap convergence path.

Correctness passes for 1000 random B3+pack islands and 1000 complete,
byte-exact deterministic Encapsulations for both variants.

## V1: compact loop plus indirect continuations

V1 keeps one compact B3 loop and dispatches each completed tile to one of
twelve immediate-permutation pack continuations.

| Metric | Delta vs 104 QL2 |
|---|---:|
| Island TSC | **+92.0** |
| 95% CI | **[+91.0,+93.0]** |
| Favorable launches | 0/16 |
| Core cycles | +88.5 |
| Retired instructions | +85 |
| Full Encap TSC | +9.5, CI crosses zero |

The per-tile pointer reconstruction and multi-target dispatch more than repay
the deleted memory instructions.

## V2: one direct-call tile core plus fall-through continuations

V2 removes the indirect dispatch and pointer reconstruction.  It contains one
copy of the B3 tile arithmetic and twelve direct calls followed by specialized
pack continuations; it does not duplicate the B3 arithmetic twelve times.

| Metric | Delta vs 104 QL2 |
|---|---:|
| Island TSC | **+64.0** |
| 95% CI | **[+64.0,+65.0]** |
| Favorable launches | 0/16 |
| Core cycles | +67.6 |
| Retired instructions | **-66** |
| Branch instructions | +10 |
| Branch misses | approximately 0 |
| Cache misses | approximately 0 |
| Full Encap TSC | +3.25, CI crosses zero |

V2 proves that the remaining loss is not an instruction-count, branch-miss,
or cache-miss problem.  Immediate per-tile consumption couples the saturated
B3 dependency graph to reduction/packing and removes the cross-tile scheduling
freedom of both the compact B3 loop and the unrolled Q24 serializer.

## Decision

```yaml
GT32-QL2-VIRTUAL-PRODUCT-105:
  correctness: PASS
  materialization_deletion: PASS
  v1_performance: FAIL
  v2_performance: FAIL
  decision: CLOSED_FOR_SCOPE
  production_modified: false
```

Closed scope: current AVX2 16-YMM B3 DAG, QL2 representation, immediate
per-tile final-Q/reduction/packing, and the current ciphertext store contract.
This does not close virtual products after a B3 register-minimum reduction,
a consumer that accepts individually emitted quartic outputs, or a wider SIMD
register file.  Experiment 104 remains the Encap research baseline;
`b2a4bea` remains production.
