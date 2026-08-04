# Round 3 differential closure and stop decision

Authoritative baseline: `round3-primary-20260804-cpu1-f059ceb`.

- Measured Official: 90611.830 cycles
- Measured GT: 186228.970 cycles
- Measured gap: 95617.140 cycles
- Reconstructed gap: 94810.219 cycles
- Differential closure error: 0.844%
- Reversed-link gap change: 7.267% (`frontend-sensitive`, but below the 10% stop threshold)

## Coherent zero-floor upper bounds

| Candidate | GT cycles | Zero-floor potential |
|---|---:|---:|
| `decap-backend-pipeline` | 53228.365 | 53228.365 |
| `forward-materialization-boundary-class` | 43867.608 | 43867.608 |
| `keypair-backend-pipeline` | 26042.638 | 26042.638 |
| `encap-backend-pipeline` | 22940.150 | 22940.150 |
| `serialization-boundary-class` | 19300.324 | 19300.324 |
| `base-arithmetic-boundary-class` | 17758.996 | 17758.996 |
| `inverse-store-reload-boundary-class` | 15036.723 | 15036.723 |

A zero floor is deliberately more optimistic than the required arithmetic/memory/byte-boundary floor. Since even that upper bound does not reach 70,000 cycles, no prototype is authorized.

Final decision: `stop-gt-unsuitable-for-avx2`.
