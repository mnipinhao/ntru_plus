# GT32 operation-minimal SUPERcop attribution (2026-08-13)

## Scope

All measurements use the `/home/nuc/supercop-20260627` `do-part` path,
the same machine profile, CPU pinning, and the forced O3+section-GC compiler.
Because the external tree was not writable in this session, the complete tree
was snapshotted to `/tmp/supercop-opmin`; this changes no benchmark machinery.

Each hybrid implementation keeps one CleanGT operation and uses Official main
for the other two operations:

- `avx2-gt-keypair-min`: CleanGT P-J1 Keypair; Official Encap/Decap.
- `avx2-gt-encap-min`: CleanGT M/H1 Encap; Official Keypair/Decap.
- `avx2-gt-decap-min`: CleanGT Q24/B3/global-inverse Decap; Official Keypair/Encap.

All three passed SUPERcop compilation, constant-branch/index checks, and KEM
correctness before timing.

## Executable image audit

| Image | `.text` bytes | `.rodata` bytes |
|---|---:|---:|
| Official AVX2 | 42,007 | 5,384 |
| Monolithic CleanGT | 66,327 | 56,776 |
| Keypair-min hybrid | 50,263 | 29,064 |
| Encap-min hybrid | 58,583 | 33,000 |
| Decap-min hybrid | 67,607 | 46,600 |

`min` means operation-minimal GT composition, not necessarily the smallest
complete ELF.  Decap-min is larger in `.text` than monolithic CleanGT because
the valid KEM image must retain Official Keypair/Encap as well as GT Decap.

The same GT symbols move substantially.  For example, the M Forward body is at
`0xaba0` in monolithic CleanGT, `0x7ca0` in Encap-min, and `0x7460` in the
earlier Decap hybrid.  The Q24 Decode3 body moves from `0x4d00` to about
`0xa820`.  Thus the experiment genuinely changes delivery while preserving the
target operation algorithm.

## Monolithic CleanGT versus operation-minimal image

Two matched A-B-B-A blocks per operation; negative means the minimal image is
faster.  These are diagnostic launch-level results, not a 100k promotion run.

| Target operation | Pooled delta (cycles) | Block deltas | Reading |
|---|---:|---:|---|
| Keypair-min Keypair | -241.0 | -192.0, -435.4 | Large image effect; target gets faster |
| Encap-min Encap | -124.1 | -170.1, +25.2 | Direction not stable across blocks |
| Decap-min Decap | +54.7 | +81.5, -320.9 | Strong launch/outlier sensitivity; no stable gain |

The diagnostic control is that operations whose algorithm was reverted to Official
also moved by tens to hundreds of cycles.  For example, in the Keypair-min
comparison its Official Encap moved by a pooled -196.9 cycles even though the
purpose of the image change was Keypair.  Whole-image composition or
launch/runtime state is therefore plausibly comparable to the GT algorithmic
margins.  Two blocks are not enough to separate those causes cleanly; this is
a hypothesis requiring a larger launch-level experiment, not a promotion result.

## Official main versus operation-minimal hybrid

Two Official-min-min-Official blocks; negative means the hybrid is faster.

| Target operation | Official Q2 | Hybrid Q2 | Delta | Block deltas | Decision |
|---|---:|---:|---:|---:|---|
| Keypair | 21,459.45 | 21,224.95 | **-234.50** | -248.1, -199.9 | GT Keypair arithmetic/path wins in this isolated delivery |
| Encap | 28,015.35 | 28,232.11 | **+216.76** | +116.4, +324.5 | GT Encap loses in the E-min delivery |
| Decap | 19,309.10 | 19,486.08 | **+176.98** | +176.6, +176.6 | GT Decap loses in the D-min delivery |

This diagnostic result does not contradict the previous monolithic CleanGT
result (Keypair -51.2, Encap +38.0, Decap -59.8 cycles versus Official).
Identical GT operation code appears on either side of parity when the other two
operation families and launch conditions change.  More launches and matched
PMU evidence are required before assigning the full difference to placement.

## Conclusion

1. Keypair has the strongest intrinsic algorithmic case: P-J1 is consistently
   faster than Official when delivered in the K-min hybrid.
2. Encap retains a real residual path/code-generation debt; E-min does not beat
   Official and is not block-stable versus monolithic CleanGT.
3. Decap's earlier win is not yet demonstrated to be placement-independent.
   D-min loses both diagnostic Official blocks even though the GT Decap
   algorithm is unchanged, but two blocks are not final causal attribution.
4. Rewriting Q24 or reopening N5/B3/I1 is not justified by these results.  The
   next work should control complete-image layout/hot-code grouping and measure
   region PMU in the final production-shaped executable.

Raw analyses:

- `tile4-supercop-keypair-operation-min-abba-20260813.json`
- `tile4-supercop-encap-operation-min-abba-20260813.json`
- `tile4-supercop-decap-operation-min-abba-20260813.json`
- `tile4-supercop-official-keypair-min-abba-20260813.json`
- `tile4-supercop-official-encap-min-abba-20260813.json`
- `tile4-supercop-official-decap-min-abba-20260813.json`
