# Symbolic Phase123 Triple Input Fusion

This is the Wave 3 `SubAgent-SAMPLE-DAG` workspace. It keeps the Wave 1
SAMPLE semantics but makes the Phase123 input-fusion path Slothy-owned instead
of patching already scheduled production assembly.

## Contract

```text
poly_ntt_triple_scheduled(out, a)      == poly_ntt(3*a)
poly_ntt_triple_add1_scheduled(out, a) == poly_ntt(3*a + e0)
```

`e0` means coefficient 0 is incremented by one after triple scaling. The output
layout remains the production GT block-major row-bitrev layout because the
production `_ntt32_8way` row kernels and final stores are unchanged.

## Files

```text
kernel-contract.yml
baseline-contract.yml
instruction-dag.yml
generate_phase123_triple_sources.py
optimize_phase123_triple.py
phase123_triple.sym.s
phase123_triple_add1.sym.s
my_ntt_phase123_triple.n1.opt.s
my_ntt_phase123_triple_add1.n1.opt.s
```

The `.sym.s` and `.n1.opt.s` files are generated artifacts. The source of truth
for the normal Phase123 DAG is:

```text
asm/slothy/inputs/my_ntt_phase123_flat.sym.s
```

## Reproducibility Map

```text
source of truth:
  asm/slothy/inputs/my_ntt_phase123_flat.sym.s

generator:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/generate_phase123_triple_sources.py

generated symbolic sources:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple.sym.s
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple_add1.sym.s

Slothy script:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/optimize_phase123_triple.py

generated Slothy ASM:
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/my_ntt_phase123_triple.n1.opt.s
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/my_ntt_phase123_triple_add1.n1.opt.s

benchmark integration ASM:
  asm/gt/experiment/ntt_gt_body_triple_scheduled.inc
  asm/gt/experiment/ntt_gt_body_triple_add1_scheduled.inc
  asm/gt/experiment/poly_ntt_triple_scheduled.S
  asm/gt/experiment/poly_ntt_triple_add1_scheduled.S
```

Benchmark-only wrapper symbols:

```text
poly_ntt_triple_scheduled
_poly_ntt_triple_scheduled
poly_ntt_triple_add1_scheduled
_poly_ntt_triple_add1_scheduled
```

The C harness calls the non-underscored labels. The symbols are not declared in
`poly.h` and do not replace production `poly_ntt`.

## Slothy

Remote host:

```sh
ssh pinhao@172.25.166.141 -p 51208
```

Expected command shape from the scheme directory:

```sh
/usr/bin/timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/optimize_phase123_triple.py \
  --variant both --target n1 --stalls 192
```

The parser-compatible add1 form is generated before Slothy by loading an
experiment-local `e0` mask through `x7`; this avoids unsupported
`ins v?.h[0], w?` scalar half-lane insertion.

## Benchmark

Build gate and benchmark target:

```text
macro gate: GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_SLOTHY
target:     bench_gt_keygen_sample_ntt_fusion_slothy_pmu
```

Checked-in benchmark command on the Pi host:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_ntt_fusion_slothy_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

The harness runs correctness first and then PMU. The equivalent benchmark-only
makefile wiring is:

```make
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET ?= bench_gt_keygen_sample_ntt_fusion_slothy_pmu_bin
GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_SOURCES = \
        bench_gt_keygen_sample_ntt_fusion_slothy_pmu.c \
        $(NTRUPLUS)/ntt.c \
        $(GT_SUPPORT_ASM) \
        $(GT_PRODUCTION_NTT_ASM) \
        $(GT_PRODUCTION_NTT32_ASM) \
        $(GT_BASEINV_BATCH_C) \
        $(GT_PRODUCTION_BASE_ASM) \
        $(GT_PRODUCTION_SELECTED_EXTRA_ASM) \
        $(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple.S \
        $(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple_add1.S \
        $(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple_scheduled.S \
        $(NTRUPLUS)/asm/gt/experiment/poly_ntt_triple_add1_scheduled.S

$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET): $(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_SOURCES)
        $(CC) $(CFLAGS_NO_RUNCOUNTS) \
                -DGT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_SLOTHY=1 \
                -DNTESTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NTESTS) \
                -DNITERATIONS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NITERATIONS) \
                -DNWARMUP=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NWARMUP) \
                -DNINPUTS=$(GT_KEYGEN_SAMPLE_NTT_FUSION_PMU_NINPUTS) \
                -DNVALID_ORACLE=$(GT_KEYGEN_SAMPLE_NTT_FUSION_VALID_CASES) \
                $(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_SOURCES) -o $@

bench_gt_keygen_sample_ntt_fusion_slothy_pmu:
        $(MAKE) -B $(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET)
        $(SUDO) taskset -c $(CORE) ./$(GT_KEYGEN_SAMPLE_NTT_FUSION_SLOTHY_PMU_TARGET)
```

