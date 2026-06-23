CC =gcc
PYTHON ?= python3
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM = /bin/rm -f
RG ?= grep -E

SOURCES= kem.c symmetric.c poly.c asm/add.s asm/ntt.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s
HEADERS= api.h params.h poly.h symmetric.h


# CE/f1600.S uses Armv8.2-A SHA3-extension instructions (eor3/rax1/xar/bcax).
# Raspberry Pi 5's default toolchain/CPU path does not accept them, so keep the
# portable C SHAKE fallback as the default.  Explicitly set HAS_SHAKE256_ASM=1
# only on systems where both assembler and CPU support +sha3.
HAS_SHAKE256_ASM ?= 0

ifeq ($(HAS_SHAKE256_ASM), 1)
	SOURCES+=CE/fips202.c CE/f1600.S
	HEADERS+=CE/fips202.h
	CFLAGS += -DSUPPORTS_SHAKE256_ASM
else
	SOURCES+=NO_CE/fips202.c
	HEADERS+=NO_CE/fips202.h
endif

.PHONY: all PQCgenKAT_kem test test_stock_base_opt analyze_invntt32_ranges dump_forward_mapping gt_phase123_flow_viewer csv_viewers clean
.PHONY: verify_invntt_constants verify_invntt_layout
.PHONY: test_invntt32_rowpack_kernel_model test_gt_forward_rowpack_output_contract test_gt_rowpack_forward_v3_register_order_contract
.PHONY: test_gt_forward_rowpack_v2_asm test_gt_rowpack_forward_v3_candidate
.PHONY: test_gt_rowpack_soa_oracle test_gt_rowvec_layout_contract test_gt_rowpack_no_entry_no_end_range_contract analyze_gt_rowpack_basemul_output_ranges
.PHONY: test_gt_forward_rowpack_v2_lazyout_asm bench_gt_forward_rowpack_v2_ntt_only bench_gt_forward_rowpack_v2_lazyout_ntt_only
.PHONY: test_gt_tmvp_quartic_tmvp_experimental_c test_gt_tmvp_quartic_tmvp_experimental_asm test_gt_tmvp_quartic_tmvp_full_asm_smoke

