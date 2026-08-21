PARAMETER := 1152
REPO_ROOT := $(shell git rev-parse --show-toplevel)
EXPERIMENT := $(CURDIR)
PYTHON ?= python3
CC ?= cc
BENCH_CPU ?= 1
SUPERCOP_IMPLEMENTATION ?= avx2-gt9x16-exp001
RESULT_TAG ?= $(shell date +%Y%m%d-%H%M%S)
RESULTS := $(EXPERIMENT)/results/$(RESULT_TAG)
COMMON_GENERATOR := $(REPO_ROOT)/ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/gt9x16/generate_gt9x16.py
COMPILER_ARG := $(if $(SUPERCOP_COMPILER_WRAPPER),--compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER),)
BUILD := $(EXPERIMENT)/build
CPPFLAGS_LOCAL := -Isrc -Iref -Igenerated
CFLAGS_STRICT := -std=c11 -mavx2 -Wall -Wextra -Wpedantic -Werror
SHEAR_SOURCES := src/gt9x16_shear.c ref/gt9x16_oracle.c
SHEAR_HEADERS := src/gt9x16_shear.h ref/gt9x16_oracle.h
UPSTREAM := upstream/supercop-avx2
OFFICIAL_FORWARD := $(UPSTREAM)/consts.c $(UPSTREAM)/ntt.s
FULL_SOURCES := src/gt9x16_shear.c src/top_split_adapter.c src/gt9x16_forward.c ref/ntt9_reference.c
FULL_HEADERS := src/gt9x16_shear.h src/gt9x16_forward.h ref/ntt9_reference.h generated/gt9x16-full-forward-tables.h
FULL_CPPFLAGS := $(CPPFLAGS_LOCAL) -I$(UPSTREAM)
PAIRED_CFLAGS := $(CFLAGS_STRICT) -O3
NTT16_ASM := asm/gt9x16_ntt16.S
NTT16_HEADERS := src/gt9x16_ntt16_asm.h generated/gt9x16-ntt16-constants.inc
OFFICIAL_PARTITIONS := generated/official-ntt-stage-partitions.s
OFFICIAL_PARTITION_HEADERS := src/official_stage_partitions.h

.PHONY: generate check sanitize audit bench-local bench-local-record bench-ntt16 bench-ntt16-record bench-c2 bench-c2-record bench-c3 bench-c3-record bench-c4 bench-c4-record bench-official-stages bench-official-stages-record bench-transform-paired \
 bench-transform-paired-record supercop-check supercop-install-candidate \
 supercop-kem-short supercop-kem-serious supercop-poly-short \
 supercop-poly-serious supercop-paired-serious supercop-promotion-report

generate:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I$(UPSTREAM) tools/probe_official_layout.c $(OFFICIAL_FORWARD) -o $(BUILD)/probe-official-layout
	$(BUILD)/probe-official-layout generated/official-avx2-layout-probe.json
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json
	$(PYTHON) tools/generate_stage8_tables.py --json generated/gt9x16-stage8-tables.json --header generated/gt9x16-stage8-tables.h
	$(PYTHON) tools/generate_full_forward_tables.py --json generated/gt9x16-component-oracle.json --header generated/gt9x16-full-forward-tables.h --asm-constants generated/gt9x16-ntt16-constants.inc
	mkdir -p $(BUILD)/structure
	$(CC) -mavx2 -c $(UPSTREAM)/ntt.s -o $(BUILD)/structure/official-ntt.o
	$(CC) -mavx2 -c $(UPSTREAM)/basemul.s -o $(BUILD)/structure/official-basemul.o
	$(CC) -mavx2 -c $(UPSTREAM)/baseinv.s -o $(BUILD)/structure/official-baseinv.o
	$(CC) -mavx2 -c $(UPSTREAM)/invntt.s -o $(BUILD)/structure/official-invntt.o
	$(PYTHON) tools/audit_ntt_domain_lifecycle.py --ntt-object $(BUILD)/structure/official-ntt.o --basemul-object $(BUILD)/structure/official-basemul.o --baseinv-object $(BUILD)/structure/official-baseinv.o --invntt-object $(BUILD)/structure/official-invntt.o --upstream $(UPSTREAM) --output generated/ntt-domain-lifecycle-audit.json
	$(PYTHON) tools/generate_pipeline_layout.py --component-oracle generated/gt9x16-component-oracle.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --output generated/gt9x16-pipeline-layout.json --cost-output generated/gt9x16-representation-cost-matrix.json
	$(PYTHON) tools/generate_ntt9_first_oracle.py --component-oracle generated/gt9x16-component-oracle.json --output generated/gt9x16-ntt9-first-oracle.json
	$(PYTHON) tools/generate_official_stage_partitions.py --source $(UPSTREAM)/ntt.s --output $(OFFICIAL_PARTITIONS)

check:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I$(UPSTREAM) tools/probe_official_layout.c $(OFFICIAL_FORWARD) -o $(BUILD)/probe-official-layout
	$(BUILD)/probe-official-layout $(BUILD)/official-avx2-layout-probe.json
	cmp generated/official-avx2-layout-probe.json $(BUILD)/official-avx2-layout-probe.json
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json --check
	$(PYTHON) tools/generate_stage8_tables.py --json generated/gt9x16-stage8-tables.json --header generated/gt9x16-stage8-tables.h --check
	$(PYTHON) tools/generate_full_forward_tables.py --json generated/gt9x16-component-oracle.json --header generated/gt9x16-full-forward-tables.h --asm-constants generated/gt9x16-ntt16-constants.inc --check
	mkdir -p $(BUILD)/structure
	$(CC) -mavx2 -c $(UPSTREAM)/ntt.s -o $(BUILD)/structure/official-ntt.o
	$(CC) -mavx2 -c $(UPSTREAM)/basemul.s -o $(BUILD)/structure/official-basemul.o
	$(CC) -mavx2 -c $(UPSTREAM)/baseinv.s -o $(BUILD)/structure/official-baseinv.o
	$(CC) -mavx2 -c $(UPSTREAM)/invntt.s -o $(BUILD)/structure/official-invntt.o
	$(PYTHON) tools/audit_ntt_domain_lifecycle.py --ntt-object $(BUILD)/structure/official-ntt.o --basemul-object $(BUILD)/structure/official-basemul.o --baseinv-object $(BUILD)/structure/official-baseinv.o --invntt-object $(BUILD)/structure/official-invntt.o --upstream $(UPSTREAM) --output generated/ntt-domain-lifecycle-audit.json --check
	$(PYTHON) tools/generate_pipeline_layout.py --component-oracle generated/gt9x16-component-oracle.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --output generated/gt9x16-pipeline-layout.json --cost-output generated/gt9x16-representation-cost-matrix.json --check
	$(PYTHON) tools/generate_ntt9_first_oracle.py --component-oracle generated/gt9x16-component-oracle.json --output generated/gt9x16-ntt9-first-oracle.json --check
	$(PYTHON) tools/generate_official_stage_partitions.py --source $(UPSTREAM)/ntt.s --output $(OFFICIAL_PARTITIONS) --check
	$(PYTHON) $(REPO_ROOT)/scripts/check_supercop_experiment.py --experiment $(EXPERIMENT) --parameter $(PARAMETER)
	$(PYTHON) tests/test_gt9x16_oracle.py
	$(PYTHON) tests/test_ntt9_first_oracle.py
	$(PYTHON) tests/test_representation_contract.py
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) tests/test_gt9x16_shear.c -o $(BUILD)/test-gt9x16-shear
	$(BUILD)/test-gt9x16-shear
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c ref/ntt9_reference.c $(NTT16_ASM) tests/test_gt9x16_ntt16_asm.c -o $(BUILD)/test-gt9x16-ntt16-asm
	$(BUILD)/test-gt9x16-ntt16-asm
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -I$(UPSTREAM) tests/test_official_stage_partitions.c $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) -o $(BUILD)/test-official-stage-partitions
	$(BUILD)/test-official-stage-partitions
	$(CC) $(CFLAGS_STRICT) -O3 $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) tests/test_full_forward.c -o $(BUILD)/test-full-forward
	$(BUILD)/test-full-forward

sanitize:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) tests/test_gt9x16_shear.c -o $(BUILD)/test-gt9x16-shear-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-shear-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c ref/ntt9_reference.c $(NTT16_ASM) tests/test_gt9x16_ntt16_asm.c -o $(BUILD)/test-gt9x16-ntt16-asm-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-ntt16-asm-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) tests/test_full_forward.c -o $(BUILD)/test-full-forward-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-full-forward-sanitize