## Current Status

```text
contract: written
instruction DAG: written
symbolic source: generated
Slothy: pass
correctness: pass
PMU: pass
decision: keep_and_refine
```

## Run Log

Contract and static gates:

```sh
python3 experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/generate_phase123_triple_sources.py
python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-kernel-contract.py \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/kernel-contract.yml
python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-symbolic-asm.py \
  --candidate \
  --kernel-contract experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/kernel-contract.yml \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple.sym.s \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple_add1.sym.s
python3 /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/check-physical-reg-leaks.py \
  --contract experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/kernel-contract.yml \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple.sym.s \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/phase123_triple_add1.sym.s
```

Results:

```text
check-kernel-contract: passed
check-symbolic-asm: passed
check-physical-reg-leaks: passed
region-size check: warnings only; iter windows are 184 instructions, add1 iter0 is 186
```

Slothy host:

```text
ssh pinhao@172.25.166.141 -p 51208
```

Commands:

```sh
/usr/bin/timeout 900 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/optimize_phase123_triple.py \
  --variant triple --target n1 --stalls 192 --solver-timeout 10

/usr/bin/timeout 900 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python \
  experiments/keygen_sample_ntt_fusion/symbolic_phase123_triple/optimize_phase123_triple.py \
  --variant add1 --target n1 --stalls 192 --solver-timeout 10
```

Slothy status:

```text
triple: parser pass, optimizer pass, output my_ntt_phase123_triple.n1.opt.s
add1: parser pass after replacing unsupported ins v?.h[0], w? with x7 e0-mask load,
      optimizer pass, output my_ntt_phase123_triple_add1.n1.opt.s
logs: slothy_sample_dag_triple_timeout10.log,
      slothy_sample_dag_add1_timeout10_retry.log
final status: split_heuristic_full:OK! for both variants
```

Manual patch status:

```text
No manual patches were applied after Slothy to
my_ntt_phase123_triple.n1.opt.s or
my_ntt_phase123_triple_add1.n1.opt.s.

The input scaling and add1 e0-mask form are generated before Slothy by
generate_phase123_triple_sources.py. The scheduled body includes and public
wrappers are hand-written benchmark integration glue only: they set up the
stack frame, provide the add1 mask pointer, include the generated Slothy output,
and call the unchanged production _ntt32_8way row kernels.
```

Pi5 benchmark host:

```text
ssh pi@100.99.191.9
```

Benchmark command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -f /tmp/sampledag.mk -B bench_gt_keygen_sample_ntt_fusion_slothy_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
correctness,valid_cases=4096
ntt_triple_add1_symbolic_mismatches=0
ntt_triple_add1_slothy_mismatches=0
ntt_triple_symbolic_mismatches=0
ntt_triple_slothy_mismatches=0
baseinv_downstream_checked_cases=16380
baseinv_downstream_symbolic_mismatches=0
baseinv_downstream_slothy_mismatches=0
keygen_sample_ntt_fusion_slothy_correctness,total_mismatches=0
```

PMU:

```text
pmu_settings,NTESTS=31,NITERATIONS=5000,NWARMUP=100,NINPUTS=64

row                                      cycles_p50  instr_p50  IQR
current_triple_plus_ntt_f                      3013       4419    1
symbolic_candidate_ntt_triple_add1_f           2804       4216    6
slothy_candidate_ntt_triple_add1_f             2738       4215    6
current_triple_plus_ntt_g                      2998       4418    3
symbolic_candidate_ntt_triple_g                2815       4214    3
slothy_candidate_ntt_triple_g                  2745       4214    1
post_cbd_x2_current                            6383       9397    3
post_cbd_x2_symbolic_candidate                 6144       9402    0
post_cbd_x2_slothy_candidate                   6041       9401    1
```

Interpretation:

```text
post_cbd_x2 slothy win: -342 cycles vs current
post_cbd_x2 slothy win over unscheduled symbolic: -103 cycles
full keygen: not run; candidate is benchmark-only and not wired into KEM call graph
decision: keep_and_refine; next step is a benchmark-only keygen wrapper gate or combination
          run with HIERK8, not production promotion yet
production default: unchanged
```