BUILD_DIR = build
POLYNTT_ASM ?= asm/my_ntt.s asm/slothy/my_32ntt.opt.s
POLYINVNTT_ASM ?= asm/inv_my_ntt.s
POLYINVNTT_BRANCHFOLD_A72_ASM ?= asm/inv_my_ntt_post_branchfold_a72.s
STOCK_BASE_ASM ?= asm/base.s
GT_BASE_ASM ?= asm/base_gt.S
BASE_GT_ASM ?= $(GT_BASE_ASM)
BASE_GT_BENCH_LABEL ?= gt_basemul_asm
GT_BASE_OPT_ASM ?= asm/base_gt.opt.s
KEM_NTT_ASM ?= asm/ntt.s
KEM_INVNTT_ASM ?=
KEM_CREPMOD3_ASM ?= asm/crepmod3.s
# Default KEM keeps stock KPQC base layout.
KEM_BASE_SOURCES ?= poly.c asm/base.s
KEM_BENCH_LABEL ?= kpqc_final_kem_dec
PMU_MODE ?= basemul
PMU_LABEL ?= $(PMU_MODE)
PMU_CALLS ?= 1024
PMU_WARMUP ?= 16
PMU_SUBTRACT_EMPTY ?= 0
PMU_FIXED_ONLY ?= 0
PMU_ROUNDS ?= 11
PMU_DISCARD_FIRST ?= 1
PMU_CFLAGS ?=
PMU_COMPARE_MODE ?= base_compare
PMU_COMPARE_LABEL ?= stock_vs_gt_base
PMU_COMPARE_LEFT_ASM ?= asm/base.s
PMU_COMPARE_RIGHT_ASM ?= asm/base_gt.S
PMU_COMPARE_LEFT_LABEL ?= stock_base
PMU_COMPARE_RIGHT_LABEL ?= gt_base
# Defaults build the stock AArch64 implementation.
PMU_BASE_SOURCES ?= poly.c asm/base.s
PMU_NTT_SOURCES ?= asm/ntt.s
PMU_INVNTT_SOURCES ?=
POLYNTT_TEST_CFLAGS ?=
POLYNTT_ASM_FLAGS ?=
NTT_PIPELINE_CYCLE_CFLAGS ?= -DBENCH_USE_PERF_CYCLES
ROWPACK_FORWARD_NTT_V2_ASM ?= asm/my_ntt.s asm/slothy/ntt32_8way.rowpack_v2.n1.opt.s
ROWPACK_FORWARD_NTT_V3_SYMBOLIC_ASM ?= asm/slothy/ntt32_v3_rowpack_stage345_symbolic.s
ROWPACK_FORWARD_NTT_V3_ASM ?= asm/my_ntt.s asm/slothy/ntt32_8way.rowpack_v3.n1.opt.s
ROWPACK_FORWARD_NTT_V3B_SYMBOLIC_ASM ?= asm/slothy/ntt32_v3b_rowpack_stage345_symbolic.s
ROWPACK_FORWARD_NTT_V3B_OPT_ASM ?= asm/slothy/ntt32_8way.rowpack_v3b.n1.opt.s
ROWPACK_FORWARD_NTT_V3B_ASM ?= asm/my_ntt.s $(ROWPACK_FORWARD_NTT_V3B_OPT_ASM)
# This full-path oracle includes scalar ntt.c reference code with intentional
# signed 16-bit wraparound assumptions; build it conservatively.
ROWPACK_FULLPATH_CFLAGS ?= -O0 -fno-strict-aliasing
ROWPACK_PIPELINE_CFLAGS ?= -O3 -fwrapv -fno-strict-aliasing
ROWPACK_PIPELINE_CYCLE_CFLAGS ?= $(ROWPACK_PIPELINE_CFLAGS) -DROWPACK_USE_PERF_CYCLES
AARCH64_BENCH_DIR ?= ../../../aarch64-bench
SLOTHY_SYMBOLIC_SKILL_DIR ?= ../../../../.agents/skills/slothy-symbolic-asm-authoring
SLOTHY_CONTRACT_SKILL_DIR ?= $(HOME)/.codex/skills/slothy-symbolic-asm-authoring
SLOTHY_CONTRACT_CHECK ?= $(SLOTHY_CONTRACT_SKILL_DIR)/scripts/check-kernel-contract.py
ROWPACK_FORWARD_NTT_V2_LAZYOUT_ASM ?= asm/my_ntt.s asm/slothy/ntt32_8way.rowpack_v2.lazyout.n1.opt.S
AARCH64_SYNTAX_CC ?= clang -target aarch64-linux-gnu

ifneq ($(BENCH_MODE),)
.DEFAULT_GOAL := aarch64_bench_redirect
.PHONY: aarch64_bench_redirect
aarch64_bench_redirect:
	@if [ ! -f "$(AARCH64_BENCH_DIR)/Makefile" ]; then \
		echo "BENCH_MODE=$(BENCH_MODE) is for aarch64-bench, but $(AARCH64_BENCH_DIR) was not found."; \
		echo "Run from ntruplus-ntt-Optimized/aarch64-bench, or keep this relative checkout layout."; \
		exit 1; \
	fi
	@echo "BENCH_MODE=$(BENCH_MODE): forwarding this build to $(AARCH64_BENCH_DIR)"
	$(MAKE) -C $(AARCH64_BENCH_DIR) clean
	$(MAKE) -C $(AARCH64_BENCH_DIR)
	ln -sf $(AARCH64_BENCH_DIR)/bench bench
endif

all: \
	test \
	PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) kat/aes.h kat/rng.h $(SOURCES) kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(SOURCES)