audit:
	mkdir -p $(BUILD) $(BUILD)/full-audit $(BUILD)/structure generated
	$(CC) $(CFLAGS_STRICT) -O3 -fno-inline $(CPPFLAGS_LOCAL) -c src/gt9x16_shear.c -o $(BUILD)/gt9x16-shear.o
	$(CC) $(CFLAGS_STRICT) -O3 -fno-inline $(CPPFLAGS_LOCAL) -S src/gt9x16_shear.c -o generated/gt9x16-shear.s
	$(PYTHON) tools/audit_gt9x16_shear.py --object $(BUILD)/gt9x16-shear.o --assembly generated/gt9x16-shear.s --compiler $(CC) --cflags "$(CFLAGS_STRICT) -O3 -fno-inline" --output generated/gt9x16-shear-audit.json
	$(CC) -mavx2 -I. -c $(NTT16_ASM) -o $(BUILD)/gt9x16-ntt16.o
	$(PYTHON) tools/audit_gt9x16_ntt16_asm.py --object $(BUILD)/gt9x16-ntt16.o --source $(NTT16_ASM) --macro-source asm/gt9x16_ntt16.inc --extra-macro-source asm/gt9x16_ntt16_c2.inc --extra-macro-source asm/gt9x16_ntt16_c4.inc --extra-macro-source asm/gt9x16_ntt9.inc --compiler $(CC) --cflags=-mavx2 --output generated/gt9x16-ntt16-audit.json
	$(CC) $(CFLAGS_STRICT) -O3 -fstack-usage $(CPPFLAGS_LOCAL) -c src/top_split_adapter.c -o $(BUILD)/full-audit/top_split_adapter.o
	$(CC) $(CFLAGS_STRICT) -O3 -fstack-usage $(CPPFLAGS_LOCAL) -c src/gt9x16_forward.c -o $(BUILD)/full-audit/gt9x16_forward.o
	$(CC) $(CFLAGS_STRICT) -O3 -fstack-usage $(CPPFLAGS_LOCAL) -c ref/ntt9_reference.c -o $(BUILD)/full-audit/ntt9_reference.o
	$(PYTHON) tools/audit_full_forward.py --object $(BUILD)/full-audit/top_split_adapter.o --object $(BUILD)/full-audit/gt9x16_forward.o --object $(BUILD)/full-audit/ntt9_reference.o --stack-usage $(BUILD)/full-audit/top_split_adapter.su --stack-usage $(BUILD)/full-audit/gt9x16_forward.su --stack-usage $(BUILD)/full-audit/ntt9_reference.su --compiler $(CC) --cflags "$(CFLAGS_STRICT) -O3 -fstack-usage" --output generated/gt9x16-full-forward-audit.json
	$(CC) $(PAIRED_CFLAGS) $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) bench/bench_full_forward_paired.c -o $(BUILD)/structure/gt-pipeline
	$(CC) -mavx2 -c $(UPSTREAM)/ntt.s -o $(BUILD)/structure/official-ntt.o
	$(CC) -mavx2 -c $(UPSTREAM)/basemul.s -o $(BUILD)/structure/official-basemul.o
	$(CC) -mavx2 -c $(UPSTREAM)/baseinv.s -o $(BUILD)/structure/official-baseinv.o
	$(CC) -mavx2 -c $(UPSTREAM)/invntt.s -o $(BUILD)/structure/official-invntt.o
	$(PYTHON) tools/audit_ntt_domain_lifecycle.py --ntt-object $(BUILD)/structure/official-ntt.o --basemul-object $(BUILD)/structure/official-basemul.o --baseinv-object $(BUILD)/structure/official-baseinv.o --invntt-object $(BUILD)/structure/official-invntt.o --upstream $(UPSTREAM) --output generated/ntt-domain-lifecycle-audit.json
	$(PYTHON) tools/generate_pipeline_layout.py --component-oracle generated/gt9x16-component-oracle.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --output generated/gt9x16-pipeline-layout.json --cost-output generated/gt9x16-representation-cost-matrix.json --check
	$(PYTHON) tools/audit_pipeline_structure.py --candidate-elf $(BUILD)/structure/gt-pipeline --official-object $(BUILD)/structure/official-ntt.o --official-object $(BUILD)/structure/official-basemul.o --official-object $(BUILD)/structure/official-baseinv.o --official-object $(BUILD)/structure/official-invntt.o --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output generated/gt9x16-pipeline-structure-audit.json

