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
COMPILER_ARG := $(if $(SUPERCOP_COMPILER_WRAPPER),--compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER),)

.PHONY: generate check sanitize audit supercop-check supercop-install-candidate \
 supercop-kem-short supercop-kem-serious supercop-poly-short \
 supercop-poly-serious supercop-paired-serious supercop-promotion-report

generate:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json

check:
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json --check
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
