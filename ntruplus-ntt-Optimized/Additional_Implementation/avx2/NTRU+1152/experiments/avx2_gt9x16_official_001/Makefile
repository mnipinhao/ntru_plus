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

.PHONY: generate check sanitize audit bench-local bench-local-record supercop-check supercop-install-candidate \
 supercop-kem-short supercop-kem-serious supercop-poly-short \
 supercop-poly-serious supercop-paired-serious supercop-promotion-report

generate:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json
	$(PYTHON) tools/generate_stage8_tables.py --json generated/gt9x16-stage8-tables.json --header generated/gt9x16-stage8-tables.h

check:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json --check
	$(PYTHON) tools/generate_stage8_tables.py --json generated/gt9x16-stage8-tables.json --header generated/gt9x16-stage8-tables.h --check
	$(PYTHON) $(REPO_ROOT)/scripts/check_supercop_experiment.py --experiment $(EXPERIMENT) --parameter $(PARAMETER)
	$(PYTHON) tests/test_gt9x16_oracle.py
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) tests/test_gt9x16_shear.c -o $(BUILD)/test-gt9x16-shear
	$(BUILD)/test-gt9x16-shear

sanitize:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) tests/test_gt9x16_shear.c -o $(BUILD)/test-gt9x16-shear-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-shear-sanitize

audit:
	mkdir -p $(BUILD) generated
	$(CC) $(CFLAGS_STRICT) -O3 -fno-inline $(CPPFLAGS_LOCAL) -c src/gt9x16_shear.c -o $(BUILD)/gt9x16-shear.o
	$(CC) $(CFLAGS_STRICT) -O3 -fno-inline $(CPPFLAGS_LOCAL) -S src/gt9x16_shear.c -o generated/gt9x16-shear.s
	$(PYTHON) tools/audit_gt9x16_shear.py --object $(BUILD)/gt9x16-shear.o --assembly generated/gt9x16-shear.s --compiler $(CC) --cflags "$(CFLAGS_STRICT) -O3 -fno-inline" --output generated/gt9x16-shear-audit.json

bench-local:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) bench/bench_gt9x16_shear.c -o $(BUILD)/bench-gt9x16-shear
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-shear

bench-local-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) bench/bench_gt9x16_shear.c -o $(BUILD)/bench-gt9x16-shear
	$(PYTHON) tools/run_shear_benchmark.py --binary $(BUILD)/bench-gt9x16-shear --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-shear-audit.json --output results/$(RESULT_TAG)/shear-diagnostic.json

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
