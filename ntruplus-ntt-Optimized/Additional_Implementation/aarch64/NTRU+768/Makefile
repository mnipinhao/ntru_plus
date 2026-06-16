CC =gcc
PYTHON ?= python3
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM = /bin/rm -f

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

.PHONY: all PQCgenKAT_kem test test_stock_base_opt test_gt_reference test_gt_base_ref test_gt_base_asm test_gt_basemul_asm test_gt_base_opt test_polyntt_harness test_polyntt_asm test_polyinvntt_asm test_kem_invntt_contract analyze_invntt32_ranges bench_gt_basemul_ref bench_gt_basemul_asm bench_gt_basemul_stock bench_gt_basemul_compare bench_base_stock bench_base_stock_opt bench_base_gt bench_base_gt_opt bench_base_compare bench_gt_basemuladd_ref bench_gt_basemuladd_asm bench_gt_basemuladd_stock bench_gt_basemuladd_compare bench_baseadd_stock bench_baseadd_stock_opt bench_baseadd_gt bench_baseadd_gt_opt bench_baseadd_compare bench_ntt_pipeline_stock bench_ntt_pipeline_gt bench_ntt_pipeline_stock_opt bench_ntt_pipeline_gt_opt bench_ntt_pipeline_compare bench_ntt_pipeline_add_stock bench_ntt_pipeline_add_gt bench_ntt_pipeline_add_stock_opt bench_ntt_pipeline_add_gt_opt bench_ntt_pipeline_add_compare bench_polyinvntt_asm bench_polyinvntt_kpqc_final bench_polyinvntt_compare bench_kem_dec bench_kem_dec_kpqc_final bench_kem_dec_gt bench_kem_dec_compare bench_pmu bench_pmu_base_compare bench_pmu_base_compare_stock_gt bench_pmu_base_compare_stockopt_gtopt bench_pmu_base_compare_stock_stockopt bench_pmu_base_compare_gt_gtopt bench_pmu_symbols dump_forward_mapping gt_phase123_flow_viewer csv_viewers clean
.PHONY: verify_invntt_constants verify_invntt_layout verify_invntt_contracts test_invntt_representatives analyze_invntt_branchfold_reductions
.PHONY: test_invntt32_rowpack_kernel_model test_invntt32_rowpack_slothy_opt test_gt_forward_rowpack_output_contract test_gt_rowpack_forward_v3_register_order_contract test_gt_rowpack_soa_invntt32_fullpath test_gt_rowpack_soa_invntt32_fullpath_canonical test_gt_rowpack_soa_invntt32_fullpath_nativebasemul
.PHONY: test_gt_forward_rowpack_v2_asm test_gt_rowpack_forward_v3_candidate test_gt_rowpack_forward_v3b_stage345_contract test_gt_rowpack_forward_v3b_symbolic_candidate test_gt_rowpack_forward_v3c_stage12_stage345_layout_search test_gt_rowpack_lazy_postmerge_asm_v3_forward_fullpath test_gt_rowpack_soa_invntt32_fullpath_forward_v2 test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_mul2 test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost_chunked
.PHONY: test_polyinvntt_branchfold_a72 bench_polyinvntt_branchfold_a72
.PHONY: test_gt_rowpack_soa_oracle test_gt_rowvec_layout_contract test_gt_rowpack_no_entry_no_end_range_contract bench_gt_basemul_soa bench_gt_basemul_soa_run bench_gt_basemul_rowvec bench_gt_basemul_rowvec_cycles analyze_gt_rowpack_basemul_output_ranges
.PHONY: bench_gt_rowpack_pipeline_fused bench_gt_rowpack_pipeline_canonical bench_gt_rowpack_pipeline_compare
.PHONY: bench_gt_rowpack_pipeline_add_fused bench_gt_rowpack_pipeline_add_canonical bench_gt_rowpack_pipeline_add_compare
.PHONY: bench_gt_rowpack_pipeline_cycles_fused bench_gt_rowpack_pipeline_cycles_canonical bench_gt_rowpack_pipeline_cycles_compare
.PHONY: bench_gt_rowpack_pipeline_add_cycles_fused bench_gt_rowpack_pipeline_add_cycles_canonical bench_gt_rowpack_pipeline_add_cycles_compare
.PHONY: bench_gt_rowpack_pipeline_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_add_nativebasemul_cycles_fused
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_compare bench_gt_rowpack_invntt_isolate_cycles
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_compare bench_gt_rowpack_invntt_nativepost_isolate_cycles
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_cycles_compare bench_gt_rowpack_invntt_nativepost_mul2_isolate_cycles
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_compare
.PHONY: bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_compare bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles bench_gt_rowpack_invntt_stage_cycles bench_gt_rowpack_invntt_rowkernel_audit bench_gt_rowpack_rowkernel_arith_breakdown bench_gt_rowpack_rowkernel_reduction_probe
.PHONY: test_gt_rowpack_no_entry_no_end_fullpath bench_gt_rowpack_no_entry_no_end_fullpath_cycles bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles bench_gt_rowpack_no_entry_no_end_fullpath_cycles_compare
.PHONY: test_gt_rowpack_lazy_postmerge_asm_fullpath bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles bench_gt_rowpack_lazy_postmerge_asm_add_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles_compare bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles bench_gt_rowpack_lazy_postmerge_asm_v3_forward_add_cycles
.PHONY: bench_ntt_pipeline_stock_cycles bench_ntt_pipeline_add_stock_cycles bench_ntt_pipeline_gt_opt_cycles bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_vs_production_cycles_compare bench_gt_rowpack_component_cycles_dashboard bench_gt_rowpack_lazy_asm_vs_kpqc_final bench_gt_rowpack_lazy_asm_fullchain_stage_compare bench_gt_rowpack_forward_overhead_probes bench_gt_rowpack_forward_v2_overhead_breakdown bench_gt_rowpack_forward_output_overhead bench_gt_rowpack_forward_scatter_lower_bound bench_gt_rowpack_forward_v3_register_order_lower_bound bench_gt_rowpack_forward_v3_register_order_cycles bench_gt_rowpack_forward_v3_candidate_cycles bench_gt_rowpack_forward_v3b_stage345_cycles bench_gt_rowpack_lazy_asm_v3_forward_fullchain_compare bench_gt_rowpack_lazy_asm_v3b_forward_fullchain_compare audit_gt_rowpack_forward_stage345_liveout test_gt_rowpack_forward_stage345_layout_search test_gt_rowpack_forward_v3c_stage12_stage345_layout_search report_gt_rowpack_forward_topology_decision

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
# Default KEM keeps stock KPQC base layout.  GT KEM tests override this with
# gt_test/poly_gt_base_ref.c ntt.c or ntt.c asm/base_gt_ref.s.
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
# Defaults build the stock AArch64 implementation.  For GT diagnostics use:
#   PMU_BASE_SOURCES='gt_test/poly_gt_base_ref.c asm/base_gt.S'
#   PMU_CFLAGS='-DGT_BASE_REF_ONLY_BASEINV_ABI'
#   PMU_NTT_SOURCES='asm/my_ntt.s asm/slothy/my_32ntt.opt.s'
#   PMU_INVNTT_SOURCES=asm/inv_my_ntt.s
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

