CC = gcc
CFLAGS = -O3 -march=native -Wall -Wextra -Wpedantic -std=c99
LDFLAGS = -lm

BASELINE_ROOT = ../ntruplus-KpqC-Final
OPTIMIZED_ROOT = ../ntruplus-Optimized
PARAM_SET = NTRU+768
IMPL_DIR = Reference_Implementation/$(PARAM_SET)

BASELINE_IMPL = $(BASELINE_ROOT)/$(IMPL_DIR)
OPTIMIZED_IMPL = $(OPTIMIZED_ROOT)/$(IMPL_DIR)

BASELINE_INCLUDES = -I$(BASELINE_IMPL) -I$(BASELINE_IMPL)/fips202
OPTIMIZED_INCLUDES = -I$(OPTIMIZED_IMPL) -I$(OPTIMIZED_IMPL)/fips202

BASELINE_SOURCES = $(BASELINE_IMPL)/kem.c \
                   $(BASELINE_IMPL)/poly.c \
                   $(BASELINE_IMPL)/ntt.c \
                   $(BASELINE_IMPL)/symmetric.c \
                   $(BASELINE_IMPL)/randombytes.c \
                   $(BASELINE_IMPL)/fips202/fips202.c
OPTIMIZED_SOURCES = $(OPTIMIZED_IMPL)/kem.c \
                    $(OPTIMIZED_IMPL)/poly.c \
                    $(OPTIMIZED_IMPL)/ntt.c \
                    $(OPTIMIZED_IMPL)/symmetric.c \
                    $(OPTIMIZED_IMPL)/randombytes.c \
                    $(OPTIMIZED_IMPL)/fips202/fips202.c

BASELINE_KAT_SOURCES = $(BASELINE_IMPL)/kat/PQCgenKAT_kem.c \
                       $(BASELINE_IMPL)/kat/aes.c \
                       $(BASELINE_IMPL)/kat/rng.c
OPTIMIZED_KAT_SOURCES = $(OPTIMIZED_IMPL)/kat/PQCgenKAT_kem.c \
                        $(OPTIMIZED_IMPL)/kat/aes.c \
                        $(OPTIMIZED_IMPL)/kat/rng.c

BUILD_DIR = build
RESULTS_DIR = results
KAT_RESULTS_DIR = $(RESULTS_DIR)/kat
CYCLES_RESULTS_DIR = $(RESULTS_DIR)/cycles
RUN_TAG ?= $(shell date +%Y%m%d_%H%M%S)
KAT_RUN_DIR = $(KAT_RESULTS_DIR)/$(RUN_TAG)
CYCLES_RUN_DIR = $(CYCLES_RESULTS_DIR)/$(RUN_TAG)

CYCLE_ITERATIONS ?= 1000
CYCLE_WARMUP ?= 100

LEGACY_INCLUDES = -I$(BASELINE_IMPL) -I$(BASELINE_IMPL)/fips202
LEGACY_SOURCES = $(BASELINE_SOURCES)

BOTTLENECK_PROFILER = ntruplus_bottleneck_profiler
INDIVIDUAL_FUNCTION_TEST = function_speed_test
COMPREHENSIVE_PROFILER = comprehensive_kem_profiler
AARCH64_BENCHMARK = aarch64_kem_benchmark
AARCH64_COMPARISON = aarch64_comparison_profiler

AARCH64_ROOT = $(BASELINE_ROOT)/Additional_Implementation/aarch64/$(PARAM_SET)
AARCH64_INCLUDES = -I$(AARCH64_ROOT) -I$(AARCH64_ROOT)/CE
AARCH64_SOURCES = $(AARCH64_ROOT)/kem.c \
                  $(AARCH64_ROOT)/poly.c \
                  $(AARCH64_ROOT)/symmetric.c \
                  $(AARCH64_ROOT)/randombytes.c \
                  $(AARCH64_ROOT)/CE/fips202.c
AARCH64_ASM = $(AARCH64_ROOT)/asm/add.s \
              $(AARCH64_ROOT)/asm/ntt.s \
              $(AARCH64_ROOT)/asm/base.s \
              $(AARCH64_ROOT)/asm/crepmod3.s \
              $(AARCH64_ROOT)/asm/pack.s \
              $(AARCH64_ROOT)/asm/cbd.s \
              $(AARCH64_ROOT)/CE/f1600.S

.PHONY: all setup validate kat-baseline kat-optimized compare-kat cycles-baseline cycles-optimized \
	cycles-compare compare clean clean-results help run run-all bottleneck-analysis \
	function-test comprehensive-analysis aarch64-benchmark aarch64-comparison