test: $(HEADERS) randombytes.h $(SOURCES) randombytes.c test/test.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test randombytes.c test/test.c $(SOURCES)

test_stock_base_opt: $(HEADERS) randombytes.h randombytes.c test/test.c kem.c symmetric.c poly.c asm/add.s asm/ntt.s asm/base.opt.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test_stock_base_opt randombytes.c test/test.c kem.c symmetric.c poly.c asm/add.s asm/ntt.s asm/base.opt.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S

test_gt_rowpack_soa_oracle: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_oracle.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_oracle gt_test/test_gt_rowpack_soa_oracle.c
	./$(BUILD_DIR)/test_gt_rowpack_soa_oracle

test_gt_forward_rowpack_output_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_forward_rowpack_output_contract.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_forward_rowpack_output_contract gt_test/test_gt_forward_rowpack_output_contract.c
	./$(BUILD_DIR)/test_gt_forward_rowpack_output_contract

test_gt_rowpack_forward_v3_register_order_contract: $(HEADERS) gt_test/test_gt_rowpack_forward_v3_register_order_contract.c $(ROWPACK_FORWARD_NTT_V3_SYMBOLIC_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_forward_v3_register_order_contract gt_test/test_gt_rowpack_forward_v3_register_order_contract.c
	./$(BUILD_DIR)/test_gt_rowpack_forward_v3_register_order_contract

test_gt_rowvec_layout_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowvec_layout_contract.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowvec_layout_contract gt_test/test_gt_rowvec_layout_contract.c
	./$(BUILD_DIR)/test_gt_rowvec_layout_contract

test_gt_forward_rowpack_v2_asm: $(HEADERS) ntt.h ntt.c gt_test/test_gt_forward_rowpack_output_contract.c $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DTEST_GT_FORWARD_ROWPACK_V2_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_forward_rowpack_v2_asm gt_test/test_gt_forward_rowpack_output_contract.c $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_forward_rowpack_v2_asm

test_gt_forward_rowpack_v2_lazyout_asm: $(HEADERS) ntt.h ntt.c gt_test/test_gt_forward_rowpack_output_contract.c $(ROWPACK_FORWARD_NTT_V2_LAZYOUT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DTEST_GT_FORWARD_ROWPACK_V2_ASM -DRANDOM_TESTS=1024 -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_forward_rowpack_v2_lazyout_asm gt_test/test_gt_forward_rowpack_output_contract.c $(ROWPACK_FORWARD_NTT_V2_LAZYOUT_ASM)
	./$(BUILD_DIR)/test_gt_forward_rowpack_v2_lazyout_asm

bench_gt_forward_rowpack_v2_ntt_only: $(HEADERS) gt_test/bench_gt_forward_rowpack_ntt_only.c $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_forward_rowpack_v2_ntt_only gt_test/bench_gt_forward_rowpack_ntt_only.c $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_forward_rowpack_v2_ntt_only

bench_gt_forward_rowpack_v2_lazyout_ntt_only: $(HEADERS) gt_test/bench_gt_forward_rowpack_ntt_only.c $(ROWPACK_FORWARD_NTT_V2_LAZYOUT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_forward_rowpack_v2_lazyout_ntt_only gt_test/bench_gt_forward_rowpack_ntt_only.c $(ROWPACK_FORWARD_NTT_V2_LAZYOUT_ASM)
	./$(BUILD_DIR)/bench_gt_forward_rowpack_v2_lazyout_ntt_only

test_gt_rowpack_forward_v3_candidate: $(HEADERS) ntt.h ntt.c gt_test/test_gt_forward_rowpack_output_contract.c $(ROWPACK_FORWARD_NTT_V3_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DTEST_GT_FORWARD_ROWPACK_V3_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_forward_v3_candidate gt_test/test_gt_forward_rowpack_output_contract.c $(ROWPACK_FORWARD_NTT_V3_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_forward_v3_candidate

test_gt_tmvp_quartic_tmvp_experimental_c: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_quartic_tmvp_experimental_c.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_c ntt.c gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_quartic_tmvp_experimental_c.c
	./$(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_c

test_gt_tmvp_quartic_tmvp_experimental_asm: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c asm/gt_tmvp_quartic_tmvp_experimental_asm.S gt_test/test_gt_tmvp_quartic_tmvp_experimental_asm.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_asm ntt.c gt_tmvp_quartic_tmvp_experimental.c asm/gt_tmvp_quartic_tmvp_experimental_asm.S gt_test/test_gt_tmvp_quartic_tmvp_experimental_asm.c
	./$(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_experimental_asm

test_gt_tmvp_quartic_tmvp_full_asm_smoke: $(HEADERS) randombytes.h gt_tmvp_quartic_tmvp_experimental.h gt_test/test_gt_tmvp_quartic_tmvp_full_c_kem.c poly_gt_tmvp_experimental_c.c gt_tmvp_quartic_tmvp_experimental.c asm/gt_tmvp_quartic_tmvp_experimental_asm.S randombytes.c kem.c symmetric.c ntt.c NO_CE/fips202.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_full_asm_kem randombytes.c gt_test/test_gt_tmvp_quartic_tmvp_full_c_kem.c kem.c symmetric.c poly_gt_tmvp_experimental_c.c ntt.c gt_tmvp_quartic_tmvp_experimental.c asm/gt_tmvp_quartic_tmvp_experimental_asm.S NO_CE/fips202.c
	./$(BUILD_DIR)/test_gt_tmvp_quartic_tmvp_full_asm_kem

verify_invntt_constants: scripts/verify_invntt_constants.py asm/slothy/invntt_opt.s
	$(PYTHON) scripts/verify_invntt_constants.py

verify_invntt_layout: scripts/verify_invntt_layout.py
	$(PYTHON) scripts/verify_invntt_layout.py

analyze_invntt32_ranges: $(HEADERS) ntt.h ntt.c gt_test/analyze_invntt32_ranges.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_invntt32_ranges gt_test/analyze_invntt32_ranges.c

test_invntt32_rowpack_kernel_model: $(HEADERS) gt_test/test_invntt32_rowpack_kernel_model.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test_invntt32_rowpack_kernel_model gt_test/test_invntt32_rowpack_kernel_model.c
	./$(BUILD_DIR)/test_invntt32_rowpack_kernel_model

analyze_gt_rowpack_basemul_output_ranges: $(HEADERS) gt_test/analyze_gt_rowpack_basemul_output_ranges.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_gt_rowpack_basemul_output_ranges gt_test/analyze_gt_rowpack_basemul_output_ranges.c
	./$(BUILD_DIR)/analyze_gt_rowpack_basemul_output_ranges

test_gt_rowpack_no_entry_no_end_range_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_no_entry_no_end_range_contract.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_range_contract gt_test/test_gt_rowpack_no_entry_no_end_range_contract.c
	./$(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_range_contract

dump_forward_mapping: $(HEADERS) ntt.h ntt.c gt_test/dump_forward_mapping.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/dump_forward_mapping gt_test/dump_forward_mapping.c
	./$(BUILD_DIR)/dump_forward_mapping
	$(PYTHON) gt_test/make_register_pack_viewer.py $(BUILD_DIR)/gt_register_pack_plan.csv -o $(BUILD_DIR)/gt_register_pack_plan.html
	$(PYTHON) gt_test/make_csv_viewers.py $(BUILD_DIR)
	$(PYTHON) gt_test/make_phase123_viewer.py $(BUILD_DIR) -o $(BUILD_DIR)/gt_phase123_flow_viewer.html

gt_phase123_flow_viewer: dump_forward_mapping

csv_viewers: dump_forward_mapping

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) bench
	$(RM) -r $(BUILD_DIR)