test_gt_reference: $(HEADERS) ntt.h ntt.c gt_test/test_gt_reference.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test_gt_reference gt_test/test_gt_reference.c

test_gt_base_ref: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/test_gt_base_ref.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test_gt_base_ref gt_test/test_gt_base_ref.c gt_test/poly_gt_base_ref.c ntt.c

test_gt_base_asm: $(HEADERS) ntt.h ntt.c gt_test/test_gt_base_ref.c asm/base_gt_ref.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DTEST_GT_BASE_USE_ABI -I. -o $(BUILD_DIR)/test_gt_base_asm gt_test/test_gt_base_ref.c ntt.c asm/base_gt_ref.s

test_gt_basemul_asm: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/test_gt_basemul_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(BASE_GT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -I. -o $(BUILD_DIR)/test_gt_basemul_asm gt_test/test_gt_basemul_asm.c gt_test/poly_gt_base_ref.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(BASE_GT_ASM)

test_gt_base_opt: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/test_gt_basemul_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(GT_BASE_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -I. -o $(BUILD_DIR)/test_gt_base_opt gt_test/test_gt_basemul_asm.c gt_test/poly_gt_base_ref.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(GT_BASE_OPT_ASM)

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

test_polyntt_harness: $(HEADERS) ntt.h ntt.c gt_test/test_polyntt_asm.c gt_test/polyntt_reference_shim.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) -I. -o $(BUILD_DIR)/test_polyntt_harness gt_test/test_polyntt_asm.c gt_test/polyntt_reference_shim.c ntt.c

test_polyntt_asm: $(HEADERS) ntt.h ntt.c gt_test/test_polyntt_asm.c $(POLYNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyntt_asm gt_test/test_polyntt_asm.c ntt.c $(POLYNTT_ASM)

test_polyinvntt_asm: $(HEADERS) ntt.h ntt.c gt_test/test_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyinvntt_asm gt_test/test_polyinvntt_asm.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)

test_polyinvntt_branchfold_a72: $(HEADERS) ntt.h ntt.c gt_test/test_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_BRANCHFOLD_A72_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyinvntt_branchfold_a72 gt_test/test_polyinvntt_asm.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_BRANCHFOLD_A72_ASM)

test_invntt_representatives: $(HEADERS) ntt.h ntt.c gt_test/test_invntt_representatives.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_invntt_representatives gt_test/test_invntt_representatives.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)

test_kem_invntt_contract: $(HEADERS) randombytes.h gt_test/test_kem_invntt_contract.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_kem_invntt_contract gt_test/test_kem_invntt_contract.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)

verify_invntt_constants: scripts/verify_invntt_constants.py asm/slothy/invntt_opt.s
	$(PYTHON) scripts/verify_invntt_constants.py

verify_invntt_layout: scripts/verify_invntt_layout.py
	$(PYTHON) scripts/verify_invntt_layout.py

verify_invntt_contracts: verify_invntt_constants verify_invntt_layout analyze_invntt32_ranges test_invntt_representatives
	./$(BUILD_DIR)/analyze_invntt32_ranges
	./$(BUILD_DIR)/test_invntt_representatives

analyze_invntt32_ranges: $(HEADERS) ntt.h ntt.c gt_test/analyze_invntt32_ranges.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_invntt32_ranges gt_test/analyze_invntt32_ranges.c

