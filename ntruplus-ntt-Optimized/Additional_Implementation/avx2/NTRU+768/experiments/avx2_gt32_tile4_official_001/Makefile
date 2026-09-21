CC ?= gcc
PYTHON ?= python3
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion
CFLAGS += -mavx2 -fno-strict-aliasing
KEM_CFLAGS := $(CFLAGS) -mbmi2 -mpopcnt -maes -march=native -mtune=native

BUILD := build
Q24_CAGE_OFFSETS := 0 32 64 96 128 160 192 224
Q24_CAGE_NORMAL_BINS := $(addprefix $(BUILD)/bench_q24_cage_,$(Q24_CAGE_OFFSETS))
Q24_CAGE_REVERSED_BINS := $(addprefix $(BUILD)/bench_q24_cage_reversed_,$(Q24_CAGE_OFFSETS))
Q24_COMPACT_INC := generated/tile4_q24_compact.inc
Q24_COMPACT_JSON := generated/tile4_q24_compact.json
Q24_LAZY_SCHEDULE_INC := generated/tile4_q24_lazy_schedules.inc
Q24_LAZY_SCHEDULE_JSON := generated/tile4_q24_lazy_schedules.json
Q24_ENCAP_HR_INC := generated/tile4_q24_encap_highrange.inc
Q24_ENCAP_HR_JSON := generated/tile4_q24_encap_highrange_gate.json
Q24_PACK3_COMPACT_ARTIFACTS := generated/tile4_q24_pack3_compact.inc \
	generated/tile4_q24_pack3_compact_gate.json
REP_FAMILY_GATE := generated/tile4_rep_family_gate.json
BASEINV_OFFICIAL_COMPAT_GATE := generated/tile4_baseinv_official_compat_gate.json
PAIR02_EXACT_DAG_TILE_GATE := generated/tile4_pair02_exact_dag_tile_gate.json
FWD_OFFICIAL_LANDING_GATE := generated/tile4_forward_official_landing_gate.json
POLYMUL_JOINT_RESCORE_GATE := generated/tile4_polymul_joint_rescore_gate.json
PRIORITY12_RESULTS := results/tile4-priority12-executable-short.json
BM_S0_TYPED_GATE := generated/tile4_bm_s0_typed_gate.json
GT64_D2_STATIC_GATE := generated/tile4_gt64_d2_static_gate.json
KEYGEN_BM_ELIMINATION_GATE := generated/tile4_keygen_bm_elimination_gate.json
N32FIRST_SPLIT_TWIST_GATE := generated/tile4_n32first_split_twist_gate.json
N32_MR_S3LOCAL_GATE := generated/tile4_n32_mr_s3local_gate.json
N32_GT_PFA_NATIVE_GATE := generated/tile4_n32_gt_pfa_native_gate.json
N32_GT_PFA_JOINT_GATE := generated/tile4_n32_gt_pfa_joint_gate.json
N32_GT_FINAL_GATES := generated/tile4_n32_gt_suffix_superopt_gate.json \
	generated/tile4_n32_gt_wave_producer_gate.json \
	generated/tile4_n32_gt_final_gate.json
N32_GT_BM_ISLAND_ARTIFACTS := generated/tile4_n32_gt_bm_island_gate.json \
	generated/tile4_n32_gt_bm_island_constants.inc
N32_PHYSICAL_SCHEDULE_GATE := generated/tile4_n32_physical_schedule_gate.json
N32_STAGE_NATIVE_TILE_GATE := generated/tile4_n32_stage_native_tile_gate.json
N32_NATIVE_INVERSE_GATE := generated/tile4_n32_native_inverse_gate.json
N32_IDFT3_L2_GATES := generated/tile4_n32_idft3_l2_fused_gate.json \
	generated/tile4_n32_r1u_safe_rep_gate.json
N32_INVERSE_INSERTION_GATE := generated/tile4_n32_inverse_insertion_gate.json
N32_BM_INV_JOINT_SEARCH := generated/tile4_n32_bm_inv_joint_range_search.json
N32_BM_INV_JOINT_GATE := generated/tile4_n32_bm_inv_joint_range_gate.json
N32_INVERSE_ASM_ARTIFACTS := generated/tile4_n32_inverse_asm_gate.json \
	generated/tile4_n32_inverse_constants.inc \
	generated/tile4_n32_inverse_test_ranges.h
N32_FORWARD_ASM_ARTIFACTS := generated/tile4_n32_forward_asm_gate.json \
	generated/tile4_n32_forward_constants.inc
N32_SUFFIX_RESCHEDULE_GATE := generated/tile4_n32_suffix_reschedule_gate.json
N32_BRANCHLOCAL_RAW160_GATE := generated/tile4_n32_branchlocal_raw160_gate.json
N32_BRANCHLOCAL_SCALE_GATE := generated/tile4_n32_branchlocal_scale_placement_gate.json
SPCRT_B3_EXEC_ARTIFACTS := generated/tile4_spcrt_b3_exec_constants.inc \
	generated/tile4_spcrt_b3_exec_manifest.json
GT32_GLOBAL_PHYSICAL_LAYOUT_GATE := generated/tile4_global_physical_layout_gate.json
N5_PM_PROGRESSIVE_SUFFIX_GATE := generated/tile4_n5_pm_progressive_suffix_survey.json
N5_M_FRONTEND_SEAM_GATE := generated/tile4_n5_m_frontend_seam_gate.json
N5_FRONTEND_LINEAR_CIRCUIT_GATE := generated/tile4_n5_frontend_linear_circuit_gate.json
N5_SCALE_EDGE_SURVEY := generated/tile4_n5_scale_edge_survey.json
SCALE_CONSUMER_FUSION_GATE := generated/tile4_scale_consumer_fusion_gate.json
ENCAP_REP_ARCH_GATE := generated/tile4_encap_representation_architecture_gate.json
GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS := \
	generated/tile4_global_physical_constants.inc \
	src/tile4_global_physical_asm.S
FWD_LANDING_BASEINV_ARTIFACTS := generated/tile4_forward_landing_baseinv_gate.json \
	generated/tile4_baseinv_p_tables.inc generated/tile4_baseinv_p_mapping.h \
	generated/tile4_q24_p_encode.inc generated/tile4_q24_p_encode_gate.json
Q24_LAZY_SCHEDULES := 0 1 2 3
Q24_LAZY_NORMAL_BINS := $(addprefix $(BUILD)/bench_q24_lazy_L,$(Q24_LAZY_SCHEDULES))
Q24_LAZY_REVERSED_BINS := $(addprefix $(BUILD)/bench_q24_lazy_reversed_L,$(Q24_LAZY_SCHEDULES))
DUAL_TERMINAL_CONSTANTS := generated/tile4_dual_terminal_constants.inc
DUAL_TERMINAL_GATE := generated/tile4_dual_terminal_gate.json
REFERENCE := ../../../../aarch64/NTRU+768/ntt.c
FROZEN := ../gt_ntt
OFFICIAL := ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
FROZEN_LAMBDA := ../avx2_gt16_quadratic_official_001/generated/quartic-lambda.c
TRANSPOSE_REDEPOSIT_GATE := generated/tile4_transpose_redeposit_gate.json
AOS_DOT_REDC16_GATE := generated/tile4_aos_dot_redc16_gate.json
AOS_DOT_REDC16_CONSTANTS := generated/tile4_aos_dot_redc16_constants.inc
GEN := generated/tile4_constants.inc generated/tile4_mapping.csv \
	generated/tile4_manifest.json generated/tile4_range_metadata.json \
	generated/tile4_frontend_constants.h generated/tile4_frontend_fixed.inc \
	generated/tile4_frontend_wide.inc generated/tile4_basemul_constants.h \
	generated/tile4_basemul_constants.inc generated/tile4_scale_contract.json \
	generated/tile4_private_inverse_constants.inc \
	generated/tile4_private_inverse_range.json \
	generated/tile4_raw_aos_inverse_range.json \
	generated/tile4_inverse_tail_constants.h \
	generated/tile4_inverse_tail_constants.inc \
	generated/tile4_inverse_tail_range.json \
	generated/tile4_serialized_mapping.h \
	generated/tile4_serialized_mapping.json \
	generated/tile4_frombytes_aos_stores.inc \
	generated/tile4_correct_semantic_decoder_gate.json \
	generated/tile4_frombytes_semantic_soa_routes.inc \
	generated/tile4_correct_semantic_encodeq_gate.json \
	generated/tile4_soa_to_official_routes.inc \
	generated/tile4_frombytes_direct_soa_plan.json \
	generated/tile4_pair_aosoa_gate.json \
	generated/tile4_e1_producer_gate.json \
	generated/tile4_wide_aos_range.json \
	generated/tile4_a2f_dag.json generated/tile4_s45_layout_gate.json \
	generated/tile4_terminal_layout_family_gate.json \
	generated/tile4_terminal_transpose_cut_gate.json \
	generated/tile4_pair_native_bm_gate.json \
	generated/tile4_terminal_karatsuba_basis_gate.json \
	generated/tile4_terminal_range_schedule_gate.json \
	generated/tile4_high_range_bm_gate.json \
	generated/tile4_permutation_native_gate.json \
	$(DUAL_TERMINAL_CONSTANTS) $(DUAL_TERMINAL_GATE) \
	$(Q24_COMPACT_INC) $(Q24_COMPACT_JSON) \
	$(Q24_LAZY_SCHEDULE_INC) $(Q24_LAZY_SCHEDULE_JSON) \
	$(Q24_ENCAP_HR_INC) $(Q24_ENCAP_HR_JSON) \
	$(Q24_PACK3_COMPACT_ARTIFACTS)
SOURCES := src/tile4_ref.c src/tile4_frontend.c src/tile4_basemul.c \
	src/tile4_pack.c src/tile4_inverse_tail.c \
	src/tile4_frombytes_asm.S src/tile4_inverse_tail_asm.S src/tile4_asm.S \
	src/tile4_basemul_asm.S src/tile4_inverse_private_asm.S \
	src/tile4_encodeq_bridge_asm.S \
	tests/test_tile4.c

.PHONY: all generate rep-family-generate pair02-exact-dag-tile-generate \
	forward-official-landing-generate polymul-joint-rescore-generate \
	gt64-d2-static-generate keygen-bm-elimination-generate \
	n32first-split-twist-generate \
	n32-mr-s3local-generate \
	n32-gt-pfa-native-generate \
	n32-gt-pfa-joint-generate \
	n32-gt-final-generate \
	n32-gt-bm-island-generate n32-gt-bm-island-check \
	bench-n32-gt-bm-island-short n32-physical-schedule-generate \
	n32-physical-schedule-check bench-n32-physical-schedule-short \
	n32-stage-native-tile-generate n32-native-inverse-generate \
	gt32-global-physical-layout-generate gt32-global-physical-asm-generate \
	gt32-global-physical-asm-check bench-gt32-global-physical-short \
	bench-gt32-global-physical-serious \
	bench-gt32-global-physical-official-short \
	bench-gt32-global-physical-official-serious \
	n32-idft3-l2-fused-generate n32-inverse-insertion-generate \
	n32-bm-inv-joint-range-generate n32-inverse-asm-generate \
	n32-inverse-asm-check bench-n32-inverse-asm-short \
	n32-forward-asm-generate n32-forward-asm-check \
	bench-n32-forward-chain-short n32-suffix-reschedule-generate \
	n32-branchlocal-raw160-generate \
	n32-branchlocal-scale-placement-generate \
	n32-suffix-reschedule-check bench-n32-suffix-reschedule-short \
	n32-branch1-qresident-check bench-n32-branch1-qresident-short \
	n32-row0-fixed-bias-generate \
	n32-suffix-mlkstyle-generate \
	n32-branch-at-time-check bench-n32-branch-at-time-short \
	bench-n32-branch-at-time-forward-short \
	poly-abi-v2 check test sanitize audit bench-short bench-official-short \
	bench-official-cold bench-inverse-short bench-consumer-short \
	bench-basemul-short bench-promotion promotion-serious \
	promotion-serious-reversed promotion-pmu promotion-symbols \
	bench-mixed-frombytes-short bench-basemul-attribution \
	bench-correct-semantic-decoder-short \
	bench-forward-bm-redeposit bench-private-caller private-caller-serious \
	bench-s5-schedule bench-terminal-layout bench-terminal-transpose-cut \
	bench-s45-wavefront-pmu \
	transpose-redeposit-generate bench-transpose-redeposit-short \
	aos-dot-redc16-generate bench-aos-dot-redc16-short \
	aos-dot-redc16-serious bench-aos-dot-official-cycles \
	bench-aos-dot-callsite-short aos-dot-forward-native-serious \
	encap-mixed-aos-soa-static keygen-fj1-p0-static \
	bench-keygen-fj1-p0-short r1u-packet-pack-static \
	bench-bm-soa-dot-redc16-short clean

.PHONY: n5-pm-progressive-suffix-generate n5-pm-progressive-suffix-check \
	bench-n5-pm-progressive-suffix-pmu

.PHONY: n5-scale-edge-survey-generate scale-consumer-fusion-generate
.PHONY: encap-representation-architecture-generate
.PHONY: forward-redesign-generate
.PHONY: encap-range-wavefront-generate encap-range-wavefront-check

encap-range-wavefront-generate:
	$(PYTHON) tools/generate_encap_range_wavefront.py
	$(PYTHON) tools/generate_encap_wavefront.py

# Non-overwriting campaign; override RESULT_TAG to repeat a validation run.
encap-range-wavefront-check:
	$(PYTHON) tools/run_encap_wavefront.py --tag "$(if $(RESULT_TAG),$(RESULT_TAG),encap-range-wavefront-check)"

forward-redesign-generate:
	$(PYTHON) tools/generate_forward_redesign_gate.py

encap-representation-architecture-generate: $(ENCAP_REP_ARCH_GATE)

$(ENCAP_REP_ARCH_GATE): \
	tools/generate_encap_representation_architecture_gate.py \
	tools/generate_p_prime_joint_abi_survey.py \
	tools/generate_gt32_global_physical_layout_gate.py \
	generated/tile4_serialized_mapping.json
	$(PYTHON) tools/generate_encap_representation_architecture_gate.py

.PHONY: spcrt-b3-exec-generate spcrt-b3-exec-check \
	bench-spcrt-b3-exec-short

.PHONY: encap-rhat-pack-static encap-rhat-range-probe keygen-j1-check \
	keygen-j1-typed-static bench-keygen-j1-k3b-pmu \
	keygen-soa-island-check bench-keygen-soa-island-pmu \
	baseinv-official-compat-generate bench-keygen-baseinv-official-reuse-pmu

.PHONY: bench-inv-radix4-short bench-forward-identity-lazy-short \
	bench-q24-codec-short bench-q24-prefix-short bench-q24-decap-short \
	bench-q24-decap-pmu bench-q24-decap-align64-short \
	bench-q24-placement-sweep bench-q24-compact-codec-short \
	bench-q24-compact-decap-short q24-compact-check \
	bench-q24-pattern-codec-short bench-q24-pattern-decap-short \
	bench-q24-pattern-cage-short bench-q24-unrolled-matched-cage-short \
	bench-q24-environment-attribution bench-q24-launch-pmu \
	q24-launch-attribution-summary q24-pattern-check \
	bench-q24-production-official-short bench-q24-production-official-pmu \
	bench-gt32-global-inverse-decap-short \
	bench-q24-lazy-production-official-short \
	bench-q24-lazy-production-official-pmu \
	bench-decap-cumulative-attribution

.PHONY: priority1-i112-check priority2-n5-half-check \
	bench-priority12-short priority3-bm-s0-typed-generate

.PHONY: dual-terminal-generate dual-terminal-check bench-dual-terminal-short \
	crep-sidecar-check bench-crep-sidecar-short \
	bench-crep-sidecar-decap-short q24-pack-verify-check \
	bench-q24-pack-verify-short q24-b3-frontier-generate \
	q24-b3-frontier-check bench-q24-b3-frontier-short

.PHONY: bench-q24-recovered-r-gtpack-short \
	bench-q24-recovered-r-gtpack-pmu

.PHONY: q24-lazy10788-static q24-lazy10788-check \
	bench-q24-lazy10788-gtpack-short bench-q24-lazy10788-gtpack-pmu \
	q24-lazy-schedules-generate bench-q24-lazy-schedules-short \
	q24-tf1-m-check bench-q24-tf1-m-short \
	bench-q24-hotcompact-c1-short \
	bench-encap-same-elf-residual bench-encap-same-elf-residual-pmu \
	bench-encap-poly-island

.PHONY: encap-candidate-check bench-keygen-encap-attribution-short \
	bench-keygen-encap-attribution-pmu q24-encap-highrange-generate

.PHONY: bench-encap-load-attribution-pmu bench-encap-load-stall-pmu \
	bench-encap-bm-add-fused-pmu bench-encap-q24-rr-pmu

.PHONY: kem-candidate-check bench-kem-decap-candidate-short \
	bench-decap-attribution-short

all: test

generate:
	$(PYTHON) tools/generate_tile4.py
	$(PYTHON) tools/generate_rep_family_gate.py
	$(PYTHON) tools/generate_q24_pack3_compact.py

$(Q24_PACK3_COMPACT_ARTIFACTS): tools/generate_q24_pack3_compact.py \
		generated/tile4_q24_p_encode_gate.json
	$(PYTHON) tools/generate_q24_pack3_compact.py

rep-family-generate: $(REP_FAMILY_GATE)

$(REP_FAMILY_GATE): tools/generate_rep_family_gate.py \
		generated/tile4_pair_native_bm_gate.json \
		generated/tile4_terminal_layout_family_gate.json
	$(PYTHON) tools/generate_rep_family_gate.py

baseinv-official-compat-generate: $(BASEINV_OFFICIAL_COMPAT_GATE)

$(BASEINV_OFFICIAL_COMPAT_GATE): tools/generate_baseinv_official_compat.py \
		generated/tile4_baseinv_p_mapping.h
	$(PYTHON) tools/generate_baseinv_official_compat.py

pair02-exact-dag-tile-generate: $(PAIR02_EXACT_DAG_TILE_GATE)

$(PAIR02_EXACT_DAG_TILE_GATE): tools/generate_pair02_exact_dag_tile_gate.py \
		generated/tile4_rep_family_gate.json \
		generated/tile4_baseinv_official_compat_gate.json
	$(PYTHON) tools/generate_pair02_exact_dag_tile_gate.py

forward-official-landing-generate: $(FWD_OFFICIAL_LANDING_GATE)

$(FWD_OFFICIAL_LANDING_GATE): tools/generate_forward_official_landing.py \
		generated/tile4_mapping.csv generated/tile4_constants.inc
	$(PYTHON) tools/generate_forward_official_landing.py

polymul-joint-rescore-generate: $(POLYMUL_JOINT_RESCORE_GATE)

$(POLYMUL_JOINT_RESCORE_GATE): tools/generate_polymul_joint_rescore.py \
		generated/poly_abi_v2_candidates.json \
		results/tile4-polymul-scope-official-cycles-20260811.json
	$(PYTHON) tools/generate_polymul_joint_rescore.py

priority1-i112-check: $(BUILD)/test_i112
	$(BUILD)/test_i112

$(BUILD)/test_i112: tests/test_i112.c src/tile4_i112_asm.S \
		src/tile4_basemul_asm.S src/tile4_inverse_private_asm.S src/tile4_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_i112.c \
		src/tile4_i112_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S src/tile4_asm.S

priority2-n5-half-check: $(BUILD)/test_n5_half_route
	$(BUILD)/test_n5_half_route

$(BUILD)/test_n5_half_route: tests/test_n5_half_route.c \
		src/tile4_n5_half_route_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n5_half_route.c \
		src/tile4_n5_half_route_asm.S

$(BUILD)/bench_i112: bench/bench_i112.c src/tile4_i112_asm.S \
		src/tile4_basemul_asm.S src/tile4_inverse_private_asm.S src/tile4_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_i112.c \
		src/tile4_basemul_asm.S src/tile4_inverse_private_asm.S \
		src/tile4_i112_asm.S src/tile4_asm.S

