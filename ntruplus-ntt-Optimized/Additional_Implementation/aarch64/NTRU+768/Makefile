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
.PHONY: test_invntt32_rowpack_kernel_model test_invntt32_rowpack_slothy_opt test_gt_forward_rowpack_output_contract test_gt_rowpack_forward_v3_register_order_contract test_gt_rowpack_soa_invntt32_fullpath test_gt_rowpack_soa_invntt32_fullpath_canonical test_gt_rowpack_soa_invntt32_fullpath_nativebasemul
.PHONY: test_gt_forward_rowpack_v2_asm test_gt_rowpack_forward_v3_candidate test_gt_rowpack_forward_v3b_stage345_contract test_gt_rowpack_forward_v3b_symbolic_candidate test_gt_rowpack_forward_v3c_stage12_stage345_layout_search test_gt_rowpack_lazy_postmerge_asm_v3_forward_fullpath test_gt_rowpack_soa_invntt32_fullpath_forward_v2 test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_mul2 test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_chunked
.PHONY: test_gt_rowpack_soa_oracle test_gt_rowvec_layout_contract test_gt_rowpack_no_entry_no_end_range_contract analyze_gt_rowpack_basemul_output_ranges
.PHONY: bench_gt_rowpack_pipeline_fused bench_gt_rowpack_pipeline_canonical bench_gt_rowpack_pipeline_compare
.PHONY: bench_gt_rowpack_pipeline_add_fused bench_gt_rowpack_pipeline_add_canonical bench_gt_rowpack_pipeline_add_compare
.PHONY: bench_gt_rowpack_pipeline_cycles_fused bench_gt_rowpack_pipeline_cycles_canonical bench_gt_rowpack_pipeline_cycles_compare
.PHONY: bench_gt_rowpack_pipeline_add_cycles_fused bench_gt_rowpack_pipeline_add_cycles_canonical bench_gt_rowpack_pipeline_add_cycles_compare
.PHONY: bench_gt_rowpack_pipeline_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_add_nativebasemul_cycles_fused
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_compare bench_gt_rowpack_invntt_isolate_cycles
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_compare bench_gt_rowpack_invntt_nativepost_isolate_cycles
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_compare bench_gt_rowpack_invntt_nativepost_mul2_isolate_cycles
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_compare
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_compare bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles bench_gt_rowpack_invntt_stage_cycles
.PHONY: test_gt_rowpack_no_entry_no_end_fullpath bench_gt_rowpack_no_entry_no_end_fullpath_cycles bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles
.PHONY: test_gt_rowpack_lazy_postmerge_asm_fullpath bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles bench_gt_rowpack_lazy_postmerge_asm_add_cycles bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles bench_gt_rowpack_lazy_postmerge_asm_v3_forward_add_cycles
.PHONY: audit_gt_rowpack_forward_stage345_liveout test_gt_rowpack_forward_stage345_layout_search test_gt_rowpack_forward_v3c_stage12_stage345_layout_search report_gt_rowpack_forward_topology_decision report_gt_rowpack_forward_v4_topology_model test_gt_rowpack_forward_v4_transform_dag_search test_gt_rowpack_forward_v4_numeric_oracle
.PHONY: test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_c_harness test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_postmerge_c test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_to5_symbolic_contract test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_to5_asm test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_fullpath_asm test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_true_forward_stage4_fullpath_asm test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_batch8_symbolic_contract test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath bench_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath
.PHONY: test_gt_forward_rowpack_v2_lazyout_asm bench_gt_forward_rowpack_v2_ntt_only bench_gt_forward_rowpack_v2_lazyout_ntt_only
.PHONY: test_gt_tmvp_quartic_tmvp_experimental_c test_gt_tmvp_quartic_tmvp_experimental_asm test_gt_tmvp_quartic_tmvp_full_asm_smoke
.PHONY: test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_c test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_asm
.PHONY: test_gt_rowpack_bounded_postmerge_asm_fullpath

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
ROWPACK_INVNTT32_SLOTHY_OPT_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.opt.S
ROWPACK_INVNTT32_ALLOC_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.alloc.S
ROWPACK_INVNTT32_SYMBOLIC_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.sym.S
ROWPACK_INVNTT32_NOINRED_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.opt.S
ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_no_entry_no_end.S
ROWPACK_INVNTT_POSTMERGE_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold.S
ROWPACK_FORWARD_NTT_V2_ASM ?= asm/my_ntt.s asm/slothy/ntt32_8way.rowpack_v2.n1.opt.s
ROWPACK_FORWARD_NTT_V3_SYMBOLIC_ASM ?= asm/slothy/ntt32_v3_rowpack_stage345_symbolic.s
ROWPACK_FORWARD_NTT_V3_ASM ?= asm/my_ntt.s asm/slothy/ntt32_8way.rowpack_v3.n1.opt.s
ROWPACK_FORWARD_NTT_V3B_SYMBOLIC_ASM ?= asm/slothy/ntt32_v3b_rowpack_stage345_symbolic.s
ROWPACK_FORWARD_NTT_V3B_OPT_ASM ?= asm/slothy/ntt32_8way.rowpack_v3b.n1.opt.s
ROWPACK_FORWARD_NTT_V3B_ASM ?= asm/my_ntt.s $(ROWPACK_FORWARD_NTT_V3B_OPT_ASM)
ROWPACK_FORWARD_NTT_V3B_CONTRACT_DIR ?= docs/gt_soa_layout_experiment/forward_v3b_stage345
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
ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded.S
ROWPACK_INVNTT32_STAGE2_TO5_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.opt.S
CANDIDATE_A_TMVP_ASM_SKELETON ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_gt_tmvp_candidate_a_tmvp_skeleton.S
CANDIDATE_A_TMVP_ASM_CONTRACT ?= docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-kernel-contract.yml
CANDIDATE_A_TMVP_BATCH8_SYMBOLIC_ASM ?= docs/gt_soa_layout_experiment/kernels/ntruplus768_gt_tmvp_candidate_a_tmvp_batch8.sym.S
CANDIDATE_A_TMVP_BATCH8_KERNEL_CONTRACT ?= docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-batch8-symbolic-kernel-contract.yml
CANDIDATE_A_TMVP_BATCH8_CANDIDATE_CONTRACT ?= docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-batch8-candidate-contract.yml
CANDIDATE_A_TMVP_BATCH8_DAG ?= docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-batch8-instruction-dag.yml
CANDIDATE_A_TMVP_BATCH8_SLOTHY_DRIVER ?= docs/gt_soa_layout_experiment/optimize_ntruplus768_gt_tmvp_candidate_a_tmvp_batch8.py

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

