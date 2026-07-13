# GT experiment assembly

Nothing below this directory may be linked by a production target. The
production layout guard enforces that rule.

| Directory | Contents | Lifecycle |
| --- | --- | --- |
| `forward_ntt/` | U01v3 forward-NTT candidates, drop-ins, and ABI sentinels | historical; G1R123+S2 was promoted to `asm/gt/ntt/` |
| `sample_ntt/` | unscheduled and rejected inserted-multiply sample-NTT variants | historical; fresh scheduled DAG was promoted to `asm/gt/ntt/` |
| `invntt/` | range, boundary, lazy-twiddle, and post-branchfold candidates | paused/historical; production snapshot lives in `asm/gt/invntt/` |
| `keygen/` | keygen arithmetic prototypes | rejected or design-only |

Keep new candidates inside a family directory. Promotion means copying the
reviewed artifact to a production path, updating `gt_production_sources.mk`,
and passing correctness, KAT, layout, and benchmark gates.