$(BUILD)/bench_i112_reversed: bench/bench_i112.c src/tile4_i112_asm.S \
		src/tile4_basemul_asm.S src/tile4_inverse_private_asm.S src/tile4_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/tile4_asm.S src/tile4_i112_asm.S \
		src/tile4_inverse_private_asm.S src/tile4_basemul_asm.S bench/bench_i112.c

$(BUILD)/bench_n5_half_chain: bench/bench_n5_half_chain.c \
		src/tile4_n5_half_route_asm.S src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/n32_bm_island_asm.S src/n32_inverse_asm.S \
		src/n32_current_idft3_attribution_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n5_half_chain.c \
		src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/tile4_n5_half_route_asm.S src/n32_bm_island_asm.S src/n32_inverse_asm.S \
		src/n32_current_idft3_attribution_asm.S

$(BUILD)/bench_n5_half_chain_reversed: bench/bench_n5_half_chain.c \
		src/tile4_n5_half_route_asm.S src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/n32_bm_island_asm.S src/n32_inverse_asm.S \
		src/n32_current_idft3_attribution_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_current_idft3_attribution_asm.S \
		src/n32_inverse_asm.S src/n32_bm_island_asm.S src/tile4_n5_half_route_asm.S \
		src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S bench/bench_n5_half_chain.c

bench-priority12-short: $(PRIORITY12_RESULTS)

$(PRIORITY12_RESULTS): priority1-i112-check priority2-n5-half-check \
		$(BUILD)/bench_i112 $(BUILD)/bench_i112_reversed \
		$(BUILD)/bench_n5_half_chain $(BUILD)/bench_n5_half_chain_reversed \
		tools/run_priority12_gates.py
	$(PYTHON) tools/run_priority12_gates.py

priority3-bm-s0-typed-generate: $(BM_S0_TYPED_GATE)

$(BM_S0_TYPED_GATE): $(PRIORITY12_RESULTS) \
		generated/tile4_a2f_dag.json tools/generate_bm_s0_typed_gate.py
	$(PYTHON) tools/generate_bm_s0_typed_gate.py

gt64-d2-static-generate: $(GT64_D2_STATIC_GATE)

$(GT64_D2_STATIC_GATE): tools/generate_gt64_d2_static_gate.py
	$(PYTHON) tools/generate_gt64_d2_static_gate.py

keygen-bm-elimination-generate: $(KEYGEN_BM_ELIMINATION_GATE)

$(KEYGEN_BM_ELIMINATION_GATE): tools/generate_keygen_bm_elimination_gate.py
	$(PYTHON) tools/generate_keygen_bm_elimination_gate.py

n32first-split-twist-generate: $(N32FIRST_SPLIT_TWIST_GATE)

$(N32FIRST_SPLIT_TWIST_GATE): tools/generate_n32first_gate.py \
		tools/generate_tile4.py
	$(PYTHON) tools/generate_n32first_gate.py

n32-mr-s3local-generate: $(N32_MR_S3LOCAL_GATE)

$(N32_MR_S3LOCAL_GATE): tools/generate_n32_mr_s3local_gate.py \
		tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_mr_s3local_gate.py

n32-gt-pfa-native-generate: $(N32_GT_PFA_NATIVE_GATE)

$(N32_GT_PFA_NATIVE_GATE): tools/generate_n32_gt_pfa_native_gate.py \
		tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_gt_pfa_native_gate.py

n32-gt-pfa-joint-generate: $(N32_GT_PFA_JOINT_GATE)

$(N32_GT_PFA_JOINT_GATE): tools/generate_n32_gt_pfa_joint_gate.py tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_gt_pfa_joint_gate.py

n32-gt-final-generate: $(N32_GT_FINAL_GATES)

$(N32_GT_FINAL_GATES): tools/generate_n32_gt_final_gate.py \
		$(N32_GT_PFA_JOINT_GATE) tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_gt_final_gate.py

n32-gt-bm-island-generate: $(N32_GT_BM_ISLAND_ARTIFACTS)

$(N32_GT_BM_ISLAND_ARTIFACTS): tools/generate_n32_gt_bm_island_gate.py \
		$(N32_GT_FINAL_GATES) $(N32_GT_PFA_NATIVE_GATE) \
		generated/tile4_aos_dot_redc16_gate.json \
		results/tile4-aos-dot-redc16-forward-native-serious.json
	$(PYTHON) tools/generate_n32_gt_bm_island_gate.py

n32-gt-bm-island-check: $(BUILD)/test_n32_bm_island
	$(BUILD)/test_n32_bm_island