test_gt_rowpack_forward_v3b_stage345_contract:
	$(PYTHON) docs/gt_soa_layout_experiment/check_forward_v3b_stage345_contract.py \
		--contract $(ROWPACK_FORWARD_NTT_V3B_CONTRACT_DIR)/kernel-contract.yml \
		--dag $(ROWPACK_FORWARD_NTT_V3B_CONTRACT_DIR)/instruction-dag.yml \
		--layout-search-dir docs/gt_soa_layout_experiment/forward_stage345_layout_search \
		--candidate $(ROWPACK_FORWARD_NTT_V3B_OPT_ASM) \
		--allow-missing-candidate

test_gt_rowpack_forward_v3b_symbolic_candidate: test_gt_rowpack_forward_v3b_stage345_contract
	$(PYTHON) docs/gt_soa_layout_experiment/analyze_forward_v3b_stage345_feasibility.py

test_gt_rowpack_forward_v3c_stage12_stage345_layout_search:
	$(PYTHON) docs/gt_soa_layout_experiment/search_forward_v3c_stage12_stage345_layout.py

report_gt_rowpack_forward_topology_decision:
	$(PYTHON) docs/gt_soa_layout_experiment/report_gt_rowpack_forward_topology_decision.py

report_gt_rowpack_forward_v4_topology_model:
	$(PYTHON) docs/gt_soa_layout_experiment/report_gt_rowpack_forward_v4_topology_model.py

test_gt_rowpack_forward_v4_transform_dag_search:
	$(PYTHON) docs/gt_soa_layout_experiment/search_forward_v4_transform_dag.py

