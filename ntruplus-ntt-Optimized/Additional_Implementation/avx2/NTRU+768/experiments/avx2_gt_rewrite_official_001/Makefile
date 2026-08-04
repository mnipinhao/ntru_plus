CC ?= gcc
BACKEND ?= official

REPO_ROOT := $(abspath ../../../../../..)
OFFICIAL_ROOT := $(REPO_ROOT)/third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
BUILD_DIR ?= build
OFFICIAL_OBJ_DIR := $(BUILD_DIR)/official

CPPFLAGS := -I$(OFFICIAL_ROOT) -Isrc
COMMON_FLAGS := -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-O3 -fomit-frame-pointer
TEST_CFLAGS := -std=c11 -Wall -Wextra -Wpedantic -Wshadow \
	-Wconversion -Wstrict-prototypes $(COMMON_FLAGS)
OFFICIAL_CFLAGS := -std=c11 -Wall -Wextra $(COMMON_FLAGS)

OFFICIAL_ASM_NAMES := ntt invntt basemul baseinv pack
OFFICIAL_ASM_OBJS := $(addprefix $(OFFICIAL_OBJ_DIR)/asm/,$(addsuffix .o,$(OFFICIAL_ASM_NAMES)))
OFFICIAL_C_OBJS := $(OFFICIAL_OBJ_DIR)/consts.o $(OFFICIAL_OBJ_DIR)/poly.o
OFFICIAL_OBJS := $(OFFICIAL_ASM_OBJS) $(OFFICIAL_C_OBJS)
ORACLE_OBJS := $(BUILD_DIR)/official_contract.o $(BUILD_DIR)/gt_schoolbook.o
GT_OBJS := $(BUILD_DIR)/gt_backend.o $(BUILD_DIR)/gt_forward_avx2.o \
	$(BUILD_DIR)/gt_inverse_avx2.o \
	$(BUILD_DIR)/gt_basemul_avx2.o $(BUILD_DIR)/gt_baseinv_avx2.o \
	$(BUILD_DIR)/gt_generated_tables.o
SCALAR_TEST_OBJS := $(BUILD_DIR)/test_scalar_gt.o $(BUILD_DIR)/gt_schoolbook.o $(GT_OBJS)
BM32_TEST_OBJS := $(BUILD_DIR)/test_bm32.o $(BUILD_DIR)/gt_schoolbook.o $(GT_OBJS)
KEM_ASM_NAMES := add cbd crepmod3
KEM_ASM_OBJS := $(addprefix $(OFFICIAL_OBJ_DIR)/asm/,$(addsuffix .o,$(KEM_ASM_NAMES)))
KEM_SUPPORT_OBJS := $(KEM_ASM_OBJS) $(OFFICIAL_OBJ_DIR)/symmetric.o \
	$(OFFICIAL_OBJ_DIR)/fips202/fips202.o \
	$(OFFICIAL_OBJ_DIR)/fips202/KeccakP-1600-AVX2.o \
	$(OFFICIAL_OBJ_DIR)/kat/rng.o $(OFFICIAL_OBJ_DIR)/kat/aes.o

.PHONY: all official-dry-run official-test official-kat-build \
	official-contract generate check-generated scalar-test check clean \
	sanitize audit-release

.PHONY: bm32-test
.PHONY: kem-differential
.PHONY: kat-differential
.PHONY: selected-kat-build selected-kat-run backend-selector-audit

ifeq ($(BACKEND),official)
SELECTED_KEM_OBJ := $(BUILD_DIR)/official_kem.o
SELECTED_GT_OBJS :=
else ifeq ($(BACKEND),gt)
SELECTED_KEM_OBJ := $(BUILD_DIR)/gt_kem_public.o
SELECTED_GT_OBJS := $(GT_OBJS)
else
$(error BACKEND must be official or gt)
endif
SELECTED_KAT_BIN := $(BUILD_DIR)/PQCgenKAT_selected_$(BACKEND)
.PHONY: bench-n32 bench-n32-smoke bench-n32-instructions \
	bench-basemul bench-basemul-smoke bench-basemul-instructions \
	bench-kem bench-kem-smoke bench-kem-instructions \
	bench-kem-reversed \
	bench-stages bench-stages-smoke bench-stages-pmu bench-call-counts \
	bench-stages-pmu-summary round2-amdahl \
	bench-symmetric bench-symmetric-smoke bench-symmetric-pmu \
	bench-round3-coarse-region

