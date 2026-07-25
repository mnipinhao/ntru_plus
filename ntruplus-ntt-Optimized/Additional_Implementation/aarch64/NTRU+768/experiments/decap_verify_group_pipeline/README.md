# Decapsulation Verify Group Pipeline

This experiment developed the pipeline now used by production
`gt_decap_verify_pointwise`. It does not modify the forward NTT. The
source-order baseline remains in `asm/gt/decap/verify_pointwise_compact.S`;
the promoted source is `asm/gt/decap/verify_pointwise_group_pipeline.S` and is
flattened into the clean release as `asm/internal/decap_verify.S`.

Each of the 24 groups has:

```text
8 fixed-offset D loads
4 INS
8 UZP
BL shared multiplication/store helper
```

The offsets are a fixed gather map from GT row/bit-reversed layout and are not
one monotonic sequence. Replacing the immediate loads with a runtime offset
table would add address loads and indexed addressing.

The first candidate keeps every address and instruction but schedules adjacent
groups together. After a group's final transpose, `q24-q27` and `q31` are dead.
The shared helper does not touch those registers, so five loads for group N+1
move before group N's helper call. The remaining `q28-q30` loads stay after the
call.

The V2 candidate widens that cross-group window without adding instructions.
The helper's temporary `q28/q29` allocation moves to its otherwise-unused
`q2/q3`. This lets `d28/d29` join the lookahead set, so seven of the next
group's eight gathers are issued immediately after their current values'
last transpose uses. Only `d30` remains after the call because the helper still
uses `q30`.

V3 reaches the maximum zero-extra-instruction lookahead. The helper schedules
its three `UZP2` temporaries through `q2/q3`, reusing `q2` only after its first
value's last use. The helper therefore leaves all of `q24-q31` untouched, and
all eight gathers for group N+1 move before group N's helper call.

Hard invariants:

- 24 groups and 24 helper calls remain.
- Arithmetic, reduction, transpose, output stores, and fixed offsets remain.
- Dynamic instruction count remains unchanged.
- Production uses the V3 gather schedule plus the audited Slothy helper
  schedule; V1, V2, plain V3, and historical baselines remain experiments or
  explicit comparison profiles.
- The private pointwise endpoint requires non-overlapping source and
  destination buffers, matching its KEM caller.

Generate with:

```sh
python3 experiments/decap_verify_group_pipeline/generate_group_pipeline.py
```

The relevant benchmark targets are
`bench-decap-verify-group-pipeline`,
`bench-decap-verify-group-pipeline-v2`, and
`bench-decap-verify-group-pipeline-v3`, plus the V3 Slothy paired targets, in
`aarch64-bench/Makefile.production`.

## Current result

All three candidates are correctness-passing and performance-positive:

- static instruction count: unchanged at 620 for all three
- helper calls: unchanged at 24
- scalar differential: 1,000/1,000 pass
- AAPCS64 ABI sentinel: `0x0`
- V1 full decapsulation same-binary paired median: 20 cycles faster
- V2 full decapsulation same-binary paired median: 38-42 cycles faster across
  three runs
- V3 full decapsulation same-binary paired median: 62-64 cycles faster across
  three runs
- retired instructions: unchanged
- V1 isolated full-decap median delta: approximately 24 cycles faster
- V2 actual verify product-to-bytes component: 43 cycles faster in the
  matching current profiler build
- V3 actual verify product-to-bytes component: 85 cycles faster in separate
  matching current profiler binaries

The full measurements and interpretation are in
`result_2026-07-24.md`. This remains a default-off experiment until a
production-promotion decision and clean-release KEM/KAT gates.

## V3 shared-helper Slothy schedule

The shared helper is exactly 100 instructions excluding `ret`, not 109. The
`slothy_helper_v3` experiment reconstructs its semantic DAG and schedules the
complete region, including the zeta load, four-vector RHS load, arithmetic,
reductions, and four-vector store.

The hard register contract is:

```text
v0       fixed reduction constants
v4-v7    current LHS group live-ins
v24-v31  next gather group, live-through and unchanged
v1-v23   helper allocation pool
spills   forbidden
```

Slothy's Neoverse-N1 model reports 25 expected cycles both before and after
scheduling, but Cortex-A76 PMU measurement is positive. Three same-binary
paired full-decapsulation runs show V3+Slothy beating V3 by 66-72 cycles and
compact production by 136-137 cycles. Correctness, scalar differential,
AAPCS64 sentinel, Slothy self-check, and the `v24-v31` static audit pass.

The candidate remains default-off. Detailed contracts, generated ASM, logs,
and PMU results are in `slothy_helper_v3/`.

## Offset-loop decision

The group offsets are generated from a fixed permutation, but they are not one
runtime affine sequence. Some even/odd group pairs differ by `+24` in every
lane, while others mix `+24` and `-24` or wrap across a 768-byte row boundary.

Keep immediate-offset loads for the speed path:

```asm
ldr d24, [x1, #312]
```

Each such load is one instruction and depends only on `x1`, so the A76 can
issue independent gathers early. A runtime offset table would add an offset
load plus an indexed address dependency. A post-increment pointer loop would
also serialize address generation and still need special handling for the
non-affine lanes. Such loops remain reasonable code-size experiments, not the
preferred speed optimization.

Assembler macros can make the fixed offsets easier to read or generate, for
example by accepting an offset parameter and emitting `ldr dN,[x1,#offset]`.
The assembler expands the macro into the same load at every call site, so this
does not reduce linked text size or dynamic instruction count.