test_gt_rowpack_forward_v4_numeric_oracle:
	$(PYTHON) docs/gt_soa_layout_experiment/search_forward_v4_numeric_oracle.py

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_c_harness:
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_c ntt.c gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_c.c
	./$(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_c
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	$(RG) -n "^candidate_a_c_harness_status: incomplete_materialized_stage5_tmvp_c_harness_pass|^selected_path: incomplete_stage4_materialized_stage5_quartic_pair_to_invntt_stage2" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	$(RG) -n "^candidate: fused_stage5_plus_current_quartic_leaves|^stage4_input_layout: rowpack_k_even_u_k_odd_v|^current_quartic_leaf_reused: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	$(RG) -n "^direct_naive_octic_asm_used: false|^product_count_delta_vs_current: 0|^stage5_materialized_inside_tmvp_c: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	$(RG) -n "^output_adapter_even_slot: ce_plus_co|^output_adapter_odd_slot: ce_minus_co|^direct_invntt_stage1_adapter_checked: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	$(RG) -n "^asm_implemented: false|^full_pipeline_replaced: false|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	$(RG) -n "^recommended_next_gate: candidate_a_stage2_to_postmerge_c_or_asm_contract" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-c-harness-report.yml
	@printf "Candidate A C harness summary: fused_stage5_load=true, current_quartic_leaf_reused=true, output=[ce+co,ce-co], product_count_delta=0, next=candidate_a_stage2_to_postmerge_c_or_asm_contract\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_postmerge_c: test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_c_harness
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c
	./$(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	$(RG) -n "^candidate_a_stage2_postmerge_c_status: pass|^selected_path: incomplete_stage4_candidate_a_tmvp_to_invntt_stage2_to_postmerge" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	$(RG) -n "^candidate_input_state: invntt_rowkernel_after_stage1_adapter|^rowkernel_stage1_skipped: true|^candidate_rowkernel: scalar_no_entry_no_end_stage2_to5" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	$(RG) -n "^adapter_mismatches: 0|^rowkernel_mismatches: 0|^postmerge_mismatches: 0|^total_mismatches: 0" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	$(RG) -n "^adapter_even_slot: ce_plus_co|^adapter_odd_slot: ce_minus_co|^postmerge_reference: scalar_rowpack_postmerge_from_rows" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	$(RG) -n "^asm_implemented: false|^full_pipeline_replaced: false|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	$(RG) -n "^recommended_next_gate: candidate_a_stage2_to5_rowkernel_asm_contract" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-postmerge-c-report.yml
	@printf "Candidate A stage2-to-postmerge C summary: adapter=ok, rowkernel_stage2_to5=ok, postmerge=ok, next=candidate_a_stage2_to5_rowkernel_asm_contract\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_to5_symbolic_contract: test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_postmerge_c
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) docs/gt_tmvp_decomposition_experiment/prove_incomplete_candidate_a_stage2_to5_symbolic_contract.py
	$(PYTHON) $(SLOTHY_SYMBOLIC_SKILL_DIR)/scripts/check-symbolic-asm.py docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.sym.S > $(BUILD_DIR)/candidate_a_stage2_to5_check_symbolic_asm.log
	$(PYTHON) $(SLOTHY_SYMBOLIC_SKILL_DIR)/scripts/check-slothy-region-size.py docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.sym.S > $(BUILD_DIR)/candidate_a_stage2_to5_check_region_size.log
	$(PYTHON) $(SLOTHY_SYMBOLIC_SKILL_DIR)/scripts/check-physical-reg-leaks.py docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.sym.S --allow-reg x0 --allow-reg x1 > $(BUILD_DIR)/candidate_a_stage2_to5_check_physical_regs.log
	$(RG) -n "check-symbolic-asm:" $(BUILD_DIR)/candidate_a_stage2_to5_check_symbolic_asm.log
	$(RG) -n "REGION002|check-slothy-region-size:" $(BUILD_DIR)/candidate_a_stage2_to5_check_region_size.log
	$(RG) -n "check-physical-reg-leaks: no warnings emitted" $(BUILD_DIR)/candidate_a_stage2_to5_check_physical_regs.log
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.md
	$(RG) -n "^candidate_a_stage2_to5_symbolic_contract_status: pass|^source_kind: slothy_symbolic_asm|^slothy_workflow: ra_then_window_opt" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml
	$(RG) -n "^input_state: invntt_rowkernel_after_stage1_adapter|^rowkernel_stage1_skipped: true|^candidate_rowkernel: symbolic_no_entry_no_end_stage2_to5" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml
	$(RG) -n "^stage1_instructions_removed: true|^stage1_mask_constant_not_loaded: true|^stage2_present: true|^stage3_present: true|^stage4_present: true|^stage5_present: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml
	$(RG) -n "^slothy_run_claimed: false|^allocated_or_optimized_asm_generated: false|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml
	$(RG) -n "^recommended_next_gate: run_slothy_ra_then_window_generate_stage2_to5_asm_then_test" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-symbolic-contract.yml
	@printf "Candidate A stage2-to5 symbolic contract summary: slothy_symbolic_source=ready, stage1_skipped=true, workflow=ra_then_window_opt, next=run_slothy_and_test_generated_asm\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_to5_asm: test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_stage2_to5_symbolic_contract
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DCANDIDATE_A_STAGE2_TO5_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_stage2_to5_asm gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(ROWPACK_INVNTT32_STAGE2_TO5_ASM)
	./$(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_stage2_to5_asm
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-asm-report.yml
	$(RG) -n "^candidate_a_stage2_to5_asm_contract_status: pass|^candidate_rowkernel: slothy_opt_no_entry_no_end_stage2_to5|^asm_compared_against: scalar_no_entry_no_end_stage2_to5_then_postmerge" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-asm-report.yml
	$(RG) -n "^asm_rowkernel_mismatches: 0|^asm_postmerge_mismatches: 0|^total_mismatches: 0" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-asm-report.yml
	$(RG) -n "^asm_implemented: true|^slothy_generated_opt_asm_used: true|^full_pipeline_replaced: false|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-asm-report.yml
	$(RG) -n "^recommended_next_gate: candidate_a_stage2_to5_rowkernel_asm_benchmark_or_fullpath_probe" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-stage2-to5-asm-report.yml
	@printf "Candidate A stage2-to5 ASM summary: slothy_opt_asm=ok, rowkernel_stage2_to5=ok, postmerge_after_asm=ok, next=benchmark_or_fullpath_probe\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_fullpath_asm: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DCANDIDATE_A_STAGE2_TO5_ASM -DCANDIDATE_A_FULLPATH_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_fullpath_asm gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	./$(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_fullpath_asm
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-fullpath-asm-report.yml
	$(RG) -n "^candidate_a_fullpath_asm_status: pass|^selected_path: incomplete_stage4_candidate_a_tmvp_to_invntt_stage2_to_postmerge|^probe_scope: stage4_boundary_to_final_poly" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-fullpath-asm-report.yml
	$(RG) -n "^true_forward_incomplete_asm_used: false|^postmerge_regular_asm_checked: true|^postmerge_bounded_asm_checked: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-fullpath-asm-report.yml
	$(RG) -n "^selected_postmerge_asm: regular_asm|^selected_postmerge_asm: bounded_asm|^bounded_postmerge_asm_mismatches: 0|^selected_postmerge_asm_mismatches: 0|^total_mismatches: 0" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-fullpath-asm-report.yml
	$(RG) -n "^tmvp_asm_implemented: false|^postmerge_asm_used_for_selected_path: true|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-fullpath-asm-report.yml
	$(RG) -n "^recommended_next_gate: true_forward_stage4_source_or_candidate_a_tmvp_asm_benchmark" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-fullpath-asm-report.yml
	@printf "Candidate A fullpath ASM summary: stage4_boundary=true, tmvp_c_adapter=true, rowkernel_stage2_to5_asm=ok, postmerge_asm=ok, next=true_forward_stage4_source_or_candidate_a_tmvp_asm_benchmark\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_true_forward_stage4_fullpath_asm: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DCANDIDATE_A_STAGE2_TO5_ASM -DCANDIDATE_A_FULLPATH_ASM -DCANDIDATE_A_TRUE_FORWARD_STAGE4 -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_true_forward_stage4_fullpath_asm gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	./$(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_true_forward_stage4_fullpath_asm
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-true-forward-stage4-fullpath-asm-report.yml
	$(RG) -n "^candidate_a_true_forward_stage4_fullpath_asm_status: pass|^stage4_input_source: true_forward_stage4_c_reference|^true_forward_stage4_source_used: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-true-forward-stage4-fullpath-asm-report.yml
	$(RG) -n "^forward_stage4_source_kind: c_reference_top_split_twist_dft3_ntt32_stage1_to4|^true_forward_incomplete_asm_used: false|^final_compare: schoolbook_product_or_product_add" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-true-forward-stage4-fullpath-asm-report.yml
	$(RG) -n "^regular_postmerge_asm_mismatches: 0|^bounded_postmerge_asm_mismatches: 0|^final_schoolbook_mismatches: 0|^total_mismatches: 0" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-true-forward-stage4-fullpath-asm-report.yml
	$(RG) -n "^selected_postmerge_asm: regular_asm|^postmerge_asm_used_for_selected_path: true|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-true-forward-stage4-fullpath-asm-report.yml
	$(RG) -n "^recommended_next_gate: forward_stage4_asm_export_or_candidate_a_tmvp_asm_benchmark" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-true-forward-stage4-fullpath-asm-report.yml
	@printf "Candidate A true-forward stage4 fullpath ASM summary: forward_stage4_c_reference=ok, tmvp_c_adapter=true, rowkernel_stage2_to5_asm=ok, postmerge_asm=ok, final_schoolbook=ok, next=forward_stage4_asm_export_or_candidate_a_tmvp_asm_benchmark\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_batch8_symbolic_contract: $(CANDIDATE_A_TMVP_BATCH8_SYMBOLIC_ASM) $(CANDIDATE_A_TMVP_BATCH8_KERNEL_CONTRACT) $(CANDIDATE_A_TMVP_BATCH8_CANDIDATE_CONTRACT) $(CANDIDATE_A_TMVP_BATCH8_DAG) $(CANDIDATE_A_TMVP_BATCH8_SLOTHY_DRIVER)
	@mkdir -p $(BUILD_DIR)
	test -f "$(SLOTHY_CONTRACT_CHECK)"
	test -f "$(SLOTHY_CONTRACT_SKILL_DIR)/scripts/check-symbolic-asm.py"
	test -f "$(SLOTHY_CONTRACT_SKILL_DIR)/scripts/check-physical-reg-leaks.py"
	$(PYTHON) $(SLOTHY_CONTRACT_CHECK) $(CANDIDATE_A_TMVP_BATCH8_KERNEL_CONTRACT) --kind kernel --mode new_symbolic_kernel > $(BUILD_DIR)/candidate_a_tmvp_batch8_check_kernel_contract.log
	$(PYTHON) $(SLOTHY_CONTRACT_CHECK) $(CANDIDATE_A_TMVP_BATCH8_CANDIDATE_CONTRACT) --kind candidate > $(BUILD_DIR)/candidate_a_tmvp_batch8_check_candidate_contract.log
	$(PYTHON) $(SLOTHY_CONTRACT_SKILL_DIR)/scripts/check-symbolic-asm.py --candidate --kernel-contract $(CANDIDATE_A_TMVP_BATCH8_KERNEL_CONTRACT) $(CANDIDATE_A_TMVP_BATCH8_SYMBOLIC_ASM) > $(BUILD_DIR)/candidate_a_tmvp_batch8_check_symbolic_asm.log
	$(PYTHON) $(SLOTHY_CONTRACT_SKILL_DIR)/scripts/check-physical-reg-leaks.py --contract $(CANDIDATE_A_TMVP_BATCH8_KERNEL_CONTRACT) $(CANDIDATE_A_TMVP_BATCH8_SYMBOLIC_ASM) > $(BUILD_DIR)/candidate_a_tmvp_batch8_check_physical_regs.log
	$(RG) -n "check-kernel-contract: kernel contract passed" $(BUILD_DIR)/candidate_a_tmvp_batch8_check_kernel_contract.log
	$(RG) -n "check-kernel-contract: candidate contract passed" $(BUILD_DIR)/candidate_a_tmvp_batch8_check_candidate_contract.log
	$(RG) -n "check-symbolic-asm: passed" $(BUILD_DIR)/candidate_a_tmvp_batch8_check_symbolic_asm.log
	$(RG) -n "check-physical-reg-leaks: passed" $(BUILD_DIR)/candidate_a_tmvp_batch8_check_physical_regs.log
	$(RG) -n "^kernel: ntruplus768_gt_tmvp_candidate_a_tmvp_batch8|^instruction_dag_status: symbolic_batch_core|^  operation: product_only" $(CANDIDATE_A_TMVP_BATCH8_DAG)
	$(RG) -n "^  scope: product_core_for_one_public_batch_not_full_tmvp_api|^  add_variant: not_yet_implemented|^  wrapper_for_all_branches_rows_kpairs: not_yet_implemented" $(CANDIDATE_A_TMVP_BATCH8_CANDIDATE_CONTRACT)
	@printf "Candidate A TMVP batch8 symbolic summary: product_core=ready_for_slothy_handoff, wrapper=false, add_variant=false, benchmark=false\n"

test_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(CANDIDATE_A_TMVP_ASM_SKELETON) $(CANDIDATE_A_TMVP_ASM_CONTRACT) $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	@mkdir -p $(BUILD_DIR)
	@if [ -f "$(SLOTHY_CONTRACT_CHECK)" ]; then \
		$(PYTHON) $(SLOTHY_CONTRACT_CHECK) $(CANDIDATE_A_TMVP_ASM_CONTRACT) --kind kernel --mode new_kernel_baseline_then_iterate; \
	else \
		echo "Skipping kernel contract checker: $(SLOTHY_CONTRACT_CHECK) not found"; \
	fi
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DCANDIDATE_A_STAGE2_TO5_ASM -DCANDIDATE_A_FULLPATH_ASM -DCANDIDATE_A_TRUE_FORWARD_STAGE4 -DCANDIDATE_A_TMVP_ASM_SKELETON -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(CANDIDATE_A_TMVP_ASM_SKELETON) $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	./$(BUILD_DIR)/test_gt_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-fullpath-report.yml
	$(RG) -n "^candidate_a_tmvp_asm_skeleton_fullpath_status: pass|^tmvp_asm_boundary_checked: true|^tmvp_asm_skeleton_trampoline_to_c: true" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-fullpath-report.yml
	$(RG) -n "^stage4_input_source: true_forward_stage4_c_reference|^final_compare: schoolbook_product_or_product_add|^tmvp_asm_implemented: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-fullpath-report.yml
	$(RG) -n "^tmvp_asm_mismatches: 0|^tmvp_asm_rowkernel_mismatches: 0|^selected_tmvp_asm_postmerge_mismatches: 0|^final_schoolbook_mismatches: 0|^total_mismatches: 0" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-fullpath-report.yml
	$(RG) -n "^selected_tmvp_asm_postmerge: regular_asm|^postmerge_asm_used_for_selected_path: true|^benchmark_or_cycle_claim_made: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-fullpath-report.yml
	$(RG) -n "^recommended_next_gate: replace_tmvp_skeleton_with_symbolic_candidate_a_tmvp_asm" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-fullpath-report.yml
	@printf "Candidate A TMVP ASM skeleton fullpath summary: tmvp_asm_boundary=skeleton_trampoline_to_c, rowkernel_stage2_to5_asm=ok, postmerge_asm=ok, final_schoolbook=ok, next=replace_tmvp_skeleton_with_symbolic_candidate_a_tmvp_asm\n"

bench_gt_tmvp_quartic_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(CANDIDATE_A_TMVP_ASM_SKELETON) $(CANDIDATE_A_TMVP_ASM_CONTRACT) $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	@mkdir -p $(BUILD_DIR)
	@if [ -f "$(SLOTHY_CONTRACT_CHECK)" ]; then \
		$(PYTHON) $(SLOTHY_CONTRACT_CHECK) $(CANDIDATE_A_TMVP_ASM_CONTRACT) --kind kernel --mode new_kernel_baseline_then_iterate; \
	else \
		echo "Skipping kernel contract checker: $(SLOTHY_CONTRACT_CHECK) not found"; \
	fi
	$(CC) $(CFLAGS) -std=c99 -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -DCANDIDATE_A_STAGE2_TO5_ASM -DCANDIDATE_A_FULLPATH_ASM -DCANDIDATE_A_TRUE_FORWARD_STAGE4 -DCANDIDATE_A_TMVP_ASM_SKELETON -DCANDIDATE_A_BENCH_TMVP_ASM_FULLPATH -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c $(CANDIDATE_A_TMVP_ASM_SKELETON) $(ROWPACK_INVNTT32_STAGE2_TO5_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM)
	./$(BUILD_DIR)/bench_gt_tmvp_incomplete_candidate_a_tmvp_asm_skeleton_fullpath
	test -f docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-bench-report.yml
	$(RG) -n "^candidate_a_tmvp_asm_skeleton_bench_status: done|^tmvp_asm_skeleton_trampoline_to_c: true|^tmvp_asm_implemented: false" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-bench-report.yml
	$(RG) -n "^rowkernel_stage2_to5_asm_used: true|^postmerge_regular_asm_used: true|^benchmark_or_cycle_claim_made: true|^correctness_precheck: pass" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-bench-report.yml
	$(RG) -n "name: tmvp_asm_skeleton_mul|name: tmvp_asm_skeleton_fullpath_mul|name: tmvp_asm_skeleton_fullpath_add" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-bench-report.yml
	$(RG) -n "^recommended_next_gate: replace_tmvp_skeleton_with_symbolic_candidate_a_tmvp_asm" docs/gt_tmvp_decomposition_experiment/decomposition-quartic-tmvp-incomplete-candidate-a-tmvp-asm-skeleton-bench-report.yml
	@printf "Candidate A TMVP ASM skeleton bench summary: measured scaffold rows for tmvp boundary and stage2_to_postmerge path; not optimized TMVP ASM\n"

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

test_invntt32_rowpack_slothy_opt: $(HEADERS) gt_test/test_invntt32_rowpack_kernel_model.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DTEST_ROWPACK_INVNTT32_ASM -I. -o $(BUILD_DIR)/test_invntt32_rowpack_slothy_opt gt_test/test_invntt32_rowpack_kernel_model.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	./$(BUILD_DIR)/test_invntt32_rowpack_slothy_opt

test_gt_rowpack_soa_invntt32_fullpath: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath

test_gt_rowpack_soa_invntt32_fullpath_canonical: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_CANONICAL_BASEMUL -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_canonical gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_canonical

test_gt_rowpack_soa_invntt32_fullpath_nativebasemul: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_NATIVE_BASEMUL -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_nativebasemul gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_nativebasemul

test_gt_rowpack_soa_invntt32_fullpath_forward_v2: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2 gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2

test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul

test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_c: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_TMVP_BASEMUL -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c gt_tmvp_quartic_tmvp_experimental.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_c

test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_asm: $(HEADERS) ntt.h ntt.c gt_tmvp_quartic_tmvp_experimental.h gt_tmvp_quartic_tmvp_experimental.c asm/gt_tmvp_quartic_tmvp_experimental_asm.S gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_TMVP_BASEMUL_ASM -DGT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_asm gt_test/test_gt_rowpack_soa_invntt32_fullpath.c gt_tmvp_quartic_tmvp_experimental.c asm/gt_tmvp_quartic_tmvp_experimental_asm.S $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_tmvp_asm

test_gt_rowpack_bounded_postmerge_asm_fullpath: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_NATIVE_POSTMERGE_BOUNDED_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_bounded_postmerge_asm_fullpath gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_BOUNDED_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_bounded_postmerge_asm_fullpath

test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost

test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_mul2: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_MUL2 -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_mul2 gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_mul2

test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_chunked: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_chunked gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_chunked

test_gt_rowpack_no_entry_no_end_fullpath: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_fullpath gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_fullpath

bench_gt_rowpack_pipeline_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DBENCH_LABEL=\"gt_rowpack_fused_ntt_mul_pipeline\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)

bench_gt_rowpack_pipeline_canonical: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_CANONICAL_BASEMUL -DBENCH_LABEL=\"gt_rowpack_canonical_ntt_mul_pipeline\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_canonical gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)

bench_gt_rowpack_pipeline_compare: bench_gt_rowpack_pipeline_fused bench_gt_rowpack_pipeline_canonical
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_canonical

bench_gt_rowpack_pipeline_add_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_fused_ntt_basemul_add_pipeline\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)

bench_gt_rowpack_pipeline_add_canonical: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DBENCH_OP_ADD -DROWPACK_CANONICAL_BASEMUL -DBENCH_LABEL=\"gt_rowpack_canonical_ntt_basemul_add_pipeline\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_canonical gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)

bench_gt_rowpack_pipeline_add_compare: bench_gt_rowpack_pipeline_add_fused bench_gt_rowpack_pipeline_add_canonical
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_canonical

bench_gt_rowpack_pipeline_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DBENCH_LABEL=\"gt_rowpack_fused_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)

bench_gt_rowpack_pipeline_cycles_canonical: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_CANONICAL_BASEMUL -DBENCH_LABEL=\"gt_rowpack_canonical_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_cycles_canonical gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)

bench_gt_rowpack_pipeline_cycles_compare: bench_gt_rowpack_pipeline_cycles_fused bench_gt_rowpack_pipeline_cycles_canonical
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_cycles_canonical

bench_gt_rowpack_pipeline_add_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_fused_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)