all: check

official-dry-run:
	$(MAKE) -C $(OFFICIAL_ROOT) CC=$(CC) -n test
	$(MAKE) -C $(OFFICIAL_ROOT) CC=$(CC) -n PQCgenKAT_kem

official-test:
	$(MAKE) -C $(OFFICIAL_ROOT) CC=$(CC) test
	$(OFFICIAL_ROOT)/build/test

official-kat-build:
	$(MAKE) -C $(OFFICIAL_ROOT) CC=$(CC) PQCgenKAT_kem

$(OFFICIAL_OBJ_DIR)/asm/%.o: $(OFFICIAL_ROOT)/asm/%.s
	@mkdir -p $(@D)
	$(CC) $(COMMON_FLAGS) -c $< -o $@

$(OFFICIAL_OBJ_DIR)/%.o: $(OFFICIAL_ROOT)/%.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(OFFICIAL_CFLAGS) -c $< -o $@

$(OFFICIAL_OBJ_DIR)/fips202/%.o: $(OFFICIAL_ROOT)/fips202/%.c
	@mkdir -p $(@D)
	$(CC) -I$(OFFICIAL_ROOT) $(OFFICIAL_CFLAGS) -c $< -o $@

$(OFFICIAL_OBJ_DIR)/fips202/%.o: $(OFFICIAL_ROOT)/fips202/%.s
	@mkdir -p $(@D)
	$(CC) $(COMMON_FLAGS) -c $< -o $@

$(OFFICIAL_OBJ_DIR)/kat/%.o: $(OFFICIAL_ROOT)/kat/%.c
	@mkdir -p $(@D)
	$(CC) -I$(OFFICIAL_ROOT)/kat $(OFFICIAL_CFLAGS) -c $< -o $@

$(BUILD_DIR)/official_contract.o: tests/official_contract.c src/gt_schoolbook.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_schoolbook.o: src/gt_schoolbook.c src/gt_schoolbook.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_backend.o: src/gt_backend.c src/gt_backend.h generated/gt_generated_tables.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_basemul_avx2.o: src/gt_basemul_avx2.c src/gt_backend.h generated/gt_generated_tables.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_baseinv_avx2.o: src/gt_baseinv_avx2.c src/gt_backend.h src/gt_avx2_arith.h generated/gt_generated_tables.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_forward_avx2.o: src/gt_forward_avx2.c src/gt_backend.h src/gt_avx2_arith.h generated/gt_generated_tables.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_inverse_avx2.o: src/gt_inverse_avx2.c src/gt_backend.h src/gt_avx2_arith.h generated/gt_generated_tables.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/gt_generated_tables.o: generated/gt_generated_tables.c generated/gt_generated_tables.h
	@mkdir -p $(@D)
	$(CC) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/test_scalar_gt.o: tests/test_scalar_gt.c src/gt_backend.h src/gt_schoolbook.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/test_bm32.o: tests/test_bm32.c src/gt_backend.h src/gt_schoolbook.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_n32.o: bench/bench_n32.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_kem.o: bench/bench_kem.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -I$(OFFICIAL_ROOT) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_basemul.o: bench/bench_basemul.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_stages.o: bench/bench_stages.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_call_counts.o: bench/bench_call_counts.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated -I$(OFFICIAL_ROOT) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_symmetric.o: bench/bench_symmetric.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -Igenerated -I$(OFFICIAL_ROOT) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/bench_round3_coarse_region.o: bench/bench_round3_coarse_region.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -I$(OFFICIAL_ROOT) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/official_kem.o: $(OFFICIAL_ROOT)/kem.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(OFFICIAL_CFLAGS) -c $< -o $@

