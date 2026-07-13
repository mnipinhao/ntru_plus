.PHONY: test_u01v3_g1_fullpath test_u01v3_g1_reduction_slothy
.PHONY: test_invntt_lazy_twiddle1_stage123 test_invntt_boundary_experiments
.PHONY: bench_invntt_next_wave_pmu
.PHONY: test_kem_invntt_lazy_twiddle1_stage123 test_kem_invntt_lazy_twiddle1_stage123_len16
.PHONY: profile_kem_gt_production_opt profile_kem_gt_production_opt_rminus1

test_u01v3_g1_fullpath: $(HEADERS) ntt.h gt_test/test_u01v3_g1_fullpath.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_S2_FULLPATH_ASM) $(U01V3_G1_ABI_SENTINEL_ASM) $(U01V3_G1_S2_ABI_SENTINEL_ASM) asm/gt/experiment/forward_ntt/u01_block_first_tables.inc
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_u01v3_g1_fullpath gt_test/test_u01v3_g1_fullpath.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_S2_FULLPATH_ASM) $(U01V3_G1_ABI_SENTINEL_ASM) $(U01V3_G1_S2_ABI_SENTINEL_ASM)
	./$(BUILD_DIR)/test_u01v3_g1_fullpath

test_u01v3_g1_reduction_slothy: $(HEADERS) ntt.h gt_test/test_u01v3_g1_reduction_slothy.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_R123_FULLPATH_ASM) $(U01V3_G1_R123_S2_FULLPATH_ASM) $(U01V3_G1_R123_ABI_SENTINEL_ASM) $(U01V3_G1_R123_S2_ABI_SENTINEL_ASM) asm/gt/experiment/forward_ntt/u01_block_first_tables.inc
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_u01v3_g1_reduction_slothy gt_test/test_u01v3_g1_reduction_slothy.c $(GT_NTT_ASM_PHASE123_N1) $(U01V3_G1_FULLPATH_ASM) $(U01V3_G1_R123_FULLPATH_ASM) $(U01V3_G1_R123_S2_FULLPATH_ASM) $(U01V3_G1_R123_ABI_SENTINEL_ASM) $(U01V3_G1_R123_S2_ABI_SENTINEL_ASM)
	./$(BUILD_DIR)/test_u01v3_g1_reduction_slothy

test_invntt_lazy_twiddle1_stage123: $(HEADERS) ntt.h ntt.c gt_test/test_invntt_lazy_twiddle1_stage123.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_BASELINE_ASM) $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. -o $(BUILD_DIR)/test_invntt_lazy_twiddle1_stage123 gt_test/test_invntt_lazy_twiddle1_stage123.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_BASELINE_ASM) $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM)
	./$(BUILD_DIR)/test_invntt_lazy_twiddle1_stage123

test_invntt_boundary_experiments: $(HEADERS) ntt.h ntt.c gt_test/test_invntt_boundary_experiments.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) asm/gt/experiment/invntt/invntt_boundary_experiments.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 -Wno-unused-function -I. -o $(BUILD_DIR)/test_invntt_boundary_experiments gt_test/test_invntt_boundary_experiments.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) asm/gt/experiment/invntt/invntt_boundary_experiments.S
	./$(BUILD_DIR)/test_invntt_boundary_experiments

bench_invntt_next_wave_pmu: $(HEADERS) ntt.h ntt.c gt_bench/bench_invntt_next_wave_pmu.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_PRODUCTION_ASM) asm/gt/experiment/invntt/poly_invntt_rminus1_baseline_namespaced.S $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM) asm/gt/experiment/invntt/invntt_boundary_experiments.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c11 -Wno-unused-function -I. -o $(BUILD_DIR)/bench_invntt_next_wave_pmu gt_bench/bench_invntt_next_wave_pmu.c ntt.c $(GT_NTT_ASM_PHASE123_N1) $(GT_BASE_RMINUS1_OPT_ASM) $(GT_INVNTT_RMINUS1_PRODUCTION_ASM) asm/gt/experiment/invntt/poly_invntt_rminus1_baseline_namespaced.S $(GT_INVNTT_LAZY_TWIDDLE1_STAGE123_ASM) $(GT_INVNTT_POST_BRANCHFOLD_SLOTHY_ASM) asm/gt/experiment/invntt/invntt_boundary_experiments.S

test_kem_invntt_lazy_twiddle1_stage123: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_INVNTT_LAZY_TWIDDLE1_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123 randombytes.c test/test.c $(GT_INVNTT_LAZY_TWIDDLE1_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123

test_kem_invntt_lazy_twiddle1_stage123_len16: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_INVNTT_LAZY_TWIDDLE1_LEN16_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123_len16 randombytes.c test/test.c $(GT_INVNTT_LAZY_TWIDDLE1_LEN16_KEM_SOURCES)
	./$(BUILD_DIR)/test_kem_invntt_lazy_twiddle1_stage123_len16

profile_kem_gt_production_opt: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c gt_bench/kem_component_profiler.c ntt.h $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) $(GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -DKEM_COMPONENT_PROFILE_TARGET=\"gt_production_default\" -Wno-unused-function -I. -o $(BUILD_DIR)/profile_kem_gt_production_opt randombytes.c gt_bench/kem_component_profiler.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES) $(GT_RMINUS1_STAGE123SCRATCH_BENCH_ASM)

profile_kem_gt_production_opt_rminus1: profile_kem_gt_production_opt