analyze_invntt_branchfold_reductions: $(HEADERS) ntt.h ntt.c gt_test/analyze_invntt_branchfold_reductions.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_invntt_branchfold_reductions gt_test/analyze_invntt_branchfold_reductions.c

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

bench_gt_rowpack_no_entry_no_end_fullpath_cycles_compare: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_no_entry_no_end_fullpath_cycles bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles
	./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_no_entry_no_end_fullpath_cycles
	./$(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_forward_v2_nativebasemul_nativepost_chunked_inplace_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles

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

bench_gt_rowpack_lazy_postmerge_asm_cycles_compare: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_no_entry_no_end_fullpath_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles bench_gt_rowpack_lazy_postmerge_asm_add_cycles
	./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_no_entry_no_end_fullpath_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_cycles
	./$(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_no_entry_no_end_fullpath_add_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_add_cycles

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

bench_gt_rowpack_invntt_rowkernel_audit: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_soa_invntt32_fullpath.c gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c docs/gt_soa_layout_experiment/audit_rowpack_invntt.py $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_INVNTT32_SYMBOLIC_ASM) asm/slothy/invntt_opt.s
	@mkdir -p $(BUILD_DIR)/rowpack_invntt_audit
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CFLAGS) -DROWPACK_PIPELINE_BENCH -DROWPACK_INVNTT_ISOLATE -DROWPACK_FORWARD_NTT_ASM -DROWPACK_NATIVE_BASEMUL -DROWPACK_NATIVE_POSTMERGE -DROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER -DROWPACK_INVNTT_AUDIT_SYMBOLS -S -Wno-unused-function -I. -o $(BUILD_DIR)/rowpack_invntt_audit/postmerge_audit.s gt_test/test_gt_rowpack_soa_invntt32_fullpath.c
	python3 docs/gt_soa_layout_experiment/audit_rowpack_invntt.py --row-kernel $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) --row-symbolic $(ROWPACK_INVNTT32_SYMBOLIC_ASM) --postmerge-asm $(BUILD_DIR)/rowpack_invntt_audit/postmerge_audit.s --production-asm asm/slothy/invntt_opt.s --generate-dir $(BUILD_DIR)/rowpack_invntt_audit
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"rowkernel_current\" -I. -o $(BUILD_DIR)/bench_rowkernel_current gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"rowkernel_arithmetic_skeleton\" -I. -o $(BUILD_DIR)/bench_rowkernel_arithmetic_skeleton gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.arithmetic_skeleton.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"rowkernel_shuffle_skeleton\" -I. -o $(BUILD_DIR)/bench_rowkernel_shuffle_skeleton gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.shuffle_skeleton.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"rowkernel_arithmetic_nop_skeleton\" -I. -o $(BUILD_DIR)/bench_rowkernel_arithmetic_nop_skeleton gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.arithmetic_nop_skeleton.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"rowkernel_shuffle_nop_skeleton\" -I. -o $(BUILD_DIR)/bench_rowkernel_shuffle_nop_skeleton gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.shuffle_nop_skeleton.S
	./$(BUILD_DIR)/bench_rowkernel_current
	./$(BUILD_DIR)/bench_rowkernel_arithmetic_skeleton
	./$(BUILD_DIR)/bench_rowkernel_shuffle_skeleton
	./$(BUILD_DIR)/bench_rowkernel_arithmetic_nop_skeleton
	./$(BUILD_DIR)/bench_rowkernel_shuffle_nop_skeleton

bench_gt_rowpack_rowkernel_arith_breakdown: $(HEADERS) gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c docs/gt_soa_layout_experiment/audit_rowpack_invntt.py $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_INVNTT32_SYMBOLIC_ASM) asm/slothy/invntt_opt.s
	@mkdir -p $(BUILD_DIR)/rowpack_invntt_audit
	python3 docs/gt_soa_layout_experiment/audit_rowpack_invntt.py --row-kernel $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) --row-symbolic $(ROWPACK_INVNTT32_SYMBOLIC_ASM) --production-asm asm/slothy/invntt_opt.s --generate-dir $(BUILD_DIR)/rowpack_invntt_audit
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"rowkernel_hotloop_24\" -I. -o $(BUILD_DIR)/bench_rowkernel_hotloop_24 gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_ROWKERNEL_CALLS=1 -DBENCH_LABEL=\"rowkernel_single_hotloop\" -I. -o $(BUILD_DIR)/bench_rowkernel_single_hotloop gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	./$(BUILD_DIR)/bench_rowkernel_hotloop_24
	./$(BUILD_DIR)/bench_rowkernel_single_hotloop

