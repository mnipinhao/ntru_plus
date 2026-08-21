# GT32-EXACT-ELF-DYNAMIC-MAP-055

Observe the frozen 043 Official and Clean-GT production measurement ELFs
without changing their machine code, symbol placement, or data layout.

The experiment replaces cumulative checkpoint subtraction with two read-only
observation methods:

1. Intel LBR `any_call,any_ret` branch stacks with cycle metadata map direct
   Encap call/return intervals in the production execution.
2. PMU sampling with LBR call chains classifies frontend and pending-load
   events whose stack still contains the real Encap caller.

The LBR map distinguishes three kinds of interval:

- `body`: a leaf callee; the return interval covers the body because internal
  loop branches are excluded by the branch filter;
- `nested_tail`: only the tail after a nested callee returned, not the whole
  component;
- `caller_interval`: caller work since the preceding recorded call/return.

Only `body` intervals are used in the descriptive semantic leaf map.  Hash and
SHAKE are intentionally not reconstructed as additive component costs; 052 and
053 already closed intrinsic Hash and Hash-address hypotheses.

## Frozen inputs

- `../gt32_load_to_compute_production_043/build/official-measure`
- `../gt32_load_to_compute_production_043/build/gt-clean-measure`

The recorder stores SHA-256 in its manifest.  Raw `perf.data` files are ignored;
the parsed JSON results are retained.

## Reproduce

```sh
python3 tools/record_lbr.py \
  --official ../gt32_load_to_compute_production_043/build/official-measure \
  --gt ../gt32_load_to_compute_production_043/build/gt-clean-measure \
  --blocks 64 --period 50000 --cpu 1 --output-dir results/raw50k

python3 tools/analyze_lbr.py \
  --manifest results/raw50k/manifest.json \
  --output results/lbr-analysis-64.json

python3 tools/record_pmu.py \
  --official ../gt32_load_to_compute_production_043/build/official-measure \
  --gt ../gt32_load_to_compute_production_043/build/gt-clean-measure \
  --repetitions 32 --cpu 1 --output-dir results/raw-pmu32

python3 tools/analyze_pmu.py \
  --manifest results/raw-pmu32/manifest.json \
  --output results/pmu-analysis-32.json
```

