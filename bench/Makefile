CC ?= gcc
CFLAGS ?= -O3 -march=native -Wall -Wextra -Wpedantic -std=c99
LDFLAGS ?= -lm

BASELINE_ROOT = ../ntruplus-KpqC-Final
OPTIMIZED_ROOT = ../ntruplus-ntt-Optimized
PARAM_SET ?= NTRU+768

BENCH_DRIVER = ./bench_impls.py
DEFAULT_IMPL_A = $(BASELINE_ROOT)/Reference_Implementation/$(PARAM_SET)
DEFAULT_IMPL_B = $(OPTIMIZED_ROOT)/Optimized_Implementation/$(PARAM_SET)
IMPL_A ?= $(DEFAULT_IMPL_A)
IMPL_B ?= $(DEFAULT_IMPL_B)
LABEL_A ?=
LABEL_B ?=

BUILD_DIR = build
RESULTS_DIR = results
KAT_RESULTS_DIR = $(RESULTS_DIR)/kat
CYCLES_RESULTS_DIR = $(RESULTS_DIR)/cycles
RUN_TAG ?= $(shell date +%Y%m%d_%H%M%S)

CYCLE_ITERATIONS ?= 1000
CYCLE_WARMUP ?= 100

COMPARE_ARGS = --impl-a "$(IMPL_A)" --impl-b "$(IMPL_B)" --run-tag "$(RUN_TAG)" \
	--iterations $(CYCLE_ITERATIONS) --warmup $(CYCLE_WARMUP) \
	$(if $(LABEL_A),--label-a "$(LABEL_A)") \
	$(if $(LABEL_B),--label-b "$(LABEL_B)")

LEGACY_IMPL = $(BASELINE_ROOT)/Reference_Implementation/$(PARAM_SET)
LEGACY_INCLUDES = -I$(LEGACY_IMPL) -I$(LEGACY_IMPL)/fips202
LEGACY_SOURCES = $(LEGACY_IMPL)/kem.c \
                 $(LEGACY_IMPL)/poly.c \
                 $(LEGACY_IMPL)/ntt.c \
                 $(LEGACY_IMPL)/symmetric.c \
                 $(LEGACY_IMPL)/randombytes.c \
                 $(LEGACY_IMPL)/fips202/fips202.c

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

.PHONY: all setup validate compare-kat cycles-compare compare impl-compare impl-compare-kat \
	clean clean-results help run run-all bottleneck-analysis function-test \
	comprehensive-analysis aarch64-benchmark aarch64-comparison

all: validate

setup:
	@mkdir -p $(BUILD_DIR) $(KAT_RESULTS_DIR) $(CYCLES_RESULTS_DIR)

validate: compare-kat

compare-kat impl-compare-kat: setup
	@python3 $(BENCH_DRIVER) kat $(COMPARE_ARGS)

cycles-compare compare impl-compare: setup
	@python3 $(BENCH_DRIVER) compare $(COMPARE_ARGS)

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
	rm -f $(BOTTLENECK_PROFILER) $(INDIVIDUAL_FUNCTION_TEST) $(COMPREHENSIVE_PROFILER) \
		$(AARCH64_BENCHMARK) $(AARCH64_COMPARISON)
	rm -rf $(BUILD_DIR)/*

clean-results:
	rm -rf $(KAT_RESULTS_DIR)/* $(CYCLES_RESULTS_DIR)/*

help:
	@echo "NTRU+ benchmark/validation targets"
	@echo ""
	@echo "Default compare flow:"
	@echo "  make compare"
	@echo "  make compare-kat"
	@echo ""
	@echo "Compare arbitrary implementations:"
	@echo "  make impl-compare IMPL_A=../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768 IMPL_B=../ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768 LABEL_A=kpqc_aarch64 LABEL_B=ntt_opt"
	@echo ""
	@echo "Useful vars:"
	@echo "  PARAM_SET=<NTRU+768|NTRU+864|NTRU+1152>    # default compare only"
	@echo "  IMPL_A=<path> IMPL_B=<path>                # arbitrary implementation dirs"
	@echo "  LABEL_A=<name> LABEL_B=<name>              # optional report labels"
	@echo "  RUN_TAG=<label>                            # result directory suffix"
	@echo "  CYCLE_ITERATIONS=<n>                       # default 1000"
	@echo "  CYCLE_WARMUP=<n>                           # default 100"
	@echo ""
	@echo "Legacy analysis targets:"
	@echo "  make bottleneck-analysis function-test comprehensive-analysis"