GT_KEM_RENAMES := \
	-Dcrypto_kem_keypair=gt_crypto_kem_keypair \
	-Dcrypto_kem_enc=gt_crypto_kem_enc \
	-Dcrypto_kem_dec=gt_crypto_kem_dec \
	-Dpoly_ntt=gt_poly_ntt \
	-Dpoly_invntt_scale=gt_poly_invntt_scale \
	-Dpoly_basemul=gt_poly_basemul \
	-Dpoly_basemul_scale=gt_poly_basemul_scale \
	-Dpoly_baseinv=gt_poly_baseinv \
	-Dpoly_tobytes=gt_poly_tobytes \
	-Dpoly_frombytes=gt_poly_frombytes

$(BUILD_DIR)/gt_kem.o: $(OFFICIAL_ROOT)/kem.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(OFFICIAL_CFLAGS) $(GT_KEM_RENAMES) -c $< -o $@

COUNTED_KEM_RENAMES := \
	-Dcrypto_kem_keypair=gt_count_crypto_kem_keypair \
	-Dcrypto_kem_enc=gt_count_crypto_kem_enc \
	-Dcrypto_kem_dec=gt_count_crypto_kem_dec \
	-Dpoly_ntt=gt_count_poly_ntt \
	-Dpoly_invntt_scale=gt_count_poly_invntt_scale \
	-Dpoly_basemul=gt_count_poly_basemul \
	-Dpoly_basemul_scale=gt_count_poly_basemul_scale \
	-Dpoly_baseinv=gt_count_poly_baseinv \
	-Dpoly_tobytes=gt_count_poly_tobytes \
	-Dpoly_frombytes=gt_count_poly_frombytes \
	-Dpoly_add=gt_count_poly_add \
	-Dpoly_sub=gt_count_poly_sub \
	-Dpoly_cbd1=gt_count_poly_cbd1 \
	-Dpoly_triple=gt_count_poly_triple \
	-Dpoly_crepmod3=gt_count_poly_crepmod3 \
	-Dpoly_sotp_encode=gt_count_poly_sotp_encode \
	-Dpoly_sotp_decode=gt_count_poly_sotp_decode \
	-Dhash_f=gt_count_hash_f \
	-Dhash_g=gt_count_hash_g \
	-Dhash_h=gt_count_hash_h \
	-Dfips202avx_shake256=gt_count_shake256 \
	-Drandombytes=gt_count_randombytes

$(BUILD_DIR)/gt_kem_counted.o: $(OFFICIAL_ROOT)/kem.c src/gt_backend.h Makefile
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(OFFICIAL_CFLAGS) $(COUNTED_KEM_RENAMES) -c $< -o $@

GT_POLY_RENAMES := \
	-Dpoly_ntt=gt_poly_ntt \
	-Dpoly_invntt_scale=gt_poly_invntt_scale \
	-Dpoly_basemul=gt_poly_basemul \
	-Dpoly_basemul_scale=gt_poly_basemul_scale \
	-Dpoly_baseinv=gt_poly_baseinv \
	-Dpoly_tobytes=gt_poly_tobytes \
	-Dpoly_frombytes=gt_poly_frombytes

$(BUILD_DIR)/gt_kem_public.o: $(OFFICIAL_ROOT)/kem.c src/gt_backend.h
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(OFFICIAL_CFLAGS) $(GT_POLY_RENAMES) -c $< -o $@

$(BUILD_DIR)/test_kem_differential.o: tests/test_kem_differential.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) -I$(OFFICIAL_ROOT) $(TEST_CFLAGS) -c $< -o $@

$(BUILD_DIR)/kat_official_main.o: $(OFFICIAL_ROOT)/kat/PQCgenKAT_kem.c
	@mkdir -p $(@D)
	$(CC) -I$(OFFICIAL_ROOT) -I$(OFFICIAL_ROOT)/kat $(OFFICIAL_CFLAGS) -c $< -o $@