bench_gt_rowpack_rowkernel_reduction_probe: $(HEADERS) gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c docs/gt_soa_layout_experiment/audit_rowpack_invntt.py $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) $(ROWPACK_INVNTT32_ALLOC_ASM) $(ROWPACK_INVNTT32_SYMBOLIC_ASM)
	@mkdir -p $(BUILD_DIR)/rowpack_invntt_audit
	python3 docs/gt_soa_layout_experiment/audit_rowpack_invntt.py --row-kernel $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM) --row-symbolic $(ROWPACK_INVNTT32_SYMBOLIC_ASM) --generate-dir $(BUILD_DIR)/rowpack_invntt_audit --reduction-probe-source $(ROWPACK_INVNTT32_ALLOC_ASM)
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_opt_current\" -I. -o $(BUILD_DIR)/bench_reduction_probe_opt_current gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(ROWPACK_INVNTT32_SLOTHY_OPT_ASM)
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_alloc_current\" -I. -o $(BUILD_DIR)/bench_reduction_probe_alloc_current gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(ROWPACK_INVNTT32_ALLOC_ASM)
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_no_entry\" -I. -o $(BUILD_DIR)/bench_reduction_probe_no_entry gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.no_entry.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_no_row_end\" -I. -o $(BUILD_DIR)/bench_reduction_probe_no_row_end gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.no_row_end.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_no_entry_no_end\" -I. -o $(BUILD_DIR)/bench_reduction_probe_no_entry_no_end gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.no_entry_no_end.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_stage23_select_copy\" -I. -o $(BUILD_DIR)/bench_reduction_probe_stage23_select_copy gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.stage23_select_copy.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_no_entry_no_end_stage23_select_copy\" -I. -o $(BUILD_DIR)/bench_reduction_probe_no_entry_no_end_stage23_select_copy gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.no_entry_no_end_stage23_select_copy.S
	$(CC) $(CFLAGS) -O3 -fomit-frame-pointer -DBENCH_USE_PERF_CYCLES -DBENCH_LABEL=\"reduction_probe_fully_lazy_lower_bound\" -I. -o $(BUILD_DIR)/bench_reduction_probe_fully_lazy_lower_bound gt_test/bench_gt_rowpack_rowkernel_variant_cycles.c $(BUILD_DIR)/rowpack_invntt_audit/ntruplus768_invntt32_rowpack_soa_row.fully_lazy_lower_bound.S
	./$(BUILD_DIR)/bench_reduction_probe_opt_current
	./$(BUILD_DIR)/bench_reduction_probe_alloc_current
	./$(BUILD_DIR)/bench_reduction_probe_no_entry
	./$(BUILD_DIR)/bench_reduction_probe_no_row_end
	./$(BUILD_DIR)/bench_reduction_probe_no_entry_no_end
	./$(BUILD_DIR)/bench_reduction_probe_stage23_select_copy
	./$(BUILD_DIR)/bench_reduction_probe_no_entry_no_end_stage23_select_copy
	./$(BUILD_DIR)/bench_reduction_probe_fully_lazy_lower_bound

analyze_gt_rowpack_basemul_output_ranges: $(HEADERS) gt_test/analyze_gt_rowpack_basemul_output_ranges.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_gt_rowpack_basemul_output_ranges gt_test/analyze_gt_rowpack_basemul_output_ranges.c
	./$(BUILD_DIR)/analyze_gt_rowpack_basemul_output_ranges

test_gt_rowpack_no_entry_no_end_range_contract: $(HEADERS) ntt.h ntt.c gt_test/test_gt_rowpack_no_entry_no_end_range_contract.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_range_contract gt_test/test_gt_rowpack_no_entry_no_end_range_contract.c
	./$(BUILD_DIR)/test_gt_rowpack_no_entry_no_end_range_contract

bench_polyinvntt_asm: $(HEADERS) ntt.h ntt.c gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_rowbitrev_invntt_default\" -I. -o $(BUILD_DIR)/bench_polyinvntt_asm gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)

bench_polyinvntt_branchfold_a72: $(HEADERS) ntt.h ntt.c gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_BRANCHFOLD_A72_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_rowbitrev_invntt_branchfold_a72\" -I. -o $(BUILD_DIR)/bench_polyinvntt_branchfold_a72 gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_BRANCHFOLD_A72_ASM)

bench_polyinvntt_kpqc_final: $(HEADERS) gt_test/bench_polyinvntt_asm.c asm/ntt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"kpqc_final_invntt\" -I. -o $(BUILD_DIR)/bench_polyinvntt_kpqc_final gt_test/bench_polyinvntt_asm.c asm/ntt.s

bench_polyinvntt_compare: bench_polyinvntt_asm bench_polyinvntt_kpqc_final
	./$(BUILD_DIR)/bench_polyinvntt_asm
	./$(BUILD_DIR)/bench_polyinvntt_kpqc_final

bench_gt_basemul_ref: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt_ref.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_LABEL=\"gt_basemul_scalar_ref\" -I. -o $(BUILD_DIR)/bench_gt_basemul_ref gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt_ref.s

