# GT32 QL2 shared convergence executable (103)

This experiment implements the `102` generator winner in three private AVX2
symbols without modifying GT Clean:

- `gt103_ntt_ql2_avx2`: post-S5 store ownership `[t0,t2,t1,t3]`;
- `gt103_basemul_general_ql2_avx2`: current B3 with W+D after its finalizer;
- `gt103_pack_ql2_sum_avx2`: memory-source add in QL2 followed only by Q and
  the unchanged high-range reduction/packet store body.

Both producer outputs are stored and reloaded. No register handoff, new
fusion, frame change, caller reorder, r-path change, or arithmetic change is
included.

## Reproduce

```sh
make clean
make check
make benchmark
```

The benchmark pins CPU 1 and uses the installed SUPERcop `libcpucycles`
backend plus RDTSCP. It first runs 16 fresh paired island launches. Full
Encap is run only when the island median is negative. A PMU companion records
core cycles and retired instructions.

The common matched-caller control calls the same caller bytes and the same
three indirect call sites with either control or QL2 function pointers. It is
an attribution device, not a proposed production ABI.

See [RESULTS.md](RESULTS.md).
