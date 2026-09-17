PARAMETER := 864
REPO_ROOT := $(shell git rev-parse --show-toplevel)
EXPERIMENT := $(CURDIR)
PYTHON ?= python3
BENCH_CPU ?= 1
SUPERCOP_IMPLEMENTATION ?= avx2-gt9x16-exp001
RESULT_TAG ?= $(shell date +%Y%m%d-%H%M%S)
SUPERCOP_FRESH_LAUNCHES_SHORT ?= 3
SUPERCOP_FRESH_LAUNCHES_SERIOUS ?= 9
RESULTS := $(EXPERIMENT)/results/$(RESULT_TAG)
COMMON_GENERATOR := $(REPO_ROOT)/ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/gt9x16/generate_gt9x16.py
P1_D3_GENERATOR := tools/generate_p1_d3_packet_map.py
P1_D3_MODEL := generated/gt9x16-model.json
P1_D3_MAP := generated/p1-d3-packet-map.json
P1_D3_ARGS := --model $(P1_D3_MODEL) --ntt-source upstream/supercop-avx2/ntt.s --pack-source upstream/supercop-avx2/pack.s --output $(P1_D3_MAP)
P3_GENERATOR := $(REPO_ROOT)/ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/gt9x16/generate_native_component_consumer.py
P3_MAP := generated/p3-native-component-consumer.json
P3_ARGS := --parameter $(PARAMETER) --model $(P1_D3_MODEL) --basemul-source upstream/supercop-avx2/basemul.s --invntt-source upstream/supercop-avx2/invntt.s --output $(P3_MAP)
D3_VPMADDWD_GENERATOR := tools/generate_d3_vpmaddwd_reduction_gate.py
D3_VPMADDWD_MAP := generated/d3-vpmaddwd-reduction-gate.json
D3_VPMADDWD_TEST := tests/test_d3_vpmaddwd_mr32.c
D3_VPMADDWD_ARGS := --basemul-source upstream/supercop-avx2/basemul.s --p3-map $(P3_MAP) --output $(D3_VPMADDWD_MAP)
D3_ASM_MASK_GENERATOR := tools/generate_d3_vpmaddwd_asm_masks.py
D3_ASM_MASKS := generated/d3-vpmaddwd-asm-masks.inc
D3_ASM := asm/d3_vpmaddwd_tile.s
D3_ASM_HEADER := src/d3_vpmaddwd_tile.h
D3_ASM_TEST := tests/test_d3_vpmaddwd_tile.c
D3_ASM_AUDITOR := tools/audit_d3_vpmaddwd_tile.py
D3_ASM_AUDIT := generated/d3-vpmaddwd-asm0-audit.json
D3_ASM_TEST_BIN := /tmp/ntruplus864-exp001-d3-asm0-test
D3_ASM_RESULT ?= results/d3-vpmaddwd-asm0-intel155h-20260910-001/tile-paired.json
COMPILER_ARG := $(if $(SUPERCOP_COMPILER_WRAPPER),--compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER),)

.PHONY: generate check sanitize audit p1-map p1-map-check p3-map p3-map-check d3-vpmaddwd-gate d3-vpmaddwd-gate-check d3-asm0 d3-asm0-check d3-asm0-price supercop-check supercop-install-candidate \
 supercop-kem-short supercop-kem-serious supercop-poly-short \
 supercop-poly-serious supercop-paired-serious supercop-promotion-report

generate:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json

p1-map: generate
	$(PYTHON) $(P1_D3_GENERATOR) $(P1_D3_ARGS)

p1-map-check:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output $(P1_D3_MODEL) --check
	$(PYTHON) $(P1_D3_GENERATOR) $(P1_D3_ARGS) --check

p3-map: generate
	$(PYTHON) $(P3_GENERATOR) $(P3_ARGS)

p3-map-check:
	$(PYTHON) $(P3_GENERATOR) $(P3_ARGS) --check

d3-vpmaddwd-gate: p3-map
	$(PYTHON) $(D3_VPMADDWD_GENERATOR) $(D3_VPMADDWD_ARGS)

d3-vpmaddwd-gate-check:
	$(PYTHON) $(D3_VPMADDWD_GENERATOR) $(D3_VPMADDWD_ARGS) --avx2-test $(D3_VPMADDWD_TEST) --check

