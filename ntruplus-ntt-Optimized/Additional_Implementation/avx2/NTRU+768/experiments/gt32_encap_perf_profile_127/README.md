# 127 — Linux perf profile of current GT Encap versus Official

Read-only profiling of the exact Experiment 099 production binaries.  No
implementation is rebuilt, relinked, or instrumented.

Inputs:

- Official SHA-256: `f7fea2cb9ad32afdd7131a0381024ec6ed263f7f88ab2e3628b11b6626b02871`
- GT Clean SHA-256: `0fc97cfa85b564f4236c7d0188cec36d6f50adcdb2a20d7c2ceb1d06498bca24`
- GT production baseline: `b2a4bea`

The experiment uses two complementary `perf` views:

1. `cpu_core/cycles/u` with `any_call,any_ret` LBR records direct leaf
   call/return intervals.  This is the component-cost view.
2. cycle, IDQ-not-delivered, and L1D-pending sampling with LBR call chains.
   This locates event pressure but is not converted into exact component
   cycles.

Both run on CPU 1 with ASLR enabled.  The LBR result uses 128 balanced
Official/GT launch blocks.  PMU sampling repeats each native SUPERCOP measure
binary 32 times.  The formal total remains Experiment 099's native SUPERCOP
stabilized-Q2 result; profiler counts do not replace it.

See `RESULTS.md` for the interpretation and `results/*.json` for raw parsed
data.  Binary `perf.data` files are deliberately ignored.