bench-local:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) bench/bench_gt9x16_shear.c -o $(BUILD)/bench-gt9x16-shear
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-shear

bench-local-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) bench/bench_gt9x16_shear.c -o $(BUILD)/bench-gt9x16-shear
	$(PYTHON) tools/run_shear_benchmark.py --binary $(BUILD)/bench-gt9x16-shear --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-shear-audit.json --output results/$(RESULT_TAG)/shear-diagnostic.json

bench-ntt16:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16.c -o $(BUILD)/bench-gt9x16-ntt16
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16

bench-ntt16-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16.c -o $(BUILD)/bench-gt9x16-ntt16
	$(PYTHON) tools/run_ntt16_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/ntt16-diagnostic.json

bench-c2:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16_c2.c -o $(BUILD)/bench-gt9x16-ntt16-c2
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16-c2

bench-c2-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16_c2.c -o $(BUILD)/bench-gt9x16-ntt16-c2
	$(PYTHON) tools/run_c2_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16-c2 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/c2-diagnostic.json

bench-c3:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c3.c -o $(BUILD)/bench-gt9x16-ntt16-c3
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16-c3

bench-c3-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c3.c -o $(BUILD)/bench-gt9x16-ntt16-c3
	$(PYTHON) tools/run_c3_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16-c3 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/c3-diagnostic.json

bench-c4:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c4.c -o $(BUILD)/bench-gt9x16-ntt16-c4
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16-c4

bench-c4-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c4.c -o $(BUILD)/bench-gt9x16-ntt16-c4
	$(PYTHON) tools/run_c4_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16-c4 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/c4-diagnostic.json

bench-official-stages:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) bench/bench_official_stages_paired.c $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) -o $(BUILD)/bench-official-stages
	taskset -c $(BENCH_CPU) $(BUILD)/bench-official-stages

bench-official-stages-record:
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) bench/bench_official_stages_paired.c $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) -o $(BUILD)/bench-official-stages
	$(PYTHON) tools/run_official_stage_benchmark.py --binary $(BUILD)/bench-official-stages --cpu $(BENCH_CPU) --launches 9 --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --upstream upstream --output results/$(RESULT_TAG)/official-stage-paired.json

bench-transform-paired:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) bench/bench_full_forward_paired.c -o $(BUILD)/bench-full-forward-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-full-forward-paired

bench-transform-paired-record:
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) bench/bench_full_forward_paired.c -o $(BUILD)/bench-full-forward-paired
	$(PYTHON) tools/run_transform_paired.py --binary $(BUILD)/bench-full-forward-paired --cpu $(BENCH_CPU) --launches 9 --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/transform-paired.json

supercop-check:
	test -n "$(SUPERCOP_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/prepare_supercop.py --supercop-root $(SUPERCOP_ROOT) --verify-only

supercop-install-candidate:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	tools/install-supercop-candidate.sh "$(SUPERCOP_CAMPAIGN_ROOT)"

supercop-kem-short supercop-kem-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode native-kem --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-poly-short supercop-poly-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-poly --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-paired-serious:
	test -n "$(OFFICIAL_MEASURE)"; test -n "$(CANDIDATE_MEASURE)"
	test -n "$(OFFICIAL_MEASURE_REVERSED)"; test -n "$(CANDIDATE_MEASURE_REVERSED)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_paired.py --official $(OFFICIAL_MEASURE) --candidate $(CANDIDATE_MEASURE) --official-reversed $(OFFICIAL_MEASURE_REVERSED) --candidate-reversed $(CANDIDATE_MEASURE_REVERSED) --compiler-recipe "$${FIXED_COMPILER_RECIPE:-O3GC}" --cpu $(BENCH_CPU) --output $(RESULTS)/paired

supercop-promotion-report:
	$(PYTHON) $(REPO_ROOT)/scripts/supercop_promotion_report.py --paired $(PAIRED_RESULTS) --native-official $(NATIVE_OFFICIAL_RESULTS) --native-candidate $(NATIVE_CANDIDATE_RESULTS) --poly-official $(POLY_OFFICIAL_RESULTS) --poly-candidate $(POLY_CANDIDATE_RESULTS) --output $(RESULTS)/promotion.json