d3-asm0: d3-vpmaddwd-gate
	$(PYTHON) $(D3_ASM_MASK_GENERATOR) --gate $(D3_VPMADDWD_MAP) --output $(D3_ASM_MASKS)
	$(PYTHON) $(D3_ASM_AUDITOR) --asm $(D3_ASM) --output $(D3_ASM_AUDIT)
	$(CC) -O2 -Wall -Wextra -Werror -mavx2 -I./src -I. $(D3_ASM_TEST) $(D3_ASM) -o $(D3_ASM_TEST_BIN)
	$(D3_ASM_TEST_BIN)

d3-asm0-check:
	$(PYTHON) $(D3_ASM_MASK_GENERATOR) --gate $(D3_VPMADDWD_MAP) --output $(D3_ASM_MASKS) --check
	$(PYTHON) $(D3_ASM_AUDITOR) --asm $(D3_ASM) --output $(D3_ASM_AUDIT) --check
	$(CC) -O2 -Wall -Wextra -Werror -mavx2 -I./src -I. $(D3_ASM_TEST) $(D3_ASM) -o $(D3_ASM_TEST_BIN)
	$(D3_ASM_TEST_BIN)

d3-asm0-price: d3-asm0-check
	$(PYTHON) tools/run_d3_vpmaddwd_tile_benchmark.py --cpu $(BENCH_CPU) --launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --output $(D3_ASM_RESULT)

check:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json --check
	$(PYTHON) $(P1_D3_GENERATOR) $(P1_D3_ARGS) --check
	$(PYTHON) $(P3_GENERATOR) $(P3_ARGS) --check
	$(PYTHON) $(D3_VPMADDWD_GENERATOR) $(D3_VPMADDWD_ARGS) --avx2-test $(D3_VPMADDWD_TEST) --check
	$(PYTHON) $(D3_ASM_MASK_GENERATOR) --gate $(D3_VPMADDWD_MAP) --output $(D3_ASM_MASKS) --check
	$(PYTHON) $(D3_ASM_AUDITOR) --asm $(D3_ASM) --output $(D3_ASM_AUDIT) --check
	$(CC) -O2 -Wall -Wextra -Werror -mavx2 -I./src -I. $(D3_ASM_TEST) $(D3_ASM) -o $(D3_ASM_TEST_BIN)
	$(D3_ASM_TEST_BIN)
	$(PYTHON) $(REPO_ROOT)/scripts/check_supercop_experiment.py --experiment $(EXPERIMENT) --parameter $(PARAMETER)

sanitize audit: check
	@echo "$@ gate is intentionally unavailable until candidate-specific tests exist" >&2
	@exit 2

supercop-check:
	test -n "$(SUPERCOP_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/prepare_supercop.py --supercop-root $(SUPERCOP_ROOT) --verify-only

supercop-install-candidate:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	tools/install-supercop-candidate.sh "$(SUPERCOP_CAMPAIGN_ROOT)"

supercop-kem-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode native-kem --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-kem-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode native-kem --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-poly-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-poly --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-poly-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-poly --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-paired-serious:
	test -n "$(OFFICIAL_MEASURE)"; test -n "$(CANDIDATE_MEASURE)"
	test -n "$(OFFICIAL_MEASURE_REVERSED)"; test -n "$(CANDIDATE_MEASURE_REVERSED)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_paired.py --official $(OFFICIAL_MEASURE) --candidate $(CANDIDATE_MEASURE) --official-reversed $(OFFICIAL_MEASURE_REVERSED) --candidate-reversed $(CANDIDATE_MEASURE_REVERSED) --compiler-recipe "$${FIXED_COMPILER_RECIPE:-O3GC}" --cpu $(BENCH_CPU) --output $(RESULTS)/paired

supercop-promotion-report:
	$(PYTHON) $(REPO_ROOT)/scripts/supercop_promotion_report.py --paired $(PAIRED_RESULTS) --native-official $(NATIVE_OFFICIAL_RESULTS) --native-candidate $(NATIVE_CANDIDATE_RESULTS) --poly-official $(POLY_OFFICIAL_RESULTS) --poly-candidate $(POLY_CANDIDATE_RESULTS) --output $(RESULTS)/promotion.json
