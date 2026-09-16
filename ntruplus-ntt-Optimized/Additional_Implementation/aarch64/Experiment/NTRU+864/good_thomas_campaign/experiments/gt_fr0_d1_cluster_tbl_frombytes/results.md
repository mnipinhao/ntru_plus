# D1-P3B20 evidence

Status: **byte-correct, but rejected.**

The exact inverse map has 15 repeated destination-set clusters.  The generated
DAG routes a cluster with `TBL2`, `TBL4`, or `TBL4+TBL2`; all 54 serialized
q-vectors are still loaded once per top and no coefficient scratch is added.
Local guarded tests and 128 Pi 5 arbitrary-byte cases pass.

The target object is the falsifier: `cluster_top` has 188 stack references,
180 of them non-ABI, and retires 1178 more instructions per polynomial.

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B11 | 936.430 | 1715.045 | 6.010 |
| P3B20 clustered TBL | 1299.217 | 2893.045 | 6.010 |
| candidate - P3B11 | +362.787 | +1178 | 0 |

The requested `-145` cycle target is missed by 507.787 cycles.  The older
same-binary P3B17 measurement remains the authoritative P3B11-to-Official gap
of +144.592 cycles; this separate run is not used as a direct Official delta.
