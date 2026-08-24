# Checkpoint HWA-A0: current GT9x16 compatibility audit

The shared semantic plane is exactly

```text
V[b,physical_p_row,j][lane] = A[b,P[row],Q[lane],j]
```

with 72 YMM vectors for degree four. This is Hwa-style coefficient-plane SIMD:
one terminal coefficient is fixed and the 16 lanes are homogeneous NTT16
leaves. The same semantic rule projects to 54 vectors for NTRU+864 degree
three.

The audit also fixes an important non-equivalence. The fastest F0 forward is a
persistent terminal-pair S/D view, not the exact terminal-major plane. The M3
producer explicitly calls F1-B1, which does emit the exact plane but costs 58.5
cycles versus F0. Therefore the M3 win cannot yet be added to F0 as a complete
caller-path result.

M3 itself now costs 1136/1108/1099 cycles for C0/C1/C2. The linked edge earns
28 cycles and persistent D2/D4/D8 earns another 9.5 cycles, both in 9/9
launches. C2 retains one repaired-D1 boundary and removes 288 later boundary
memory instructions relative to C1.

No separate Hwa implementation is forked. The semantic plane contract is
frozen, but the complete physical ABI is not. Before inverse NTT9 assembly,
derive a direct consumer map from C2's physical P/Q/j state and reject any
standalone natural-q or full-array repack. In parallel, the larger complete-
path question is whether BMScale can consume F0 persistent S/D without paying
F1's producer debt.
