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

.PHONY: all setup validate compare-kat cycles-compare compare impl-compare impl-compare-kat \
	clean clean-results help run

all: validate

setup:
	@mkdir -p $(BUILD_DIR) $(KAT_RESULTS_DIR) $(CYCLES_RESULTS_DIR)

validate: compare-kat

compare-kat impl-compare-kat: setup
	@python3 $(BENCH_DRIVER) kat $(COMPARE_ARGS)

cycles-compare compare impl-compare: setup
	@python3 $(BENCH_DRIVER) compare $(COMPARE_ARGS)

run: compare

clean:
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