all: validate

setup:
	@mkdir -p $(BUILD_DIR) $(KAT_RESULTS_DIR) $(CYCLES_RESULTS_DIR)

validate: compare-kat

kat-baseline: setup
	@mkdir -p $(KAT_RUN_DIR)
	@echo "[KAT] building baseline generator..."
	$(CC) $(CFLAGS) $(BASELINE_INCLUDES) -o $(BUILD_DIR)/kat_baseline \
		$(BASELINE_KAT_SOURCES) \
		$(BASELINE_IMPL)/kem.c \
		$(BASELINE_IMPL)/poly.c \
		$(BASELINE_IMPL)/ntt.c \
		$(BASELINE_IMPL)/symmetric.c \
		$(BASELINE_IMPL)/fips202/fips202.c
	@rm -f $(BUILD_DIR)/PQCkemKAT_*.req $(BUILD_DIR)/PQCkemKAT_*.rsp
	@cd $(BUILD_DIR) && ./kat_baseline > /dev/null
	@mv $(BUILD_DIR)/PQCkemKAT_*.rsp $(KAT_RUN_DIR)/baseline.rsp
	@mv $(BUILD_DIR)/PQCkemKAT_*.req $(KAT_RUN_DIR)/baseline.req
	@echo "[KAT] baseline output: $(KAT_RUN_DIR)/baseline.rsp"

kat-optimized: setup
	@mkdir -p $(KAT_RUN_DIR)
	@echo "[KAT] building optimized generator..."
	$(CC) $(CFLAGS) $(OPTIMIZED_INCLUDES) -o $(BUILD_DIR)/kat_optimized \
		$(OPTIMIZED_KAT_SOURCES) \
		$(OPTIMIZED_IMPL)/kem.c \
		$(OPTIMIZED_IMPL)/poly.c \
		$(OPTIMIZED_IMPL)/ntt.c \
		$(OPTIMIZED_IMPL)/symmetric.c \
		$(OPTIMIZED_IMPL)/fips202/fips202.c
	@rm -f $(BUILD_DIR)/PQCkemKAT_*.req $(BUILD_DIR)/PQCkemKAT_*.rsp
	@cd $(BUILD_DIR) && ./kat_optimized > /dev/null
	@mv $(BUILD_DIR)/PQCkemKAT_*.rsp $(KAT_RUN_DIR)/optimized.rsp
	@mv $(BUILD_DIR)/PQCkemKAT_*.req $(KAT_RUN_DIR)/optimized.req
	@echo "[KAT] optimized output: $(KAT_RUN_DIR)/optimized.rsp"

compare-kat: kat-baseline kat-optimized
	@mkdir -p $(KAT_RUN_DIR)
	@echo "[KAT] comparing baseline vs optimized..."
	@if diff -q $(KAT_RUN_DIR)/baseline.rsp $(KAT_RUN_DIR)/optimized.rsp > /dev/null; then \
		echo "[KAT] PASS: byte-identical outputs"; \
		printf "PASS\n" > $(KAT_RUN_DIR)/status.txt; \
	else \
		echo "[KAT] FAIL: outputs differ"; \
		diff $(KAT_RUN_DIR)/baseline.rsp $(KAT_RUN_DIR)/optimized.rsp > $(KAT_RUN_DIR)/diff.txt || true; \
		printf "FAIL\n" > $(KAT_RUN_DIR)/status.txt; \
		exit 1; \
	fi

$(BUILD_DIR)/cycle_bench_baseline: cycles/ntruplus_cycle_bench.c
	$(CC) $(CFLAGS) $(BASELINE_INCLUDES) -DBENCH_LABEL=\"baseline\" $< $(BASELINE_SOURCES) -o $@ $(LDFLAGS)

$(BUILD_DIR)/cycle_bench_optimized: cycles/ntruplus_cycle_bench.c
	$(CC) $(CFLAGS) $(OPTIMIZED_INCLUDES) -DBENCH_LABEL=\"optimized\" $< $(OPTIMIZED_SOURCES) -o $@ $(LDFLAGS)

cycles-baseline: setup $(BUILD_DIR)/cycle_bench_baseline
	@mkdir -p $(CYCLES_RUN_DIR)
	@$(BUILD_DIR)/cycle_bench_baseline $(CYCLES_RUN_DIR)/raw_baseline.json $(CYCLE_ITERATIONS) $(CYCLE_WARMUP)
	@echo "[CYCLES] baseline output: $(CYCLES_RUN_DIR)/raw_baseline.json"