bench_gt_basemul_asm: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c $(BASE_GT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_LABEL=\"$(BASE_GT_BENCH_LABEL)\" -I. -o $(BUILD_DIR)/bench_gt_basemul_asm gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c $(BASE_GT_ASM)

bench_gt_basemul_stock: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c $(STOCK_BASE_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"stock_basemul_raw\" -I. -o $(BUILD_DIR)/bench_gt_basemul_stock gt_test/bench_gt_basemul.c ntt.c $(STOCK_BASE_ASM)

bench_gt_basemul_compare: bench_gt_basemul_ref bench_gt_basemul_asm bench_gt_basemul_stock
	./$(BUILD_DIR)/bench_gt_basemul_ref
	./$(BUILD_DIR)/bench_gt_basemul_asm
	./$(BUILD_DIR)/bench_gt_basemul_stock

bench_base_stock: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"stock_base\" -I. -o $(BUILD_DIR)/bench_base_stock gt_test/bench_gt_basemul.c ntt.c asm/base.s

bench_base_stock_opt: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c asm/base.opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"stock_base_opt\" -I. -o $(BUILD_DIR)/bench_base_stock_opt gt_test/bench_gt_basemul.c ntt.c asm/base.opt.s

bench_base_gt: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_LABEL=\"gt_base\" -I. -o $(BUILD_DIR)/bench_base_gt gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt.S

bench_base_gt_opt: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c $(GT_BASE_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_LABEL=\"gt_base_opt\" -I. -o $(BUILD_DIR)/bench_base_gt_opt gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c $(GT_BASE_OPT_ASM)

bench_base_compare: bench_base_stock bench_base_stock_opt bench_base_gt bench_base_gt_opt
	./$(BUILD_DIR)/bench_base_stock
	./$(BUILD_DIR)/bench_base_stock_opt
	./$(BUILD_DIR)/bench_base_gt
	./$(BUILD_DIR)/bench_base_gt_opt

bench_gt_basemul_soa: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul_soa.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) -I. -o $(BUILD_DIR)/bench_gt_basemul_soa gt_test/bench_gt_basemul_soa.c ntt.c

bench_gt_basemul_soa_run: bench_gt_basemul_soa
	./$(BUILD_DIR)/bench_gt_basemul_soa

bench_gt_basemul_rowvec: bench_gt_basemul_soa_run

bench_gt_basemul_rowvec_cycles: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul_soa.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) -DBENCH_USE_PERF_CYCLES -I. -o $(BUILD_DIR)/bench_gt_basemul_rowvec_cycles gt_test/bench_gt_basemul_soa.c ntt.c
	./$(BUILD_DIR)/bench_gt_basemul_rowvec_cycles

bench_gt_basemuladd_ref: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt_ref.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_basemuladd_scalar_ref\" -I. -o $(BUILD_DIR)/bench_gt_basemuladd_ref gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt_ref.s

bench_gt_basemuladd_asm: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c $(BASE_GT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_basemuladd_asm\" -I. -o $(BUILD_DIR)/bench_gt_basemuladd_asm gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c $(BASE_GT_ASM)

bench_gt_basemuladd_stock: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c $(STOCK_BASE_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"stock_basemuladd_raw\" -I. -o $(BUILD_DIR)/bench_gt_basemuladd_stock gt_test/bench_gt_basemul.c ntt.c $(STOCK_BASE_ASM)

bench_gt_basemuladd_compare: bench_gt_basemuladd_ref bench_gt_basemuladd_asm bench_gt_basemuladd_stock
	./$(BUILD_DIR)/bench_gt_basemuladd_ref
	./$(BUILD_DIR)/bench_gt_basemuladd_asm
	./$(BUILD_DIR)/bench_gt_basemuladd_stock

bench_baseadd_stock: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"stock_baseadd\" -I. -o $(BUILD_DIR)/bench_baseadd_stock gt_test/bench_gt_basemul.c ntt.c asm/base.s

bench_baseadd_stock_opt: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c asm/base.opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"stock_baseadd_opt\" -I. -o $(BUILD_DIR)/bench_baseadd_stock_opt gt_test/bench_gt_basemul.c ntt.c asm/base.opt.s

bench_baseadd_gt: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_baseadd\" -I. -o $(BUILD_DIR)/bench_baseadd_gt gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt.S

bench_baseadd_gt_opt: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c $(GT_BASE_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_baseadd_opt\" -I. -o $(BUILD_DIR)/bench_baseadd_gt_opt gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c $(GT_BASE_OPT_ASM)

bench_baseadd_compare: bench_baseadd_stock bench_baseadd_stock_opt bench_baseadd_gt bench_baseadd_gt_opt
	./$(BUILD_DIR)/bench_baseadd_stock
	./$(BUILD_DIR)/bench_baseadd_stock_opt
	./$(BUILD_DIR)/bench_baseadd_gt
	./$(BUILD_DIR)/bench_baseadd_gt_opt

bench_ntt_pipeline_stock: $(HEADERS) gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"kpqc_final_ntt_mul_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_stock gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s

bench_ntt_pipeline_gt: $(HEADERS) ntt.h ntt.c gt_test/bench_ntt_pipeline.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_current_ntt_mul_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_gt gt_test/bench_ntt_pipeline.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.S

bench_ntt_pipeline_stock_opt: $(HEADERS) gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"kpqc_baseopt_ntt_mul_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_stock_opt gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.opt.s

bench_ntt_pipeline_gt_opt: $(HEADERS) ntt.h ntt.c gt_test/bench_ntt_pipeline.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_baseopt_ntt_mul_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_gt_opt gt_test/bench_ntt_pipeline.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.opt.s

bench_ntt_pipeline_compare: bench_ntt_pipeline_stock bench_ntt_pipeline_gt
	./$(BUILD_DIR)/bench_ntt_pipeline_stock
	./$(BUILD_DIR)/bench_ntt_pipeline_gt

bench_ntt_pipeline_add_stock: $(HEADERS) gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"kpqc_final_ntt_basemul_add_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_add_stock gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s

bench_ntt_pipeline_add_gt: $(HEADERS) ntt.h ntt.c gt_test/bench_ntt_pipeline.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_current_ntt_basemul_add_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_add_gt gt_test/bench_ntt_pipeline.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.S

bench_ntt_pipeline_add_stock_opt: $(HEADERS) gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"kpqc_baseopt_ntt_basemul_add_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_add_stock_opt gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.opt.s

bench_ntt_pipeline_add_gt_opt: $(HEADERS) ntt.h ntt.c gt_test/bench_ntt_pipeline.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_baseopt_ntt_basemul_add_pipeline\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt gt_test/bench_ntt_pipeline.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) asm/base_gt.opt.s

bench_ntt_pipeline_add_compare: bench_ntt_pipeline_add_stock bench_ntt_pipeline_add_gt
	./$(BUILD_DIR)/bench_ntt_pipeline_add_stock
	./$(BUILD_DIR)/bench_ntt_pipeline_add_gt

bench_ntt_pipeline_stock_cycles: $(HEADERS) gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(NTT_PIPELINE_CYCLE_CFLAGS) -DBENCH_LABEL=\"kpqc_final_ntt_mul_pipeline_cycles\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_stock_cycles gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s

bench_ntt_pipeline_add_stock_cycles: $(HEADERS) gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(NTT_PIPELINE_CYCLE_CFLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"kpqc_final_ntt_basemul_add_pipeline_cycles\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_add_stock_cycles gt_test/bench_ntt_pipeline.c asm/ntt.s asm/base.s

bench_ntt_pipeline_gt_opt_cycles: $(HEADERS) ntt.h ntt.c gt_test/bench_ntt_pipeline.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(GT_BASE_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(NTT_PIPELINE_CYCLE_CFLAGS) -DBENCH_LABEL=\"gt_baseopt_ntt_mul_pipeline_cycles\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles gt_test/bench_ntt_pipeline.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(GT_BASE_OPT_ASM)

bench_ntt_pipeline_add_gt_opt_cycles: $(HEADERS) ntt.h ntt.c gt_test/bench_ntt_pipeline.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(GT_BASE_OPT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(NTT_PIPELINE_CYCLE_CFLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_baseopt_ntt_basemul_add_pipeline_cycles\" -I. -o $(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles gt_test/bench_ntt_pipeline.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(GT_BASE_OPT_ASM)

bench_gt_rowpack_vs_production_cycles_compare: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_pipeline_cycles_fused bench_gt_rowpack_pipeline_nativebasemul_cycles_fused bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_pipeline_add_cycles_fused bench_gt_rowpack_pipeline_add_nativebasemul_cycles_fused
	./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_nativebasemul_cycles_fused
	./$(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_cycles_fused
	./$(BUILD_DIR)/bench_gt_rowpack_pipeline_add_nativebasemul_cycles_fused

bench_gt_rowpack_component_cycles_dashboard: bench_gt_rowpack_vs_production_cycles_compare

bench_gt_rowpack_lazy_asm_vs_kpqc_final: bench_ntt_pipeline_stock_cycles bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles bench_ntt_pipeline_add_stock_cycles bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_add_cycles
	$(PYTHON) docs/gt_soa_layout_experiment/compare_lazy_rowpack_vs_kpqc.py \
		--kpqc-product ./$(BUILD_DIR)/bench_ntt_pipeline_stock_cycles \
		--gt-product ./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles \
		--rowpack-product ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_cycles \
		--kpqc-add ./$(BUILD_DIR)/bench_ntt_pipeline_add_stock_cycles \
		--gt-add ./$(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles \
		--rowpack-add ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_add_cycles

bench_gt_rowpack_lazy_asm_fullchain_stage_compare: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_add_cycles
	$(PYTHON) docs/gt_soa_layout_experiment/compare_lazy_rowpack_fullchain_stages.py \
		--gt-product ./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles \
		--rowpack-product ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_cycles \
		--gt-add ./$(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles \
		--rowpack-add ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_add_cycles

bench_gt_rowpack_forward_overhead_probes: $(HEADERS) gt_test/bench_gt_rowpack_forward_overhead.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(ROWPACK_PIPELINE_CYCLE_CFLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/bench_gt_rowpack_forward_overhead_probes gt_test/bench_gt_rowpack_forward_overhead.c

bench_gt_rowpack_forward_v2_overhead_breakdown: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_cycles bench_gt_rowpack_forward_overhead_probes
	$(PYTHON) docs/gt_soa_layout_experiment/compare_rowpack_forward_overhead.py \
		--gt-forward ./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles \
		--rowpack-forward ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_cycles \
		--probes ./$(BUILD_DIR)/bench_gt_rowpack_forward_overhead_probes

bench_gt_rowpack_forward_output_overhead: bench_gt_rowpack_forward_v2_overhead_breakdown

bench_gt_rowpack_forward_scatter_lower_bound: bench_gt_rowpack_forward_v2_overhead_breakdown

bench_gt_rowpack_forward_v3_register_order_lower_bound:
	@echo "NOTE: Forward v3 register-order candidate is not implemented yet."
	@echo "NOTE: This target reports Gate 4 lower-bound / recoverable-window numbers."
	$(MAKE) test_gt_rowpack_forward_v3_register_order_contract
	$(MAKE) bench_gt_rowpack_forward_scatter_lower_bound

bench_gt_rowpack_forward_v3_register_order_cycles: bench_gt_rowpack_forward_v3_register_order_lower_bound

bench_gt_rowpack_forward_v3_candidate_cycles: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles bench_gt_rowpack_forward_overhead_probes
	$(PYTHON) docs/gt_soa_layout_experiment/compare_rowpack_forward_overhead.py \
		--gt-forward ./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles \
		--rowpack-forward ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles \
		--rowpack-label "rowpack Forward v3 structured-store candidate" \
		--probes ./$(BUILD_DIR)/bench_gt_rowpack_forward_overhead_probes

bench_gt_rowpack_forward_v3b_stage345_cycles: test_gt_rowpack_forward_v3b_stage345_contract
	@if [ ! -f "$(ROWPACK_FORWARD_NTT_V3B_OPT_ASM)" ]; then \
		echo "Forward v3b ASM candidate is not implemented yet: $(ROWPACK_FORWARD_NTT_V3B_OPT_ASM)"; \
		exit 1; \
	fi; \
	make bench_gt_rowpack_forward_v3_candidate_cycles \
		ROWPACK_FORWARD_NTT_V3_ASM="$(ROWPACK_FORWARD_NTT_V3B_ASM)"

bench_gt_rowpack_lazy_asm_v3_forward_fullchain_compare: bench_ntt_pipeline_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles bench_ntt_pipeline_add_gt_opt_cycles bench_gt_rowpack_lazy_postmerge_asm_v3_forward_add_cycles
	$(PYTHON) docs/gt_soa_layout_experiment/compare_lazy_rowpack_fullchain_stages.py \
		--gt-product ./$(BUILD_DIR)/bench_ntt_pipeline_gt_opt_cycles \
		--rowpack-product ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_v3_forward_cycles \
		--gt-add ./$(BUILD_DIR)/bench_ntt_pipeline_add_gt_opt_cycles \
		--rowpack-add ./$(BUILD_DIR)/bench_gt_rowpack_lazy_postmerge_asm_v3_forward_add_cycles

bench_gt_rowpack_lazy_asm_v3b_forward_fullchain_compare: test_gt_rowpack_forward_v3b_stage345_contract
	@if [ ! -f "$(ROWPACK_FORWARD_NTT_V3B_OPT_ASM)" ]; then \
		echo "Forward v3b ASM candidate is not implemented yet: $(ROWPACK_FORWARD_NTT_V3B_OPT_ASM)"; \
		exit 1; \
	fi; \
	make bench_gt_rowpack_lazy_asm_v3_forward_fullchain_compare \
		ROWPACK_FORWARD_NTT_V3_ASM="$(ROWPACK_FORWARD_NTT_V3B_ASM)"

audit_gt_rowpack_forward_stage345_liveout:
	$(PYTHON) docs/gt_soa_layout_experiment/audit_forward_stage345_liveout.py

test_gt_rowpack_forward_stage345_layout_search: audit_gt_rowpack_forward_stage345_liveout
	$(PYTHON) docs/gt_soa_layout_experiment/search_forward_stage345_layout.py

bench_kem_dec: $(HEADERS) randombytes.h gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"$(KEM_BENCH_LABEL)\" -I. -o $(BUILD_DIR)/bench_kem_dec gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)

bench_kem_dec_kpqc_final: $(HEADERS) randombytes.h gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c poly.c asm/add.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S asm/ntt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"kpqc_final_kem_dec\" -I. -o $(BUILD_DIR)/bench_kem_dec_kpqc_final gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c poly.c asm/add.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S asm/ntt.s

bench_kem_dec_gt: $(HEADERS) randombytes.h ntt.h ntt.c gt_test/bench_kem_dec.c gt_test/poly_gt_base_ref.c randombytes.c kem.c symmetric.c asm/base_gt.S asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_ONLY_BASEINV_ABI -DBENCH_LABEL=\"gt_current_kem_dec\" -I. -o $(BUILD_DIR)/bench_kem_dec_gt gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt.S asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(POLYNTT_ASM) $(POLYINVNTT_ASM)

bench_kem_dec_compare: bench_kem_dec_kpqc_final bench_kem_dec_gt
	./$(BUILD_DIR)/bench_kem_dec_kpqc_final
	./$(BUILD_DIR)/bench_kem_dec_gt

bench_pmu: $(HEADERS) randombytes.h gt_test/bench_pmu.c randombytes.c kem.c symmetric.c ntt.c $(PMU_BASE_SOURCES) asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(PMU_NTT_SOURCES) $(PMU_INVNTT_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(PMU_CFLAGS) -DPMU_BENCH_MODE=\"$(PMU_MODE)\" -DPMU_BENCH_LABEL=\"$(PMU_LABEL)\" -DPMU_BENCH_CALLS=$(PMU_CALLS) -DPMU_BENCH_WARMUP=$(PMU_WARMUP) -DPMU_SUBTRACT_EMPTY=$(PMU_SUBTRACT_EMPTY) -DPMU_FIXED_ONLY=$(PMU_FIXED_ONLY) -DPMU_ROUNDS=$(PMU_ROUNDS) -DPMU_DISCARD_FIRST=$(PMU_DISCARD_FIRST) -I. -o $(BUILD_DIR)/bench_pmu gt_test/bench_pmu.c randombytes.c kem.c symmetric.c ntt.c $(PMU_BASE_SOURCES) asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(PMU_NTT_SOURCES) $(PMU_INVNTT_SOURCES)

bench_pmu_base_compare: $(HEADERS) randombytes.h gt_test/bench_pmu.c gt_test/bench_pmu_stock_base_renamed.S gt_test/bench_pmu_gt_base_renamed.S randombytes.c kem.c symmetric.c ntt.c poly.c asm/base.s $(PMU_COMPARE_LEFT_ASM) $(PMU_COMPARE_RIGHT_ASM) asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S asm/ntt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(PMU_CFLAGS) -DPMU_BASE_COMPARE=1 -DPMU_BENCH_MODE=\"$(PMU_COMPARE_MODE)\" -DPMU_BENCH_LABEL=\"$(PMU_COMPARE_LABEL)\" -DPMU_BENCH_CALLS=$(PMU_CALLS) -DPMU_BENCH_WARMUP=$(PMU_WARMUP) -DPMU_SUBTRACT_EMPTY=$(PMU_SUBTRACT_EMPTY) -DPMU_FIXED_ONLY=$(PMU_FIXED_ONLY) -DPMU_ROUNDS=$(PMU_ROUNDS) -DPMU_DISCARD_FIRST=$(PMU_DISCARD_FIRST) -DPMU_COMPARE_LEFT_LABEL=\"$(PMU_COMPARE_LEFT_LABEL)\" -DPMU_COMPARE_RIGHT_LABEL=\"$(PMU_COMPARE_RIGHT_LABEL)\" -DBENCH_PMU_STOCK_BASE_INCLUDE=\"$(abspath $(PMU_COMPARE_LEFT_ASM))\" -DBENCH_PMU_GT_BASE_INCLUDE=\"$(abspath $(PMU_COMPARE_RIGHT_ASM))\" -I. -o $(BUILD_DIR)/bench_pmu_base_compare gt_test/bench_pmu.c randombytes.c kem.c symmetric.c ntt.c poly.c asm/base.s asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S asm/ntt.s gt_test/bench_pmu_stock_base_renamed.S gt_test/bench_pmu_gt_base_renamed.S

bench_pmu_base_compare_stock_gt:
	$(MAKE) bench_pmu_base_compare PMU_COMPARE_LABEL=stock_vs_gt_base PMU_COMPARE_LEFT_ASM=asm/base.s PMU_COMPARE_RIGHT_ASM=asm/base_gt.S PMU_COMPARE_LEFT_LABEL=stock_base PMU_COMPARE_RIGHT_LABEL=gt_base

bench_pmu_base_compare_stockopt_gtopt:
	$(MAKE) bench_pmu_base_compare PMU_COMPARE_LABEL=stockopt_vs_gtopt_base PMU_COMPARE_LEFT_ASM=asm/base.opt.s PMU_COMPARE_RIGHT_ASM=asm/base_gt.opt.s PMU_COMPARE_LEFT_LABEL=stock_base_opt PMU_COMPARE_RIGHT_LABEL=gt_base_opt

bench_pmu_base_compare_stock_stockopt:
	$(MAKE) bench_pmu_base_compare PMU_COMPARE_LABEL=stock_base_vs_stock_base_opt PMU_COMPARE_LEFT_ASM=asm/base.s PMU_COMPARE_RIGHT_ASM=asm/base.opt.s PMU_COMPARE_LEFT_LABEL=stock_base PMU_COMPARE_RIGHT_LABEL=stock_base_opt

bench_pmu_base_compare_gt_gtopt:
	$(MAKE) bench_pmu_base_compare PMU_COMPARE_LABEL=gt_base_vs_gt_base_opt PMU_COMPARE_LEFT_ASM=asm/base_gt.S PMU_COMPARE_RIGHT_ASM=asm/base_gt.opt.s PMU_COMPARE_LEFT_LABEL=gt_base PMU_COMPARE_RIGHT_LABEL=gt_base_opt

bench_pmu_symbols: $(HEADERS) randombytes.h gt_test/bench_pmu.c randombytes.c kem.c symmetric.c ntt.c $(PMU_BASE_SOURCES) asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(PMU_NTT_SOURCES) $(PMU_INVNTT_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) $(PMU_CFLAGS) -DPMU_SYMBOLS_ONLY=1 -DPMU_BENCH_MODE=\"empty\" -DPMU_BENCH_LABEL=\"pmu_symbols\" -DPMU_BENCH_CALLS=1 -DPMU_BENCH_WARMUP=0 -DPMU_SUBTRACT_EMPTY=0 -DPMU_FIXED_ONLY=1 -DPMU_ROUNDS=1 -DPMU_DISCARD_FIRST=0 -I. -o $(BUILD_DIR)/bench_pmu_symbols gt_test/bench_pmu.c randombytes.c kem.c symmetric.c ntt.c $(PMU_BASE_SOURCES) asm/add.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(PMU_NTT_SOURCES) $(PMU_INVNTT_SOURCES)
	./$(BUILD_DIR)/bench_pmu_symbols

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
