# 140 — promoted QL2 Encap production profile

This read-only gate profiles the exact Official and promoted GT ELFs from
Experiment 139. LBR call/return intervals describe direct leaf costs; they are
not added to reconstruct the full Encap time. The formal whole-operation result
remains Experiment 139.

The capture uses 128 balanced fresh processes on CPU 1, ASLR enabled,
`cpu_core/cycles/u`, period 50,000, and `any_call,any_ret` branch records.
Binary `perf.data` files are ignored after parsed JSON is produced.