$(BUILD_DIR)/kat_gt_main.o: $(OFFICIAL_ROOT)/kat/PQCgenKAT_kem.c
	@mkdir -p $(@D)
	$(CC) -I$(OFFICIAL_ROOT) -I$(OFFICIAL_ROOT)/kat $(OFFICIAL_CFLAGS) \
		-Dcrypto_kem_keypair=gt_crypto_kem_keypair \
		-Dcrypto_kem_enc=gt_crypto_kem_enc \
		-Dcrypto_kem_dec=gt_crypto_kem_dec -c $< -o $@

$(BUILD_DIR)/official_contract: $(ORACLE_OBJS) $(OFFICIAL_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

official-contract: $(BUILD_DIR)/official_contract
	$(BUILD_DIR)/official_contract | tee $(BUILD_DIR)/official-contract.json
	cmp contracts/official-contract.expected.json $(BUILD_DIR)/official-contract.json

generate:
	python3 tools/generate_gt_rewrite.py

check-generated:
	python3 tools/generate_gt_rewrite.py --check

$(BUILD_DIR)/test_scalar_gt: $(SCALAR_TEST_OBJS) $(OFFICIAL_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

scalar-test: check-generated $(BUILD_DIR)/test_scalar_gt
	$(BUILD_DIR)/test_scalar_gt

$(BUILD_DIR)/test_bm32: $(BM32_TEST_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

bm32-test: check-generated $(BUILD_DIR)/test_bm32
	$(BUILD_DIR)/test_bm32

$(BUILD_DIR)/test_kem_differential: $(BUILD_DIR)/test_kem_differential.o \
	$(BUILD_DIR)/official_kem.o $(BUILD_DIR)/gt_kem.o $(GT_OBJS) \
	$(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

kem-differential: check-generated $(BUILD_DIR)/test_kem_differential
	$(BUILD_DIR)/test_kem_differential

$(BUILD_DIR)/PQCgenKAT_official: $(BUILD_DIR)/kat_official_main.o \
	$(BUILD_DIR)/official_kem.o $(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

$(BUILD_DIR)/PQCgenKAT_gt: $(BUILD_DIR)/kat_gt_main.o $(BUILD_DIR)/gt_kem.o \
	$(GT_OBJS) $(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

kat-differential: check-generated $(BUILD_DIR)/PQCgenKAT_official $(BUILD_DIR)/PQCgenKAT_gt
	mkdir -p $(BUILD_DIR)/kat/official $(BUILD_DIR)/kat/gt
	cd $(BUILD_DIR)/kat/official && ../../PQCgenKAT_official
	cd $(BUILD_DIR)/kat/gt && ../../PQCgenKAT_gt
	cmp $(BUILD_DIR)/kat/official/PQCkemKAT_2336.req $(BUILD_DIR)/kat/gt/PQCkemKAT_2336.req
	cmp $(BUILD_DIR)/kat/official/PQCkemKAT_2336.rsp $(BUILD_DIR)/kat/gt/PQCkemKAT_2336.rsp

$(SELECTED_KAT_BIN): $(BUILD_DIR)/kat_official_main.o \
	$(SELECTED_KEM_OBJ) $(SELECTED_GT_OBJS) $(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

selected-kat-build: $(SELECTED_KAT_BIN)

selected-kat-run: selected-kat-build
	mkdir -p $(BUILD_DIR)/selected/$(BACKEND)
	cd $(BUILD_DIR)/selected/$(BACKEND) && ../../PQCgenKAT_selected_$(BACKEND)

backend-selector-audit:
	$(MAKE) CC=$(CC) BACKEND=official selected-kat-build
	@if nm -g --defined-only $(BUILD_DIR)/PQCgenKAT_selected_official \
		| awk '$$3 ~ /^gt_/ { found=1 } END { exit found ? 0 : 1 }'; then \
		echo 'Official selected binary unexpectedly contains GT symbols'; exit 1; \
	fi
	$(MAKE) CC=$(CC) BACKEND=gt selected-kat-build
	@nm -g --defined-only $(BUILD_DIR)/PQCgenKAT_selected_gt \
		| awk '$$3 ~ /^gt_/ { found=1 } END { exit found ? 0 : 1 }'

$(BUILD_DIR)/bench_n32: $(BUILD_DIR)/bench_n32.o $(GT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

bench-n32-smoke: $(BUILD_DIR)/bench_n32
	$(BUILD_DIR)/bench_n32 --iterations 1000 --samples 4

bench-n32: $(BUILD_DIR)/bench_n32
	$(BUILD_DIR)/bench_n32 --iterations 1000000 --samples 20 | tee $(BUILD_DIR)/n32-benchmark.json

bench-n32-instructions: $(BUILD_DIR)/bench_n32
	perf stat -x, -o results/n32-b1-perf.csv \
		-e cpu_core/cycles/,cpu_core/instructions/ -- \
		$(BUILD_DIR)/bench_n32 --candidate B1 --iterations 1000000 --samples 20 \
		| tee results/n32-b1-run.json
	perf stat -x, -o results/n32-b2-perf.csv \
		-e cpu_core/cycles/,cpu_core/instructions/ -- \
		$(BUILD_DIR)/bench_n32 --candidate B2 --iterations 1000000 --samples 20 \
		| tee results/n32-b2-run.json

$(BUILD_DIR)/bench_basemul: $(BUILD_DIR)/bench_basemul.o $(GT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

bench-basemul-smoke: $(BUILD_DIR)/bench_basemul
	$(BUILD_DIR)/bench_basemul --iterations 100 --samples 4

bench-basemul: $(BUILD_DIR)/bench_basemul
	$(BUILD_DIR)/bench_basemul --iterations 25000 --samples 20 \
		| tee results/basemul-selection.json

bench-basemul-instructions: $(BUILD_DIR)/bench_basemul
	perf stat -x, -o results/bm-a-perf.csv \
		-e cpu_core/cycles/,cpu_core/instructions/ -- \
		$(BUILD_DIR)/bench_basemul --candidate BM-A --iterations 25000 --samples 20 \
		| tee results/bm-a-run.json
	perf stat -x, -o results/bm-b-perf.csv \
		-e cpu_core/cycles/,cpu_core/instructions/ -- \
		$(BUILD_DIR)/bench_basemul --candidate BM-B --iterations 25000 --samples 20 \
		| tee results/bm-b-run.json

$(BUILD_DIR)/bench_kem: $(BUILD_DIR)/bench_kem.o $(BUILD_DIR)/official_kem.o \
	$(BUILD_DIR)/gt_kem.o $(GT_OBJS) $(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

$(BUILD_DIR)/bench_kem_reversed: $(BUILD_DIR)/bench_kem.o \
	$(BUILD_DIR)/gt_kem.o $(BUILD_DIR)/official_kem.o \
	$(OFFICIAL_OBJS) $(GT_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

bench-kem-smoke: $(BUILD_DIR)/bench_kem
	$(BUILD_DIR)/bench_kem --iterations 1 --samples 4

bench-kem: $(BUILD_DIR)/bench_kem
	$(BUILD_DIR)/bench_kem --iterations 100 --samples 20 | tee results/kem-caller-benchmark.json

bench-kem-reversed: $(BUILD_DIR)/bench_kem_reversed
	$(BUILD_DIR)/bench_kem_reversed --iterations 100 --samples 20 \
		| tee results/round3-kem-reversed.json

bench-kem-instructions: $(BUILD_DIR)/bench_kem
	perf stat -x, -o results/kem-official-perf.csv \
		-e cpu_core/cycles/,cpu_core/instructions/ -- \
		$(BUILD_DIR)/bench_kem --candidate official --iterations 100 --samples 20 \
		| tee results/kem-official-run.json
	perf stat -x, -o results/kem-gt-perf.csv \
		-e cpu_core/cycles/,cpu_core/instructions/ -- \
		$(BUILD_DIR)/bench_kem --candidate gt --iterations 100 --samples 20 \
		| tee results/kem-gt-run.json

$(BUILD_DIR)/bench_stages: $(BUILD_DIR)/bench_stages.o $(GT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

bench-stages-smoke: $(BUILD_DIR)/bench_stages
	$(BUILD_DIR)/bench_stages --iterations 100 --samples 4

bench-stages: $(BUILD_DIR)/bench_stages
	$(BUILD_DIR)/bench_stages --iterations 1000000 --samples 20 \
		| tee results/round2-stage-cycles.json

bench-stages-pmu: $(BUILD_DIR)/bench_stages
	@for stage in forward_frontend forward_b1 basemul_bm_a baseinv \
		inverse_b1 inverse_tail tobytes frombytes; do \
		perf stat -x, -o results/round2-$${stage}-perf.csv \
			-e cpu_core/cycles/,cpu_core/instructions/,cpu_core/uops_retired.slots/,cpu_core/mem_inst_retired.all_loads/,cpu_core/mem_inst_retired.all_stores/,cpu_core/mem_load_retired.l1_miss/,cpu_core/branches/,cpu_core/branch-misses/,cpu_core/topdown-fe-bound/,cpu_core/topdown-be-bound/ -- \
			$(BUILD_DIR)/bench_stages --candidate $${stage} \
			--iterations 1000000 --samples 20 \
			> results/round2-$${stage}-run.json || exit; \
	done

bench-stages-pmu-summary:
	python3 tools/summarize_stage_pmu.py

$(BUILD_DIR)/bench_call_counts: $(BUILD_DIR)/bench_call_counts.o \
	$(BUILD_DIR)/gt_kem_counted.o $(GT_OBJS) $(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -o $@

bench-call-counts: $(BUILD_DIR)/bench_call_counts
	$(BUILD_DIR)/bench_call_counts | tee results/round3-call-counts.json

$(BUILD_DIR)/bench_symmetric: $(BUILD_DIR)/bench_symmetric.o $(GT_OBJS) \
	$(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

bench-symmetric-smoke: $(BUILD_DIR)/bench_symmetric
	$(BUILD_DIR)/bench_symmetric --iterations 100 --samples 4

bench-symmetric: $(BUILD_DIR)/bench_symmetric
	bash tools/run_round3_direct.sh $(BUILD_DIR)/bench_symmetric
	python3 tools/merge_round3_direct.py \
		| tee results/round3-symmetric-cycles.json

bench-symmetric-pmu: $(BUILD_DIR)/bench_symmetric
	bash tools/run_round3_pmu.sh $(BUILD_DIR)/bench_symmetric
	python3 tools/summarize_round3_pmu.py \
		| tee results/round3-symmetric-pmu.stdout.json

$(BUILD_DIR)/bench_round3_coarse_region: \
		$(BUILD_DIR)/bench_round3_coarse_region.o $(BUILD_DIR)/official_kem.o \
		$(BUILD_DIR)/gt_kem.o $(GT_OBJS) $(OFFICIAL_OBJS) $(KEM_SUPPORT_OBJS)
	$(CC) $(COMMON_FLAGS) $^ -lm -o $@

bench-round3-coarse-region: $(BUILD_DIR)/bench_round3_coarse_region
	PROFILE_SCOPE=shared_differential \
		$(BUILD_DIR)/bench_round3_coarse_region --iterations 100 --samples 20 \
		| tee results/round3-coarse-shared-differential.json

.PHONY: round3-attribution
round3-attribution: results/round3-symmetric-cycles.json \
		results/round3-call-counts.json results/kem-caller-benchmark.json \
		results/round3-kem-reversed.json \
		results/round3-coarse-shared-differential.json \
		results/round3-symmetric-pmu.json
	python3 tools/analyze_round3.py

round2-amdahl: results/round2-stage-cycles.json results/round2-call-counts.json
	python3 tools/analyze_round2.py

audit-release: $(GT_OBJS)
	python3 tools/audit_release.py --build-dir $(BUILD_DIR) | tee results/release-audit.json

SANITIZER_FLAGS := -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined

sanitize:
	ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 \
	UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
	$(MAKE) BUILD_DIR=$(BUILD_DIR)/sanitize \
		COMMON_FLAGS='$(SANITIZER_FLAGS)' \
		scalar-test bm32-test kem-differential

check: official-contract scalar-test bm32-test kem-differential kat-differential \
	backend-selector-audit audit-release sanitize

clean:
	$(RM) -r $(BUILD_DIR)