$(BUILD)/test_n32_bm_island: tests/test_n32_bm_island.c \
		src/n32_bm_island_asm.S src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S \
		$(N32_GT_BM_ISLAND_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_bm_island.c \
		src/n32_bm_island_asm.S src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S

bench-n32-gt-bm-island-short: $(BUILD)/bench_n32_bm_island \
		$(BUILD)/bench_n32_bm_island_reversed n32-gt-bm-island-check
	$(PYTHON) tools/run_n32_bm_island.py $(BUILD)/bench_n32_bm_island \
		--reversed-binary $(BUILD)/bench_n32_bm_island_reversed \
		--iterations 5000 --output results/tile4-n32-bm-island-short.json

$(BUILD)/bench_n32_bm_island: bench/bench_n32_bm_island.c \
		src/n32_bm_island_asm.S src/tile4_aos_dot_redc16_asm.S \
		$(N32_GT_BM_ISLAND_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_bm_island.c \
		src/n32_bm_island_asm.S src/tile4_aos_dot_redc16_asm.S

$(BUILD)/bench_n32_bm_island_reversed: bench/bench_n32_bm_island.c \
		src/n32_bm_island_asm.S src/tile4_aos_dot_redc16_asm.S \
		$(N32_GT_BM_ISLAND_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/tile4_aos_dot_redc16_asm.S \
		src/n32_bm_island_asm.S bench/bench_n32_bm_island.c

n32-physical-schedule-generate: $(N32_PHYSICAL_SCHEDULE_GATE)

$(N32_PHYSICAL_SCHEDULE_GATE): tools/generate_n32_physical_schedule_gate.py \
		$(N32_GT_PFA_NATIVE_GATE) $(N32_GT_FINAL_GATES) tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_physical_schedule_gate.py

n32-physical-schedule-check: $(BUILD)/test_n32_wave_schedule
	$(BUILD)/test_n32_wave_schedule

$(BUILD)/test_n32_wave_schedule: tests/test_n32_wave_schedule.c \
		src/n32_wave_schedule_asm.S $(N32_PHYSICAL_SCHEDULE_GATE) \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_wave_schedule.c \
		src/n32_wave_schedule_asm.S

bench-n32-physical-schedule-short: $(BUILD)/bench_n32_wave_schedule \
		$(BUILD)/bench_n32_wave_schedule_reversed n32-physical-schedule-check
	$(PYTHON) tools/run_n32_wave_schedule.py $(BUILD)/bench_n32_wave_schedule \
		--reversed-binary $(BUILD)/bench_n32_wave_schedule_reversed \
		--iterations 5000 --output results/tile4-n32-wave-schedule-short.json

$(BUILD)/bench_n32_wave_schedule: bench/bench_n32_wave_schedule.c \
		src/n32_wave_schedule_asm.S $(N32_PHYSICAL_SCHEDULE_GATE) \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_wave_schedule.c \
		src/n32_wave_schedule_asm.S

$(BUILD)/bench_n32_wave_schedule_reversed: bench/bench_n32_wave_schedule.c \
		src/n32_wave_schedule_asm.S $(N32_PHYSICAL_SCHEDULE_GATE) \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_wave_schedule_asm.S \
		bench/bench_n32_wave_schedule.c

n32-stage-native-tile-generate: $(N32_STAGE_NATIVE_TILE_GATE)

$(N32_STAGE_NATIVE_TILE_GATE): tools/generate_n32_stage_native_tile_gate.py \
		results/tile4-n32-wave-schedule-short.json tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_stage_native_tile_gate.py

gt32-global-physical-layout-generate: $(GT32_GLOBAL_PHYSICAL_LAYOUT_GATE)

$(GT32_GLOBAL_PHYSICAL_LAYOUT_GATE): \
		tools/generate_gt32_global_physical_layout_gate.py \
		tools/generate_poly_abi_v2.py tools/generate_tile4.py \
		generated/tile4_range_metadata.json \
		generated/tile4_n32_bm_inv_joint_range_gate.json
	$(PYTHON) tools/generate_gt32_global_physical_layout_gate.py

n5-pm-progressive-suffix-generate: $(N5_PM_PROGRESSIVE_SUFFIX_GATE)

$(N5_PM_PROGRESSIVE_SUFFIX_GATE): \
		tools/generate_n5_pm_progressive_suffix_survey.py \
		tools/generate_gt32_global_physical_layout_gate.py \
		$(GT32_GLOBAL_PHYSICAL_LAYOUT_GATE)
	$(PYTHON) tools/generate_n5_pm_progressive_suffix_survey.py

n5-m-frontend-seam-generate: $(N5_M_FRONTEND_SEAM_GATE)

$(N5_M_FRONTEND_SEAM_GATE): \
		tools/generate_n5_m_frontend_seam_gate.py \
		src/tile4_asm.S generated/tile4_frontend_wide.inc
	$(PYTHON) tools/generate_n5_m_frontend_seam_gate.py

n5-frontend-linear-circuit-generate: $(N5_FRONTEND_LINEAR_CIRCUIT_GATE)

$(N5_FRONTEND_LINEAR_CIRCUIT_GATE): \
		tools/generate_n5_frontend_linear_circuit_gate.py \
		tools/generate_tile4.py src/tile4_asm.S
	$(PYTHON) tools/generate_n5_frontend_linear_circuit_gate.py

n5-scale-edge-survey-generate: $(N5_SCALE_EDGE_SURVEY)

$(N5_SCALE_EDGE_SURVEY): tools/generate_n5_scale_edge_survey.py \
		tools/generate_tile4.py generated/tile4_scale_contract.json
	$(PYTHON) tools/generate_n5_scale_edge_survey.py

scale-consumer-fusion-generate: $(SCALE_CONSUMER_FUSION_GATE)

$(SCALE_CONSUMER_FUSION_GATE): \
		tools/generate_scale_consumer_fusion_gate.py tools/generate_tile4.py \
		$(N5_SCALE_EDGE_SURVEY) generated/tile4_e1_producer_gate.json \
		generated/tile4_q24_lazy10788_gate.json \
		generated/tile4_q24_encap_highrange_gate.json
	$(PYTHON) tools/generate_scale_consumer_fusion_gate.py

gt32-global-physical-asm-generate: $(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS)

$(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS): \
		tools/generate_gt32_global_physical_asm.py \
		$(GT32_GLOBAL_PHYSICAL_LAYOUT_GATE) $(N5_PM_PROGRESSIVE_SUFFIX_GATE) \
		tools/generate_tile4.py
	$(PYTHON) tools/generate_gt32_global_physical_asm.py

$(BUILD)/test_global_physical: tests/test_global_physical.c \
		src/tile4_global_physical_asm.S src/tile4_asm.S \
		src/tile4_inverse_private_asm.S src/tile4_basemul_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) generated/tile4_constants.inc \
		generated/tile4_private_inverse_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_global_physical.c \
		src/tile4_global_physical_asm.S src/tile4_asm.S \
		src/tile4_inverse_private_asm.S src/tile4_basemul_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S

gt32-global-physical-asm-check: $(BUILD)/test_global_physical
	$(BUILD)/test_global_physical

GLOBAL_PHYSICAL_BENCH_SOURCES := src/tile4_global_physical_asm.S \
	src/tile4_global_physical.c \
	src/tile4_asm.S src/tile4_inverse_private_asm.S \
	src/tile4_basemul_asm.S src/tile4_forward_bm_soa_attribution_asm.S

$(BUILD)/bench_global_physical: bench/bench_global_physical.c \
		src/tile4_global_physical.h \
		$(GLOBAL_PHYSICAL_BENCH_SOURCES) $(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) \
		generated/tile4_constants.inc generated/tile4_basemul_constants.inc \
		generated/tile4_private_inverse_constants.inc \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(GLOBAL_PHYSICAL_BENCH_SOURCES) \
		bench/bench_global_physical.c $(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_global_physical_reversed: bench/bench_global_physical.c \
		src/tile4_global_physical.h \
		$(GLOBAL_PHYSICAL_BENCH_SOURCES) $(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) \
		generated/tile4_constants.inc generated/tile4_basemul_constants.inc \
		generated/tile4_private_inverse_constants.inc \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_global_physical.c \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S \
		src/tile4_asm.S \
		src/tile4_global_physical_asm.S src/tile4_global_physical.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

bench-gt32-global-physical-short: gt32-global-physical-asm-check \
		$(BUILD)/bench_global_physical \
		$(BUILD)/bench_global_physical_reversed
	$(PYTHON) tools/run_global_physical.py $(BUILD)/bench_global_physical \
		--reversed-binary $(BUILD)/bench_global_physical_reversed \
		--iterations 5000 --launches 4 \
		--output results/tile4-global-physical-whole-short.json

bench-gt32-global-physical-serious: gt32-global-physical-asm-check \
		$(BUILD)/bench_global_physical \
		$(BUILD)/bench_global_physical_reversed
	$(PYTHON) tools/run_global_physical.py $(BUILD)/bench_global_physical \
		--reversed-binary $(BUILD)/bench_global_physical_reversed \
		--iterations 100000 --launches 4 \
		--output results/tile4-global-physical-whole-serious.json

GLOBAL_PHYSICAL_OFFICIAL_SOURCES := $(OFFICIAL)/asm/basemul.s \
	$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
	$(OFFICIAL)/consts.c

$(BUILD)/bench_global_physical_official: bench/bench_global_physical.c \
		src/tile4_global_physical.h \
		$(GLOBAL_PHYSICAL_BENCH_SOURCES) $(GLOBAL_PHYSICAL_OFFICIAL_SOURCES) \
		$(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -DGLOBAL_COMPARE_OFFICIAL=1 -Werror -Isrc \
		-I$(OFFICIAL) -o $@ $(GLOBAL_PHYSICAL_BENCH_SOURCES) \
		bench/bench_global_physical.c $(BUILD)/tile4_inverse_tail_isolated.o \
		$(GLOBAL_PHYSICAL_OFFICIAL_SOURCES)

$(BUILD)/bench_global_physical_official_reversed: \
		bench/bench_global_physical.c src/tile4_global_physical.h \
		$(GLOBAL_PHYSICAL_BENCH_SOURCES) \
		$(GLOBAL_PHYSICAL_OFFICIAL_SOURCES) \
		$(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -DGLOBAL_COMPARE_OFFICIAL=1 -Werror -Isrc \
		-I$(OFFICIAL) -o $@ $(GLOBAL_PHYSICAL_OFFICIAL_SOURCES) \
		bench/bench_global_physical.c \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S src/tile4_asm.S \
		src/tile4_global_physical_asm.S src/tile4_global_physical.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

bench-gt32-global-physical-official-short: gt32-global-physical-asm-check \
		$(BUILD)/bench_global_physical_official \
		$(BUILD)/bench_global_physical_official_reversed
	$(PYTHON) tools/run_global_physical.py \
		$(BUILD)/bench_global_physical_official \
		--reversed-binary $(BUILD)/bench_global_physical_official_reversed \
		--comparison official-main --iterations 5000 --launches 4 \
		--output results/tile4-global-physical-vs-official-short.json

bench-gt32-global-physical-official-serious: \
		gt32-global-physical-asm-check \
		$(BUILD)/bench_global_physical_official \
		$(BUILD)/bench_global_physical_official_reversed
	$(PYTHON) tools/run_global_physical.py \
		$(BUILD)/bench_global_physical_official \
		--reversed-binary $(BUILD)/bench_global_physical_official_reversed \
		--comparison official-main --iterations 100000 --launches 4 \
		--output results/tile4-global-physical-vs-official-serious.json

n32-native-inverse-generate: $(N32_NATIVE_INVERSE_GATE)

$(N32_NATIVE_INVERSE_GATE): tools/generate_n32_native_inverse_gate.py \
		generated/tile4_aos_dot_redc16_gate.json \
		generated/tile4_n32_gt_bm_island_gate.json \
		results/tile4-n32-wave-schedule-short.json tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_native_inverse_gate.py

n32-idft3-l2-fused-generate: $(N32_IDFT3_L2_GATES)

$(N32_IDFT3_L2_GATES): tools/generate_n32_idft3_l2_fused_gate.py \
		tools/generate_n32_native_inverse_gate.py \
		generated/tile4_aos_dot_redc16_gate.json \
		generated/tile4_n32_native_inverse_gate.json tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_idft3_l2_fused_gate.py

n32-inverse-insertion-generate: $(N32_INVERSE_INSERTION_GATE)

$(N32_INVERSE_INSERTION_GATE): tools/generate_n32_inverse_insertion_gate.py \
		tools/generate_n32_idft3_l2_fused_gate.py \
		tools/generate_n32_native_inverse_gate.py \
		generated/tile4_aos_dot_redc16_gate.json \
		results/tile4-n32-wave-schedule-short.json tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_inverse_insertion_gate.py

n32-bm-inv-joint-range-generate: $(N32_BM_INV_JOINT_GATE)

$(BUILD)/n32_bm_inv_joint_range_search: \
		tools/n32_bm_inv_joint_range_search.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -o $@ $<

$(N32_BM_INV_JOINT_SEARCH): $(BUILD)/n32_bm_inv_joint_range_search
	$< 100000 12 20000 $@

$(N32_BM_INV_JOINT_GATE): \
		tools/generate_n32_bm_inv_joint_range_gate.py \
		tools/generate_aos_dot_redc16.py \
		tools/generate_n32_idft3_l2_fused_gate.py \
		tools/generate_n32_inverse_insertion_gate.py \
		generated/tile4_n32first_split_twist_gate.json \
		generated/tile4_n32_native_inverse_gate.json \
		$(N32_BM_INV_JOINT_SEARCH) tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_bm_inv_joint_range_gate.py

n32-inverse-asm-generate: $(N32_INVERSE_ASM_ARTIFACTS)

$(N32_INVERSE_ASM_ARTIFACTS): tools/generate_n32_inverse_asm.py \
		$(N32_BM_INV_JOINT_GATE) tools/generate_tile4.py \
		tools/generate_n32_native_inverse_gate.py
	$(PYTHON) tools/generate_n32_inverse_asm.py

n32-inverse-asm-check: $(BUILD)/test_n32_inverse_asm
	$(BUILD)/test_n32_inverse_asm

$(BUILD)/test_n32_inverse_asm: tests/test_n32_inverse_asm.c \
		src/n32_inverse_asm.S $(N32_INVERSE_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_inverse_asm.c \
		src/n32_inverse_asm.S

bench-n32-inverse-asm-short: n32-inverse-asm-check \
		$(BUILD)/bench_n32_inverse_asm \
		$(BUILD)/bench_n32_inverse_asm_reversed
	$(PYTHON) tools/run_n32_inverse_asm.py $(BUILD)/bench_n32_inverse_asm \
		--reversed-binary $(BUILD)/bench_n32_inverse_asm_reversed \
		--iterations 5000 --output results/tile4-n32-inverse-asm-short.json

$(BUILD)/bench_n32_inverse_asm: bench/bench_n32_inverse_asm.c \
		src/n32_inverse_asm.S $(N32_INVERSE_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_inverse_asm.c \
		src/n32_inverse_asm.S

$(BUILD)/bench_n32_inverse_asm_reversed: bench/bench_n32_inverse_asm.c \
		src/n32_inverse_asm.S $(N32_INVERSE_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_inverse_asm.S \
		bench/bench_n32_inverse_asm.c

n32-forward-asm-generate: $(N32_FORWARD_ASM_ARTIFACTS)

$(N32_FORWARD_ASM_ARTIFACTS): tools/generate_n32_forward_asm.py \
		$(N32_BM_INV_JOINT_GATE) $(N32_GT_PFA_JOINT_GATE) \
		tools/generate_tile4.py
	$(PYTHON) tools/generate_n32_forward_asm.py

n32-forward-asm-check: $(BUILD)/test_n32_forward_asm
	$(BUILD)/test_n32_forward_asm

$(BUILD)/test_n32_forward_asm: tests/test_n32_forward_asm.c \
		src/n32_forward_asm.S src/tile4_asm.S \
		$(N32_FORWARD_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_forward_asm.c \
		src/n32_forward_asm.S src/tile4_asm.S

bench-n32-forward-chain-short: n32-forward-asm-check \
		$(BUILD)/bench_n32_forward_chain \
		$(BUILD)/bench_n32_forward_chain_reversed
	$(PYTHON) tools/run_n32_forward_chain.py $(BUILD)/bench_n32_forward_chain \
		--reversed-binary $(BUILD)/bench_n32_forward_chain_reversed \
		--iterations 5000 --output results/tile4-n32-forward-chain-short.json

$(BUILD)/bench_n32_forward_chain: bench/bench_n32_forward_chain.c \
		src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/n32_forward_asm.S src/n32_bm_island_asm.S src/n32_inverse_asm.S \
		src/n32_current_idft3_attribution_asm.S \
		$(N32_FORWARD_ASM_ARTIFACTS) $(N32_GT_BM_ISLAND_ARTIFACTS) \
		$(N32_INVERSE_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_forward_chain.c \
		src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/n32_forward_asm.S src/n32_bm_island_asm.S src/n32_inverse_asm.S \
		src/n32_current_idft3_attribution_asm.S

$(BUILD)/bench_n32_forward_chain_reversed: bench/bench_n32_forward_chain.c \
		src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/n32_forward_asm.S src/n32_bm_island_asm.S src/n32_inverse_asm.S \
		src/n32_current_idft3_attribution_asm.S \
		$(N32_FORWARD_ASM_ARTIFACTS) $(N32_GT_BM_ISLAND_ARTIFACTS) \
		$(N32_INVERSE_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_current_idft3_attribution_asm.S \
		src/n32_inverse_asm.S src/n32_bm_island_asm.S src/n32_forward_asm.S \
		src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S \
		bench/bench_n32_forward_chain.c

n32-suffix-reschedule-generate: $(N32_SUFFIX_RESCHEDULE_GATE)

n32-branchlocal-raw160-generate: $(N32_BRANCHLOCAL_RAW160_GATE)

$(N32_BRANCHLOCAL_RAW160_GATE): tools/generate_n32_branchlocal_raw160_gate.py \
		generated/tile4_n32_forward_asm_gate.json \
		generated/tile4_n32_gt_pfa_joint_gate.json
	$(PYTHON) tools/generate_n32_branchlocal_raw160_gate.py

n32-branchlocal-scale-placement-generate: $(N32_BRANCHLOCAL_SCALE_GATE)

$(N32_BRANCHLOCAL_SCALE_GATE): \
		tools/generate_n32_branchlocal_scale_placement_gate.py \
		$(N32_BRANCHLOCAL_RAW160_GATE)
	$(PYTHON) tools/generate_n32_branchlocal_scale_placement_gate.py

$(N32_SUFFIX_RESCHEDULE_GATE): tools/generate_n32_suffix_reschedule_gate.py
	$(PYTHON) tools/generate_n32_suffix_reschedule_gate.py

n32-suffix-reschedule-check: $(BUILD)/test_n32_suffix_schedule
	$(BUILD)/test_n32_suffix_schedule

$(BUILD)/test_n32_suffix_schedule: tests/test_n32_suffix_schedule.c \
		src/n32_forward_asm.S $(N32_FORWARD_ASM_ARTIFACTS) \
		$(N32_SUFFIX_RESCHEDULE_GATE) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_suffix_schedule.c \
		src/n32_forward_asm.S

bench-n32-suffix-reschedule-short: n32-suffix-reschedule-check \
		$(BUILD)/bench_n32_suffix_schedule \
		$(BUILD)/bench_n32_suffix_schedule_reversed
	$(PYTHON) tools/run_n32_suffix_schedule.py $(BUILD)/bench_n32_suffix_schedule \
		--reversed-binary $(BUILD)/bench_n32_suffix_schedule_reversed \
		--iterations 5000 --output results/tile4-n32-suffix-reschedule-short.json

$(BUILD)/bench_n32_suffix_schedule: bench/bench_n32_suffix_schedule.c \
		src/n32_forward_asm.S $(N32_FORWARD_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_suffix_schedule.c \
		src/n32_forward_asm.S

$(BUILD)/bench_n32_suffix_schedule_reversed: bench/bench_n32_suffix_schedule.c \
		src/n32_forward_asm.S $(N32_FORWARD_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_forward_asm.S \
		bench/bench_n32_suffix_schedule.c

n32-branch1-qresident-check: $(BUILD)/test_n32_branch1_qresident
	$(BUILD)/test_n32_branch1_qresident

$(BUILD)/test_n32_branch1_qresident: tests/test_n32_branch1_qresident.c \
		src/n32_wave_schedule_asm.S generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_branch1_qresident.c \
		src/n32_wave_schedule_asm.S

bench-n32-branch1-qresident-short: n32-branch1-qresident-check \
		$(BUILD)/bench_n32_branch1_qresident \
		$(BUILD)/bench_n32_branch1_qresident_reversed
	$(PYTHON) tools/run_n32_branch1_qresident.py \
		$(BUILD)/bench_n32_branch1_qresident \
		--reversed-binary $(BUILD)/bench_n32_branch1_qresident_reversed \
		--iterations 10000 \
		--output results/tile4-n32-branch1-qresident-short.json

$(BUILD)/bench_n32_branch1_qresident: bench/bench_n32_branch1_qresident.c \
		src/n32_wave_schedule_asm.S generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_branch1_qresident.c \
		src/n32_wave_schedule_asm.S

$(BUILD)/bench_n32_branch1_qresident_reversed: \
		bench/bench_n32_branch1_qresident.c src/n32_wave_schedule_asm.S \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_wave_schedule_asm.S \
		bench/bench_n32_branch1_qresident.c

n32-row0-fixed-bias-generate: tools/generate_n32_row0_fixed_bias_gate.py
	$(PYTHON) tools/generate_n32_row0_fixed_bias_gate.py

n32-suffix-mlkstyle-generate: tools/generate_n32_suffix_mlkstyle_gate.py
	$(PYTHON) tools/generate_n32_suffix_mlkstyle_gate.py

n32-branch-at-time-check: $(BUILD)/test_n32_branch_at_time
	$(BUILD)/test_n32_branch_at_time

$(BUILD)/test_n32_branch_at_time: tests/test_n32_branch_at_time.c \
		src/n32_branch_at_time_asm.S generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_n32_branch_at_time.c \
		src/n32_branch_at_time_asm.S

bench-n32-branch-at-time-short: n32-branch-at-time-check \
		$(BUILD)/bench_n32_branch_at_time \
		$(BUILD)/bench_n32_branch_at_time_reversed
	$(PYTHON) tools/run_n32_branch_at_time.py $(BUILD)/bench_n32_branch_at_time \
		--reversed-binary $(BUILD)/bench_n32_branch_at_time_reversed \
		--iterations 10000 --output results/tile4-n32-branch-at-time-short.json

$(BUILD)/bench_n32_branch_at_time: bench/bench_n32_branch_at_time.c \
		src/n32_branch_at_time_asm.S generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_branch_at_time.c \
		src/n32_branch_at_time_asm.S

$(BUILD)/bench_n32_branch_at_time_reversed: bench/bench_n32_branch_at_time.c \
		src/n32_branch_at_time_asm.S generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_branch_at_time_asm.S \
		bench/bench_n32_branch_at_time.c

bench-n32-branch-at-time-forward-short: n32-forward-asm-check \
		$(BUILD)/bench_n32_branch_at_time_forward \
		$(BUILD)/bench_n32_branch_at_time_forward_reversed
	$(PYTHON) tools/run_n32_branch_at_time_forward.py \
		$(BUILD)/bench_n32_branch_at_time_forward \
		--reversed-binary $(BUILD)/bench_n32_branch_at_time_forward_reversed \
		--iterations 5000 \
		--output results/tile4-n32-branch-at-time-forward-short.json

$(BUILD)/bench_n32_branch_at_time_forward: bench/bench_n32_branch_at_time_forward.c \
		src/n32_forward_asm.S generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_n32_branch_at_time_forward.c \
		src/n32_forward_asm.S

$(BUILD)/bench_n32_branch_at_time_forward_reversed: \
		bench/bench_n32_branch_at_time_forward.c src/n32_forward_asm.S \
		generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/n32_forward_asm.S \
		bench/bench_n32_branch_at_time_forward.c

poly-abi-v2: generate
	$(PYTHON) tools/generate_poly_abi_v2.py

dual-terminal-generate: $(DUAL_TERMINAL_CONSTANTS) $(DUAL_TERMINAL_GATE)

$(DUAL_TERMINAL_CONSTANTS): tools/generate_dual_terminal.py \
		generated/tile4_constants.inc generated/tile4_inverse_tail_range.json
	$(PYTHON) tools/generate_dual_terminal.py

$(DUAL_TERMINAL_GATE): $(DUAL_TERMINAL_CONSTANTS)
	@test -f $@

dual-terminal-check: $(BUILD)/bench_dual_terminal
	$(BUILD)/bench_dual_terminal 1 >/dev/null

bench-dual-terminal-short: dual-terminal-check \
		$(BUILD)/bench_dual_terminal_reversed
	$(PYTHON) tools/run_dual_terminal.py $(BUILD)/bench_dual_terminal \
		--reversed-binary $(BUILD)/bench_dual_terminal_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-dual-terminal-short.json

crep-sidecar-check: $(BUILD)/bench_crep_sidecar
	$(BUILD)/bench_crep_sidecar 1 >/dev/null

bench-crep-sidecar-short: crep-sidecar-check \
		$(BUILD)/bench_crep_sidecar_reversed
	$(PYTHON) tools/run_crep_sidecar.py $(BUILD)/bench_crep_sidecar \
		--reversed-binary $(BUILD)/bench_crep_sidecar_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-crep-sidecar-short.json

bench-crep-sidecar-decap-short: kem-candidate-check \
		$(BUILD)/bench_q24_decap $(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_crep_sidecar_decap.py $(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-crep-sidecar-decap-short.json

q24-pack-verify-check: $(BUILD)/bench_q24_pack_verify
	$(BUILD)/bench_q24_pack_verify 1 >/dev/null

bench-q24-pack-verify-short: q24-pack-verify-check \
		$(BUILD)/bench_q24_pack_verify_reversed
	$(PYTHON) tools/run_q24_pack_verify.py $(BUILD)/bench_q24_pack_verify \
		--reversed-binary $(BUILD)/bench_q24_pack_verify_reversed \
		--iterations 2000 --launches 16 \
		--output results/tile4-q24-pack-verify-short.json

q24-b3-frontier-generate: generated/tile4_q24_codec.json \
		tools/generate_q24_b3_frontier.py
	$(PYTHON) tools/generate_q24_b3_frontier.py

q24-b3-frontier-check: q24-b3-frontier-generate \
		$(BUILD)/bench_q24_b3_frontier
	$(BUILD)/bench_q24_b3_frontier 1 >/dev/null

bench-q24-b3-frontier-short: q24-b3-frontier-check \
		$(BUILD)/bench_q24_b3_frontier_reversed
	$(PYTHON) tools/run_q24_b3_frontier.py $(BUILD)/bench_q24_b3_frontier \
		--reversed-binary $(BUILD)/bench_q24_b3_frontier_reversed \
		--iterations 2000 --launches 16 \
		--output results/tile4-q24-b3-frontier-short.json

$(Q24_COMPACT_INC): tools/generate_q24_compact.py \
		generated/tile4_q24_codec.json
	$(PYTHON) tools/generate_q24_compact.py \
		--metadata generated/tile4_q24_codec.json \
		--asm-output $(Q24_COMPACT_INC) \
		--json-output $(Q24_COMPACT_JSON)

$(Q24_COMPACT_JSON): $(Q24_COMPACT_INC)
	@test -f $@

keygen-fj1-p0-static: generate generated/tile4_keygen_fj1_p0_routes.inc
	$(PYTHON) tools/generate_keygen_fj1_p0_gate.py

generated/tile4_keygen_fj1_p0_routes.inc: \
		tools/generate_keygen_fj1_p0_gate.py \
		generated/tile4_serialized_mapping.json \
		generated/tile4_correct_semantic_encodeq_gate.json
	$(PYTHON) tools/generate_keygen_fj1_p0_gate.py

bench-keygen-fj1-p0-short: keygen-fj1-p0-static \
		$(BUILD)/bench_keygen_fj1_p0 \
		$(BUILD)/bench_keygen_fj1_p0_reversed
	$(PYTHON) tools/run_keygen_fj1_p0.py \
		$(BUILD)/bench_keygen_fj1_p0 \
		--reversed-binary $(BUILD)/bench_keygen_fj1_p0_reversed \
		--iterations 2000 \
		--output results/tile4-keygen-fj1-p0-asm-short.json

r1u-packet-pack-static: generate
	$(PYTHON) tools/generate_r1u_packet_pack_gate.py

bench-bm-soa-dot-redc16-short: generate \
		$(BUILD)/bench_bm_soa_dot_redc16 \
		$(BUILD)/bench_bm_soa_dot_redc16_reversed
	$(PYTHON) tools/run_bm_soa_dot_redc16.py \
		$(BUILD)/bench_bm_soa_dot_redc16 \
		--reversed-binary $(BUILD)/bench_bm_soa_dot_redc16_reversed \
		--iterations 2000 \
		--output results/tile4-bm-soa-dot-redc16-short.json

bench-inv-radix4-short: generate $(BUILD)/bench_inv_radix4 \
		$(BUILD)/bench_inv_radix4_reversed
	$(BUILD)/bench_inv_radix4 2000 > $(BUILD)/bench_inv_radix4.csv
	$(BUILD)/bench_inv_radix4_reversed 2000 > $(BUILD)/bench_inv_radix4_reversed.csv

bench-forward-identity-lazy-short: generate \
		$(BUILD)/bench_forward_identity_lazy \
		$(BUILD)/bench_forward_identity_lazy_reversed
	$(PYTHON) tools/run_forward_identity_lazy.py \
		$(BUILD)/bench_forward_identity_lazy \
		--reversed-binary $(BUILD)/bench_forward_identity_lazy_reversed \
		--iterations 2000 \
		--output results/tile4-forward-identity-lazy-short.json

bench-q24-codec-short: generate $(BUILD)/bench_q24_codec \
		$(BUILD)/bench_q24_codec_reversed
	$(PYTHON) tools/run_q24_codec.py $(BUILD)/bench_q24_codec \
		--reversed-binary $(BUILD)/bench_q24_codec_reversed \
		--iterations 2000 --output results/tile4-q24-codec-short.json

decode-debt-generate: generated/tile4_decode_debt.inc \
		generated/tile4_decode_debt_static.json

generated/tile4_decode_debt.inc generated/tile4_decode_debt_static.json: \
		tools/generate_decode_debt_gate.py generated/tile4_q24_codec.json
	$(PYTHON) tools/generate_decode_debt_gate.py

encap-h-d01-mixed-tmvp-static: \
		generated/tile4_encap_h_d01_mixed_tmvp_gate.json

generated/tile4_encap_h_d01_mixed_tmvp_gate.json: \
		tools/generate_encap_h_d01_mixed_tmvp_gate.py \
		generated/tile4_q24_codec.json \
		generated/tile4_pair02_exact_dag_tile_gate.json
	$(PYTHON) tools/generate_encap_h_d01_mixed_tmvp_gate.py

bench-decode-debt: decode-debt-generate $(BUILD)/bench_decode_debt \
		$(BUILD)/bench_decode_debt_reversed
	$(PYTHON) tools/run_decode_debt_gate.py $(BUILD)/bench_decode_debt \
		$(BUILD)/bench_decode_debt_reversed --iterations 4000 --launches 4 \
		--output results/tile4-decode-debt-gate.json

bench-q24-prefix-short: generate $(BUILD)/bench_q24_prefix \
		$(BUILD)/bench_q24_prefix_reversed
	$(PYTHON) tools/run_q24_prefix.py $(BUILD)/bench_q24_prefix \
		--reversed-binary $(BUILD)/bench_q24_prefix_reversed \
		--iterations 2000 --output results/tile4-q24-prefix-short.json

bench-q24-decap-short: generate kem-candidate-check \
		$(BUILD)/bench_q24_decap $(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_q24_decap.py $(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --launches 2 \
		--output results/tile4-q24-decap-short.json

bench-q24-production-official-short: \
		bench-q24-lazy-production-official-short

bench-q24-production-official-pmu: \
		bench-q24-lazy-production-official-pmu

bench-q24-lazy-production-official-short: kem-candidate-check \
		$(BUILD)/bench_q24_decap $(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_q24_production_official.py \
		$(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-q24-lazy-production-official-short.json

bench-q24-lazy-production-official-pmu: $(BUILD)/bench_q24_decap \
		$(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_q24_production_official_pmu.py \
		$(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-q24-lazy-production-official-pmu.json

bench-decap-cumulative-attribution: $(BUILD)/bench_decap_cumulative \
		$(BUILD)/bench_decap_cumulative_reversed
	$(PYTHON) tools/run_decap_cumulative.py \
		$(BUILD)/bench_decap_cumulative \
		--reversed-binary $(BUILD)/bench_decap_cumulative_reversed \
		--iterations 2000 --tsc-launches 8 --pmu-launches 8 \
		--full-result results/tile4-q24-lazy-production-official-short.json \
		--output results/tile4-decap-cumulative-attribution.json

bench-q24-recovered-r-gtpack-short: $(BUILD)/bench_q24_decap \
		$(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_q24_gtpack.py $(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --launches 48 --bootstrap-resamples 100000 \
		--output results/tile4-q24-recovered-r-gtpack-short.json

bench-q24-recovered-r-gtpack-pmu: $(BUILD)/bench_q24_decap \
		$(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_q24_gtpack_pmu.py $(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --launches 32 --bootstrap-resamples 100000 \
		--output results/tile4-q24-recovered-r-gtpack-pmu.json

q24-lazy10788-static: generated/tile4_q24_lazy10788_gate.json

q24-lazy-schedules-generate: $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_LAZY_SCHEDULE_JSON)

q24-encap-highrange-generate: $(Q24_ENCAP_HR_INC) $(Q24_ENCAP_HR_JSON)

$(Q24_ENCAP_HR_INC): tools/generate_q24_encap_highrange.py \
		generated/tile4_q24_codec.inc tools/generate_tile4.py
	$(PYTHON) tools/generate_q24_encap_highrange.py \
		--codec generated/tile4_q24_codec.inc \
		--asm-output $(Q24_ENCAP_HR_INC) \
		--json-output $(Q24_ENCAP_HR_JSON)

$(Q24_ENCAP_HR_JSON): $(Q24_ENCAP_HR_INC)
	@test -f $@

$(Q24_LAZY_SCHEDULE_INC): tools/generate_q24_lazy_schedules.py \
		generated/tile4_q24_codec.inc
	$(PYTHON) tools/generate_q24_lazy_schedules.py \
		--source generated/tile4_q24_codec.inc \
		--asm-output $(Q24_LAZY_SCHEDULE_INC) \
		--json-output $(Q24_LAZY_SCHEDULE_JSON)

$(Q24_LAZY_SCHEDULE_JSON): $(Q24_LAZY_SCHEDULE_INC)
	@test -f $@

generated/tile4_q24_lazy10788_gate.json: tools/generate_q24_lazy10788.py
	$(PYTHON) tools/generate_q24_lazy10788.py --output $@

q24-lazy10788-check: q24-lazy10788-static $(BUILD)/bench_q24_codec \
		$(BUILD)/test_tile4_kem_candidate
	$(BUILD)/bench_q24_codec 1 >/dev/null
	$(BUILD)/test_tile4_kem_candidate

bench-q24-lazy10788-gtpack-short: q24-lazy10788-check \
		$(BUILD)/bench_q24_lazy_L0 $(BUILD)/bench_q24_lazy_reversed_L0
	$(PYTHON) tools/run_q24_lazy_gtpack.py $(BUILD)/bench_q24_lazy_L0 \
		--reversed-binary $(BUILD)/bench_q24_lazy_reversed_L0 \
		--iterations 2000 --launches 48 \
		--output results/tile4-q24-lazy-caged-L0-final.json

bench-q24-lazy10788-gtpack-pmu: q24-lazy10788-check \
		$(BUILD)/bench_q24_lazy_L0 $(BUILD)/bench_q24_lazy_reversed_L0
	$(PYTHON) tools/run_q24_lazy_gtpack_pmu.py $(BUILD)/bench_q24_lazy_L0 \
		--reversed-binary $(BUILD)/bench_q24_lazy_reversed_L0 \
		--iterations 2000 --launches 32 \
		--output results/tile4-q24-lazy-caged-L0-pmu.json

bench-q24-lazy-schedules-short: q24-lazy-schedules-generate \
		$(Q24_LAZY_NORMAL_BINS) $(Q24_LAZY_REVERSED_BINS)
	$(PYTHON) tools/run_q24_lazy_schedule.py \
		--normal-binaries $(Q24_LAZY_NORMAL_BINS) \
		--reversed-binaries $(Q24_LAZY_REVERSED_BINS) \
		--iterations 2000 --launches 8 \
		--output results/tile4-q24-lazy-schedules-short.json

$(BUILD)/bench_q24_tf1_m: bench/bench_q24_tf1_m.c \
		src/tile4_q24_codec_asm.S src/tile4.h \
		generated/tile4_q24_codec.inc $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_M_TF1_GATE=1 -Isrc -o $@ bench/bench_q24_tf1_m.c \
		src/tile4_q24_codec_asm.S

$(BUILD)/bench_q24_tf1_m_reversed: bench/bench_q24_tf1_m.c \
		src/tile4_q24_codec_asm.S src/tile4.h \
		generated/tile4_q24_codec.inc $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_M_TF1_GATE=1 -Isrc -o $@ src/tile4_q24_codec_asm.S \
		bench/bench_q24_tf1_m.c

q24-tf1-m-check: q24-lazy-schedules-generate $(BUILD)/bench_q24_tf1_m
	$(BUILD)/bench_q24_tf1_m 1 >/dev/null
	@test "$$(nm -S $(BUILD)/bench_q24_tf1_m | awk \
		'/ gt32_q24_encode_soa_lazy10788_asm$$/{print $$2}')" = \
		"$$(nm -S $(BUILD)/bench_q24_tf1_m | awk \
		'/ gt32_q24_encode_soa_tf1_asm$$/{print $$2}')"

bench-q24-tf1-m-short: q24-tf1-m-check $(BUILD)/bench_q24_tf1_m_reversed
	$(BUILD)/bench_q24_tf1_m 4000
	$(BUILD)/bench_q24_tf1_m_reversed 4000

$(BUILD)/bench_q24_hotcompact_c1: bench/bench_q24_hotcompact_c1.c \
		src/tile4_q24_codec_asm.S src/tile4.h \
		generated/tile4_q24_codec.inc $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -o $@ bench/bench_q24_hotcompact_c1.c \
		src/tile4_q24_codec_asm.S

$(BUILD)/bench_q24_hotcompact_c1_reversed: bench/bench_q24_hotcompact_c1.c \
		src/tile4_q24_codec_asm.S src/tile4.h \
		generated/tile4_q24_codec.inc $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -o $@ src/tile4_q24_codec_asm.S \
		bench/bench_q24_hotcompact_c1.c

bench-q24-hotcompact-c1-short: $(BUILD)/bench_q24_hotcompact_c1 \
		$(BUILD)/bench_q24_hotcompact_c1_reversed
	$(BUILD)/bench_q24_hotcompact_c1 4000
	$(BUILD)/bench_q24_hotcompact_c1_reversed 4000

bench-q24-decap-pmu: $(BUILD)/bench_q24_decap \
		$(BUILD)/bench_q24_decap_reversed
	$(PYTHON) tools/run_q24_decap_pmu.py $(BUILD)/bench_q24_decap \
		--reversed-binary $(BUILD)/bench_q24_decap_reversed \
		--iterations 2000 --repeats 3 \
		--output results/tile4-q24-decap-pmu.json

bench-q24-decap-align64-short: $(BUILD)/bench_q24_decap_align64 \
		$(BUILD)/bench_q24_decap_align64_reversed
	$(PYTHON) tools/run_q24_decap.py $(BUILD)/bench_q24_decap_align64 \
		--reversed-binary $(BUILD)/bench_q24_decap_align64_reversed \
		--iterations 2000 --launches 2 \
		--output results/tile4-q24-decap-align64-short.json

bench-q24-placement-sweep: $(Q24_CAGE_NORMAL_BINS) \
		$(Q24_CAGE_REVERSED_BINS)
	$(PYTHON) tools/run_q24_placement_sweep.py \
		--build-dir $(BUILD) --iterations 2000 --launches 4 \
		--output results/tile4-q24-placement-sweep.json

bench-q24-compact-codec-short: $(BUILD)/bench_q24_codec_compact \
		$(BUILD)/bench_q24_codec_compact_reversed
	$(PYTHON) tools/run_q24_codec.py $(BUILD)/bench_q24_codec_compact \
		--reversed-binary $(BUILD)/bench_q24_codec_compact_reversed \
		--iterations 2000 --output results/tile4-q24-compact-codec-short.json

bench-q24-compact-decap-short: q24-compact-check \
		$(BUILD)/bench_q24_decap_compact \
		$(BUILD)/bench_q24_decap_compact_reversed
	$(PYTHON) tools/run_q24_decap.py $(BUILD)/bench_q24_decap_compact \
		--reversed-binary $(BUILD)/bench_q24_decap_compact_reversed \
		--iterations 2000 --launches 4 \
		--output results/tile4-q24-compact-decap-short.json

q24-compact-check: $(BUILD)/test_tile4_kem_candidate_compact
	$(BUILD)/test_tile4_kem_candidate_compact

bench-q24-pattern-codec-short: $(BUILD)/bench_q24_codec_pattern \
		$(BUILD)/bench_q24_codec_pattern_reversed
	$(PYTHON) tools/run_q24_codec.py $(BUILD)/bench_q24_codec_pattern \
		--reversed-binary $(BUILD)/bench_q24_codec_pattern_reversed \
		--iterations 2000 --output results/tile4-q24-pattern-codec-short.json

bench-q24-pattern-decap-short: q24-pattern-check \
		$(BUILD)/bench_q24_decap_pattern \
		$(BUILD)/bench_q24_decap_pattern_reversed
	$(PYTHON) tools/run_q24_decap.py $(BUILD)/bench_q24_decap_pattern \
		--reversed-binary $(BUILD)/bench_q24_decap_pattern_reversed \
		--iterations 2000 --launches 4 \
		--output results/tile4-q24-pattern-decap-short.json

bench-q24-pattern-cage-short: q24-pattern-check \
		$(BUILD)/bench_q24_pattern_cage \
		$(BUILD)/bench_q24_pattern_cage_reversed
	$(PYTHON) tools/run_q24_decap.py $(BUILD)/bench_q24_pattern_cage \
		--reversed-binary $(BUILD)/bench_q24_pattern_cage_reversed \
		--iterations 2000 --launches 4 \
		--output results/tile4-q24-pattern-cage-short.json

bench-q24-unrolled-matched-cage-short: \
		$(BUILD)/bench_q24_unrolled_matched_cage \
		$(BUILD)/bench_q24_unrolled_matched_cage_reversed
	$(PYTHON) tools/run_q24_decap.py $(BUILD)/bench_q24_unrolled_matched_cage \
		--reversed-binary $(BUILD)/bench_q24_unrolled_matched_cage_reversed \
		--iterations 2000 --launches 4 \
		--output results/tile4-q24-unrolled-matched-cage-short.json

bench-q24-environment-attribution: \
		$(BUILD)/bench_q24_unrolled_matched_cage \
		$(BUILD)/bench_q24_unrolled_matched_cage_reversed \
		$(BUILD)/bench_q24_unrolled_matched_cage_nonpie \
		$(BUILD)/bench_q24_unrolled_matched_cage_nonpie_reversed
	$(PYTHON) tools/run_q24_environment_attribution.py \
		$(BUILD)/bench_q24_unrolled_matched_cage \
		--reversed-binary $(BUILD)/bench_q24_unrolled_matched_cage_reversed \
		--nonpie-binary $(BUILD)/bench_q24_unrolled_matched_cage_nonpie \
		--nonpie-reversed-binary \
			$(BUILD)/bench_q24_unrolled_matched_cage_nonpie_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-q24-launch-environment.json

bench-q24-launch-pmu: \
		$(BUILD)/bench_q24_unrolled_matched_cage \
		$(BUILD)/bench_q24_unrolled_matched_cage_reversed \
		$(BUILD)/bench_q24_unrolled_matched_cage_nonpie \
		$(BUILD)/bench_q24_unrolled_matched_cage_nonpie_reversed
	$(PYTHON) tools/run_q24_launch_pmu.py \
		$(BUILD)/bench_q24_unrolled_matched_cage \
		--reversed-binary $(BUILD)/bench_q24_unrolled_matched_cage_reversed \
		--nonpie-binary $(BUILD)/bench_q24_unrolled_matched_cage_nonpie \
		--nonpie-reversed-binary \
			$(BUILD)/bench_q24_unrolled_matched_cage_nonpie_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-q24-launch-pmu.json

q24-launch-attribution-summary:
	$(PYTHON) tools/summarize_q24_launch_attribution.py \
		--environment results/tile4-q24-launch-environment.json \
		--pmu results/tile4-q24-launch-pmu.json \
		--output results/tile4-q24-launch-attribution-summary.json

q24-pattern-check: $(BUILD)/test_tile4_kem_candidate_pattern
	$(BUILD)/test_tile4_kem_candidate_pattern

transpose-redeposit-generate: generate
	$(PYTHON) tools/generate_transpose_redeposit.py \
		--output $(TRANSPOSE_REDEPOSIT_GATE)

aos-dot-redc16-generate: generate
	$(PYTHON) tools/generate_aos_dot_redc16.py

check: generate $(BUILD)/test_tile4
	$(BUILD)/test_tile4

test: check

kem-candidate-check: generate
	$(MAKE) CC=$(CC) $(BUILD)/test_tile4_kem_candidate
	$(BUILD)/test_tile4_kem_candidate

bench-kem-decap-candidate-short: generate \
		$(BUILD)/bench_kem_decap_candidate
	$(PYTHON) tools/run_kem_decap_candidate.py \
		$(BUILD)/bench_kem_decap_candidate --iterations 2000 \
		--output results/tile4-kem-decap-candidate-short.json

bench-decap-attribution-short: generate \
		$(BUILD)/bench_decap_phase_attribution \
		$(BUILD)/bench_kem_decap_candidate
	$(PYTHON) tools/run_kem_decap_candidate.py \
		$(BUILD)/bench_kem_decap_candidate --iterations 2000 \
		--output results/tile4-kem-decap-candidate-short.json
	$(PYTHON) tools/run_decap_phase_attribution.py \
		$(BUILD)/bench_decap_phase_attribution --iterations 2000 \
		--full-result results/tile4-kem-decap-candidate-short.json \
		--output results/tile4-decap-phase-attribution-short.json

sanitize: generate $(BUILD)/test_tile4_sanitize
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_tile4_sanitize

audit: generate $(BUILD)/tile4_asm.o $(BUILD)/tile4_basemul_asm.o \
		$(BUILD)/tile4_aos_dot_redc16_asm.o \
		$(BUILD)/tile4_keygen_fj1_p0_asm.o \
		$(BUILD)/tile4_bm_soa_dot_redc16_asm.o \
		$(BUILD)/tile4_inv_radix4_asm.o \
		$(BUILD)/tile4_basemul_attribution_asm.o \
		$(BUILD)/tile4_forward_bm_soa_attribution_asm.o \
		$(BUILD)/tile4_inverse_private_asm.o $(BUILD)/tile4_inverse_tail_asm.o \
		$(BUILD)/tile4_inverse_tail_isolated.o $(BUILD)/tile4_frombytes_asm.o \
		$(BUILD)/tile4_encodeq_bridge_asm.o $(BUILD)/tile4_q24_codec_asm.o
	objdump -drwC -Mintel $(BUILD)/tile4_asm.o > $(BUILD)/tile4_asm.dump
	! objdump -drwC -Mintel --disassemble=gt32_tile4_forward_tile_asm \
		$(BUILD)/tile4_asm.o | rg -n '\[(?:r|e)?sp[+\-]'
	! objdump -drwC -Mintel \
		--disassemble=gt32_tile4_forward_all_pair_id_center_asm \
		$(BUILD)/tile4_asm.o | rg -n '\[(?:r|e)?sp[+\-]|vpmulld'
	! objdump -drwC -Mintel --disassemble=gt32_tile4_inverse_tile_asm \
		$(BUILD)/tile4_asm.o | rg -n '\[(?:r|e)?sp[+\-]'
	rg -n 'sub[[:space:]]+rsp,0x600|add[[:space:]]+rsp,0x600' \
		$(BUILD)/tile4_asm.dump
	nm -g --defined-only $(BUILD)/tile4_asm.o | \
		rg 'gt32_tile4_(frontend.*|forward.*|inverse.*)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_basemul_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_basemul_asm.o | \
		rg 'gt32_tile4_basemul_(b2|b3_late|b4b_partial|k2|general_b2|scale_soa_private|scale_soa_aos_to_aos_private|raw_(soa|aos)_private|c3center(_late)?_aos_private)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_aos_dot_redc16_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]|vpmulld'
	nm -g --defined-only $(BUILD)/tile4_aos_dot_redc16_asm.o | \
		rg 'gt32_tile4_basemul_(aos_dot_r1[us]|scale_ff_aos_r1u)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_keygen_fj1_p0_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]|vpmulld'
	nm -g --defined-only $(BUILD)/tile4_keygen_fj1_p0_asm.o | \
		rg 'gt32_tile4_keygen_fj1_p0_s[01]_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_bm_soa_dot_redc16_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]|vpmulld'
	nm -g --defined-only $(BUILD)/tile4_bm_soa_dot_redc16_asm.o | \
		rg 'gt32_tile4_bm_soa_dot_redc16_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_inv_radix4_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]|vpmulld'
	nm -g --defined-only $(BUILD)/tile4_inv_radix4_asm.o | \
		rg 'gt32_tile4_inverse_radix4_identity_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_basemul_attribution_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_basemul_attribution_asm.o | \
		rg 'gt32_tile4_attr_(transpose_(one(_shufps)?|two|three)|basemul_(raw|c3)_soa|basemul_i1_stage01_fused|inverse_i1_cross3|center_c3_soa)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_forward_bm_soa_attribution_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_forward_bm_soa_attribution_asm.o | \
		rg 'gt32_tile4_attr_(forward_all_bm_soa(_s5x4|_qpair02|_shufps)?|basemul_c3_(p|qpair02)_to_aos)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_inverse_private_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_inverse_private_asm.o | \
		rg 'gt32_tile4_inverse_soa_private(_parallel)?_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_inverse_tail_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_inverse_tail_asm.o | \
		rg 'gt32_tile4_inverse_tail_(asm_rminus1|t[1-8]_|t10_|champion_)'
	! objdump -drwC -Mintel $(BUILD)/tile4_inverse_tail_isolated.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_inverse_tail_isolated.o | \
		rg 'gt32_tile4_inverse_tail_t9_isolated_private_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_frombytes_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_frombytes_asm.o | \
		rg 'gt32_tile4_frombytes(2_aos_1soa_semantic|3_bm_soa_semantic|_(aos|bm_soa_aos_control|bm_soa_semantic))_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_encodeq_bridge_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_encodeq_bridge_asm.o | \
		rg 'gt32_tile4_soa_to_official_words(_grouped)?_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_q24_codec_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]|\bzmm|\bk[0-7]\b'
	nm -g --defined-only $(BUILD)/tile4_q24_codec_asm.o | \
		rg 'gt32_q24_(decode_(aos|soa)|decode3_soa|encode_(aos|soa))_asm'

bench-short: generate $(BUILD)/bench_forward_short
	$(BUILD)/bench_forward_short 2000

.PHONY: bench-frontend-f1 bench-frontend-f14-wave
bench-frontend-f1: generate $(BUILD)/bench_frontend_f1 \
		$(BUILD)/bench_frontend_f1_reversed
	$(BUILD)/bench_frontend_f1 4000
	$(BUILD)/bench_frontend_f1_reversed 4000

$(BUILD)/bench_frontend_f1: bench/bench_frontend_f1.c src/tile4_asm.S \
		generated/tile4_frontend_wide.inc generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DGT32_FRONTEND_GATE_VARIANTS -Isrc -o $@ src/tile4_asm.S \
		bench/bench_frontend_f1.c

$(BUILD)/bench_frontend_f1_reversed: bench/bench_frontend_f1.c src/tile4_asm.S \
		generated/tile4_frontend_wide.inc generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DGT32_FRONTEND_GATE_VARIANTS -DGT32_F1_FIRST \
		-Isrc -o $@ src/tile4_asm.S \
		bench/bench_frontend_f1.c

bench-frontend-f14-wave: generate $(BUILD)/bench_frontend_f1 \
		$(BUILD)/bench_frontend_f14_wave_reversed
	$(PYTHON) tools/run_frontend_f14_wave_gate.py \
		--normal $(BUILD)/bench_frontend_f1 \
		--reversed $(BUILD)/bench_frontend_f14_wave_reversed \
		--iterations 4000 --launches 8 \
		--output results/tile4-frontend-f14-wavefront.json

$(BUILD)/bench_frontend_f14_wave_reversed: bench/bench_frontend_f1.c src/tile4_asm.S \
		generated/tile4_frontend_wide.inc generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DGT32_FRONTEND_GATE_VARIANTS -DGT32_F14_W2_FIRST \
		-Isrc -o $@ src/tile4_asm.S bench/bench_frontend_f1.c

.PHONY: bench-b3-wave
bench-b3-wave: generate $(BUILD)/bench_b3_wave
	$(BUILD)/bench_b3_wave 4000

$(BUILD)/bench_b3_wave: bench/bench_b3_wave.c src/tile4_basemul_asm.S | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/tile4_basemul_asm.S bench/bench_b3_wave.c

bench-official-short: generate $(BUILD)/bench_official_short
	$(BUILD)/bench_official_short 2000

bench-official-cold: generate $(BUILD)/bench_official_short
	$(BUILD)/bench_official_short 2000 cold

bench-inverse-short: generate $(BUILD)/bench_inverse_short
	$(BUILD)/bench_inverse_short 2000

bench-consumer-short: generate $(BUILD)/bench_consumer_short
	$(BUILD)/bench_consumer_short 2000

bench-basemul-short: generate $(BUILD)/bench_basemul_short
	$(BUILD)/bench_basemul_short 2000

bench-mixed-frombytes-short: generate $(BUILD)/bench_mixed_frombytes
	$(PYTHON) tools/run_mixed_frombytes.py $(BUILD)/bench_mixed_frombytes \
		--iterations 2000 --output results/tile4-mixed-frombytes-short.json

bench-correct-semantic-decoder-short: generate \
		$(BUILD)/bench_correct_semantic_decoder
	$(PYTHON) tools/run_correct_semantic_decoder.py \
		$(BUILD)/bench_correct_semantic_decoder --iterations 2000 \
		--output results/tile4-correct-semantic-decoder-short.json

bench-basemul-attribution: generate $(BUILD)/bench_basemul_attribution
	$(PYTHON) tools/run_basemul_attribution.py \
		$(BUILD)/bench_basemul_attribution --iterations 2000 \
		--output results/tile4-basemul-attribution-short.json

bench-forward-bm-redeposit: generate $(BUILD)/bench_forward_bm_redeposit
	$(PYTHON) tools/run_forward_bm_redeposit.py \
		$(BUILD)/bench_forward_bm_redeposit --iterations 2000 \
		--output results/tile4-forward-bm-redeposit-short.json

bench-s5-schedule: generate $(BUILD)/bench_s5_schedule
	$(PYTHON) tools/run_s5_schedule.py $(BUILD)/bench_s5_schedule \
		--iterations 2000 --output results/tile4-s5-schedule-short.json

bench-s45-wavefront-pmu: generate $(BUILD)/bench_s5_schedule
	$(PYTHON) tools/run_s45_wavefront.py $(BUILD)/bench_s5_schedule \
		--iterations 10000 --repeats 20 \
		--output results/tile4-s45-wavefront-pmu.json

bench-transpose-redeposit-short: transpose-redeposit-generate \
		$(BUILD)/bench_transpose_redeposit \
		$(BUILD)/bench_transpose_redeposit_reversed
	$(PYTHON) tools/run_transpose_redeposit.py \
		$(BUILD)/bench_transpose_redeposit \
		--reversed-binary $(BUILD)/bench_transpose_redeposit_reversed \
		--iterations 2000 --static-gate $(TRANSPOSE_REDEPOSIT_GATE) \
		--output results/tile4-transpose-redeposit-short.json

bench-aos-dot-redc16-short: aos-dot-redc16-generate \
		$(BUILD)/bench_aos_dot_redc16 \
		$(BUILD)/bench_aos_dot_redc16_reversed
	$(PYTHON) tools/run_aos_dot_redc16.py \
		$(BUILD)/bench_aos_dot_redc16 \
		--reversed-binary $(BUILD)/bench_aos_dot_redc16_reversed \
		--iterations 2000 --static-gate $(AOS_DOT_REDC16_GATE) \
		--output results/tile4-aos-dot-redc16-short.json

aos-dot-redc16-serious: aos-dot-redc16-generate \
		$(BUILD)/bench_aos_dot_redc16 \
		$(BUILD)/bench_aos_dot_redc16_reversed
	$(PYTHON) tools/run_aos_dot_redc16.py \
		$(BUILD)/bench_aos_dot_redc16 \
		--reversed-binary $(BUILD)/bench_aos_dot_redc16_reversed \
		--iterations 100000 --mode serious \
		--static-gate $(AOS_DOT_REDC16_GATE) \
		--output results/tile4-aos-dot-redc16-serious.json

bench-aos-dot-official-cycles: aos-dot-redc16-generate \
		$(BUILD)/bench_aos_dot_official_cycles \
		$(BUILD)/bench_aos_dot_official_cycles_reversed
	$(PYTHON) tools/run_aos_dot_official_cycles.py \
		$(BUILD)/bench_aos_dot_official_cycles \
		--reversed-binary $(BUILD)/bench_aos_dot_official_cycles_reversed \
		--iterations 1000000 --repeats 3 \
		--output results/tile4-aos-dot-redc16-official-cycles.json

bench-aos-dot-callsite-short: aos-dot-redc16-generate \
		$(BUILD)/bench_aos_dot_callsite \
		$(BUILD)/bench_aos_dot_callsite_reversed
	$(PYTHON) tools/run_aos_dot_callsite.py \
		$(BUILD)/bench_aos_dot_callsite \
		--reversed-binary $(BUILD)/bench_aos_dot_callsite_reversed \
		--iterations 2000 \
		--output results/tile4-aos-dot-redc16-callsite-short.json

aos-dot-forward-native-serious: aos-dot-redc16-generate \
		$(BUILD)/bench_aos_dot_callsite \
		$(BUILD)/bench_aos_dot_callsite_reversed
	$(PYTHON) tools/run_aos_dot_forward_native_serious.py \
		$(BUILD)/bench_aos_dot_callsite \
		--reversed-binary $(BUILD)/bench_aos_dot_callsite_reversed \
		--iterations 100000 \
		--output results/tile4-aos-dot-redc16-forward-native-serious.json

encap-mixed-aos-soa-static: generate
	$(PYTHON) tools/generate_encap_mixed_aos_soa_gate.py

bench-private-caller: generate $(BUILD)/bench_private_caller \
		$(BUILD)/bench_private_caller_reversed
	$(PYTHON) tools/run_private_caller.py \
		$(BUILD)/bench_private_caller --iterations 2000 --launches 2 \
		--corroboration-binary $(BUILD)/bench_private_caller_reversed \
		--output results/tile4-private-caller-transpose-cut-asymmetric-short.json

private-caller-serious: generate $(BUILD)/bench_private_caller \
		$(BUILD)/bench_private_caller_reversed
	$(PYTHON) tools/run_private_caller.py \
		$(BUILD)/bench_private_caller --iterations 100000 --mode serious \
		--corroboration-binary $(BUILD)/bench_private_caller_reversed \
		--output results/tile4-private-caller-serious.json

bench-promotion: generate $(BUILD)/bench_promotion
	$(BUILD)/bench_promotion 100000 0

promotion-serious: generate $(BUILD)/bench_promotion
	$(PYTHON) tools/run_promotion.py $(BUILD)/bench_promotion \
		--iterations 100000 --launches 5 \
		--output results/tile4-promotion-serious.json

promotion-serious-reversed: generate $(BUILD)/bench_promotion_reversed
	$(PYTHON) tools/run_promotion.py $(BUILD)/bench_promotion_reversed \
		--iterations 100000 --launches 5 \
		--output results/tile4-promotion-serious-reversed.json

promotion-pmu: generate $(BUILD)/bench_promotion
	$(PYTHON) tools/run_promotion_pmu.py $(BUILD)/bench_promotion \
		--iterations 1000000 --repeats 3 \
		--output results/tile4-promotion-pmu.json

promotion-symbols: $(BUILD)/bench_promotion $(BUILD)/bench_promotion_reversed
	$(PYTHON) tools/report_promotion_symbols.py \
		$(BUILD)/bench_promotion $(BUILD)/bench_promotion_reversed \
		--output results/tile4-promotion-symbols.json

$(BUILD):
	mkdir -p $@

$(BUILD)/test_tile4: $(SOURCES) src/tile4.h $(GEN) \
		$(BUILD)/parent_ntt.o $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(SOURCES) $(BUILD)/parent_ntt.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/test_tile4_sanitize: $(SOURCES) src/tile4.h $(GEN) \
		$(BUILD)/parent_ntt_sanitize.o $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -Isrc -o $@ $(SOURCES) \
		$(BUILD)/parent_ntt_sanitize.o $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/parent_ntt.o: $(REFERENCE) | $(BUILD)
	$(CC) $(CFLAGS) -Wno-conversion -Wno-sign-conversion -c -o $@ $<

$(BUILD)/parent_ntt_sanitize.o: $(REFERENCE) | $(BUILD)
	$(CC) $(CFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -Wno-conversion -Wno-sign-conversion \
		-c -o $@ $<

$(BUILD)/tile4_asm.o: src/tile4_asm.S generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_asm.S

$(BUILD)/tile4_basemul_asm.o: src/tile4_basemul_asm.S \
		generated/tile4_basemul_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_basemul_asm.S

$(BUILD)/tile4_aos_dot_redc16_asm.o: src/tile4_aos_dot_redc16_asm.S \
		$(AOS_DOT_REDC16_CONSTANTS) | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_aos_dot_redc16_asm.S

$(BUILD)/tile4_keygen_fj1_p0_asm.o: src/tile4_keygen_fj1_p0_asm.S \
		generated/tile4_keygen_fj1_p0_routes.inc \
		$(AOS_DOT_REDC16_CONSTANTS) | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_keygen_fj1_p0_asm.S

$(BUILD)/tile4_bm_soa_dot_redc16_asm.o: \
		src/tile4_bm_soa_dot_redc16_asm.S \
		generated/tile4_basemul_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_bm_soa_dot_redc16_asm.S

$(BUILD)/tile4_inv_radix4_asm.o: src/tile4_inv_radix4_asm.S \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_inv_radix4_asm.S

$(BUILD)/tile4_basemul_attribution_asm.o: \
		src/tile4_basemul_attribution_asm.S \
		generated/tile4_basemul_constants.inc \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_basemul_attribution_asm.S

$(BUILD)/tile4_forward_bm_soa_attribution_asm.o: \
		src/tile4_forward_bm_soa_attribution_asm.S \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_forward_bm_soa_attribution_asm.S

$(BUILD)/tile4_inverse_private_asm.o: src/tile4_inverse_private_asm.S \
		generated/tile4_private_inverse_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_inverse_private_asm.S

$(BUILD)/tile4_inverse_tail_asm.o: src/tile4_inverse_tail_asm.S \
		generated/tile4_inverse_tail_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_inverse_tail_asm.S

$(BUILD)/tile4_inverse_tail_isolated.o: src/tile4_inverse_tail_asm.S \
		generated/tile4_inverse_tail_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -DTILE4_ISOLATED=1 -c -o $@ src/tile4_inverse_tail_asm.S

$(BUILD)/tile4_dual_terminal_asm.o: src/tile4_inverse_tail_asm.S \
		generated/tile4_inverse_tail_constants.inc \
		$(DUAL_TERMINAL_CONSTANTS) | $(BUILD)
	$(CC) $(CFLAGS) -DTILE4_DUAL_ONLY=1 -c -o $@ src/tile4_inverse_tail_asm.S

$(BUILD)/tile4_dual_terminal.o: src/tile4_dual_terminal.c \
		src/tile4_dual_terminal.h src/tile4.h | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -c -o $@ src/tile4_dual_terminal.c

$(BUILD)/tile4_frombytes_asm.o: src/tile4_frombytes_asm.S \
		generated/tile4_frombytes_aos_stores.inc \
		generated/tile4_frombytes_semantic_soa_routes.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_frombytes_asm.S

$(BUILD)/tile4_encodeq_bridge_asm.o: src/tile4_encodeq_bridge_asm.S \
		generated/tile4_soa_to_official_routes.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_encodeq_bridge_asm.S

$(BUILD)/tile4_q24_codec_asm.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc $(Q24_COMPACT_INC) \
		$(Q24_LAZY_SCHEDULE_INC) $(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_q24_codec_asm.S

$(BUILD)/tile4_q24_decode_debt.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc generated/tile4_decode_debt.inc \
		$(Q24_COMPACT_INC) $(Q24_LAZY_SCHEDULE_INC) $(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_DECODE_DEBT_GATE=1 -c -o $@ $<

$(BUILD)/tile4_q24_codec_cage_%.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc $(Q24_COMPACT_INC) \
		$(Q24_LAZY_SCHEDULE_INC) $(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_SOA_CAGE_OFFSET=$* -c -o $@ $<

$(BUILD)/tile4_q24_codec_compact.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc $(Q24_COMPACT_INC) \
		$(Q24_LAZY_SCHEDULE_INC) $(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_SOA_COMPACT=1 -c -o $@ $<

$(BUILD)/tile4_q24_codec_pattern.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc $(Q24_COMPACT_INC) \
		$(Q24_LAZY_SCHEDULE_INC) $(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_SOA_PATTERN_COMPACT=1 -c -o $@ $<

$(BUILD)/tile4_q24_codec_pattern_cage.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc $(Q24_COMPACT_INC) \
		$(Q24_LAZY_SCHEDULE_INC) $(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_SOA_PATTERN_COMPACT=1 \
		-DQ24_SOA_CAGE_OFFSET=0 -c -o $@ $<

$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o: \
		src/tile4_q24_codec_asm.S generated/tile4_q24_codec.inc \
		$(Q24_COMPACT_INC) $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_INCLUDE_COMPACT_TABLES=1 \
		-DQ24_SOA_CAGE_OFFSET=0 -c -o $@ $<

$(BUILD)/tile4_kem_candidate.o: src/tile4_kem_candidate.c \
		src/tile4_kem_candidate.h src/tile4.h src/tile4_dual_terminal.h \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S \
		generated/tile4_serialized_mapping.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -r -nostdlib \
		-Isrc -I$(OFFICIAL) -o $@ src/tile4_kem_candidate.c \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S

$(BUILD)/tile4_kem_candidate_global_inverse.o: src/tile4_kem_candidate.c \
		src/tile4_kem_candidate.h src/tile4.h src/tile4_dual_terminal.h \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S \
		generated/tile4_serialized_mapping.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -DGT32_GLOBAL_PHYSICAL_KEM=1 -r -nostdlib \
		-Isrc -I$(OFFICIAL) -o $@ src/tile4_kem_candidate.c \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S

$(BUILD)/tile4_kem_candidate_testing.o: src/tile4_kem_candidate.c \
		src/tile4_kem_candidate.h src/tile4.h src/tile4_dual_terminal.h \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S \
		generated/tile4_serialized_mapping.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -DGT32_TILE4_KEM_TESTING=1 -r -nostdlib \
		-Isrc -I$(OFFICIAL) -o $@ src/tile4_kem_candidate.c \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S

$(BUILD)/tile4_kem_candidate_global_inverse_testing.o: \
		src/tile4_kem_candidate.c src/tile4_kem_candidate.h src/tile4.h \
		src/tile4_dual_terminal.h src/tile4_dual_terminal.c \
		src/tile4_crep_sidecar_asm.S \
		generated/tile4_serialized_mapping.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -DGT32_TILE4_KEM_TESTING=1 \
		-DGT32_GLOBAL_PHYSICAL_KEM=1 -r -nostdlib \
		-Isrc -I$(OFFICIAL) -o $@ src/tile4_kem_candidate.c \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S

$(BUILD)/tile4_kem_candidate_nonpie.o: src/tile4_kem_candidate.c \
		src/tile4_kem_candidate.h src/tile4.h src/tile4_dual_terminal.h \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S \
		generated/tile4_serialized_mapping.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -fno-pie -Werror -r -nostdlib \
		-Isrc -I$(OFFICIAL) -o $@ src/tile4_kem_candidate.c \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S

$(BUILD)/tile4_kem_candidate_align64.o: src/tile4_kem_candidate.c \
		src/tile4_kem_candidate.h src/tile4.h src/tile4_dual_terminal.h \
		src/tile4_dual_terminal.c src/tile4_crep_sidecar_asm.S \
		generated/tile4_serialized_mapping.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -DGT32_TILE4_RECOVER_ALIGN64=1 \
		-r -nostdlib -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_kem_candidate.c src/tile4_dual_terminal.c \
		src/tile4_crep_sidecar_asm.S

$(BUILD)/tile4_kem_encap_candidate.o: src/tile4_kem_encap_candidate.c \
		src/tile4_kem_encap_candidate.h src/tile4.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -c -Isrc -I$(OFFICIAL) -o $@ $<

$(BUILD)/tile4_kem_encap_q24_sum.o: src/tile4_kem_encap_q24_sum.c \
		src/tile4_kem_encap_candidate.c src/tile4_kem_encap_candidate.h \
		src/tile4.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -c -Isrc -I$(OFFICIAL) -o $@ $<

$(BUILD)/tile4_kem_encap_f14.o: src/tile4_kem_encap_f14.c \
		src/tile4_kem_encap_candidate.c src/tile4_kem_encap_candidate.h \
		src/tile4.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -c -Isrc -I$(OFFICIAL) -o $@ $<

$(BUILD)/tile4_kem_encap_tf1.o: src/tile4_kem_encap_tf1.c \
		src/tile4_kem_encap_candidate.c src/tile4_kem_encap_candidate.h \
		src/tile4.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -c -Isrc -I$(OFFICIAL) -o $@ $<

$(BUILD)/tile4_kem_encap_f14_tf1.o: src/tile4_kem_encap_f14_tf1.c \
		src/tile4_kem_encap_candidate.c src/tile4_kem_encap_candidate.h \
		src/tile4.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -c -Isrc -I$(OFFICIAL) -o $@ $<

$(BUILD)/test_tile4_kem_encap_candidate: \
		tests/test_tile4_kem_encap_candidate.c \
		$(BUILD)/tile4_kem_encap_candidate.o \
		$(BUILD)/tile4_kem_encap_q24_sum.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DQ24_M_TF1_GATE=1 -Isrc -I$(OFFICIAL) -o $@ \
		tests/test_tile4_kem_encap_candidate.c \
		$(BUILD)/tile4_kem_encap_candidate.o \
		$(BUILD)/tile4_kem_encap_q24_sum.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

encap-candidate-check: generate $(BUILD)/test_tile4_kem_encap_candidate
	$(BUILD)/test_tile4_kem_encap_candidate

KEYGEN_ENCAP_ATTR_GT := $(BUILD)/tile4_kem_encap_candidate.o \
		$(BUILD)/tile4_kem_encap_q24_sum.o \
		$(BUILD)/tile4_kem_encap_f14.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S
KEYGEN_ENCAP_ATTR_OFFICIAL := $(OFFICIAL)/kem.c $(OFFICIAL)/poly.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/consts.c \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_keygen_encap_attribution: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_ATTR_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS \
		-Isrc -I$(OFFICIAL) -o $@ \
		-DGT32_FRONTEND_GATE_VARIANTS -DGT32_ENCAP_F14_WRAPPER \
		bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_ATTR_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_keygen_encap_attribution_reversed: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_ATTR_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS \
		-Isrc -I$(OFFICIAL) -o $@ \
		-DGT32_FRONTEND_GATE_VARIANTS -DGT32_ENCAP_F14_WRAPPER \
		bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(KEYGEN_ENCAP_ATTR_GT)

KEYGEN_ENCAP_F14_CLEAN_GT := $(BUILD)/tile4_kem_encap_candidate.o \
		$(BUILD)/tile4_kem_encap_q24_sum.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S

$(BUILD)/bench_encap_f14_clean_control: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DQ24_M_TF1_GATE=1 -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_F14_CLEAN_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_tf1_clean_control_reversed: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DQ24_M_TF1_GATE=1 -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(KEYGEN_ENCAP_F14_CLEAN_GT)

$(BUILD)/bench_encap_f14_clean_candidate: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_F14_PRODUCTION -Isrc -I$(OFFICIAL) \
		-o $@ bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_F14_CLEAN_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_f14_clean_control_nonpie: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -fno-pie -no-pie -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_F14_CLEAN_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_f14_clean_candidate_nonpie: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -fno-pie -no-pie -DGT32_FRONTEND_F14_PRODUCTION \
		-Isrc -I$(OFFICIAL) -o $@ bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_F14_CLEAN_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_tf1_clean_candidate: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DQ24_M_TF1_GATE=1 -DQ24_M_TF1_PRODUCTION=1 -Isrc -I$(OFFICIAL) \
		-o $@ bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_F14_CLEAN_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_tf1_clean_candidate_reversed: \
		bench/bench_keygen_encap_attribution.c $(KEYGEN_ENCAP_F14_CLEAN_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DQ24_M_TF1_GATE=1 -DQ24_M_TF1_PRODUCTION=1 -Isrc -I$(OFFICIAL) \
		-o $@ bench/bench_keygen_encap_attribution.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(KEYGEN_ENCAP_F14_CLEAN_GT)

bench-keygen-encap-attribution-short: encap-candidate-check \
		$(BUILD)/bench_keygen_encap_attribution \
		$(BUILD)/bench_keygen_encap_attribution_reversed
	$(PYTHON) tools/run_keygen_encap_attribution.py \
		$(BUILD)/bench_keygen_encap_attribution \
		--reversed-binary $(BUILD)/bench_keygen_encap_attribution_reversed \
		--iterations 2000 --launches 8 \
		--output results/tile4-keygen-encap-attribution-short.json

bench-keygen-encap-attribution-pmu: encap-candidate-check \
		$(BUILD)/bench_keygen_encap_attribution \
		$(BUILD)/bench_keygen_encap_attribution_reversed
	$(PYTHON) tools/run_keygen_encap_pmu.py \
		$(BUILD)/bench_keygen_encap_attribution \
		--reversed-binary $(BUILD)/bench_keygen_encap_attribution_reversed \
		--iterations 10000 \
		--output results/tile4-keygen-encap-attribution-pmu.json

ENCAP_RESIDUAL_GT := $(BUILD)/tile4_kem_encap_candidate.o \
		$(BUILD)/tile4_kem_encap_f14.o $(BUILD)/tile4_kem_encap_tf1.o \
		$(BUILD)/tile4_kem_encap_f14_tf1.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S

$(BUILD)/bench_encap_same_elf_residual: \
		bench/bench_encap_same_elf_residual.c $(ENCAP_RESIDUAL_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS \
		-DQ24_M_TF1_GATE=1 -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_encap_same_elf_residual.c \
		$(ENCAP_RESIDUAL_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_same_elf_residual_reversed: \
		bench/bench_encap_same_elf_residual.c $(ENCAP_RESIDUAL_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS \
		-DQ24_M_TF1_GATE=1 -Isrc -I$(OFFICIAL) -o $@ \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(ENCAP_RESIDUAL_GT) \
		bench/bench_encap_same_elf_residual.c

bench-encap-same-elf-residual: $(BUILD)/bench_encap_same_elf_residual \
		$(BUILD)/bench_encap_same_elf_residual_reversed
	$(PYTHON) tools/run_encap_same_elf_residual.py \
		$(BUILD)/bench_encap_same_elf_residual \
		--reversed-binary $(BUILD)/bench_encap_same_elf_residual_reversed \
		--iterations 1000 --launches 8 --disable-aslr \
		--output results/tile4-encap-same-elf-residual-aslr-off.json

bench-encap-same-elf-residual-pmu: $(BUILD)/bench_encap_same_elf_residual \
		$(BUILD)/bench_encap_same_elf_residual_reversed
	$(PYTHON) tools/run_encap_same_elf_pmu.py \
		$(BUILD)/bench_encap_same_elf_residual \
		--reversed-binary $(BUILD)/bench_encap_same_elf_residual_reversed \
		--iterations 20000 --launches 8 --disable-aslr \
		--output results/tile4-encap-same-elf-residual-pmu-aslr-off.json

ENCAP_POLY_ISLAND_GT := src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_q24_codec_asm.S src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S

$(BUILD)/bench_encap_poly_island: bench/bench_encap_poly_island.c \
		$(ENCAP_POLY_ISLAND_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS -DQ24_M_TF1_GATE=1 \
		-Isrc -I$(OFFICIAL) -o $@ bench/bench_encap_poly_island.c \
		$(ENCAP_POLY_ISLAND_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_poly_island_reversed: bench/bench_encap_poly_island.c \
		$(ENCAP_POLY_ISLAND_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS -DQ24_M_TF1_GATE=1 \
		-Isrc -I$(OFFICIAL) -o $@ $(KEYGEN_ENCAP_ATTR_OFFICIAL) \
		$(ENCAP_POLY_ISLAND_GT) bench/bench_encap_poly_island.c

bench-encap-poly-island: $(BUILD)/bench_encap_poly_island \
		$(BUILD)/bench_encap_poly_island_reversed
	$(PYTHON) tools/run_encap_poly_island.py $(BUILD)/bench_encap_poly_island \
		--reversed-binary $(BUILD)/bench_encap_poly_island_reversed \
		--tsc-iterations 1000 --pmu-iterations 20000 --launches 8 \
		--output results/tile4-encap-poly-island.json

$(BUILD)/bench_encap_cumulative: bench/bench_encap_cumulative.c \
		$(KEYGEN_ENCAP_ATTR_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_encap_cumulative.c \
		$(KEYGEN_ENCAP_ATTR_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_cumulative_reversed: bench/bench_encap_cumulative.c \
		$(KEYGEN_ENCAP_ATTR_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_encap_cumulative.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(KEYGEN_ENCAP_ATTR_GT)

bench-encap-cumulative-short: encap-candidate-check \
		$(BUILD)/bench_encap_cumulative \
		$(BUILD)/bench_encap_cumulative_reversed
	$(PYTHON) tools/run_encap_cumulative.py $(BUILD)/bench_encap_cumulative \
		--reversed-binary $(BUILD)/bench_encap_cumulative_reversed \
		--iterations 500 --launches 8 \
		--output results/tile4-encap-cumulative-short.json

bench-encap-cumulative-pmu: $(BUILD)/bench_encap_cumulative \
		$(BUILD)/bench_encap_cumulative_reversed
	$(PYTHON) tools/run_encap_cumulative_pmu.py $(BUILD)/bench_encap_cumulative \
		--reversed-binary $(BUILD)/bench_encap_cumulative_reversed \
		--iterations 10000 \
		--output results/tile4-encap-cumulative-pmu.json

$(BUILD)/bench_encap_load_attribution: bench/bench_encap_load_attribution.c \
		$(KEYGEN_ENCAP_ATTR_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS \
		-Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_encap_load_attribution.c \
		$(KEYGEN_ENCAP_ATTR_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_encap_load_attribution_reversed: \
		bench/bench_encap_load_attribution.c $(KEYGEN_ENCAP_ATTR_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS \
		-Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_encap_load_attribution.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(KEYGEN_ENCAP_ATTR_GT)

bench-encap-load-attribution-pmu: $(BUILD)/bench_encap_load_attribution \
		$(BUILD)/bench_encap_load_attribution_reversed
	$(PYTHON) tools/run_encap_load_attribution_pmu.py \
		$(BUILD)/bench_encap_load_attribution \
		--reversed-binary $(BUILD)/bench_encap_load_attribution_reversed \
		--iterations 10000 --pairs 8 \
		--output results/tile4-encap-load-attribution-pmu.json

.PHONY: bench-encap-outside-island-waterfall \
	bench-encap-shared-transition-tsc
bench-encap-outside-island-waterfall: $(BUILD)/bench_encap_load_attribution \
		$(BUILD)/bench_encap_load_attribution_reversed
	$(PYTHON) tools/run_encap_outside_island_waterfall.py \
		$(BUILD)/bench_encap_load_attribution \
		--reversed-binary $(BUILD)/bench_encap_load_attribution_reversed \
		--iterations 10000 --pairs 4 \
		--output results/tile4-encap-outside-island-waterfall.json

bench-encap-shared-transition-tsc: $(BUILD)/bench_encap_load_attribution \
		$(BUILD)/bench_encap_load_attribution_reversed
	$(PYTHON) tools/run_encap_shared_transition_tsc.py \
		$(BUILD)/bench_encap_load_attribution \
		--reversed-binary $(BUILD)/bench_encap_load_attribution_reversed \
		--iterations 10100 --pairs 8 \
		--output results/tile4-encap-shared-transition-tsc.json

bench-encap-load-stall-pmu: $(BUILD)/bench_encap_load_attribution \
		$(BUILD)/bench_encap_load_attribution_reversed
	$(PYTHON) tools/run_encap_load_stall_pmu.py \
		$(BUILD)/bench_encap_load_attribution \
		--reversed-binary $(BUILD)/bench_encap_load_attribution_reversed \
		--iterations 10000 --pairs 8 \
		--output results/tile4-encap-load-stall-pmu.json

bench-encap-bm-add-fused-pmu: $(BUILD)/bench_encap_load_attribution \
		$(BUILD)/bench_encap_load_attribution_reversed
	$(PYTHON) tools/run_encap_bm_add_fused_pmu.py \
		$(BUILD)/bench_encap_load_attribution \
		--reversed-binary $(BUILD)/bench_encap_load_attribution_reversed \
		--iterations 10000 --pairs 12 \
		--output results/tile4-encap-bm-add-fused-pmu.json

bench-encap-q24-rr-pmu: $(BUILD)/bench_encap_load_attribution \
		$(BUILD)/bench_encap_load_attribution_reversed
	$(PYTHON) tools/run_encap_q24_rr_pmu.py \
		$(BUILD)/bench_encap_load_attribution \
		--reversed-binary $(BUILD)/bench_encap_load_attribution_reversed \
		--iterations 20000 --pairs 20 \
		--output results/tile4-encap-q24-rr-pmu.json

encap-rhat-pack-static:
	$(PYTHON) tools/generate_encap_rhat_pack_gate.py

$(BUILD)/probe_encap_rhat_range: tests/probe_encap_rhat_range.c \
		src/tile4_asm.S src/tile4_forward_bm_soa_attribution_asm.S \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/consts.c $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		tests/probe_encap_rhat_range.c src/tile4_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/consts.c

encap-rhat-range-probe: $(BUILD)/probe_encap_rhat_range
	taskset -c 1 $(BUILD)/probe_encap_rhat_range 10000

$(BUILD)/test_tile4_baseinv_j1: tests/test_tile4_baseinv_j1.c \
		src/tile4_baseinv_j1_ref.c src/tile4_baseinv_j1_avx2.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		tests/test_tile4_baseinv_j1.c src/tile4_baseinv_j1_ref.c \
		src/tile4_baseinv_j1_avx2.c \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL)

keygen-j1-typed-static:
	$(PYTHON) tools/generate_keygen_j1_typed_gate.py

keygen-j1-check: keygen-j1-typed-static $(BUILD)/test_tile4_baseinv_j1
	$(BUILD)/test_tile4_baseinv_j1

K3B_GT := src/tile4_baseinv_j1_avx2.c src/tile4_aos_dot_redc16_asm.S

$(BUILD)/bench_keygen_j1_k3b: bench/bench_keygen_j1_k3b.c $(K3B_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_j1_k3b.c $(K3B_GT) \
		$(KEYGEN_ENCAP_ATTR_OFFICIAL)

$(BUILD)/bench_keygen_j1_k3b_reversed: bench/bench_keygen_j1_k3b.c \
		$(K3B_GT) $(KEYGEN_ENCAP_ATTR_OFFICIAL) $(GEN) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_j1_k3b.c $(KEYGEN_ENCAP_ATTR_OFFICIAL) \
		$(K3B_GT)

bench-keygen-j1-k3b-pmu: keygen-j1-check \
		$(BUILD)/bench_keygen_j1_k3b \
		$(BUILD)/bench_keygen_j1_k3b_reversed
	$(PYTHON) tools/run_keygen_j1_k3b.py \
		$(BUILD)/bench_keygen_j1_k3b \
		--reversed-binary $(BUILD)/bench_keygen_j1_k3b_reversed \
		--iterations 10000 --repeats 20 \
		--output results/tile4-keygen-j1-k3b-pmu.json

KEYGEN_SOA_ISLAND_GT := src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S src/tile4_baseinv_p_soa.c \
		src/tile4_baseinv_p_j1_soa.c \
		src/tile4_baseinv_p_j1_control.c \
		src/tile4_baseinv_p_j1_batch_asm.S \
		../gt_ntt/gt_baseinv_native_prepare_asm.S \
		../gt_ntt/gt_basemul_layout_asm.S src/tile4_q24_codec_asm.S
KEYGEN_SOA_ISLAND_OFFICIAL := $(OFFICIAL)/poly.c $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/pack.s

$(BUILD)/bench_keygen_soa_island: bench/bench_keygen_soa_island.c \
		$(KEYGEN_SOA_ISLAND_GT) $(KEYGEN_SOA_ISLAND_OFFICIAL) $(GEN) \
		$(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_soa_island.c $(KEYGEN_SOA_ISLAND_GT) \
		$(KEYGEN_SOA_ISLAND_OFFICIAL)

$(BUILD)/bench_keygen_soa_island_reversed: bench/bench_keygen_soa_island.c \
		$(KEYGEN_SOA_ISLAND_GT) $(KEYGEN_SOA_ISLAND_OFFICIAL) $(GEN) \
		$(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_soa_island.c $(KEYGEN_SOA_ISLAND_OFFICIAL) \
		$(KEYGEN_SOA_ISLAND_GT)

keygen-soa-island-check: generate $(BUILD)/bench_keygen_soa_island
	$(BUILD)/bench_keygen_soa_island 1000 island official
	$(BUILD)/bench_keygen_soa_island 1000 island gt32-soa

bench-keygen-soa-island-pmu: keygen-soa-island-check \
		$(BUILD)/bench_keygen_soa_island_reversed
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_keygen_soa_island \
		--reversed-binary $(BUILD)/bench_keygen_soa_island_reversed \
		--iterations 10000 --repeats 20 --gt-backend gt32-half \
		--output results/tile4-keygen-soa-island-q24-halfscatter-pmu.json

bench-keygen-baseinv-official-reuse-pmu: baseinv-official-compat-generate \
		$(BUILD)/bench_keygen_soa_island \
		$(BUILD)/bench_keygen_soa_island_reversed
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_keygen_soa_island \
		--reversed-binary $(BUILD)/bench_keygen_soa_island_reversed \
		--iterations 10000 --repeats 20 \
		--control-backend gt32-soa --gt-backend gt32-asm \
		--gates fbi,island \
		--experiment GT32-BASEINV-OFFICIAL-REUSE-O1-O2-001 \
		--output results/tile4-keygen-baseinv-official-reuse-pmu.json

KEYGEN_BASEINV_BM_EDGE_GT := src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S src/tile4_baseinv_p_soa.c \
		src/tile4_baseinv_bm_edge_asm.S \
		../gt_ntt/gt_baseinv_native_prepare_asm.S \
		../gt_ntt/gt_basemul_layout_asm.S

$(BUILD)/bench_keygen_baseinv_bm_edge: \
		bench/bench_keygen_baseinv_bm_edge.c $(KEYGEN_BASEINV_BM_EDGE_GT) \
		$(GEN) $(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections \
		-fdata-sections -Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_baseinv_bm_edge.c $(KEYGEN_BASEINV_BM_EDGE_GT)

$(BUILD)/bench_keygen_baseinv_bm_edge_reversed: \
		bench/bench_keygen_baseinv_bm_edge.c $(KEYGEN_BASEINV_BM_EDGE_GT) \
		$(GEN) $(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections \
		-fdata-sections -Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		$(KEYGEN_BASEINV_BM_EDGE_GT) bench/bench_keygen_baseinv_bm_edge.c

keygen-baseinv-bm-edge-check: generate $(BUILD)/bench_keygen_baseinv_bm_edge
	$(BUILD)/bench_keygen_baseinv_bm_edge 1000 two control
	$(BUILD)/bench_keygen_baseinv_bm_edge 1000 two candidate

bench-keygen-baseinv-bm-edge-pmu: keygen-baseinv-bm-edge-check \
		$(BUILD)/bench_keygen_baseinv_bm_edge_reversed
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_keygen_baseinv_bm_edge \
		--reversed-binary $(BUILD)/bench_keygen_baseinv_bm_edge_reversed \
		--iterations 10000 --repeats 20 \
		--control-backend control --gt-backend candidate \
		--gates boundary-one,boundary-two \
		--experiment GT32-KEYGEN-BASEINV-BM-EDGE-P1-001 \
		--output results/tile4-keygen-baseinv-bm-edge-pmu.json

BASEINV_STAGE_ATTR_SRC := src/tile4_baseinv_p_j1_attribution.c \
		src/tile4_baseinv_p_j1_batch_asm.S

$(BUILD)/bench_baseinv_stage_attribution: \
		bench/bench_baseinv_stage_attribution.c $(BASEINV_STAGE_ATTR_SRC) \
		generated/tile4_baseinv_p_tables.inc | $(BUILD)
	$(CC) $(KEM_CFLAGS) -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_baseinv_stage_attribution.c $(BASEINV_STAGE_ATTR_SRC)

$(BUILD)/bench_baseinv_stage_attribution_reversed: \
		bench/bench_baseinv_stage_attribution.c $(BASEINV_STAGE_ATTR_SRC) \
		generated/tile4_baseinv_p_tables.inc | $(BUILD)
	$(CC) $(KEM_CFLAGS) -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		$(BASEINV_STAGE_ATTR_SRC) bench/bench_baseinv_stage_attribution.c

baseinv-stage-attribution-check: $(BUILD)/bench_baseinv_stage_attribution
	$(BUILD)/bench_baseinv_stage_attribution 1000 full candidate
	$(BUILD)/bench_baseinv_stage_attribution 1000 full asm
	$(BUILD)/bench_baseinv_stage_attribution 1000 full tree

bench-baseinv-stage-attribution-pmu: baseinv-stage-attribution-check \
		$(BUILD)/bench_baseinv_stage_attribution_reversed
	$(PYTHON) tools/run_baseinv_stage_attribution.py \
		$(BUILD)/bench_baseinv_stage_attribution \
		--reversed-binary $(BUILD)/bench_baseinv_stage_attribution_reversed \
		--iterations 100000 --repeats 20 \
		--output results/tile4-keygen-baseinv-stage-attribution-pmu.json

bench-baseinv-batch-asm-pmu: baseinv-stage-attribution-check \
		$(BUILD)/bench_baseinv_stage_attribution_reversed
	$(PYTHON) tools/run_baseinv_batch_asm.py \
		$(BUILD)/bench_baseinv_stage_attribution \
		--reversed-binary $(BUILD)/bench_baseinv_stage_attribution_reversed \
		--iterations 100000 --repeats 20 \
		--output results/tile4-keygen-p-j1-batch-asm-pmu.json

$(BUILD)/bench_keygen_production: bench/bench_keygen_production.c \
		$(KEYGEN_SOA_ISLAND_GT) $(KEYGEN_SOA_ISLAND_OFFICIAL) $(GEN) \
		$(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_production.c $(KEYGEN_SOA_ISLAND_GT) \
		$(KEYGEN_SOA_ISLAND_OFFICIAL)

$(BUILD)/bench_keygen_production_reversed: bench/bench_keygen_production.c \
		$(KEYGEN_SOA_ISLAND_GT) $(KEYGEN_SOA_ISLAND_OFFICIAL) $(GEN) \
		$(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_keygen_production.c $(KEYGEN_SOA_ISLAND_OFFICIAL) \
		$(KEYGEN_SOA_ISLAND_GT)

keygen-production-check: generate $(BUILD)/bench_keygen_production
	$(BUILD)/bench_keygen_production 8 g1 official
	$(BUILD)/bench_keygen_production 8 g1 gt32-prod
	$(BUILD)/bench_keygen_production 64 g2 official
	$(BUILD)/bench_keygen_production 64 g2 gt32-prod

bench-keygen-production-pmu: keygen-production-check \
		$(BUILD)/bench_keygen_production_reversed
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_keygen_production \
		--reversed-binary $(BUILD)/bench_keygen_production_reversed \
		--iterations 1000 --repeats 48 --gt-backend gt32-prod \
		--gates g1,g2 \
		--output results/tile4-keygen-production-g1-g2-pmu.json

$(BUILD)/test_tile4_kem_candidate.o: tests/test_tile4_kem_candidate.c \
		src/tile4_kem_candidate.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -DGT32_TILE4_KEM_TESTING=1 \
		-Isrc -I$(OFFICIAL) -c -o $@ $<

$(BUILD)/test_tile4_kem_candidate: $(BUILD)/tile4_kem_candidate_testing.o \
		$(BUILD)/test_tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) \
		-o $@ $(BUILD)/test_tile4_kem_candidate.o \
		$(BUILD)/tile4_kem_candidate_testing.o src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/test_tile4_kem_candidate_compact: \
		$(BUILD)/tile4_kem_candidate_testing.o \
		$(BUILD)/test_tile4_kem_candidate.o \
		$(BUILD)/tile4_q24_codec_compact.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(BUILD)/test_tile4_kem_candidate.o \
		$(BUILD)/tile4_kem_candidate_testing.o src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_compact.o \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/test_tile4_kem_candidate_pattern: \
		$(BUILD)/tile4_kem_candidate_testing.o \
		$(BUILD)/test_tile4_kem_candidate.o \
		$(BUILD)/tile4_q24_codec_pattern.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(BUILD)/test_tile4_kem_candidate.o \
		$(BUILD)/tile4_kem_candidate_testing.o src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_pattern.o \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_kem_decap_candidate: $(BUILD)/tile4_kem_candidate.o \
		bench/bench_kem_decap_candidate.c \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_kem_decap_candidate.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_decap_phase_attribution: $(BUILD)/tile4_kem_candidate.o \
		bench/bench_decap_phase_attribution.c \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_TILE4_KEM_TESTING=1 \
		-DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_decap_phase_attribution.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

Q24_DECAP_DEPS := $(BUILD)/tile4_kem_candidate.o bench/bench_q24_decap.c \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S $(Q24_LAZY_SCHEDULE_INC) \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

CUMULATIVE_DEPS := $(BUILD)/tile4_kem_candidate.o \
		bench/bench_decap_cumulative.c \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S $(Q24_LAZY_SCHEDULE_INC) \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o $(GEN) \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

DUAL_TERMINAL_DEPS := bench/bench_dual_terminal.c \
		$(BUILD)/tile4_dual_terminal.o $(BUILD)/tile4_dual_terminal_asm.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(BUILD)/tile4_inverse_private_asm.o \
		$(BUILD)/tile4_basemul_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_asm.o $(DUAL_TERMINAL_GATE) \
		$(OFFICIAL)/poly.c $(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s

$(BUILD)/bench_dual_terminal: $(DUAL_TERMINAL_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_dual_terminal.c $(BUILD)/tile4_dual_terminal.o \
		$(BUILD)/tile4_dual_terminal_asm.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(BUILD)/tile4_inverse_private_asm.o \
		$(BUILD)/tile4_basemul_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_asm.o $(OFFICIAL)/poly.c $(OFFICIAL)/consts.c \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/pack.s

$(BUILD)/bench_dual_terminal_reversed: $(DUAL_TERMINAL_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/consts.c $(OFFICIAL)/poly.c \
		$(BUILD)/tile4_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_basemul_asm.o \
		$(BUILD)/tile4_inverse_private_asm.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(BUILD)/tile4_dual_terminal_asm.o \
		$(BUILD)/tile4_dual_terminal.o bench/bench_dual_terminal.c

CREP_SIDECAR_DEPS := bench/bench_crep_sidecar.c \
		src/tile4_crep_sidecar_asm.S $(BUILD)/tile4_dual_terminal.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(BUILD)/tile4_inverse_private_asm.o \
		$(BUILD)/tile4_basemul_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_asm.o \
		$(OFFICIAL)/poly.c $(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s

$(BUILD)/bench_crep_sidecar: $(CREP_SIDECAR_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -Wno-conversion -Wno-sign-conversion \
		-Isrc -I$(OFFICIAL) -o $@ bench/bench_crep_sidecar.c \
		src/tile4_crep_sidecar_asm.S $(BUILD)/tile4_dual_terminal.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(BUILD)/tile4_inverse_private_asm.o \
		$(BUILD)/tile4_basemul_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_asm.o $(OFFICIAL)/poly.c $(OFFICIAL)/consts.c \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/pack.s

$(BUILD)/bench_crep_sidecar_reversed: $(CREP_SIDECAR_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -Wno-conversion -Wno-sign-conversion \
		-Isrc -I$(OFFICIAL) -o $@ $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c $(OFFICIAL)/poly.c \
		$(BUILD)/tile4_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_basemul_asm.o \
		$(BUILD)/tile4_inverse_private_asm.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(BUILD)/tile4_dual_terminal.o src/tile4_crep_sidecar_asm.S \
		bench/bench_crep_sidecar.c

Q24_PACK_VERIFY_DEPS := bench/bench_q24_pack_verify.c \
		$(BUILD)/tile4_q24_codec_asm.o $(BUILD)/tile4_asm.o \
		$(BUILD)/tile4_forward_bm_soa_attribution_asm.o \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_q24_pack_verify: $(Q24_PACK_VERIFY_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_pack_verify.c $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_asm.o \
		$(BUILD)/tile4_forward_bm_soa_attribution_asm.o \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_q24_pack_verify_reversed: $(Q24_PACK_VERIFY_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/consts.c \
		$(BUILD)/tile4_forward_bm_soa_attribution_asm.o \
		$(BUILD)/tile4_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		bench/bench_q24_pack_verify.c

Q24_B3_FRONTIER_DEPS := bench/bench_q24_b3_frontier.c \
		$(BUILD)/tile4_q24_b3_frontier_asm.o \
		$(BUILD)/tile4_q24_codec_asm.o $(BUILD)/tile4_basemul_asm.o

$(BUILD)/tile4_q24_b3_frontier_asm.o: \
		src/tile4_q24_b3_frontier_asm.S \
		generated/tile4_q24_b3_frontier.inc \
		generated/tile4_basemul_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_q24_b3_frontier_asm.S

$(BUILD)/bench_q24_b3_frontier: $(Q24_B3_FRONTIER_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -Isrc -o $@ \
		bench/bench_q24_b3_frontier.c \
		$(BUILD)/tile4_q24_b3_frontier_asm.o \
		$(BUILD)/tile4_q24_codec_asm.o $(BUILD)/tile4_basemul_asm.o

$(BUILD)/bench_q24_b3_frontier_reversed: $(Q24_B3_FRONTIER_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -Isrc -o $@ \
		$(BUILD)/tile4_basemul_asm.o $(BUILD)/tile4_q24_codec_asm.o \
		$(BUILD)/tile4_q24_b3_frontier_asm.o \
		bench/bench_q24_b3_frontier.c

$(BUILD)/bench_decap_cumulative: $(CUMULATIVE_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_decap_cumulative.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_decap_cumulative_reversed: $(CUMULATIVE_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_decap_cumulative.c \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/tile4_q24_lazy_L%.o: src/tile4_q24_codec_asm.S \
		generated/tile4_q24_codec.inc $(Q24_LAZY_SCHEDULE_INC) \
		$(Q24_ENCAP_HR_INC) | $(BUILD)
	$(CC) $(CFLAGS) -DQ24_LAZY_SCHEDULE=$* -c -o $@ $<

$(BUILD)/bench_q24_lazy_L%: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_lazy_L%.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_lazy_L$*.o src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_lazy_reversed_L%: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_lazy_L%.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S $(BUILD)/tile4_q24_lazy_L$*.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_decap: $(Q24_DECAP_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_decap_reversed: $(Q24_DECAP_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

GLOBAL_INVERSE_DECAP_DEPS := $(filter-out $(BUILD)/tile4_kem_candidate.o,$(Q24_DECAP_DEPS)) \
	$(BUILD)/tile4_kem_candidate_global_inverse.o \
	src/tile4_global_physical_asm.S generated/tile4_global_physical_constants.inc

$(BUILD)/bench_global_inverse_decap: $(GLOBAL_INVERSE_DECAP_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_GLOBAL_PHYSICAL_KEM=1 -Isrc -I$(OFFICIAL) \
		-o $@ bench/bench_q24_decap.c \
		$(BUILD)/tile4_kem_candidate_global_inverse.o \
		src/tile4_global_physical_asm.S \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_global_inverse_decap_reversed: \
		$(GLOBAL_INVERSE_DECAP_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_GLOBAL_PHYSICAL_KEM=1 -Isrc -I$(OFFICIAL) \
		-o $@ $(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		src/tile4_global_physical_asm.S \
		$(BUILD)/tile4_kem_candidate_global_inverse.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

bench-gt32-global-inverse-decap-short: \
		$(BUILD)/bench_global_inverse_decap \
		$(BUILD)/bench_global_inverse_decap_reversed \
		$(BUILD)/test_tile4_kem_global_inverse
	$(BUILD)/test_tile4_kem_global_inverse
	$(PYTHON) tools/run_global_inverse_decap.py \
		$(BUILD)/bench_global_inverse_decap \
		--reversed-binary $(BUILD)/bench_global_inverse_decap_reversed \
		--iterations 10000 --launches 8 \
		--output results/tile4-global-inverse-decap-short.json

.PHONY: bench-full-kem-serious-100k
bench-full-kem-serious-100k: $(BUILD)/test_tile4_kem_global_inverse \
		$(BUILD)/bench_global_inverse_decap \
		$(BUILD)/bench_global_inverse_decap_reversed \
		$(BUILD)/bench_keygen_encap_attribution \
		$(BUILD)/bench_keygen_encap_attribution_reversed \
		$(BUILD)/bench_keygen_production \
		$(BUILD)/bench_keygen_production_reversed
	$(BUILD)/test_tile4_kem_global_inverse
	$(PYTHON) tools/run_global_inverse_decap.py \
		$(BUILD)/bench_global_inverse_decap \
		--reversed-binary $(BUILD)/bench_global_inverse_decap_reversed \
		--iterations 100000 --launches 4 \
		--output results/tile4-global-inverse-decap-serious.json
	$(PYTHON) tools/run_encap_full_serious.py \
		$(BUILD)/bench_keygen_encap_attribution \
		--reversed-binary $(BUILD)/bench_keygen_encap_attribution_reversed \
		--iterations 100000 \
		--output results/tile4-encap-full-serious.json
	$(PYTHON) tools/run_keygen_full_serious.py \
		$(BUILD)/bench_keygen_production \
		--reversed-binary $(BUILD)/bench_keygen_production_reversed \
		--iterations 100000 --pairs 20 \
		--output results/tile4-keygen-full-serious-100k.json

$(BUILD)/test_tile4_kem_global_inverse.o: tests/test_tile4_kem_candidate.c \
		src/tile4_kem_candidate.h | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -DGT32_TILE4_KEM_TESTING=1 \
		-DGT32_GLOBAL_PHYSICAL_KEM=1 -Isrc -I$(OFFICIAL) -c -o $@ $<

$(BUILD)/test_tile4_kem_global_inverse: \
		$(BUILD)/test_tile4_kem_global_inverse.o \
		$(BUILD)/tile4_kem_candidate_global_inverse_testing.o \
		$(GLOBAL_INVERSE_DECAP_DEPS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT32_TILE4_KEM_TESTING=1 \
		-DGT32_GLOBAL_PHYSICAL_KEM=1 -Isrc -I$(OFFICIAL) -o $@ \
		$(BUILD)/test_tile4_kem_global_inverse.o \
		$(BUILD)/tile4_kem_candidate_global_inverse_testing.o \
		src/tile4_global_physical_asm.S \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_decap_compact: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_compact.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_compact.o src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_decap_compact_reversed: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_compact.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		$(BUILD)/tile4_q24_codec_compact.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_decap_pattern: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_pattern.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_pattern.o src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_decap_pattern_reversed: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_pattern.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		$(BUILD)/tile4_q24_codec_pattern.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_decap_align64: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_kem_candidate_align64.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate_align64.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		src/tile4_q24_codec_asm.S src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_decap_align64_reversed: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_kem_candidate_align64.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S src/tile4_q24_codec_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate_align64.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_cage_%: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_cage_%.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_cage_$*.o src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_cage_reversed_%: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_cage_%.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		$(BUILD)/tile4_q24_codec_cage_$*.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_pattern_cage: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_pattern_cage.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_pattern_cage.o \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_pattern_cage_reversed: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_pattern_cage.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		$(BUILD)/tile4_q24_codec_pattern_cage.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_unrolled_matched_cage: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_unrolled_matched_cage_reversed: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_q24_unrolled_matched_cage_nonpie: $(Q24_DECAP_DEPS) \
		$(BUILD)/tile4_kem_candidate_nonpie.o \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -fno-pie -no-pie -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_q24_decap.c $(BUILD)/tile4_kem_candidate_nonpie.o \
		src/tile4_asm.S src/tile4_basemul_asm.S src/tile4_frombytes_asm.S \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o \
		src/tile4_encodeq_bridge_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/kem.c $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/add.s \
		$(OFFICIAL)/asm/baseinv.s $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/cbd.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/fips202/fips202.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

$(BUILD)/bench_q24_unrolled_matched_cage_nonpie_reversed: \
		$(Q24_DECAP_DEPS) $(BUILD)/tile4_kem_candidate_nonpie.o \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o | $(BUILD)
	$(CC) $(KEM_CFLAGS) -fno-pie -no-pie -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/kat/rng.c $(OFFICIAL)/kat/aes.c \
		$(OFFICIAL)/fips202/KeccakP-1600-AVX2.s \
		$(OFFICIAL)/fips202/fips202.c $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/asm/cbd.s \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/baseinv.s \
		$(OFFICIAL)/asm/add.s $(OFFICIAL)/consts.c \
		$(OFFICIAL)/symmetric.c $(OFFICIAL)/poly.c $(OFFICIAL)/kem.c \
		bench/bench_q24_decap.c src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S \
		$(BUILD)/tile4_q24_codec_unrolled_matched_cage.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_kem_candidate_nonpie.o \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_forward_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_asm.S bench/bench_forward_short.c $(GEN) \
		$(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_asm.S \
		bench/bench_forward_short.c $(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c

$(BUILD)/bench_official_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_asm.S bench/bench_official_short.c $(GEN) \
		$(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -I$(OFFICIAL) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_asm.S \
		bench/bench_official_short.c $(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/consts.c

$(BUILD)/bench_inverse_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_inverse_tail.c \
		src/tile4_inverse_tail_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S bench/bench_inverse_short.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -o $@ src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_inverse_tail.c \
		src/tile4_inverse_tail_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S bench/bench_inverse_short.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_basemul_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_basemul.c src/tile4_asm.S src/tile4_inverse_private_asm.S \
		bench/bench_basemul_short.c $(GEN) \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN)/gt_basemul_soa.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -I$(OFFICIAL) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_basemul.c \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S bench/bench_basemul_short.c \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN)/gt_basemul_soa.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/consts.c

$(BUILD)/bench_consumer_short: src/tile4_inverse_tail_asm.S src/tile4_asm.S \
		src/tile4_basemul_asm.S bench/bench_consumer_short.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN_LAMBDA) \
		$(FROZEN)/gt_invntt_soa.c \
		$(FROZEN)/gt_invntt_fused_soa.S $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -DGT_HAVE_AVX2_ASM=1 -Isrc -I$(FROZEN) -I$(OFFICIAL) \
		-o $@ src/tile4_inverse_tail_asm.S src/tile4_asm.S \
		src/tile4_basemul_asm.S bench/bench_consumer_short.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN_LAMBDA) \
		$(FROZEN)/gt_invntt_soa.c \
		$(FROZEN)/gt_invntt_fused_soa.S $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_mixed_frombytes: src/tile4_pack.c src/tile4_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S \
		bench/bench_mixed_frombytes.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/tile4_pack.c \
		src/tile4_frombytes_asm.S \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_mixed_frombytes.c $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/bench_correct_semantic_decoder: src/tile4_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S \
		bench/bench_correct_semantic_decoder.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_frombytes_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_correct_semantic_decoder.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_promotion: src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_promotion.c $(GEN) $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -Werror \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S bench/bench_promotion.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_promotion_reversed: src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_promotion.c $(GEN) $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -Werror \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c \
		bench/bench_promotion.c src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_basemul_attribution: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		bench/bench_basemul_attribution.c $(GEN) \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		bench/bench_basemul_attribution.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_forward_bm_redeposit: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_forward_bm_redeposit.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_forward_bm_redeposit.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_s5_schedule: src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_s5_schedule.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_s5_schedule.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_transpose_redeposit: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_transpose_redeposit.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_transpose_redeposit.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_transpose_redeposit_reversed: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_transpose_redeposit.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_REDEPOSIT_REVERSED=1 \
		-Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_transpose_redeposit.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_aos_dot_redc16: src/tile4_basemul.c \
		src/tile4_aos_dot_redc16_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S bench/bench_aos_dot_redc16.c \
		$(AOS_DOT_REDC16_GATE) $(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_basemul.c src/tile4_aos_dot_redc16_asm.S \
		src/tile4_basemul_asm.S src/tile4_asm.S \
		bench/bench_aos_dot_redc16.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_aos_dot_redc16_reversed: src/tile4_basemul.c \
		src/tile4_aos_dot_redc16_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S bench/bench_aos_dot_redc16.c \
		$(AOS_DOT_REDC16_GATE) $(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/crepmod3.s \
		bench/bench_aos_dot_redc16.c src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_aos_dot_redc16_asm.S \
		src/tile4_basemul.c $(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_aos_dot_official_cycles: src/tile4_aos_dot_redc16_asm.S \
		src/tile4_asm.S bench/bench_aos_dot_official_cycles.c \
		$(AOS_DOT_REDC16_GATE) $(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S \
		bench/bench_aos_dot_official_cycles.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_aos_dot_official_cycles_reversed: \
		src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S \
		bench/bench_aos_dot_official_cycles.c \
		$(AOS_DOT_REDC16_GATE) $(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/basemul.s \
		bench/bench_aos_dot_official_cycles.c src/tile4_asm.S \
		src/tile4_aos_dot_redc16_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_aos_dot_callsite: src/tile4_frombytes_asm.S \
		src/tile4_aos_dot_redc16_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S bench/bench_aos_dot_callsite.c \
		$(AOS_DOT_REDC16_GATE) $(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S src/tile4_asm.S \
		src/tile4_aos_dot_redc16_asm.S bench/bench_aos_dot_callsite.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_aos_dot_callsite_reversed: src/tile4_frombytes_asm.S \
		src/tile4_aos_dot_redc16_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S bench/bench_aos_dot_callsite.c \
		$(AOS_DOT_REDC16_GATE) $(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/crepmod3.s \
		bench/bench_aos_dot_callsite.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_frombytes_asm.S

FJ1_P0_BENCH_SOURCES := src/tile4_keygen_fj1_p0_asm.S \
	src/tile4_aos_dot_redc16_asm.S src/tile4_basemul_attribution_asm.S \
	src/tile4_basemul_asm.S src/tile4_encodeq_bridge_asm.S \
	bench/bench_keygen_fj1_p0.c
FJ1_P0_BENCH_DEPS := generated/tile4_keygen_fj1_p0_routes.inc \
	$(AOS_DOT_REDC16_CONSTANTS) $(GEN) \
	$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/bench_keygen_fj1_p0: $(FJ1_P0_BENCH_SOURCES) \
		$(FJ1_P0_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(FJ1_P0_BENCH_SOURCES) $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_keygen_fj1_p0_reversed: $(FJ1_P0_BENCH_SOURCES) \
		$(FJ1_P0_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/pack.s \
		bench/bench_keygen_fj1_p0.c src/tile4_encodeq_bridge_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_aos_dot_redc16_asm.S src/tile4_keygen_fj1_p0_asm.S

SOA_DOT_BENCH_SOURCES := src/tile4_bm_soa_dot_redc16_asm.S \
	src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
	src/tile4_asm.S bench/bench_bm_soa_dot_redc16.c
SOA_DOT_BENCH_DEPS := generated/tile4_basemul_constants.inc $(GEN) \
	$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/consts.c

$(BUILD)/bench_bm_soa_dot_redc16: $(SOA_DOT_BENCH_SOURCES) \
		$(SOA_DOT_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(SOA_DOT_BENCH_SOURCES) \
		$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/consts.c

$(BUILD)/bench_bm_soa_dot_redc16_reversed: $(SOA_DOT_BENCH_SOURCES) \
		$(SOA_DOT_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(OFFICIAL)/consts.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		bench/bench_bm_soa_dot_redc16.c src/tile4_asm.S \
		src/tile4_basemul_attribution_asm.S src/tile4_basemul_asm.S \
		src/tile4_bm_soa_dot_redc16_asm.S

INV_RADIX4_BENCH_SOURCES := src/tile4_asm.S src/tile4_inv_radix4_asm.S \
	bench/bench_inv_radix4.c
INV_RADIX4_BENCH_DEPS := $(GEN) $(BUILD)/tile4_inverse_tail_isolated.o \
	$(OFFICIAL)/consts.c

$(BUILD)/bench_inv_radix4: $(INV_RADIX4_BENCH_SOURCES) \
		$(INV_RADIX4_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(INV_RADIX4_BENCH_SOURCES) \
		$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/consts.c

$(BUILD)/bench_inv_radix4_reversed: $(INV_RADIX4_BENCH_SOURCES) \
		$(INV_RADIX4_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(OFFICIAL)/consts.c \
		$(BUILD)/tile4_inverse_tail_isolated.o bench/bench_inv_radix4.c \
		src/tile4_inv_radix4_asm.S src/tile4_asm.S

FWD_ID_BENCH_SOURCES := src/tile4_asm.S src/tile4_aos_dot_redc16_asm.S \
	bench/bench_forward_identity_lazy.c
FWD_ID_BENCH_DEPS := $(GEN) $(BUILD)/tile4_inverse_tail_isolated.o \
	$(OFFICIAL)/consts.c

$(BUILD)/bench_forward_identity_lazy: $(FWD_ID_BENCH_SOURCES) \
		$(FWD_ID_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(FWD_ID_BENCH_SOURCES) \
		$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/consts.c

$(BUILD)/bench_forward_identity_lazy_reversed: $(FWD_ID_BENCH_SOURCES) \
		$(FWD_ID_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(OFFICIAL)/consts.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		bench/bench_forward_identity_lazy.c \
		src/tile4_aos_dot_redc16_asm.S src/tile4_asm.S

Q24_BENCH_SOURCES := src/tile4_q24_codec_asm.S src/tile4_frombytes_asm.S \
	src/tile4_basemul_attribution_asm.S src/tile4_encodeq_bridge_asm.S \
	bench/bench_q24_codec.c
Q24_BENCH_DEPS := generated/tile4_q24_codec.inc \
	$(Q24_COMPACT_INC) $(Q24_LAZY_SCHEDULE_INC) \
	generated/tile4_serialized_mapping.h $(OFFICIAL)/asm/pack.s \
	$(OFFICIAL)/consts.c

$(BUILD)/bench_decode_debt: $(BUILD)/tile4_q24_decode_debt.o \
		bench/bench_decode_debt.c src/tile4.h | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		$(BUILD)/tile4_q24_decode_debt.o bench/bench_decode_debt.c

$(BUILD)/bench_decode_debt_reversed: $(BUILD)/tile4_q24_decode_debt.o \
		bench/bench_decode_debt.c src/tile4.h | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		bench/bench_decode_debt.c $(BUILD)/tile4_q24_decode_debt.o

$(BUILD)/bench_q24_codec: $(Q24_BENCH_SOURCES) $(Q24_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -o $@ $(Q24_BENCH_SOURCES) \
		src/tile4_pack.c $(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/bench_q24_codec_reversed: $(Q24_BENCH_SOURCES) \
		$(Q24_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -o $@ $(OFFICIAL)/consts.c \
		$(OFFICIAL)/asm/pack.s src/tile4_pack.c bench/bench_q24_codec.c \
		src/tile4_encodeq_bridge_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_frombytes_asm.S src/tile4_q24_codec_asm.S

$(BUILD)/bench_q24_codec_compact: $(BUILD)/tile4_q24_codec_compact.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S bench/bench_q24_codec.c \
		$(Q24_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -o $@ $(BUILD)/tile4_q24_codec_compact.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S bench/bench_q24_codec.c \
		src/tile4_pack.c $(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/bench_q24_codec_compact_reversed: \
		$(BUILD)/tile4_q24_codec_compact.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S bench/bench_q24_codec.c \
		$(Q24_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -o $@ $(OFFICIAL)/consts.c $(OFFICIAL)/asm/pack.s \
		src/tile4_pack.c bench/bench_q24_codec.c \
		src/tile4_encodeq_bridge_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_frombytes_asm.S $(BUILD)/tile4_q24_codec_compact.o

$(BUILD)/bench_q24_codec_pattern: $(BUILD)/tile4_q24_codec_pattern.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S bench/bench_q24_codec.c \
		$(Q24_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -o $@ $(BUILD)/tile4_q24_codec_pattern.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S bench/bench_q24_codec.c \
		src/tile4_pack.c $(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/bench_q24_codec_pattern_reversed: \
		$(BUILD)/tile4_q24_codec_pattern.o \
		src/tile4_frombytes_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_encodeq_bridge_asm.S bench/bench_q24_codec.c \
		$(Q24_BENCH_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DTILE4_ENCODEQ_DIRECT_EXPERIMENT=1 \
		-Isrc -o $@ $(OFFICIAL)/consts.c $(OFFICIAL)/asm/pack.s \
		src/tile4_pack.c bench/bench_q24_codec.c \
		src/tile4_encodeq_bridge_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_frombytes_asm.S $(BUILD)/tile4_q24_codec_pattern.o

Q24_PREFIX_SOURCES := src/tile4_q24_codec_asm.S src/tile4_frombytes_asm.S \
	src/tile4_asm.S src/tile4_basemul_asm.S bench/bench_q24_prefix.c
Q24_PREFIX_DEPS := generated/tile4_q24_codec.inc \
	generated/tile4_frombytes_semantic_soa_routes.inc \
	generated/tile4_constants.inc generated/tile4_basemul_constants.inc \
	$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/asm/crepmod3.s \
	$(OFFICIAL)/consts.c

$(BUILD)/bench_q24_prefix: $(Q24_PREFIX_SOURCES) $(Q24_PREFIX_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(Q24_PREFIX_SOURCES) $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_q24_prefix_reversed: $(Q24_PREFIX_SOURCES) \
		$(Q24_PREFIX_DEPS) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/consts.c $(OFFICIAL)/asm/crepmod3.s \
		bench/bench_q24_prefix.c src/tile4_basemul_asm.S src/tile4_asm.S \
		src/tile4_frombytes_asm.S src/tile4_q24_codec_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_streaming_b: src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_streaming_b.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_streaming_b.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_terminal_layout: src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_permutation_relaxed_asm.S \
		bench/bench_terminal_layout.c $(GEN) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_permutation_relaxed_asm.S \
		bench/bench_terminal_layout.c

bench-terminal-layout: bench-terminal-transpose-cut

bench-terminal-transpose-cut: generate $(BUILD)/bench_terminal_layout
	$(PYTHON) tools/run_terminal_layout.py \
		$(BUILD)/bench_terminal_layout --iterations 2000 \
		--output results/tile4-terminal-transpose-cut-asymmetric-short.json

$(BUILD)/bench_permutation_relaxed: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_permutation_relaxed_asm.S \
		bench/bench_permutation_relaxed.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_permutation_relaxed_asm.S \
		bench/bench_permutation_relaxed.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_forward_landing_baseinv: src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S \
		bench/bench_forward_landing_baseinv.c $(GEN) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_permutation_relaxed_asm.S \
		bench/bench_forward_landing_baseinv.c

$(FWD_LANDING_BASEINV_ARTIFACTS): tools/generate_forward_landing_baseinv.py \
		generated/tile4_manifest.json generated/tile4_constants.inc
	$(PYTHON) tools/generate_forward_landing_baseinv.py

bench-forward-landing-baseinv: generate $(BUILD)/bench_forward_landing_baseinv
	$(PYTHON) tools/generate_forward_landing_baseinv.py
	$(PYTHON) tools/run_forward_landing_baseinv.py \
		$(BUILD)/bench_forward_landing_baseinv --iterations 2000

$(BUILD)/bench_forward_landing_baseinv_chain: src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S src/tile4_baseinv_p_soa.c \
		bench/bench_forward_landing_baseinv_chain.c \
		$(FWD_LANDING_BASEINV_ARTIFACTS) | $(BUILD)
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -Werror -Isrc \
		-Wl,--gc-sections -o $@ src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S src/tile4_baseinv_p_soa.c \
		bench/bench_forward_landing_baseinv_chain.c

bench-forward-landing-baseinv-chain: generate
	$(PYTHON) tools/generate_forward_landing_baseinv.py
	$(MAKE) $(BUILD)/bench_forward_landing_baseinv_chain
	$(PYTHON) tools/run_forward_landing_baseinv_chain.py \
		$(BUILD)/bench_forward_landing_baseinv_chain --iterations 2000

$(BUILD)/bench_private_caller: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_private_caller.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_private_caller.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_private_caller_reversed: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_private_caller.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c \
		bench/bench_private_caller.c \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_basemul_attribution_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S $(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_encap_mixed_general: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_frombytes_asm.S \
		bench/bench_encap_mixed_general.c $(OFFICIAL)/consts.c $(GEN) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_frombytes_asm.S \
		bench/bench_encap_mixed_general.c $(OFFICIAL)/consts.c

$(BUILD)/bench_encap_mixed_general_reversed: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_frombytes_asm.S \
		bench/bench_encap_mixed_general.c $(OFFICIAL)/consts.c $(GEN) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		$(OFFICIAL)/consts.c bench/bench_encap_mixed_general.c \
		src/tile4_frombytes_asm.S src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_basemul_attribution_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S

$(BUILD)/bench_encap_e1_producer: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_frombytes_asm.S \
		bench/bench_encap_e1_producer.c $(OFFICIAL)/consts.c $(GEN) | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S src/tile4_frombytes_asm.S \
		bench/bench_encap_e1_producer.c $(OFFICIAL)/consts.c

spcrt-b3-exec-generate: $(SPCRT_B3_EXEC_ARTIFACTS)

$(SPCRT_B3_EXEC_ARTIFACTS): tools/generate_spcrt_b3_exec.py \
		tools/generate_tile4.py generated/tile4_spcrt_auto11_gate.json \
		generated/tile4_spcrt_raw_consumer_closure_gate.json
	$(PYTHON) tools/generate_spcrt_b3_exec.py

$(BUILD)/test_spcrt_b3_exec: tests/test_spcrt_b3_exec.c \
		src/spcrt_b3_exec_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		$(SPCRT_B3_EXEC_ARTIFACTS) generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ tests/test_spcrt_b3_exec.c \
		src/spcrt_b3_exec_asm.S src/tile4_asm.S src/tile4_basemul_asm.S

spcrt-b3-exec-check: $(BUILD)/test_spcrt_b3_exec
	$(BUILD)/test_spcrt_b3_exec

$(BUILD)/bench_spcrt_b3_exec: bench/bench_spcrt_b3_exec.c \
		src/spcrt_b3_exec_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		$(SPCRT_B3_EXEC_ARTIFACTS) generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ bench/bench_spcrt_b3_exec.c \
		src/spcrt_b3_exec_asm.S src/tile4_asm.S src/tile4_basemul_asm.S

$(BUILD)/bench_spcrt_b3_exec_reversed: bench/bench_spcrt_b3_exec.c \
		src/spcrt_b3_exec_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		$(SPCRT_B3_EXEC_ARTIFACTS) generated/tile4_n32_forward_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/tile4_basemul_asm.S \
		src/tile4_asm.S src/spcrt_b3_exec_asm.S bench/bench_spcrt_b3_exec.c

bench-spcrt-b3-exec-short: spcrt-b3-exec-check \
		$(BUILD)/bench_spcrt_b3_exec $(BUILD)/bench_spcrt_b3_exec_reversed
	$(PYTHON) tools/run_spcrt_b3_exec.py $(BUILD)/bench_spcrt_b3_exec \
		--reversed-binary $(BUILD)/bench_spcrt_b3_exec_reversed \
		--iterations 5000 --launches 4 \
		--output results/tile4-spcrt-repair-sched-short.json

b3-quartic-twist-generate: tools/generate_b3_quartic_twist_gate.py \
		tools/generate_tile4.py
	$(PYTHON) tools/generate_b3_quartic_twist_gate.py

m-baseinv-unification-generate: tools/generate_m_baseinv_unification_gate.py \
		tools/generate_tile4.py \
		generated/tile4_global_physical_layout_gate.json \
		generated/tile4_forward_landing_baseinv_gate.json \
		generated/tile4_n5_consumer_contract_audit.json
	$(PYTHON) tools/generate_m_baseinv_unification_gate.py

M_BASEINV_UNIFICATION_GT := src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S src/tile4_global_physical_asm.S \
		src/tile4_baseinv_p_soa.c src/tile4_baseinv_m_soa.c \
		src/tile4_baseinv_m_prepare_asm.S \
		../gt_ntt/gt_baseinv_native_prepare_asm.S \
		../gt_ntt/gt_basemul_layout_asm.S src/tile4_basemul_asm.S \
		src/tile4_q24_codec_asm.S

$(BUILD)/bench_m_baseinv_unification: \
		bench/bench_m_baseinv_unification.c $(M_BASEINV_UNIFICATION_GT) \
		$(GEN) $(FWD_LANDING_BASEINV_ARTIFACTS) \
		generated/tile4_m_baseinv_unification_gate.json \
		generated/tile4_baseinv_m_tables.inc | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections \
		-fdata-sections -Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_m_baseinv_unification.c $(M_BASEINV_UNIFICATION_GT)

$(BUILD)/bench_m_baseinv_unification_reversed: \
		bench/bench_m_baseinv_unification.c $(M_BASEINV_UNIFICATION_GT) \
		$(GEN) $(FWD_LANDING_BASEINV_ARTIFACTS) \
		generated/tile4_m_baseinv_unification_gate.json \
		generated/tile4_baseinv_m_tables.inc | $(BUILD)
	$(CC) $(KEM_CFLAGS) -DGT_HAVE_AVX2_ASM=1 -ffunction-sections \
		-fdata-sections -Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		$(M_BASEINV_UNIFICATION_GT) bench/bench_m_baseinv_unification.c

m-baseinv-unification-check: m-baseinv-unification-generate \
		$(BUILD)/bench_m_baseinv_unification
	$(BUILD)/bench_m_baseinv_unification 1000 m4 control
	$(BUILD)/bench_m_baseinv_unification 1000 m4 candidate

bench-m-baseinv-unification-pmu: m-baseinv-unification-check \
		$(BUILD)/bench_m_baseinv_unification_reversed
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_m_baseinv_unification \
		--reversed-binary $(BUILD)/bench_m_baseinv_unification_reversed \
		--iterations 10000 --repeats 20 \
		--control-backend control --gt-backend candidate \
		--gates m1,m2,m3,mpack,m4 \
		--experiment GT32-M-BASEINV-UNIFICATION-EXEC-001 \
		--output results/tile4-m-baseinv-unification-pmu.json
	$(PYTHON) tools/summarize_m_baseinv_unification.py

N5_PM_SUFFIX_SOURCES := src/tile4_asm.S \
		src/tile4_permutation_relaxed_asm.S src/tile4_global_physical_asm.S

$(BUILD)/bench_n5_pm_progressive_suffix: \
		bench/bench_n5_pm_progressive_suffix.c $(N5_PM_SUFFIX_SOURCES) \
		$(GEN) $(FWD_LANDING_BASEINV_ARTIFACTS) \
		$(N5_PM_PROGRESSIVE_SUFFIX_GATE) \
		$(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		bench/bench_n5_pm_progressive_suffix.c $(N5_PM_SUFFIX_SOURCES)

$(BUILD)/bench_n5_pm_progressive_suffix_reversed: \
		bench/bench_n5_pm_progressive_suffix.c $(N5_PM_SUFFIX_SOURCES) \
		$(GEN) $(FWD_LANDING_BASEINV_ARTIFACTS) \
		$(N5_PM_PROGRESSIVE_SUFFIX_GATE) \
		$(GT32_GLOBAL_PHYSICAL_ASM_ARTIFACTS) | $(BUILD)
	$(CC) $(KEM_CFLAGS) -Werror -ffunction-sections -fdata-sections \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		$(N5_PM_SUFFIX_SOURCES) bench/bench_n5_pm_progressive_suffix.c

n5-pm-progressive-suffix-check: n5-pm-progressive-suffix-generate \
		$(BUILD)/bench_n5_pm_progressive_suffix
	$(BUILD)/bench_n5_pm_progressive_suffix 1000 weighted control
	$(BUILD)/bench_n5_pm_progressive_suffix 1000 weighted candidate

bench-n5-pm-progressive-suffix-pmu: n5-pm-progressive-suffix-check \
		$(BUILD)/bench_n5_pm_progressive_suffix_reversed \
		$(BUILD)/bench_m_baseinv_unification \
		$(BUILD)/bench_m_baseinv_unification_reversed
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_n5_pm_progressive_suffix \
		--reversed-binary $(BUILD)/bench_n5_pm_progressive_suffix_reversed \
		--iterations 10000 --repeats 20 \
		--control-backend control --gt-backend candidate \
		--gates p,m,weighted \
		--experiment N5-P-M-PROGRESSIVE-SUFFIX-EXEC-001 \
		--output results/tile4-n5-pm-progressive-suffix-pmu.json
	$(PYTHON) tools/run_keygen_soa_island.py \
		$(BUILD)/bench_m_baseinv_unification \
		--reversed-binary $(BUILD)/bench_m_baseinv_unification_reversed \
		--iterations 10000 --repeats 20 \
		--control-backend control --gt-backend candidate \
		--gates p_suffix_k3k5 \
		--experiment N5-P-S5-SUFFIX-K3-K5-001 \
		--output results/tile4-n5-p-s5-suffix-k3k5-pmu.json
	$(PYTHON) tools/summarize_n5_pm_progressive_suffix.py

vpblendd-crosslane-generate:
	$(PYTHON) tools/generate_vpblendd_crosslane_gate.py

inverse-s2-s3-pairpacked-generate:
	$(PYTHON) tools/generate_inverse_s2_s3_pairpacked_gate.py

inverse-s1-s3-joint-physical-generate:
	$(PYTHON) tools/generate_inverse_s1_s3_joint_physical_gate.py

inverse-s1-s5-free-terminal-generate:
	$(PYTHON) tools/generate_inverse_s1_s5_free_terminal_gate.py

$(BUILD)/bench_mtl_shuffle_class: bench/bench_mtl_shuffle_class.c bench/bench_mtl_shuffle_class.S | $(BUILD)
	$(CC) -O3 -mavx2 -Wall -Wextra -Werror -o $@ $^

$(BUILD)/bench_mtl_shuffle_class_reversed: bench/bench_mtl_shuffle_class.c bench/bench_mtl_shuffle_class.S | $(BUILD)
	$(CC) -O3 -mavx2 -Wall -Wextra -Werror -o $@ bench/bench_mtl_shuffle_class.S bench/bench_mtl_shuffle_class.c

bench-mtl-shuffle-class: $(BUILD)/bench_mtl_shuffle_class $(BUILD)/bench_mtl_shuffle_class_reversed
	$(PYTHON) tools/run_mtl_shuffle_class_cost.py $^ --output results/tile4-mtl-shuffle-mix-cost.json

crt-twist-coordinate-generate:
	$(PYTHON) tools/generate_gt32_crt_twist_coordinate_gate.py

geometric-twist-stage-gauge-generate:
	$(PYTHON) tools/generate_gt32_geometric_twist_stage_gauge_gate.py

shifted-dft3-two-chain-generate:
	$(PYTHON) tools/generate_gt32_shifted_dft3_two_chain_gate.py

.PHONY: encap-wire-generate encap-wire-short
encap-wire-generate:
	$(PYTHON) tools/generate_encap_wire_schedule.py
	$(PYTHON) tools/generate_encap_wire_asm.py

encap-wire-short:
	$(PYTHON) tools/run_encap_wire_short.py --supercop-root "$(SUPERCOP_ROOT)" --cpu "$(or $(BENCH_CPU),1)" --tag "$(RESULT_TAG)"

WIRE_CLEAN := ../../clean/avx2-gt32-clean
WIRE_KEM_C := keygen.c encap.c decap.c poly.c symmetric.c fips202.c baseinv.c consts.c
WIRE_KEM_ASM := KeccakP-1600-AVX2.s cbd.s crepmod3.s add.s ntt.s ntt_m.s ntt_p.s invntt.s basemul.s batch_inverse.s pack.s
WIRE_KEM_SOURCES := $(addprefix $(WIRE_CLEAN)/,$(WIRE_KEM_C) $(WIRE_KEM_ASM))

$(BUILD)/test_encap_wire_kem: tests/test_encap_wire_kem.c src/encap_wire_research.c \
		generated/encap_wire_forward.S generated/encap_wire_codec.S \
		generated/encap_wire_muladd.S $(WIRE_KEM_SOURCES) \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c | $(BUILD)
	$(CC) $(KEM_CFLAGS) -fwrapv -fno-strict-aliasing -I$(WIRE_CLEAN) -I$(OFFICIAL) \
		-o $@ tests/test_encap_wire_kem.c src/encap_wire_research.c \
		generated/encap_wire_forward.S generated/encap_wire_codec.S \
		generated/encap_wire_muladd.S $(WIRE_KEM_SOURCES) \
		$(OFFICIAL)/kat/aes.c $(OFFICIAL)/kat/rng.c

.PHONY: encap-wire-kem-check
encap-wire-kem-check: $(BUILD)/test_encap_wire_kem
	$(BUILD)/test_encap_wire_kem

clean:
	$(RM) -r $(BUILD) __pycache__ tools/__pycache__
