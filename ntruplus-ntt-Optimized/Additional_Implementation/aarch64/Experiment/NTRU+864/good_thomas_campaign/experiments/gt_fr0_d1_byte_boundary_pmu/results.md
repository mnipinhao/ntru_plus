# D1-P3B3 evidence

- Local Apple clang 21 arm64 build of actual stock pack.s and all Neon candidates passed.
- 128 signed-int16 input cases include index tags, INT16_MIN, INT16_MAX and random inputs.
- All candidate encodings match stock assembly byte-for-byte.
- All candidate decodings match stock for canonical roundtrips and 128 arbitrary byte strings, including noncanonical 12-bit values.
- Guard pages check input/output starts and ends, including the final twelve packed bytes.
- After replacing C2's compiler-materialized small array loop and precomputing C1 reverse addresses/shifts, all four local direct functions have no stack traffic.
- C1 local assembly has 32 lane loads in each four-output loop body, interleaved over four distinct vector destinations.
- Pi5 GCC 14.2.0 correctness passed on Linux 6.18.33 with `throttled=0x0` before and after each repetition.
- Three repetitions, two opposite execution orders, and 410 samples/order produced stable Cortex-A76 medians. Forward selects R9-A at 1849.450 cycles; reverse selects C1 at 1183.250 cycles.
- Relative to current, R9-A Forward saves 404.418 cycles (17.94%). C1 Forward saves only 114.405 cycles and loses 290.013 cycles (15.68%) to R9-A.
- Relative to current, C1 reverse saves 1836.230 cycles (60.81%) and beats R9-A by 28.225 cycles (2.33%).
- C2 is rejected in both directions: 2854.140 Forward and 4368.690 reverse cycles.
- GCC object audit finds no stack reference in either C1 function or C2 Forward. C2 reverse has four GPR ABI save/restore references and no vector spill.
- New exact routing witness disproves the inherited simultaneous-54-output claim: forward partial-output peak 16, reverse 14. This is not a minimum proof.

Build manifests and raw local evidence are generated under build/. The prior P3B2 972/1512 counts exclude addresses and actual encoding/decoding work and must not be used as full-byte cost estimates.

| complete boundary | cycles | instructions | branches | decision |
| --- | ---: | ---: | ---: | --- |
| ToBytes current | 2253.868 | 5357.13 | 150.03 | control |
| ToBytes R9-A + stock | **1849.450** | 4360.13 | 182.03 | Forward winner |
| ToBytes C1 direct | 2139.462 | **4335.13** | **30.03** | loses on cycles |
| ToBytes C2 direct | 2854.140 | 6927.13 | 112.03 | reject |
| FromBytes current | 3019.480 | 8553.15 | 906.04 | control |
| FromBytes R9-A + stock | 1211.475 | **2971.15** | 74.03 | close control |
| FromBytes C1 direct | **1183.250** | 3173.15 | **30.04** | reverse winner |
| FromBytes C2 direct | 4368.690 | 12114.15 | 112.03 | reject |

The isolated normalization (526.955 cycles) and pack (543.495 cycles) numbers are attribution controls, not additive decomposition: overlap, call shape, and memory state differ from a complete path. The selected pair remains experimental until the production-shaped KEM rerun closes the actual callers.
