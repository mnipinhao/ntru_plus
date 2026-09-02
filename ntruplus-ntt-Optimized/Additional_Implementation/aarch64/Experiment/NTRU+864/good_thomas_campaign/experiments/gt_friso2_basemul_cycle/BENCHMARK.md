# Cortex-A76 isolated benchmark

## Target and build

- Operation: one complete 864-halfword FR-ISO2 BaseMul or BaseMulAdd.
- Host: Raspberry Pi 5, Cortex-A76 r4p1, core 3.
- Compiler: GCC 14.2.0, `-O3 -march=armv8-a+simd`.
- Measurement: Linux grouped `perf_event_open`, CPU cycles and instructions.
- Sampling: 61 samples in each of two opposite orders, three repetitions;
  366 samples per variant, 20,000 calls per sample.
- Inputs: 64 deterministic pseudorandom buffers within the proved component
  bounds.  Data values do not alter control flow or memory addresses.
- Thermal: `get_throttled=0x0` before and after every repetition.

## Included and excluded work

Both variants include all 864 input loads, cubic arithmetic, Montgomery finish,
and 864 output stores.  BaseMulAdd also includes addend loads and accumulation.
No Forward normalization, Inverse denormalization, BaseInv, serialization, KEM,
or SUPERCOP work is included; this gate deliberately isolates BaseMul.

## Results

| Operation | Staged p50 | Direct p50 | Saved | Improvement |
| --- | ---: | ---: | ---: | ---: |
| BaseMul cycles | 2579.606 | 2245.412 | 334.194 | 12.955% |
| BaseMul instructions | 2808 kernel | 2447 kernel | 361 | 12.856% |
| BaseMulAdd cycles | 2872.696 | 2369.547 | 503.149 | 17.515% |
| BaseMulAdd instructions | 3243 kernel | 2881 kernel | 362 | 11.163% |

BaseMul IPC is 1.0932 staged versus 1.0951 direct.  BaseMulAdd IPC rises from
1.1331 to 1.2209, showing an additional scheduling/dependency benefit beyond
the instruction deletion.

Returned GCC disassembly contains no stack access, call, spill, or use of
callee-saved `v8-v15`.  Static function sizes are 104/96 instructions for
staged/direct BaseMul and 121/110 for BaseMulAdd.