bench_gt_rowpack_pipeline_add_cycles_canonical: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DBENCH_OP_ADD -DROWPACK_CANONICAL_BASEMUL -DBENCH_LABEL=\"gt_rowpack_canonical_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_cycles_canonical gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NOINRED_ASM)

bench_gt_rowpack_pipeline_add_cycles_compare: bench_gt_rowpack_pipeline_add_cycles_fused bench_gt_rowpack_pipeline_add_cycles_canonical
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_cycles_canonical

bench_gt_rowpack_pipeline_nativebasemul_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_NATIVE_BASEMUL -DBENCH_LABEL=\"gt_rowpack_fused_nativebasemul_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_nativebasemul_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)

bench_gt_rowpack_pipeline_add_nativebasemul_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_NATIVE_BASEMUL -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_fused_nativebasemul_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_nativebasemul_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_compare: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_cycles_fused

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_compare: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_cycles_fused

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_MUL2 -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_mul2_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_MUL2 -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_mul2_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_compare: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_cycles_fused

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_MUL2 -DROWPACK_PIPELINE_INVNTT_INPLACE -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_mul2_inplace_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_MUL2 -DROWPACK_PIPELINE_INVNTT_INPLACE -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_mul2_inplace_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_compare: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_PIPELINE_INVNTT_INPLACE -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_chunked_inplace_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_PIPELINE_INVNTT_INPLACE -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_forward_v2_nativebasemul_nativepost_chunked_inplace_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_compare: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused

bench_gt_rowpack_no_entry_no_end_fullpath_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_LABEL=\"gt_rowpack_no_entry_no_end_forward_v2_nativebasemul_nativepost_chunked_inplace_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_no_entry_no_end_fullpath_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_no_entry_no_end_forward_v2_nativebasemul_nativepost_chunked_inplace_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

test_gt_rowpack_lazy_postmerge_asm_fullpath: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_lazy_postmerge_asm_fullpath gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_lazy_postmerge_asm_fullpath

test_gt_rowpack_lazy_postmerge_asm_v3_forward_fullpath: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V3_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_FULLPATH_CFLAGS) -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_lazy_postmerge_asm_v3_forward_fullpath gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V3_ASM)
	./$(BUILD_DIR)/test_gt_rowpack_lazy_postmerge_asm_v3_forward_fullpath

bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_INVNTT_STAGE_SPLIT -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_LABEL=\"gt_rowpack_lazy_postmerge_asm_isolate_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles

bench_gt_rowpack_lazy_postmerge_asm_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_LABEL=\"gt_rowpack_lazy_postmerge_asm_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_lazy_postmerge_asm_add_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_lazy_postmerge_asm_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_add_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)

bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V3_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_LABEL=\"gt_rowpack_lazy_postmerge_asm_v3_forward_ntt_mul_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V3_ASM)

