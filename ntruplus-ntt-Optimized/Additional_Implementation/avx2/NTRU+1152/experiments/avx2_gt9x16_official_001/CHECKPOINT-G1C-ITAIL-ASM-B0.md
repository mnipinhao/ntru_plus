# Checkpoint G1C-ITAIL-ASM-B0

## Decision

The proven B physical-P ABI is now consumed by a straight-line AVX2 inverse
NTT9. This is a correctness-first baseline, not a promoted kernel. It retains
physical order `[0,3,6][1,4,7][8,2,5]`, verified inverse paper-R2 arithmetic,
the `R^-1` input scale, and natural-`s` centered output. It has no canonical
repack, fused radix-9, Winograd, or inverse16 live handoff.

## Arithmetic, range, and liveness

Each `(branch,j)` loads nine YMM registers and computes six in-place radix-3
cores with no lane routing. Generated exact interval analysis proves every
signed-i16 add/subtract precondition for `[-17377,17377]`. Barrett steps
contract input and inter-layer states; final Barrett plus branch-free
correction gives `[-1728,1728]`.

There are 10 Montgomery chains per vector inverse9 and 80 over all eight
`(branch,j)` bodies: three kappa chains per layer plus four untwists. Peak
liveness is 15 YMM. The linked leaf has no call, branch, frame, stack access,
spill, lane permutation, or `vzeroupper`.

## Correctness gates

- 1,003 arbitrary transform inputs, including both range endpoints;
- 257 real C2 producer outputs and all nine physical-P basis vectors;
- all 1,152 cells against the independent inverse-DFT matrix oracle;
- vector-canonical A equivalence, in-place alias, immutability, range, canary;
- ASan/UBSan and linked static audit.

## Repository-local pricing

Intel Core Ultra 7 155H, CPU 1, strict `-O3 -mavx2`, 9 fresh launches, 16
balanced paired blocks, and 96 observations per slot:

| Region | Cycles |
| --- | ---: |
| Pure eight-vector-inverse9 B0 body | 490 |
| C2 stores -> vector-canonical repack -> B0 A | 1548 |
| C2 stores -> direct physical-P B0 B | 1532 |
| Paired B - A | -16 (9/9) |

A performs an explicit 72-load plus 72-store vector natural-P materialization
and then instantiates the same B0 arithmetic macro. Thus `-16` is an optimized
representation-edge price, not the earlier scalar artifact. It is much smaller
than scalar-reference `-667.5`, but directional in every launch.

The 490-cycle B0 body is 216 cycles above the earlier 274-cycle forward
R2-cached diagnostic. The contracts differ: B0 accepts the wider inverse input
and promises centered output. Static attribution points first to 9 input
Barrett reductions, 5 inter-layer Barrett reductions, and 9 final
Barrett-plus-center corrections; its Montgomery count is already the expected
80. These timings are repository-local and cannot promote production.

## Next gate

Keep B as the selected physical ABI. Before D live handoff, build
`ITAIL-ASM-B1` as a same-arithmetic reduction-placement experiment. Use real
C2 per-row provenance to test which reductions can be removed or folded while
retaining a separately safe general entry when required, and price centered
output correction independently. D stays deferred until the arithmetic floor
and avoidable reduction debt are known.