cycles-optimized: setup $(BUILD_DIR)/cycle_bench_optimized
	@mkdir -p $(CYCLES_RUN_DIR)
	@$(BUILD_DIR)/cycle_bench_optimized $(CYCLES_RUN_DIR)/raw_optimized.json $(CYCLE_ITERATIONS) $(CYCLE_WARMUP)
	@echo "[CYCLES] optimized output: $(CYCLES_RUN_DIR)/raw_optimized.json"

cycles-compare: compare-kat cycles-baseline cycles-optimized
	@python3 cycles/compare_cycles.py \
		--baseline $(CYCLES_RUN_DIR)/raw_baseline.json \
		--optimized $(CYCLES_RUN_DIR)/raw_optimized.json \
		--output-json $(CYCLES_RUN_DIR)/comparison.json \
		--output-md $(CYCLES_RUN_DIR)/summary.md \
		--tag $(RUN_TAG)
	@echo "[CYCLES] comparison output: $(CYCLES_RUN_DIR)/comparison.json"
	@echo "[CYCLES] summary output: $(CYCLES_RUN_DIR)/summary.md"

compare: cycles-compare
run: compare
run-all: compare bottleneck-analysis function-test comprehensive-analysis

bottleneck-analysis: $(BOTTLENECK_PROFILER)
	@./$(BOTTLENECK_PROFILER)

$(BOTTLENECK_PROFILER): ntruplus_bottleneck_profiler.c
	$(CC) $(CFLAGS) $(LEGACY_INCLUDES) $< $(LEGACY_SOURCES) -o $@ $(LDFLAGS)

function-test: $(INDIVIDUAL_FUNCTION_TEST)
	@./$(INDIVIDUAL_FUNCTION_TEST)

$(INDIVIDUAL_FUNCTION_TEST): function_speed_test.c
	$(CC) $(CFLAGS) $(LEGACY_INCLUDES) $< $(LEGACY_SOURCES) -o $@ $(LDFLAGS)

comprehensive-analysis: $(COMPREHENSIVE_PROFILER)
	@./$(COMPREHENSIVE_PROFILER)

$(COMPREHENSIVE_PROFILER): comprehensive_kem_profiler.c
	$(CC) $(CFLAGS) $(LEGACY_INCLUDES) $< $(LEGACY_SOURCES) -o $@ $(LDFLAGS)

aarch64-benchmark: $(AARCH64_BENCHMARK)
	@./$(AARCH64_BENCHMARK)

$(AARCH64_BENCHMARK): aarch64_kem_benchmark.c
	$(CC) $(CFLAGS) $(AARCH64_INCLUDES) -DSUPPORTS_SHAKE256_ASM $< $(AARCH64_SOURCES) $(AARCH64_ASM) -o $@ $(LDFLAGS)

aarch64-comparison: $(AARCH64_COMPARISON)
	$(CC) $(CFLAGS) $(LEGACY_INCLUDES) $(AARCH64_INCLUDES) aarch64_comparison_profiler.c -o $(AARCH64_COMPARISON) $(LDFLAGS)
	@./$(AARCH64_COMPARISON)

clean:
	rm -f $(BUILD_DIR)/kat_baseline $(BUILD_DIR)/kat_optimized \
		$(BUILD_DIR)/cycle_bench_baseline $(BUILD_DIR)/cycle_bench_optimized \
		$(BOTTLENECK_PROFILER) $(INDIVIDUAL_FUNCTION_TEST) $(COMPREHENSIVE_PROFILER) \
		$(AARCH64_BENCHMARK) $(AARCH64_COMPARISON)
	rm -f $(BUILD_DIR)/PQCkemKAT_*.req $(BUILD_DIR)/PQCkemKAT_*.rsp

clean-results:
	rm -rf $(RESULTS_DIR)/kat/* $(RESULTS_DIR)/cycles/*

help:
	@echo "NTRU+ unified benchmark/validation targets"
	@echo ""
	@echo "Core workflow:"
	@echo "  make compare-kat                      # KAT baseline vs optimized"
	@echo "  make cycles-compare                   # KAT-gated cycle comparison"
	@echo "  make compare                          # Alias of cycles-compare"
	@echo ""
	@echo "Useful vars:"
	@echo "  RUN_TAG=<label>                       # result directory suffix"
	@echo "  CYCLE_ITERATIONS=<n>                  # default 1000"
	@echo "  CYCLE_WARMUP=<n>                      # default 100"
	@echo ""
	@echo "Legacy analysis targets still available:"
	@echo "  make bottleneck-analysis function-test comprehensive-analysis"