bench_gt_rowpack_lazy_postmerge_asm_v3_forward_add_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V3_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_NATIVE_POSTMERGE_ASM -DROWPACK_PIPELINE_INVNTT_INPLACE -DROWPACK_CHECK_FINAL_BOUNDED -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_rowpack_lazy_postmerge_asm_v3_forward_ntt_basemul_add_pipeline_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_v3_forward_add_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_NO_ENTRY_NO_END_ASM) $(ROWPACK_INVNTT_POSTMERGE_ASM) $(ROWPACK_FORWARD_NTT_V3_ASM)

bench_gt_rowpack_invntt_isolate_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DBENCH_LABEL=\"gt_rowpack_invntt_isolate_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_invntt_isolate_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_rowpack_invntt_isolate_cycles

bench_gt_rowpack_invntt_nativepost_isolate_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DBENCH_LABEL=\"gt_rowpack_invntt_nativepost_isolate_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_invntt_nativepost_isolate_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_rowpack_invntt_nativepost_isolate_cycles

bench_gt_rowpack_invntt_nativepost_mul2_isolate_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_MUL2 -DBENCH_LABEL=\"gt_rowpack_invntt_nativepost_mul2_isolate_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_invntt_nativepost_mul2_isolate_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_rowpack_invntt_nativepost_mul2_isolate_cycles

bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DBENCH_LABEL=\"gt_rowpack_invntt_nativepost_chunked_isolate_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles

bench_gt_rowpack_invntt_stage_cycles: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_INVNTT_STAGE_SPLIT -DBENCH_LABEL=\"gt_rowpack_invntt_stage_cycles\" -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_invntt_stage_cycles gt_test/test_gt_rowpack_soa_invntt32_fullpath.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_FORWARD_NTT_V2_ASM)
	./$(BUILD_DIR)/bench_gt_rowpack_invntt_stage_cycles

analyze_gt_rowpack_basemul_output_ranges: $(HEADERS) gt_test/analyze_gt_rowpack_basemul_output_ranges.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_gt_rowpack_basemul_output_ranges gt_test/analyze_gt_rowpack_basemul_output_ranges.c
	./$(BUILD_DIR)/analyze_gt_rowpack_basemul_output_ranges

test_gt_rowpack_no_entry_no_end_range_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_no_entry_no_end_range_contract.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_range_contract gt_test/test_gt_rowpack_no_entry_no_end_range_contract.c
	./$(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_range_contract

audit_gt_rowpack_forward_stage345_liveout:
	$(PYTHON) docs/gt_soa_layout_experiment/audit_forward_stage345_liveout.py

test_gt_rowpack_forward_stage345_layout_search: audit_gt_rowpack_forward_stage345_liveout
	$(PYTHON) docs/gt_soa_layout_experiment/search_forward_stage345_layout.py

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
