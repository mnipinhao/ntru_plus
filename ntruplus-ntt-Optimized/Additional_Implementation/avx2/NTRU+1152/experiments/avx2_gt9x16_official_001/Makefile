PARAMETER := 1152
REPO_ROOT := $(shell git rev-parse --show-toplevel)
EXPERIMENT := $(CURDIR)
PYTHON ?= python3
CC ?= cc
BENCH_CPU ?= 1
SUPERCOP_IMPLEMENTATION ?= avx2-gt9x16-exp001
RESULT_TAG ?= $(shell date +%Y%m%d-%H%M%S)
SUPERCOP_FRESH_LAUNCHES_SHORT ?= 3
SUPERCOP_FRESH_LAUNCHES_SERIOUS ?= 9
RESULTS := $(EXPERIMENT)/results/$(RESULT_TAG)
COMMON_GENERATOR := $(REPO_ROOT)/ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/gt9x16/generate_gt9x16.py
COMPILER_ARG := $(if $(SUPERCOP_COMPILER_WRAPPER),--compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER),)
BUILD := $(EXPERIMENT)/build
CPPFLAGS_LOCAL := -Isrc -Iref -Igenerated
CFLAGS_STRICT := -std=c11 -mavx2 -Wall -Wextra -Wpedantic -Werror
SHEAR_SOURCES := src/gt9x16_shear.c ref/gt9x16_oracle.c
SHEAR_HEADERS := src/gt9x16_shear.h ref/gt9x16_oracle.h
UPSTREAM := upstream/supercop-avx2
OFFICIAL_FORWARD := $(UPSTREAM)/consts.c $(UPSTREAM)/ntt.s
FULL_SOURCES := src/gt9x16_shear.c src/top_split_adapter.c src/gt9x16_forward.c ref/ntt9_reference.c
FULL_HEADERS := src/gt9x16_shear.h src/gt9x16_forward.h ref/ntt9_reference.h generated/gt9x16-full-forward-tables.h
FULL_CPPFLAGS := $(CPPFLAGS_LOCAL) -I$(UPSTREAM)
PAIRED_CFLAGS := $(CFLAGS_STRICT) -O3
NTT16_ASM := asm/gt9x16_ntt16.S
NTT16_HEADERS := src/gt9x16_ntt16_asm.h generated/gt9x16-ntt16-constants.inc generated/gt9x16-paper-adjusted-ntt16-constants.inc
OFFICIAL_PARTITIONS := generated/official-ntt-stage-partitions.s
OFFICIAL_PARTITION_HEADERS := src/official_stage_partitions.h
G0_CONTROL_RESULT := results/f-r3d-intel155h-20260821-001/paper-pipeline-paired.json
G0_GENERATOR_ARGS := --component-oracle generated/gt9x16-component-oracle.json --pipeline-layout generated/gt9x16-pipeline-layout.json --cost-matrix generated/gt9x16-representation-cost-matrix.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --control-result $(G0_CONTROL_RESULT) --graph-output generated/g0-consumer-graph.json --views-output generated/g0-representation-views.json
G1B_RESULT := results/g1b-intel155h-20260821-001/g1b-f1-paired.json
G1_GENERATOR_ARGS := --pipeline-layout generated/gt9x16-pipeline-layout.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --g0-views generated/g0-representation-views.json --g1b-result $(G1B_RESULT) --oracle-output generated/g1-edge-oracles.json --debt-output generated/g1-edge-debt-matrix.json
G1C_AUDIT_ARGS := --basemul $(UPSTREAM)/basemul.s --invntt $(UPSTREAM)/invntt.s --baseinv $(UPSTREAM)/baseinv.s --poly $(UPSTREAM)/poly.c --edge-oracle generated/g1-edge-oracles.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --output generated/g1c-inverse-sink-audit.json
G1C_HEAD_ARGS := --pipeline-layout generated/gt9x16-pipeline-layout.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --g1c-audit generated/g1c-inverse-sink-audit.json --output generated/g1c-adjusted-inverse-head.json --header generated/g1c-adjusted-inverse-head.h --asm-constants generated/g1c-adjusted-inverse-head.inc
G1C_LIVE_ARGS := --basemul-source $(UPSTREAM)/basemul.s --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --inverse-head-oracle generated/g1c-adjusted-inverse-head.json --pipeline-layout generated/gt9x16-pipeline-layout.json --output generated/g1c-bmscale-live-tail-contract.json --header generated/g1c-bmscale-live-tail.h --asm-constants generated/g1c-bmscale-live-tail.inc
G1C_LINKED_ASM := asm/g1c_bmscale_inverse_d1.S
G1C_LINKED_AUDIT_ARGS := --object $(BUILD)/g1c/g1c-bmscale-inverse-d1.o --source $(G1C_LINKED_ASM) --contract generated/g1c-bmscale-live-tail-contract.json --output generated/g1c-linked-bmscale-inverse-d1-audit.json --compiler $(CC) --cflags=-mavx2
G1C_M2_ARGS := --source $(G1C_LINKED_ASM) --contract generated/g1c-bmscale-live-tail-contract.json --inverse-head generated/g1c-adjusted-inverse-head.json --output generated/g1c-m2-live-basis.json
G1C_M2_RESULT := results/g1c-m2-intel155h-20260821-001/g1c-m2-paired.json
G1C_M3_ARGS := --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --m2-result $(G1C_M2_RESULT) --output generated/g1c-m3-inverse16-oracle.json --header generated/g1c-m3-inverse16.h --asm-constants generated/g1c-m3-inverse16.inc
G1C_M3B_RESULT := results/g1c-m3b-producer-range-20260822-001/correlated-range.json
G1C_M3B_ARGS := --m3-oracle generated/g1c-m3-inverse16-oracle.json --observation $(G1C_M3B_RESULT) --output generated/g1c-m3b-provenance.json
G1C_M3C0_ARGS := --m3-oracle generated/g1c-m3-inverse16-oracle.json --m3b-observation $(G1C_M3B_RESULT) --output generated/g1c-m3c0-orientation-search.json
G1C_M3C2_RESULT := results/g1c-m3c2-repair-20260823-001/repair-observation.json
G1C_M3C2_ARGS := --observation $(G1C_M3C2_RESULT) --m3c0-oracle generated/g1c-m3c0-orientation-search.json --output generated/g1c-m3c2-repair-plan.json
G1C_M3C2P_ARGS := --repair-plan generated/g1c-m3c2-repair-plan.json --m3-oracle generated/g1c-m3-inverse16-oracle.json --output generated/g1c-m3c2p-exact-proof.json
G1C_M3C3_ASM := asm/g1c_m3c3_reduction.S
G1C_M3C3_AUDIT_ARGS := --object $(BUILD)/g1c/g1c-m3c3-reduction.o --source $(G1C_M3C3_ASM) --proof generated/g1c-m3c2p-exact-proof.json --output generated/g1c-m3c3-reduction-audit.json --compiler $(CC) --cflags=-mavx2
G1C_M3C3_RESULT := results/g1c-m3c3-reduction-intel155h-20260823-001/reduction-paired.json
G1C_M3_FULL_PROOF_ARGS := --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --m3c2p-proof generated/g1c-m3c2p-exact-proof.json --output generated/g1c-m3-full-path-proof.json
G1C_M3_FULL_AUDIT_ARGS := --object $(BUILD)/g1c/g1c-bmscale-inverse-d1.o --source $(G1C_LINKED_ASM) --proof generated/g1c-m3-full-path-proof.json --output generated/g1c-m3-full-inverse16-audit.json --compiler $(CC) --cflags=-mavx2
G1C_M3_FULL_RESULT := results/g1c-m3-full-intel155h-20260824-001/full-paired.json
HWA_A0_ARGS := --layout generated/gt9x16-pipeline-layout.json --views generated/g0-representation-views.json --g1b-result $(G1B_RESULT) --m3-result $(G1C_M3_FULL_RESULT) --m3-audit generated/g1c-m3-full-inverse16-audit.json --producer-source bench/g1c_m3_producer_common.h --output generated/hwa-compatibility-audit.json
INVERSE_TAIL_MAP_ARGS := --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --ntt9-oracle generated/gt9x16-ntt9-first-oracle.json --full-proof generated/g1c-m3-full-path-proof.json --m3-audit generated/g1c-m3-full-inverse16-audit.json --asm-source $(G1C_LINKED_ASM) --output generated/g1c-inverse-tail-consumer-map.json --header generated/g1c-inverse-tail-map.h
INVERSE_NTT9_REF := ref/inverse_ntt9_reference.c
INVERSE_NTT9_AUDIT_ARGS := --object $(BUILD)/g1c/inverse-ntt9-reference.o --source $(INVERSE_NTT9_REF) --map generated/g1c-inverse-tail-consumer-map.json --compiler $(CC) --cflags="$(PAIRED_CFLAGS)"
INVERSE_TAIL_RESULT := results/inverse-tail-reference-intel155h-20260824-001/paired.json
INVERSE_NTT9_B0_ASM := asm/inverse_ntt9_b0.S
INVERSE_NTT9_B0_GENERATOR_ARGS := --output generated/g1c-inverse-ntt9-b0-range.json --asm-constants generated/g1c-inverse-ntt9-b0-constants.inc
INVERSE_NTT9_B0_AUDIT_ARGS := --object $(BUILD)/g1c/inverse-ntt9-b0.o --source $(INVERSE_NTT9_B0_ASM) --proof generated/g1c-inverse-ntt9-b0-range.json --output generated/g1c-inverse-ntt9-b0-audit.json --compiler $(CC) --cflags=-mavx2
INVERSE_NTT9_B1P_ARGS := --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --tail-map generated/g1c-inverse-tail-consumer-map.json --output generated/g1c-inverse-ntt9-b1p.json
INVERSE_NTT9_B1R_ARGS := --b1p generated/g1c-inverse-ntt9-b1p.json --b0-proof generated/g1c-inverse-ntt9-b0-range.json --output generated/g1c-inverse-ntt9-b1r.json
INVERSE_NTT9_B1_ASM := asm/inverse_ntt9_b1.S
INVERSE_NTT9_B1_AUDIT_ARGS := --object $(BUILD)/g1c/inverse-ntt9-b1.o --source $(INVERSE_NTT9_B1_ASM) --proof generated/g1c-inverse-ntt9-b1r.json --b0-audit generated/g1c-inverse-ntt9-b0-audit.json --output generated/g1c-inverse-ntt9-b1-audit.json --compiler $(CC) --cflags=-mavx2
INVERSE_TAIL_D0_ASM := asm/inverse_tail_d0.S
INVERSE_TAIL_D0_PROOF_ARGS := --m3-proof generated/g1c-m3-full-path-proof.json --b1r-proof generated/g1c-inverse-ntt9-b1r.json --output generated/g1c-inverse-tail-d0-proof.json
INVERSE_TAIL_D0_M2_PROOF_ARGS := --m3-proof generated/g1c-m3-full-path-proof.json --b1r-proof generated/g1c-inverse-ntt9-b1r.json --schedule late --output generated/g1c-inverse-tail-d0-m2-proof.json
INVERSE_TAIL_D0_AUDIT_ARGS := --object $(BUILD)/g1c/inverse-tail-d0.o --source $(INVERSE_TAIL_D0_ASM) --proof generated/g1c-inverse-tail-d0-proof.json --m2-proof generated/g1c-inverse-tail-d0-m2-proof.json --output generated/g1c-inverse-tail-d0-audit.json --compiler $(CC) --cflags=-mavx2
F0_MA_MAP_ARGS := --pipeline-layout generated/gt9x16-pipeline-layout.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --range-proof generated/gt9x16-ntt9-paper-range.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --kem-source $(UPSTREAM)/kem.c --basemul-source $(UPSTREAM)/basemul.s --add-source $(UPSTREAM)/add.s --pack-source $(UPSTREAM)/pack.s --map-output generated/f0-ma-consumer-map.json --synthesis-output generated/f0-ma-symbolic-synthesis.json
F0_MA_SCHED_ARGS := --consumer-map generated/f0-ma-consumer-map.json --synthesis generated/f0-ma-symbolic-synthesis.json --poly-header $(UPSTREAM)/poly.h --pack-source $(UPSTREAM)/pack.s --basemul-source $(UPSTREAM)/basemul.s --output generated/f0-ma-schedule.json
F0_MA1_ASM := asm/f0_ma1_asm0.S
F0_MA1_GENERATOR_ARGS := --schedule generated/f0-ma-schedule.json --json generated/f0-ma1-asm0.json --asm-constants generated/f0-ma1-asm0-constants.inc --header generated/f0-ma1-asm0.h
F0_MA1_AUDIT_ARGS := --object $(BUILD)/f0ma1/f0-ma1-asm0.o --elf $(BUILD)/f0ma1/test-f0-ma1-asm0 --source $(F0_MA1_ASM) --contract generated/f0-ma1-asm0.json --output generated/f0-ma1-asm0-audit.json
F0_MA1_ASM1 := asm/f0_ma1_asm1.S
F0_MA1_ASM1_GENERATOR_ARGS := --schedule generated/f0-ma-schedule.json --asm $(F0_MA1_ASM1) --constants generated/f0-ma1-asm1-constants.inc --header generated/f0-ma1-asm1.h --oracle-header generated/f0-ma1-asm1-oracle.h --contract generated/f0-ma1-asm1.json
F0_MA1_ASM1_AUDIT_ARGS := --object $(BUILD)/f0ma1/f0-ma1-asm1.o --elf $(BUILD)/f0ma1/test-f0-ma1-asm1 --source $(F0_MA1_ASM1) --contract generated/f0-ma1-asm1.json --output generated/f0-ma1-asm1-audit.json
F0_MA0_ADAPTER := asm/f0_ma0_adapter.S
F0_MA0_GENERATOR_ARGS := --schedule generated/f0-ma-schedule.json --asm $(F0_MA0_ADAPTER) --constants generated/f0-ma0-adapter-constants.inc --header generated/f0-ma0-adapter.h --contract generated/f0-ma0-adapter.json
F0_MA0_AUDIT_ARGS := --object $(BUILD)/f0ma1/f0-ma0-adapter.o --elf $(BUILD)/f0ma1/test-f0-ma1-asm1 --source $(F0_MA0_ADAPTER) --contract generated/f0-ma0-adapter.json --output generated/f0-ma0-adapter-audit.json
F0_MA0_SOURCES := $(F0_MA0_ADAPTER) src/f0_ma0_control.c $(UPSTREAM)/basemul.s $(UPSTREAM)/add.s
F0_MA1_ASM1_TEST_SOURCES := $(F0_MA0_SOURCES) $(F0_MA1_ASM1) $(UPSTREAM)/consts.c $(UPSTREAM)/pack.s tests/test_f0_ma1_asm1.c
F0_MA1_ASM1_LINK_FLAGS := -Wl,-x
F0_MA3_ASM := asm/f0_ma3.S
F0_MA3_GENERATOR_ARGS := --schedule generated/f0-ma-schedule.json --asm $(F0_MA3_ASM) --constants generated/f0-ma3-constants.inc --header generated/f0-ma3-asm.h --contract generated/f0-ma3-asm.json
F0_MA3_RANGE_ARGS := --schedule generated/f0-ma-schedule.json --output generated/f0-ma3-final-range.json
F0_MA3_AUDIT_ARGS := --object $(BUILD)/f0ma1/f0-ma3.o --elf $(BUILD)/f0ma1/test-f0-ma3 --source $(F0_MA3_ASM) --contract generated/f0-ma3-asm.json --range-proof generated/f0-ma3-final-range.json --output generated/f0-ma3-audit.json
F0_MA3_TEST_SOURCES := $(F0_MA0_SOURCES) $(F0_MA1_ASM1) $(F0_MA3_ASM) $(UPSTREAM)/consts.c $(UPSTREAM)/pack.s tests/test_f0_ma1_asm1.c
F0_MA2_ASM := asm/f0_ma2.S
F0_MA2_GENERATOR_ARGS := --schedule generated/f0-ma-schedule.json --range-proof generated/f0-ma2-range.json --asm $(F0_MA2_ASM) --constants generated/f0-ma2-constants.inc --header generated/f0-ma2-asm.h --contract generated/f0-ma2-asm.json
F0_MA2_RANGE_ARGS := --schedule generated/f0-ma-schedule.json --output generated/f0-ma2-range.json
F0_MA2_AUDIT_ARGS := --object $(BUILD)/f0ma1/f0-ma2.o --elf $(BUILD)/f0ma1/test-f0-ma2 --source $(F0_MA2_ASM) --contract generated/f0-ma2-asm.json --range-proof generated/f0-ma2-range.json --output generated/f0-ma2-audit.json
F0_MA2_TEST_SOURCES := $(F0_MA2_ASM) $(UPSTREAM)/consts.c $(UPSTREAM)/pack.s tests/test_f0_ma2.c
F0_MA2_KEM_ADAPTER := asm/f0_official_to_f0.S
F0_MA2_KEM_ADAPTER_ARGS := --schedule generated/f0-ma-schedule.json --asm $(F0_MA2_KEM_ADAPTER) --constants generated/f0-official-to-f0-constants.inc --header generated/f0-official-to-f0.h --contract generated/f0-official-to-f0.json
F0_MA2_KEM_ARGS := --upstream $(UPSTREAM)/kem.c --output src/kem.c
F0_PROD0_CONTRACT_ARGS := --map generated/f0-ma-consumer-map.json --range-proof generated/gt9x16-ntt9-paper-range.json --kem-source $(UPSTREAM)/kem.c --cbd-source $(UPSTREAM)/cbd.s --producer-source src/f0_forward_for_ma2.c --json generated/f0-prod0-contract.json --header generated/f0-prod0-ranges.h
F0_PROD0_AUDIT_ARGS := --object $(BUILD)/f0prod0/f0-forward-for-ma2.o --source src/f0_forward_for_ma2.c --contract generated/f0-prod0-contract.json --output generated/f0-prod0-audit.json
F0_PROD0_TEST_SOURCES := src/f0_forward_for_ma2.c src/top_split_adapter.c $(NTT16_ASM) $(F0_MA2_KEM_ADAPTER) $(OFFICIAL_FORWARD) tests/test_f0_prod0.c
F0_PROD1_SCHED_ARGS := --tables generated/gt9x16-full-forward-tables.h --map generated/f0-ma-consumer-map.json --prod0-contract generated/f0-prod0-contract.json --paper-range generated/gt9x16-ntt9-paper-range.json --ma2-range generated/f0-ma2-range.json --ntt9-macro asm/gt9x16_ntt9_paper.inc --ntt16-macro asm/gt9x16_ntt16_paper.inc --output generated/f0-prod1-schedule.json --asm-constants generated/f0-prod1-constants.inc
F0_PROD1_ASM := asm/f0_prod1_p1h.S
F0_PROD1_TEST_SOURCES := src/f0_forward_for_ma2.c src/f0_prod1_wrapper.c src/top_split_adapter.c $(F0_PROD1_ASM) $(NTT16_ASM) $(F0_MA2_KEM_ADAPTER) $(OFFICIAL_FORWARD) tests/test_f0_prod1_p1h.c
F0_PROD1_AUDIT_ARGS := --wrapper-object $(BUILD)/f0prod1/f0-prod1-p1h-wrapper.o --helper-object $(BUILD)/f0prod1/f0-prod1-p1h.o --wrapper-source src/f0_prod1_wrapper.c --helper-source $(F0_PROD1_ASM) --schedule generated/f0-prod1-schedule.json --output generated/f0-prod1-p1h-audit.json
F0_PROD2_MAP_ARGS := --consumer-map generated/f0-ma-consumer-map.json --ma2-schedule generated/f0-ma-schedule.json --prod1-schedule generated/f0-prod1-schedule.json --ma2-contract generated/f0-ma2-asm.json --ma2-audit generated/f0-ma2-audit.json --ma2-asm $(F0_MA2_ASM) --output generated/f0-prod2-ma2-map.json
F0_PROD2_ASM := asm/f0_prod2_ma2_p2b.S
F0_PROD2_PROJECTION_ASM := asm/f0_generic_to_ma2_planes.S
F0_PROD2_GENERATOR_ARGS := --p1h-source $(F0_PROD1_ASM) --map generated/f0-prod2-ma2-map.json --asm $(F0_PROD2_ASM) --header generated/f0-prod2-ma2-asm.h --contract generated/f0-prod2-ma2-asm.json
F0_PROD2_TEST_SOURCES := src/f0_prod1_wrapper.c src/f0_prod2_ma2_wrapper.c src/top_split_adapter.c $(F0_PROD1_ASM) $(F0_PROD2_ASM) $(F0_PROD2_PROJECTION_ASM) $(F0_MA2_ASM) tests/test_f0_prod2_ma2_asm0.c
F0_PROD2_AUDIT_ARGS := --wrapper-object $(BUILD)/f0prod2/f0-prod2-wrapper.o --helper-object $(BUILD)/f0prod2/f0-prod2-p2b.o --ma2-object $(BUILD)/f0prod2/f0-ma2.o --wrapper-source src/f0_prod2_ma2_wrapper.c --helper-source $(F0_PROD2_ASM) --ma2-source $(F0_MA2_ASM) --contract generated/f0-prod2-ma2-asm.json --map generated/f0-prod2-ma2-map.json --prod1-audit generated/f0-prod1-p1h-audit.json --output generated/f0-prod2-ma2-audit.json
F0_PROD2_BOUNDARY_AUDIT_ARGS := --projection-object $(BUILD)/f0prod2/f0-generic-to-ma2-planes.o --projection-source $(F0_PROD2_PROJECTION_ASM) --prod1-audit generated/f0-prod1-p1h-audit.json --prod2-audit generated/f0-prod2-ma2-audit.json --output generated/f0-prod2-boundary-audit.json
GT9X16_PROD3_MAP_ARGS := --component-oracle generated/gt9x16-component-oracle.json --ntt9-first-oracle generated/gt9x16-ntt9-first-oracle.json --prod1-schedule generated/f0-prod1-schedule.json --prod2-map generated/f0-prod2-ma2-map.json --output generated/gt9x16-prod3-map.json
GT9X16_PROD3_AOS_SCHED_ARGS := --prod3-map generated/gt9x16-prod3-map.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --paper-range generated/gt9x16-ntt9-paper-range.json --ntt9-macro asm/gt9x16_ntt9_paper.inc --ntt16-macro asm/gt9x16_ntt16_paper.inc --prod2-audit generated/f0-prod2-ma2-audit.json --output generated/gt9x16-prod3-aos-schedule.json --asm-constants generated/gt9x16-prod3-aos-tile-constants.inc
GT9X16_PROD3_AOS_TILE_ASM := asm/gt9x16_prod3_aos_c1_tile.S
GT9X16_PROD3_AOS_TILE_AUDIT_ARGS := --object $(BUILD)/prod3/gt9x16-prod3-aos-c1-tile.o --source $(GT9X16_PROD3_AOS_TILE_ASM) --constants generated/gt9x16-prod3-aos-tile-constants.inc --schedule generated/gt9x16-prod3-aos-schedule.json --output generated/gt9x16-prod3-aos-c1-tile-audit.json
GT9X16_PROD3_AOS_BRANCH_ASM := asm/gt9x16_prod3_aos_branch0.S
GT9X16_PROD3_AOS_BRANCH_ARGS := --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --paper-range generated/gt9x16-ntt9-paper-range.json --twist-constants generated/f0-prod1-constants.inc --schedule generated/gt9x16-prod3-aos-schedule.json --output generated/gt9x16-prod3-aos-branch0.json --asm-constants generated/gt9x16-prod3-aos-branch0-constants.inc
GT9X16_PROD3_AOS_BRANCH_AUDIT_ARGS := --object $(BUILD)/prod3/gt9x16-prod3-aos-branch0.o --source $(GT9X16_PROD3_AOS_BRANCH_ASM) --constants generated/gt9x16-prod3-aos-branch0-constants.inc --proof generated/gt9x16-prod3-aos-branch0.json --output generated/gt9x16-prod3-aos-branch0-audit.json
GT9X16_PROD3_AOS_BRANCH_TEST_SOURCES := src/top_split_adapter.c $(F0_PROD2_ASM) $(GT9X16_PROD3_AOS_BRANCH_ASM) tests/test_gt9x16_prod3_aos_branch0.c
GT9X16_PROD3_AOS_FULL_ARGS := --branch-proof generated/gt9x16-prod3-aos-branch0.json --branch1-constants generated/gt9x16-prod3-aos-branch1-constants.inc --output generated/gt9x16-prod3-aos-full.json
GT9X16_PROD3_AOS_FULL_AUDIT_ARGS := --candidate-object $(BUILD)/prod3/gt9x16-prod3-aos-full.o --control-object $(BUILD)/prod3/f0-prod2-p2b.o --source $(GT9X16_PROD3_AOS_BRANCH_ASM) --proof generated/gt9x16-prod3-aos-full.json --output generated/gt9x16-prod3-aos-full-audit.json
GT9X16_PROD3_AOS_FULL_TEST_SOURCES := src/top_split_adapter.c $(F0_PROD2_ASM) $(GT9X16_PROD3_AOS_BRANCH_ASM) tests/test_gt9x16_prod3_aos_full.c
GT9X16_PROD3_AOS_PRICE_ASM := asm/gt9x16_prod3_aos_full_price.S
GT9X16_PROD3_AOS_CONSUMER_TEST_SOURCES := src/top_split_adapter.c $(F0_PROD2_ASM) $(F0_MA2_ASM) $(GT9X16_PROD3_AOS_PRICE_ASM) tests/test_gt9x16_prod3_aos_consumer.c
GT9X16_PROD3_HASH_UNPROJECT_ASM := asm/f0_ma2_planes_to_generic.S
GT9X16_PROD3_HASH_TEST_SOURCES := src/top_split_adapter.c $(GT9X16_PROD3_AOS_BRANCH_ASM) $(GT9X16_PROD3_HASH_UNPROJECT_ASM) $(F0_MA0_ADAPTER) src/f0_prod3_hash_bridge.c $(OFFICIAL_FORWARD) $(UPSTREAM)/pack.s tests/test_f0_prod3_hash_bridge.c
GT9X16_PROD3_HASH_FANOUT_TEST_SOURCES := src/top_split_adapter.c $(GT9X16_PROD3_AOS_PRICE_ASM) $(GT9X16_PROD3_HASH_UNPROJECT_ASM) $(F0_MA0_ADAPTER) src/f0_prod3_hash_bridge.c src/gt9x16_prod3_hash_fanout.c $(OFFICIAL_FORWARD) $(UPSTREAM)/pack.s tests/test_gt9x16_prod3_hash_fanout.c
GT9X16_PROD3_HASH_PACK_LAYOUT := generated/official-pack-layout.json
GT9X16_PROD3_HASH_DIRECT_MAP_ARGS := --prod2-map generated/f0-prod2-ma2-map.json --consumer-map generated/f0-ma-consumer-map.json --ma0-contract generated/f0-ma0-adapter.json --pack-source $(UPSTREAM)/pack.s --pack-layout $(GT9X16_PROD3_HASH_PACK_LAYOUT) --output generated/gt9x16-prod3-ma2-hash-direct-map.json
GT9X16_PROD3_HASH_DIRECT_SCHED_ARGS := --direct-map generated/gt9x16-prod3-ma2-hash-direct-map.json --output generated/gt9x16-prod3-ma2-hash-direct-schedule.json
GT9X16_PROD3_QORDER_CODESIGN_ARGS := --prod3-schedule generated/gt9x16-prod3-aos-schedule.json --ma-schedule generated/f0-ma-schedule.json --ma2-audit generated/f0-ma2-audit.json --direct-map generated/gt9x16-prod3-ma2-hash-direct-map.json --hash-schedule generated/gt9x16-prod3-ma2-hash-direct-schedule.json --output generated/gt9x16-prod3-ma2-qorder-codesign.json
GT9X16_PROD3_QORDER_NATURAL_SCHED_ARGS := --codesign generated/gt9x16-prod3-ma2-qorder-codesign.json --ma-schedule generated/f0-ma-schedule.json --ma2-audit generated/f0-ma2-audit.json --direct-map generated/gt9x16-prod3-ma2-hash-direct-map.json --hash-schedule generated/gt9x16-prod3-ma2-hash-direct-schedule.json --output generated/gt9x16-prod3-ma2-qorder-natural-schedule.json
GT9X16_PROD3_QORDER_NATURAL_ASM := asm/gt9x16_prod3_ma2_qorder_natural.S
GT9X16_PROD3_QORDER_NATURAL_PRODUCER := asm/gt9x16_prod3_aos_natural.S
GT9X16_PROD3_QORDER_NATURAL_ASM_ARGS := --ma-schedule generated/f0-ma-schedule.json --natural-schedule generated/gt9x16-prod3-ma2-qorder-natural-schedule.json --asm $(GT9X16_PROD3_QORDER_NATURAL_ASM) --constants generated/gt9x16-prod3-ma2-qorder-natural-constants.inc --header generated/gt9x16-prod3-ma2-qorder-natural-asm.h --contract generated/gt9x16-prod3-ma2-qorder-natural-asm.json
GT9X16_PROD3_QORDER_NATURAL_TEST_SOURCES = src/top_split_adapter.c $(GT9X16_PROD3_AOS_BRANCH_ASM) $(GT9X16_PROD3_QORDER_NATURAL_PRODUCER) $(GT9X16_PROD3_QORDER_NATURAL_ASM) $(GT9X16_PROD3_HASH_H1_ASM) tests/test_gt9x16_prod3_ma2_qorder_natural_asm0.c
GT9X16_PROD3_QORDER_NATURAL_AUDIT_ARGS := --elf $(BUILD)/prod3/test-gt9x16-prod3-ma2-qorder-natural-asm0 --contract generated/gt9x16-prod3-ma2-qorder-natural-asm.json --constants generated/gt9x16-prod3-ma2-qorder-natural-constants.inc --output generated/gt9x16-prod3-ma2-qorder-natural-asm-audit.json
GT9X16_PROD3_T0_MAP_ARGS := --component-oracle generated/gt9x16-component-oracle.json --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --paper-range generated/gt9x16-ntt9-paper-range.json --prod3-schedule generated/gt9x16-prod3-aos-schedule.json --natural-schedule generated/gt9x16-prod3-ma2-qorder-natural-schedule.json --qorder-price results/gt9x16-prod3-qorder-price-intel155h-20260827-001/summary.json --top-split-source src/top_split_adapter.c --output generated/gt9x16-prod3-natural-q-t0-absorption-map.json
GT9X16_PROD3_HASH_H1_ASM := asm/gt9x16_prod3_ma2_hash_h1.S
GT9X16_PROD3_HASH_H1_GENERATOR_ARGS := --schedule generated/gt9x16-prod3-ma2-hash-direct-schedule.json --direct-map generated/gt9x16-prod3-ma2-hash-direct-map.json --asm $(GT9X16_PROD3_HASH_H1_ASM) --constants generated/gt9x16-prod3-ma2-hash-h1-constants.json --header generated/gt9x16-prod3-ma2-hash-h1.h --map-header generated/gt9x16-prod3-ma2-hash-h1-map.h --contract generated/gt9x16-prod3-ma2-hash-h1-asm.json
GT9X16_PROD3_HASH_H1_TEST_SOURCES := src/top_split_adapter.c $(GT9X16_PROD3_AOS_BRANCH_ASM) $(GT9X16_PROD3_HASH_H1_ASM) $(OFFICIAL_FORWARD) $(UPSTREAM)/pack.s tests/test_gt9x16_prod3_ma2_hash_h1.c
GT9X16_PROD3_HASH_H1_AUDIT_ARGS := --object $(BUILD)/prod3/gt9x16-prod3-ma2-hash-h1.o --elf $(BUILD)/prod3/test-gt9x16-prod3-ma2-hash-h1 --source $(GT9X16_PROD3_HASH_H1_ASM) --constants generated/gt9x16-prod3-ma2-hash-h1-constants.json --contract generated/gt9x16-prod3-ma2-hash-h1-asm.json --output generated/gt9x16-prod3-ma2-hash-h1-audit.json

.PHONY: generate check sanitize audit bench-local bench-local-record bench-ntt16 bench-ntt16-record bench-c2 bench-c2-record bench-c3 bench-c3-record bench-c4 bench-c4-record bench-official-stages bench-official-stages-record bench-transform-paired bench-f-r3b bench-f-r3b-record bench-f-r3c bench-f-r3c-record bench-f-r3d bench-f-r3d-record bench-g1b bench-g1b-record bench-g1c-m2 bench-g1c-m2-record bench-g1c-m3b-range bench-g1c-m3b-range-record bench-g1c-m3c2-repair bench-g1c-m3c2-repair-record bench-g1c-m3c3-reduction bench-g1c-m3c3-reduction-record bench-g1c-m3-full bench-g1c-m3-full-record bench-inverse-tail bench-inverse-tail-record bench-inverse-ntt9-b0 bench-inverse-ntt9-b0-record \
 bench-transform-paired-record supercop-check supercop-install-candidate \
 supercop-kem-short supercop-kem-serious supercop-poly-short \
 supercop-poly-serious supercop-itail-short supercop-itail-serious \
 supercop-itail-d0-short supercop-itail-d0-serious \
 supercop-itail-d0-m2-short supercop-itail-d0-m2-serious \
 supercop-f0-ma1-short supercop-f0-ma1-serious \
 supercop-f0-ma1-ma0-short supercop-f0-ma1-ma0-serious \
 supercop-f0-ma3-short supercop-f0-ma3-serious \
 supercop-f0-ma2-chunk-short supercop-f0-ma2-chunk-serious \
 supercop-f0-ma2-short supercop-f0-ma2-serious \
 supercop-f0-prod1-short supercop-f0-prod1-serious \
 supercop-f0-prod2-short supercop-f0-prod2-serious \
 supercop-f0-prod2-consumer-short supercop-f0-prod2-consumer-serious \
 supercop-gt9x16-prod3-price supercop-gt9x16-prod3-consumer \
 supercop-gt9x16-prod3-hash-fanout supercop-gt9x16-prod3-hash-h1-price \
 supercop-gt9x16-prod3-qorder-price \
 gt9x16-prod3-h1-kat \
 supercop-paired-serious supercop-promotion-report

generate:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I$(UPSTREAM) tools/probe_official_layout.c $(OFFICIAL_FORWARD) -o $(BUILD)/probe-official-layout
	$(BUILD)/probe-official-layout generated/official-avx2-layout-probe.json
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json
	$(PYTHON) tools/generate_stage8_tables.py --json generated/gt9x16-stage8-tables.json --header generated/gt9x16-stage8-tables.h
	$(PYTHON) tools/generate_full_forward_tables.py --json generated/gt9x16-component-oracle.json --header generated/gt9x16-full-forward-tables.h --asm-constants generated/gt9x16-ntt16-constants.inc
	mkdir -p $(BUILD)/structure
	$(CC) -mavx2 -c $(UPSTREAM)/ntt.s -o $(BUILD)/structure/official-ntt.o
	$(CC) -mavx2 -c $(UPSTREAM)/basemul.s -o $(BUILD)/structure/official-basemul.o
	$(CC) -mavx2 -c $(UPSTREAM)/baseinv.s -o $(BUILD)/structure/official-baseinv.o
	$(CC) -mavx2 -c $(UPSTREAM)/invntt.s -o $(BUILD)/structure/official-invntt.o
	$(PYTHON) tools/audit_ntt_domain_lifecycle.py --ntt-object $(BUILD)/structure/official-ntt.o --basemul-object $(BUILD)/structure/official-basemul.o --baseinv-object $(BUILD)/structure/official-baseinv.o --invntt-object $(BUILD)/structure/official-invntt.o --upstream $(UPSTREAM) --output generated/ntt-domain-lifecycle-audit.json
	$(PYTHON) tools/generate_pipeline_layout.py --component-oracle generated/gt9x16-component-oracle.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --output generated/gt9x16-pipeline-layout.json --cost-output generated/gt9x16-representation-cost-matrix.json
	$(PYTHON) tools/generate_ntt9_first_oracle.py --component-oracle generated/gt9x16-component-oracle.json --output generated/gt9x16-ntt9-first-oracle.json
	$(PYTHON) tools/generate_scaled_r3r3_oracle.py --ntt9-first-oracle generated/gt9x16-ntt9-first-oracle.json --pipeline-layout generated/gt9x16-pipeline-layout.json --output generated/gt9x16-scaled-r3r3-oracle.json
	$(PYTHON) tools/generate_ntt9_paper_range.py --tables generated/gt9x16-full-forward-tables.h --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --json generated/gt9x16-ntt9-paper-range.json --header generated/gt9x16-ntt9-paper-range.h --asm-constants generated/gt9x16-paper-adjusted-ntt16-constants.inc
	$(PYTHON) tools/generate_official_stage_partitions.py --source $(UPSTREAM)/ntt.s --output $(OFFICIAL_PARTITIONS)
	$(PYTHON) tools/generate_g0_representation_views.py $(G0_GENERATOR_ARGS)
	$(PYTHON) tools/generate_g1_edge_oracles.py $(G1_GENERATOR_ARGS)
	$(PYTHON) tools/audit_g1c_inverse_sink.py $(G1C_AUDIT_ARGS)
	$(PYTHON) tools/generate_g1c_adjusted_inverse_head.py $(G1C_HEAD_ARGS)
	$(PYTHON) tools/generate_g1c_bmscale_live_tail_contract.py $(G1C_LIVE_ARGS)
	$(PYTHON) tools/generate_g1c_m2_live_basis.py $(G1C_M2_ARGS)
	$(PYTHON) tools/generate_g1c_m3_inverse16_oracle.py $(G1C_M3_ARGS)
	$(PYTHON) tools/generate_g1c_m3b_provenance.py $(G1C_M3B_ARGS)
	$(PYTHON) tools/generate_g1c_m3c0_orientation_search.py $(G1C_M3C0_ARGS)
	$(PYTHON) tools/generate_g1c_m3c2_repair_plan.py $(G1C_M3C2_ARGS)
	$(PYTHON) tools/generate_g1c_m3c2p_exact_proof.py $(G1C_M3C2P_ARGS)
	$(PYTHON) tools/generate_g1c_m3_full_path_proof.py $(G1C_M3_FULL_PROOF_ARGS)
	$(PYTHON) tools/generate_hwa_compatibility_audit.py $(HWA_A0_ARGS)
	$(PYTHON) tools/generate_inverse_tail_consumer_map.py $(INVERSE_TAIL_MAP_ARGS)
	$(PYTHON) tools/generate_inverse_ntt9_b0.py $(INVERSE_NTT9_B0_GENERATOR_ARGS)
	$(PYTHON) tools/generate_inverse_ntt9_b1p.py $(INVERSE_NTT9_B1P_ARGS)
	$(PYTHON) tools/generate_inverse_ntt9_b1r.py $(INVERSE_NTT9_B1R_ARGS)
	$(PYTHON) tools/generate_f0_ma_map.py $(F0_MA_MAP_ARGS)
	$(PYTHON) tools/generate_f0_ma_schedule.py $(F0_MA_SCHED_ARGS)
	$(PYTHON) tools/prove_f0_ma3_final_range.py $(F0_MA3_RANGE_ARGS)
	$(PYTHON) tools/generate_f0_ma3_asm.py $(F0_MA3_GENERATOR_ARGS)
	$(PYTHON) tools/generate_f0_ma1_asm0.py $(F0_MA1_GENERATOR_ARGS)
	mkdir -p $(BUILD)/f0ma1
	$(CC) -mavx2 -I. -c $(F0_MA1_ASM) -o $(BUILD)/f0ma1/f0-ma1-asm0.o
	$(CC) $(CFLAGS_STRICT) -O3 -Igenerated -I. $(F0_MA1_ASM) tests/test_f0_ma1_asm0.c -o $(BUILD)/f0ma1/test-f0-ma1-asm0
	$(PYTHON) tools/audit_f0_ma1_asm0.py $(F0_MA1_AUDIT_ARGS)
	$(PYTHON) tools/generate_f0_ma1_asm1.py $(F0_MA1_ASM1_GENERATOR_ARGS)
	$(PYTHON) tools/generate_f0_ma0_adapter.py $(F0_MA0_GENERATOR_ARGS)
	$(CC) -mavx2 -I. -c $(F0_MA0_ADAPTER) -o $(BUILD)/f0ma1/f0-ma0-adapter.o
	$(CC) -mavx2 -I. -c $(F0_MA1_ASM1) -o $(BUILD)/f0ma1/f0-ma1-asm1.o
	$(CC) $(CFLAGS_STRICT) -O3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA1_ASM1_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma1-asm1
	$(PYTHON) tools/audit_f0_ma1_asm1.py $(F0_MA1_ASM1_AUDIT_ARGS)
	$(PYTHON) tools/audit_f0_ma0_adapter.py $(F0_MA0_AUDIT_ARGS)
	$(PYTHON) tools/prove_f0_ma3_final_range.py $(F0_MA3_RANGE_ARGS)
	$(PYTHON) tools/generate_f0_ma3_asm.py $(F0_MA3_GENERATOR_ARGS)
	$(CC) -mavx2 -I. -c $(F0_MA3_ASM) -o $(BUILD)/f0ma1/f0-ma3.o
	$(CC) $(CFLAGS_STRICT) -O3 -DTEST_F0_MA3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA3_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma3
	$(BUILD)/f0ma1/test-f0-ma3
	$(PYTHON) tools/audit_f0_ma3.py $(F0_MA3_AUDIT_ARGS)
	$(PYTHON) tools/prove_f0_ma2_range.py $(F0_MA2_RANGE_ARGS)
	$(PYTHON) tools/generate_f0_ma2_asm.py $(F0_MA2_GENERATOR_ARGS)
	$(CC) -mavx2 -I. -c $(F0_MA2_ASM) -o $(BUILD)/f0ma1/f0-ma2.o
	$(CC) $(CFLAGS_STRICT) -O3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -I$(UPSTREAM) -I. $(F0_MA2_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma2
	$(BUILD)/f0ma1/test-f0-ma2
	$(PYTHON) tools/audit_f0_ma2.py $(F0_MA2_AUDIT_ARGS)
	$(PYTHON) tools/generate_f0_official_to_f0.py $(F0_MA2_KEM_ADAPTER_ARGS)
	$(PYTHON) tools/generate_f0_ma2_kem.py $(F0_MA2_KEM_ARGS)
	$(PYTHON) tools/generate_f0_prod0_contract.py $(F0_PROD0_CONTRACT_ARGS)
	$(PYTHON) tools/generate_f0_prod1_schedule.py $(F0_PROD1_SCHED_ARGS)
	$(PYTHON) tools/generate_f0_prod2_ma2_map.py $(F0_PROD2_MAP_ARGS)
	$(PYTHON) tools/generate_f0_prod2_ma2_asm.py $(F0_PROD2_GENERATOR_ARGS)
	$(PYTHON) tools/generate_gt9x16_prod3_map.py $(GT9X16_PROD3_MAP_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_map.py
	mkdir -p $(BUILD)/f0prod0
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_forward_for_ma2.c -o $(BUILD)/f0prod0/f0-forward-for-ma2.o
	$(PYTHON) tools/audit_f0_prod0.py $(F0_PROD0_AUDIT_ARGS)
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -I$(UPSTREAM) $(F0_PROD0_TEST_SOURCES) -o $(BUILD)/f0prod0/test-f0-prod0
	$(BUILD)/f0prod0/test-f0-prod0
	mkdir -p $(BUILD)/f0prod1
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_prod1_wrapper.c -o $(BUILD)/f0prod1/f0-prod1-p1h-wrapper.o
	$(CC) -mavx2 -I. -c $(F0_PROD1_ASM) -o $(BUILD)/f0prod1/f0-prod1-p1h.o
	$(PYTHON) tools/audit_f0_prod1_p1h.py $(F0_PROD1_AUDIT_ARGS)
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -I$(UPSTREAM) $(F0_PROD1_TEST_SOURCES) -o $(BUILD)/f0prod1/test-f0-prod1-p1h
	$(BUILD)/f0prod1/test-f0-prod1-p1h
	mkdir -p $(BUILD)/f0prod2
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_prod2_ma2_wrapper.c -o $(BUILD)/f0prod2/f0-prod2-wrapper.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_ASM) -o $(BUILD)/f0prod2/f0-prod2-p2b.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_PROJECTION_ASM) -o $(BUILD)/f0prod2/f0-generic-to-ma2-planes.o
	$(CC) -mavx2 -I. -c $(F0_MA2_ASM) -o $(BUILD)/f0prod2/f0-ma2.o
	$(PYTHON) tools/audit_f0_prod2_ma2_asm.py $(F0_PROD2_AUDIT_ARGS)
	$(PYTHON) tools/audit_f0_prod2_boundary.py $(F0_PROD2_BOUNDARY_AUDIT_ARGS)
	$(PYTHON) tools/generate_gt9x16_prod3_aos_schedule.py $(GT9X16_PROD3_AOS_SCHED_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_aos_schedule.py
	mkdir -p $(BUILD)/prod3
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_TILE_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-c1-tile.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -I. $(GT9X16_PROD3_AOS_TILE_ASM) tests/test_gt9x16_prod3_aos_c1_tile.c -o $(BUILD)/prod3/test-gt9x16-prod3-aos-c1-tile
	$(BUILD)/prod3/test-gt9x16-prod3-aos-c1-tile
	$(PYTHON) tools/audit_gt9x16_prod3_aos_c1_tile.py $(GT9X16_PROD3_AOS_TILE_AUDIT_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_aos_c1_tile_evidence.py
	$(PYTHON) tools/generate_gt9x16_prod3_aos_branch0.py $(GT9X16_PROD3_AOS_BRANCH_ARGS)
	$(PYTHON) tools/generate_gt9x16_prod3_aos_branch1.py --twist-constants generated/f0-prod1-constants.inc --asm-constants generated/gt9x16-prod3-aos-branch1-constants.inc
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_BRANCH_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-branch0.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_BRANCH_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-aos-branch0
	$(BUILD)/prod3/test-gt9x16-prod3-aos-branch0
	$(PYTHON) tools/audit_gt9x16_prod3_aos_branch0.py $(GT9X16_PROD3_AOS_BRANCH_AUDIT_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_aos_branch0_evidence.py
	$(PYTHON) tools/generate_gt9x16_prod3_aos_full.py $(GT9X16_PROD3_AOS_FULL_ARGS)
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_BRANCH_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-full.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_ASM) -o $(BUILD)/prod3/f0-prod2-p2b.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_FULL_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-aos-full
	$(BUILD)/prod3/test-gt9x16-prod3-aos-full
	$(PYTHON) tools/audit_gt9x16_prod3_aos_full.py $(GT9X16_PROD3_AOS_FULL_AUDIT_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_aos_full_evidence.py
	$(CC) $(CFLAGS_STRICT) -O3 -I$(UPSTREAM) tools/probe_official_pack_layout.c $(UPSTREAM)/consts.c $(UPSTREAM)/pack.s -o $(BUILD)/prod3/probe-official-pack-layout
	$(BUILD)/prod3/probe-official-pack-layout $(GT9X16_PROD3_HASH_PACK_LAYOUT)
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_hash_direct_map.py $(GT9X16_PROD3_HASH_DIRECT_MAP_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_direct_map.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_hash_direct_schedule.py $(GT9X16_PROD3_HASH_DIRECT_SCHED_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_direct_schedule.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_qorder_codesign.py $(GT9X16_PROD3_QORDER_CODESIGN_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_ma2_qorder_codesign.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_qorder_natural_schedule.py $(GT9X16_PROD3_QORDER_NATURAL_SCHED_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_ma2_qorder_natural_schedule.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_qorder_natural_asm.py $(GT9X16_PROD3_QORDER_NATURAL_ASM_ARGS)
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_QORDER_NATURAL_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-ma2-qorder-natural-asm0
	$(BUILD)/prod3/test-gt9x16-prod3-ma2-qorder-natural-asm0
	$(PYTHON) tools/audit_gt9x16_prod3_ma2_qorder_natural_asm0.py $(GT9X16_PROD3_QORDER_NATURAL_AUDIT_ARGS)
	$(PYTHON) tools/generate_gt9x16_prod3_t0_absorption_map.py $(GT9X16_PROD3_T0_MAP_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_t0_absorption_map.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_hash_h1_asm.py $(GT9X16_PROD3_HASH_H1_GENERATOR_ARGS)
	$(CC) -mavx2 -c $(GT9X16_PROD3_HASH_H1_ASM) -o $(BUILD)/prod3/gt9x16-prod3-ma2-hash-h1.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_H1_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-ma2-hash-h1
	$(BUILD)/prod3/test-gt9x16-prod3-ma2-hash-h1
	$(PYTHON) tools/audit_gt9x16_prod3_ma2_hash_h1.py $(GT9X16_PROD3_HASH_H1_AUDIT_ARGS)
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_h1_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_hash_h1_price_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_h1_integration_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_qorder_price_evidence.py
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated $(F0_PROD2_TEST_SOURCES) -o $(BUILD)/f0prod2/test-f0-prod2-ma2-asm0
	$(BUILD)/f0prod2/test-f0-prod2-ma2-asm0

check:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I$(UPSTREAM) tools/probe_official_layout.c $(OFFICIAL_FORWARD) -o $(BUILD)/probe-official-layout
	$(BUILD)/probe-official-layout $(BUILD)/official-avx2-layout-probe.json
	cmp generated/official-avx2-layout-probe.json $(BUILD)/official-avx2-layout-probe.json
	$(PYTHON) $(COMMON_GENERATOR) --parameter $(PARAMETER) --output generated/gt9x16-model.json --check
	$(PYTHON) tools/generate_stage8_tables.py --json generated/gt9x16-stage8-tables.json --header generated/gt9x16-stage8-tables.h --check
	$(PYTHON) tools/generate_full_forward_tables.py --json generated/gt9x16-component-oracle.json --header generated/gt9x16-full-forward-tables.h --asm-constants generated/gt9x16-ntt16-constants.inc --check
	mkdir -p $(BUILD)/structure
	$(CC) -mavx2 -c $(UPSTREAM)/ntt.s -o $(BUILD)/structure/official-ntt.o
	$(CC) -mavx2 -c $(UPSTREAM)/basemul.s -o $(BUILD)/structure/official-basemul.o
	$(CC) -mavx2 -c $(UPSTREAM)/baseinv.s -o $(BUILD)/structure/official-baseinv.o
	$(CC) -mavx2 -c $(UPSTREAM)/invntt.s -o $(BUILD)/structure/official-invntt.o
	$(PYTHON) tools/audit_ntt_domain_lifecycle.py --ntt-object $(BUILD)/structure/official-ntt.o --basemul-object $(BUILD)/structure/official-basemul.o --baseinv-object $(BUILD)/structure/official-baseinv.o --invntt-object $(BUILD)/structure/official-invntt.o --upstream $(UPSTREAM) --output generated/ntt-domain-lifecycle-audit.json --check
	$(PYTHON) tools/generate_pipeline_layout.py --component-oracle generated/gt9x16-component-oracle.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --output generated/gt9x16-pipeline-layout.json --cost-output generated/gt9x16-representation-cost-matrix.json --check
	$(PYTHON) tools/generate_ntt9_first_oracle.py --component-oracle generated/gt9x16-component-oracle.json --output generated/gt9x16-ntt9-first-oracle.json --check
	$(PYTHON) tools/generate_scaled_r3r3_oracle.py --ntt9-first-oracle generated/gt9x16-ntt9-first-oracle.json --pipeline-layout generated/gt9x16-pipeline-layout.json --output generated/gt9x16-scaled-r3r3-oracle.json --check
	$(PYTHON) tools/generate_ntt9_paper_range.py --tables generated/gt9x16-full-forward-tables.h --scaled-oracle generated/gt9x16-scaled-r3r3-oracle.json --json generated/gt9x16-ntt9-paper-range.json --header generated/gt9x16-ntt9-paper-range.h --asm-constants generated/gt9x16-paper-adjusted-ntt16-constants.inc --check
	$(PYTHON) tools/generate_official_stage_partitions.py --source $(UPSTREAM)/ntt.s --output $(OFFICIAL_PARTITIONS) --check
	$(PYTHON) tools/generate_g0_representation_views.py $(G0_GENERATOR_ARGS) --check
	$(PYTHON) tools/generate_g1_edge_oracles.py $(G1_GENERATOR_ARGS) --check
	$(PYTHON) tools/audit_g1c_inverse_sink.py $(G1C_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_g1c_adjusted_inverse_head.py $(G1C_HEAD_ARGS) --check
	$(PYTHON) tools/generate_g1c_bmscale_live_tail_contract.py $(G1C_LIVE_ARGS) --check
	$(PYTHON) tools/generate_g1c_m2_live_basis.py $(G1C_M2_ARGS) --check
	$(PYTHON) tools/generate_g1c_m3_inverse16_oracle.py $(G1C_M3_ARGS) --check
	$(PYTHON) tools/generate_g1c_m3b_provenance.py $(G1C_M3B_ARGS) --check
	$(PYTHON) tools/generate_g1c_m3c0_orientation_search.py $(G1C_M3C0_ARGS) --check
	$(PYTHON) tools/generate_g1c_m3c2_repair_plan.py $(G1C_M3C2_ARGS) --check
	$(PYTHON) tools/generate_g1c_m3c2p_exact_proof.py $(G1C_M3C2P_ARGS) --check
	$(PYTHON) tools/generate_g1c_m3_full_path_proof.py $(G1C_M3_FULL_PROOF_ARGS) --check
	mkdir -p $(BUILD)/g1c
	$(CC) -mavx2 -I. -c $(G1C_LINKED_ASM) -o $(BUILD)/g1c/g1c-bmscale-inverse-d1.o
	$(PYTHON) tools/audit_g1c_bmscale_inverse_d1.py $(G1C_LINKED_AUDIT_ARGS) --check
	$(PYTHON) tools/audit_g1c_m3_full_inverse16.py $(G1C_M3_FULL_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_hwa_compatibility_audit.py $(HWA_A0_ARGS) --check
	$(PYTHON) tools/generate_inverse_tail_consumer_map.py $(INVERSE_TAIL_MAP_ARGS) --check
	$(PYTHON) tools/generate_inverse_ntt9_b0.py $(INVERSE_NTT9_B0_GENERATOR_ARGS) --check
	$(PYTHON) tools/generate_inverse_ntt9_b1p.py $(INVERSE_NTT9_B1P_ARGS) --check
	$(PYTHON) tools/generate_inverse_ntt9_b1r.py $(INVERSE_NTT9_B1R_ARGS) --check
	$(PYTHON) tools/generate_f0_ma_map.py $(F0_MA_MAP_ARGS) --check
	$(PYTHON) tools/generate_f0_ma_schedule.py $(F0_MA_SCHED_ARGS) --check
	$(PYTHON) tools/prove_f0_ma3_final_range.py $(F0_MA3_RANGE_ARGS) --check
	$(PYTHON) tools/generate_f0_ma3_asm.py $(F0_MA3_GENERATOR_ARGS) --check
	$(PYTHON) tools/generate_f0_ma1_asm0.py $(F0_MA1_GENERATOR_ARGS) --check
	mkdir -p $(BUILD)/f0ma1
	$(CC) -mavx2 -I. -c $(F0_MA1_ASM) -o $(BUILD)/f0ma1/f0-ma1-asm0.o
	$(CC) $(CFLAGS_STRICT) -O3 -Igenerated -I. $(F0_MA1_ASM) tests/test_f0_ma1_asm0.c -o $(BUILD)/f0ma1/test-f0-ma1-asm0
	$(BUILD)/f0ma1/test-f0-ma1-asm0
	$(PYTHON) tools/audit_f0_ma1_asm0.py $(F0_MA1_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_f0_ma1_asm1.py $(F0_MA1_ASM1_GENERATOR_ARGS) --check
	$(PYTHON) tools/generate_f0_ma0_adapter.py $(F0_MA0_GENERATOR_ARGS) --check
	$(CC) -mavx2 -I. -c $(F0_MA0_ADAPTER) -o $(BUILD)/f0ma1/f0-ma0-adapter.o
	$(CC) -mavx2 -I. -c $(F0_MA1_ASM1) -o $(BUILD)/f0ma1/f0-ma1-asm1.o
	$(CC) $(CFLAGS_STRICT) -O3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA1_ASM1_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma1-asm1
	$(BUILD)/f0ma1/test-f0-ma1-asm1
	$(PYTHON) tools/audit_f0_ma1_asm1.py $(F0_MA1_ASM1_AUDIT_ARGS) --check
	$(PYTHON) tools/audit_f0_ma0_adapter.py $(F0_MA0_AUDIT_ARGS) --check
	$(PYTHON) tools/prove_f0_ma3_final_range.py $(F0_MA3_RANGE_ARGS) --check
	$(PYTHON) tools/generate_f0_ma3_asm.py $(F0_MA3_GENERATOR_ARGS) --check
	$(CC) -mavx2 -I. -c $(F0_MA3_ASM) -o $(BUILD)/f0ma1/f0-ma3.o
	$(CC) $(CFLAGS_STRICT) -O3 -DTEST_F0_MA3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA3_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma3
	$(BUILD)/f0ma1/test-f0-ma3
	$(PYTHON) tools/audit_f0_ma3.py $(F0_MA3_AUDIT_ARGS) --check
	$(PYTHON) tools/prove_f0_ma2_range.py $(F0_MA2_RANGE_ARGS) --check
	$(PYTHON) tools/generate_f0_ma2_asm.py $(F0_MA2_GENERATOR_ARGS) --check
	$(CC) -mavx2 -I. -c $(F0_MA2_ASM) -o $(BUILD)/f0ma1/f0-ma2.o
	$(CC) $(CFLAGS_STRICT) -O3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -I$(UPSTREAM) -I. $(F0_MA2_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma2
	$(BUILD)/f0ma1/test-f0-ma2
	$(PYTHON) tools/audit_f0_ma2.py $(F0_MA2_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_f0_official_to_f0.py $(F0_MA2_KEM_ADAPTER_ARGS) --check
	$(PYTHON) tools/generate_f0_ma2_kem.py $(F0_MA2_KEM_ARGS) --check
	$(CC) $(CFLAGS_STRICT) -O3 -Igenerated -I. $(F0_MA2_KEM_ADAPTER) $(F0_MA0_ADAPTER) tests/test_f0_official_to_f0.c -o $(BUILD)/f0ma1/test-f0-official-to-f0
	$(BUILD)/f0ma1/test-f0-official-to-f0
	$(PYTHON) tools/generate_f0_prod0_contract.py $(F0_PROD0_CONTRACT_ARGS) --check
	$(PYTHON) tools/generate_f0_prod1_schedule.py $(F0_PROD1_SCHED_ARGS) --check
	$(PYTHON) tools/generate_f0_prod2_ma2_map.py $(F0_PROD2_MAP_ARGS) --check
	$(PYTHON) tools/generate_f0_prod2_ma2_asm.py $(F0_PROD2_GENERATOR_ARGS) --check
	$(PYTHON) tools/generate_gt9x16_prod3_map.py $(GT9X16_PROD3_MAP_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_map.py
	mkdir -p $(BUILD)/f0prod0
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_forward_for_ma2.c -o $(BUILD)/f0prod0/f0-forward-for-ma2.o
	$(PYTHON) tools/audit_f0_prod0.py $(F0_PROD0_AUDIT_ARGS) --check
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -I$(UPSTREAM) $(F0_PROD0_TEST_SOURCES) -o $(BUILD)/f0prod0/test-f0-prod0
	$(BUILD)/f0prod0/test-f0-prod0
	mkdir -p $(BUILD)/f0prod1
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_prod1_wrapper.c -o $(BUILD)/f0prod1/f0-prod1-p1h-wrapper.o
	$(CC) -mavx2 -I. -c $(F0_PROD1_ASM) -o $(BUILD)/f0prod1/f0-prod1-p1h.o
	$(PYTHON) tools/audit_f0_prod1_p1h.py $(F0_PROD1_AUDIT_ARGS) --check
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -I$(UPSTREAM) $(F0_PROD1_TEST_SOURCES) -o $(BUILD)/f0prod1/test-f0-prod1-p1h
	$(BUILD)/f0prod1/test-f0-prod1-p1h
	mkdir -p $(BUILD)/f0prod2
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_prod2_ma2_wrapper.c -o $(BUILD)/f0prod2/f0-prod2-wrapper.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_ASM) -o $(BUILD)/f0prod2/f0-prod2-p2b.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_PROJECTION_ASM) -o $(BUILD)/f0prod2/f0-generic-to-ma2-planes.o
	$(CC) -mavx2 -I. -c $(F0_MA2_ASM) -o $(BUILD)/f0prod2/f0-ma2.o
	$(PYTHON) tools/audit_f0_prod2_ma2_asm.py $(F0_PROD2_AUDIT_ARGS) --check
	$(PYTHON) tools/audit_f0_prod2_boundary.py $(F0_PROD2_BOUNDARY_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_gt9x16_prod3_aos_schedule.py $(GT9X16_PROD3_AOS_SCHED_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_aos_schedule.py
	mkdir -p $(BUILD)/prod3
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_TILE_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-c1-tile.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -I. $(GT9X16_PROD3_AOS_TILE_ASM) tests/test_gt9x16_prod3_aos_c1_tile.c -o $(BUILD)/prod3/test-gt9x16-prod3-aos-c1-tile
	$(BUILD)/prod3/test-gt9x16-prod3-aos-c1-tile
	$(PYTHON) tools/audit_gt9x16_prod3_aos_c1_tile.py $(GT9X16_PROD3_AOS_TILE_AUDIT_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_aos_c1_tile_evidence.py
	$(PYTHON) tools/generate_gt9x16_prod3_aos_branch0.py $(GT9X16_PROD3_AOS_BRANCH_ARGS) --check
	$(PYTHON) tools/generate_gt9x16_prod3_aos_branch1.py --twist-constants generated/f0-prod1-constants.inc --asm-constants generated/gt9x16-prod3-aos-branch1-constants.inc --check
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_BRANCH_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-branch0.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_BRANCH_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-aos-branch0
	$(BUILD)/prod3/test-gt9x16-prod3-aos-branch0
	$(PYTHON) tools/audit_gt9x16_prod3_aos_branch0.py $(GT9X16_PROD3_AOS_BRANCH_AUDIT_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_aos_branch0_evidence.py
	$(PYTHON) tools/generate_gt9x16_prod3_aos_full.py $(GT9X16_PROD3_AOS_FULL_ARGS) --check
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_BRANCH_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-full.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_ASM) -o $(BUILD)/prod3/f0-prod2-p2b.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_FULL_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-aos-full
	$(BUILD)/prod3/test-gt9x16-prod3-aos-full
	$(PYTHON) tools/audit_gt9x16_prod3_aos_full.py $(GT9X16_PROD3_AOS_FULL_AUDIT_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_aos_full_evidence.py
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_CONSUMER_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-aos-consumer
	$(BUILD)/prod3/test-gt9x16-prod3-aos-consumer
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_TEST_SOURCES) -o $(BUILD)/prod3/test-f0-prod3-hash-bridge
	$(BUILD)/prod3/test-f0-prod3-hash-bridge
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_FANOUT_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-hash-fanout
	$(BUILD)/prod3/test-gt9x16-prod3-hash-fanout
	$(CC) $(CFLAGS_STRICT) -O3 -I$(UPSTREAM) tools/probe_official_pack_layout.c $(UPSTREAM)/consts.c $(UPSTREAM)/pack.s -o $(BUILD)/prod3/probe-official-pack-layout
	$(BUILD)/prod3/probe-official-pack-layout $(BUILD)/prod3/official-pack-layout.json
	cmp $(GT9X16_PROD3_HASH_PACK_LAYOUT) $(BUILD)/prod3/official-pack-layout.json
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_hash_direct_map.py $(GT9X16_PROD3_HASH_DIRECT_MAP_ARGS) --check
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_hash_direct_schedule.py $(GT9X16_PROD3_HASH_DIRECT_SCHED_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_direct_map.py
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_direct_schedule.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_qorder_codesign.py $(GT9X16_PROD3_QORDER_CODESIGN_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_ma2_qorder_codesign.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_qorder_natural_schedule.py $(GT9X16_PROD3_QORDER_NATURAL_SCHED_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_ma2_qorder_natural_schedule.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_qorder_natural_asm.py $(GT9X16_PROD3_QORDER_NATURAL_ASM_ARGS) --check
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I. $(GT9X16_PROD3_QORDER_NATURAL_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-ma2-qorder-natural-asm0
	$(BUILD)/prod3/test-gt9x16-prod3-ma2-qorder-natural-asm0
	$(PYTHON) tools/audit_gt9x16_prod3_ma2_qorder_natural_asm0.py $(GT9X16_PROD3_QORDER_NATURAL_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_gt9x16_prod3_t0_absorption_map.py $(GT9X16_PROD3_T0_MAP_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_t0_absorption_map.py
	$(PYTHON) tools/generate_gt9x16_prod3_ma2_hash_h1_asm.py $(GT9X16_PROD3_HASH_H1_GENERATOR_ARGS) --check
	$(CC) -mavx2 -c $(GT9X16_PROD3_HASH_H1_ASM) -o $(BUILD)/prod3/gt9x16-prod3-ma2-hash-h1.o
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_H1_TEST_SOURCES) -o $(BUILD)/prod3/test-gt9x16-prod3-ma2-hash-h1
	$(BUILD)/prod3/test-gt9x16-prod3-ma2-hash-h1
	$(PYTHON) tools/audit_gt9x16_prod3_ma2_hash_h1.py $(GT9X16_PROD3_HASH_H1_AUDIT_ARGS) --check
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_h1_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_hash_h1_price_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_h1_integration_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_qorder_price_evidence.py
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated $(F0_PROD2_TEST_SOURCES) -o $(BUILD)/f0prod2/test-f0-prod2-ma2-asm0
	$(BUILD)/f0prod2/test-f0-prod2-ma2-asm0
	$(CC) -mavx2 -I. -c $(INVERSE_NTT9_B0_ASM) -o $(BUILD)/g1c/inverse-ntt9-b0.o
	$(PYTHON) tools/audit_inverse_ntt9_b0.py $(INVERSE_NTT9_B0_AUDIT_ARGS) --check
	$(CC) -mavx2 -I. -c $(INVERSE_NTT9_B1_ASM) -o $(BUILD)/g1c/inverse-ntt9-b1.o
	$(PYTHON) tools/audit_inverse_ntt9_b1.py $(INVERSE_NTT9_B1_AUDIT_ARGS) --check
	$(PYTHON) tools/generate_inverse_tail_d0.py $(INVERSE_TAIL_D0_PROOF_ARGS) --check
	$(PYTHON) tools/generate_inverse_tail_d0.py $(INVERSE_TAIL_D0_M2_PROOF_ARGS) --check
	$(CC) -mavx2 -I. -c $(INVERSE_TAIL_D0_ASM) -o $(BUILD)/g1c/inverse-tail-d0.o
	$(PYTHON) tools/audit_inverse_tail_d0.py $(INVERSE_TAIL_D0_AUDIT_ARGS) --check
	$(CC) $(PAIRED_CFLAGS) -Isrc -Iref -Igenerated -c $(INVERSE_NTT9_REF) -o $(BUILD)/g1c/inverse-ntt9-reference.o
	$(PYTHON) tools/audit_inverse_ntt9_reference.py $(INVERSE_NTT9_AUDIT_ARGS) --output generated/g1c-inverse-ntt9-reference-audit.json --check
	$(CC) -mavx2 -Isrc -c $(G1C_M3C3_ASM) -o $(BUILD)/g1c/g1c-m3c3-reduction.o
	$(PYTHON) tools/audit_g1c_m3c3_reduction.py $(G1C_M3C3_AUDIT_ARGS) --check
	$(PYTHON) $(REPO_ROOT)/scripts/check_supercop_experiment.py --experiment $(EXPERIMENT) --parameter $(PARAMETER)
	$(PYTHON) tests/test_gt9x16_oracle.py
	$(PYTHON) tests/test_ntt9_first_oracle.py
	$(PYTHON) tests/test_representation_contract.py
	$(PYTHON) tests/test_scaled_r3r3_oracle.py
	$(PYTHON) tests/test_g0_representation_views.py
	$(PYTHON) tests/test_g1_edge_oracles.py
	$(PYTHON) tests/test_g1c_inverse_sink.py
	$(PYTHON) tests/test_g1c_adjusted_inverse_head.py
	$(PYTHON) tests/test_g1c_bmscale_live_tail_contract.py
	$(PYTHON) tests/test_g1c_m2_live_basis.py
	$(PYTHON) tests/test_g1c_m3_inverse16_oracle.py
	$(PYTHON) tests/test_g1c_m3b_provenance.py
	$(PYTHON) tests/test_g1c_m3c0_orientation_search.py
	$(PYTHON) tests/test_g1c_m3c2_repair_plan.py
	$(PYTHON) tests/test_g1c_m3c2p_exact_proof.py
	$(PYTHON) tests/test_g1c_m3c3_reduction_evidence.py
	$(PYTHON) tests/test_g1c_m3_full_path_proof.py
	$(PYTHON) tests/test_hwa_compatibility_audit.py
	$(PYTHON) tests/test_inverse_tail_consumer_map.py
	$(PYTHON) tests/test_inverse_tail_reference_evidence.py
	$(PYTHON) tests/test_inverse_ntt9_b0_evidence.py
	$(PYTHON) tests/test_inverse_ntt9_b1p.py
	$(PYTHON) tests/test_inverse_ntt9_b1r.py
	$(PYTHON) tests/test_inverse_ntt9_b1_evidence.py
	$(PYTHON) tests/test_inverse_tail_d0_proof.py
	$(PYTHON) tests/test_inverse_tail_d0_m2_proof.py
	$(PYTHON) tests/test_inverse_tail_d0_evidence.py
	$(PYTHON) tests/test_inverse_tail_d0_m2_evidence.py
	$(PYTHON) tests/test_f0_ma_consumer_map.py
	$(PYTHON) tests/test_f0_ma_symbolic_synthesis.py
	$(PYTHON) tests/test_f0_ma_schedule.py
	$(PYTHON) tests/test_f0_ma1_asm0_evidence.py
	$(PYTHON) tests/test_f0_ma1_asm1_evidence.py
	$(PYTHON) tests/test_f0_ma1_asm1_benchmark.py
	$(PYTHON) tests/test_f0_ma3_evidence.py
	$(PYTHON) tests/test_f0_ma2_evidence.py
	$(PYTHON) tests/test_f0_ma2_kem_evidence.py
	$(PYTHON) tests/test_f0_prod1_schedule.py
	$(PYTHON) tests/test_f0_prod1_p1h_evidence.py
	$(PYTHON) tests/test_f0_prod1_price_evidence.py
	$(PYTHON) tests/test_f0_prod2_ma2_map.py
	$(PYTHON) tests/test_f0_prod2_ma2_asm0_evidence.py
	$(PYTHON) tests/test_f0_prod2_price_evidence.py
	$(PYTHON) tests/test_f0_prod2_consumer_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_hash_fanout_evidence.py
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_direct_map.py
	$(PYTHON) tests/test_gt9x16_prod3_ma2_hash_direct_schedule.py
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) tests/test_gt9x16_shear.c -o $(BUILD)/test-gt9x16-shear
	$(BUILD)/test-gt9x16-shear
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c ref/ntt9_reference.c $(NTT16_ASM) tests/test_gt9x16_ntt16_asm.c -o $(BUILD)/test-gt9x16-ntt16-asm
	$(BUILD)/test-gt9x16-ntt16-asm
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) ref/ntt9_reference.c $(NTT16_ASM) tests/test_ntt9_paper.c -o $(BUILD)/test-ntt9-paper
	$(BUILD)/test-ntt9-paper
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) ref/ntt9_reference.c $(NTT16_ASM) tests/test_paper_adjusted_forward.c -o $(BUILD)/test-paper-adjusted-forward
	$(BUILD)/test-paper-adjusted-forward
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) tests/test_g1b_f1_tail.c -o $(BUILD)/test-g1b-f1-tail
	$(BUILD)/test-g1b-f1-tail
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) tests/test_g1c_bmscale_inverse_d1.c -o $(BUILD)/test-g1c-bmscale-inverse-d1
	$(BUILD)/test-g1c-bmscale-inverse-d1
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) tests/test_g1c_m3_full_inverse16.c -o $(BUILD)/test-g1c-m3-full-inverse16
	$(BUILD)/test-g1c-m3-full-inverse16
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(INVERSE_NTT9_REF) $(NTT16_ASM) $(G1C_LINKED_ASM) $(INVERSE_NTT9_B0_ASM) $(INVERSE_NTT9_B1_ASM) tests/test_inverse_ntt9_reference.c -o $(BUILD)/test-inverse-ntt9-reference
	$(BUILD)/test-inverse-ntt9-reference
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) $(INVERSE_NTT9_B1_ASM) $(INVERSE_TAIL_D0_ASM) tests/test_inverse_tail_d0.c -o $(BUILD)/test-inverse-tail-d0
	$(BUILD)/test-inverse-tail-d0
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc $(G1C_M3C3_ASM) tests/test_g1c_m3c3_reduction.c -o $(BUILD)/test-g1c-m3c3-reduction
	$(BUILD)/test-g1c-m3c3-reduction
	$(CC) $(CFLAGS_STRICT) -O3 -Isrc -I$(UPSTREAM) tests/test_official_stage_partitions.c $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) -o $(BUILD)/test-official-stage-partitions
	$(BUILD)/test-official-stage-partitions
	$(CC) $(CFLAGS_STRICT) -O3 $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) tests/test_full_forward.c -o $(BUILD)/test-full-forward
	$(BUILD)/test-full-forward

sanitize:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) tests/test_gt9x16_shear.c -o $(BUILD)/test-gt9x16-shear-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-shear-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c ref/ntt9_reference.c $(NTT16_ASM) tests/test_gt9x16_ntt16_asm.c -o $(BUILD)/test-gt9x16-ntt16-asm-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-ntt16-asm-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) ref/ntt9_reference.c $(NTT16_ASM) tests/test_ntt9_paper.c -o $(BUILD)/test-ntt9-paper-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-ntt9-paper-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) ref/ntt9_reference.c $(NTT16_ASM) tests/test_paper_adjusted_forward.c -o $(BUILD)/test-paper-adjusted-forward-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-paper-adjusted-forward-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) tests/test_g1b_f1_tail.c -o $(BUILD)/test-g1b-f1-tail-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-g1b-f1-tail-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) tests/test_g1c_bmscale_inverse_d1.c -o $(BUILD)/test-g1c-bmscale-inverse-d1-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-g1c-bmscale-inverse-d1-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) tests/test_g1c_m3_full_inverse16.c -o $(BUILD)/test-g1c-m3-full-inverse16-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-g1c-m3-full-inverse16-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(INVERSE_NTT9_REF) $(NTT16_ASM) $(G1C_LINKED_ASM) $(INVERSE_NTT9_B0_ASM) $(INVERSE_NTT9_B1_ASM) tests/test_inverse_ntt9_reference.c -o $(BUILD)/test-inverse-ntt9-reference-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-inverse-ntt9-reference-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) $(INVERSE_NTT9_B1_ASM) $(INVERSE_TAIL_D0_ASM) tests/test_inverse_tail_d0.c -o $(BUILD)/test-inverse-tail-d0-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-inverse-tail-d0-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Igenerated -I. $(F0_MA1_ASM) tests/test_f0_ma1_asm0.c -o $(BUILD)/test-f0-ma1-asm0-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-ma1-asm0-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA1_ASM1_TEST_SOURCES) -o $(BUILD)/test-f0-ma1-asm1-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-ma1-asm1-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -DTEST_F0_MA3 -fno-omit-frame-pointer -fsanitize=address,undefined -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA3_TEST_SOURCES) -o $(BUILD)/test-f0-ma3-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-ma3-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Igenerated -I$(UPSTREAM) -I. $(F0_MA2_TEST_SOURCES) -o $(BUILD)/test-f0-ma2-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-ma2-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. -Isrc -Igenerated $(F0_PROD2_TEST_SOURCES) -o $(BUILD)/test-f0-prod2-ma2-asm0-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-prod2-ma2-asm0-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -I. $(GT9X16_PROD3_AOS_TILE_ASM) tests/test_gt9x16_prod3_aos_c1_tile.c -o $(BUILD)/test-gt9x16-prod3-aos-c1-tile-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-prod3-aos-c1-tile-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_BRANCH_TEST_SOURCES) -o $(BUILD)/test-gt9x16-prod3-aos-branch0-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-prod3-aos-branch0-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_FULL_TEST_SOURCES) -o $(BUILD)/test-gt9x16-prod3-aos-full-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-prod3-aos-full-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -Igenerated -I. $(GT9X16_PROD3_AOS_CONSUMER_TEST_SOURCES) -o $(BUILD)/test-gt9x16-prod3-aos-consumer-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-prod3-aos-consumer-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_TEST_SOURCES) -o $(BUILD)/test-f0-prod3-hash-bridge-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-prod3-hash-bridge-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_FANOUT_TEST_SOURCES) -o $(BUILD)/test-gt9x16-prod3-hash-fanout-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-prod3-hash-fanout-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc -Igenerated -I$(UPSTREAM) -I. $(GT9X16_PROD3_HASH_H1_TEST_SOURCES) -o $(BUILD)/test-gt9x16-prod3-ma2-hash-h1-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-gt9x16-prod3-ma2-hash-h1-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/probe_g1c_m3b_correlated_range.c -o $(BUILD)/probe-g1c-m3b-range-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/probe-g1c-m3b-range-sanitize > /dev/null
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/probe_g1c_m3c2_repair.c -o $(BUILD)/probe-g1c-m3c2-repair-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/probe-g1c-m3c2-repair-sanitize > /dev/null
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Isrc $(G1C_M3C3_ASM) tests/test_g1c_m3c3_reduction.c -o $(BUILD)/test-g1c-m3c3-reduction-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-g1c-m3c3-reduction-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) tests/test_full_forward.c -o $(BUILD)/test-full-forward-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-full-forward-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. -Isrc -Igenerated -I$(UPSTREAM) $(F0_PROD0_TEST_SOURCES) -o $(BUILD)/test-f0-prod0-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-prod0-sanitize
	$(CC) $(CFLAGS_STRICT) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -I. -Isrc -Igenerated -I$(UPSTREAM) $(F0_PROD1_TEST_SOURCES) -o $(BUILD)/test-f0-prod1-p1h-sanitize
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 $(BUILD)/test-f0-prod1-p1h-sanitize

audit:
	mkdir -p $(BUILD) $(BUILD)/full-audit $(BUILD)/structure generated
	$(CC) $(CFLAGS_STRICT) -O3 -fno-inline $(CPPFLAGS_LOCAL) -c src/gt9x16_shear.c -o $(BUILD)/gt9x16-shear.o
	$(CC) $(CFLAGS_STRICT) -O3 -fno-inline $(CPPFLAGS_LOCAL) -S src/gt9x16_shear.c -o generated/gt9x16-shear.s
	$(PYTHON) tools/audit_gt9x16_shear.py --object $(BUILD)/gt9x16-shear.o --assembly generated/gt9x16-shear.s --compiler $(CC) --cflags "$(CFLAGS_STRICT) -O3 -fno-inline" --output generated/gt9x16-shear-audit.json
	$(CC) -mavx2 -I. -c $(NTT16_ASM) -o $(BUILD)/gt9x16-ntt16.o
	$(PYTHON) tools/audit_gt9x16_ntt16_asm.py --object $(BUILD)/gt9x16-ntt16.o --source $(NTT16_ASM) --macro-source asm/gt9x16_ntt16.inc --extra-macro-source asm/gt9x16_ntt16_c2.inc --extra-macro-source asm/gt9x16_ntt16_c4.inc --extra-macro-source asm/gt9x16_ntt9.inc --extra-macro-source asm/gt9x16_ntt9_paper.inc --extra-macro-source asm/gt9x16_ntt16_paper.inc --compiler $(CC) --cflags=-mavx2 --output generated/gt9x16-ntt16-audit.json
	$(PYTHON) tools/audit_paper_combined_boundary.py --object $(BUILD)/gt9x16-ntt16.o --output generated/gt9x16-paper-boundary-audit.json
	mkdir -p $(BUILD)/prod3
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_TILE_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-c1-tile.o
	$(PYTHON) tools/audit_gt9x16_prod3_aos_c1_tile.py $(GT9X16_PROD3_AOS_TILE_AUDIT_ARGS)
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_BRANCH_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-branch0.o
	$(PYTHON) tools/audit_gt9x16_prod3_aos_branch0.py $(GT9X16_PROD3_AOS_BRANCH_AUDIT_ARGS)
	$(CC) -mavx2 -I. -c $(GT9X16_PROD3_AOS_BRANCH_ASM) -o $(BUILD)/prod3/gt9x16-prod3-aos-full.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_ASM) -o $(BUILD)/prod3/f0-prod2-p2b.o
	$(PYTHON) tools/audit_gt9x16_prod3_aos_full.py $(GT9X16_PROD3_AOS_FULL_AUDIT_ARGS)
	$(CC) $(CFLAGS_STRICT) -O3 -fstack-usage $(CPPFLAGS_LOCAL) -c src/top_split_adapter.c -o $(BUILD)/full-audit/top_split_adapter.o
	$(CC) $(CFLAGS_STRICT) -O3 -fstack-usage $(CPPFLAGS_LOCAL) -c src/gt9x16_forward.c -o $(BUILD)/full-audit/gt9x16_forward.o
	$(CC) $(CFLAGS_STRICT) -O3 -fstack-usage $(CPPFLAGS_LOCAL) -c ref/ntt9_reference.c -o $(BUILD)/full-audit/ntt9_reference.o
	$(PYTHON) tools/audit_full_forward.py --object $(BUILD)/full-audit/top_split_adapter.o --object $(BUILD)/full-audit/gt9x16_forward.o --object $(BUILD)/full-audit/ntt9_reference.o --stack-usage $(BUILD)/full-audit/top_split_adapter.su --stack-usage $(BUILD)/full-audit/gt9x16_forward.su --stack-usage $(BUILD)/full-audit/ntt9_reference.su --compiler $(CC) --cflags "$(CFLAGS_STRICT) -O3 -fstack-usage" --output generated/gt9x16-full-forward-audit.json
	$(CC) $(PAIRED_CFLAGS) $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) bench/bench_full_forward_paired.c -o $(BUILD)/structure/gt-pipeline
	$(CC) -mavx2 -c $(UPSTREAM)/ntt.s -o $(BUILD)/structure/official-ntt.o
	$(CC) -mavx2 -c $(UPSTREAM)/basemul.s -o $(BUILD)/structure/official-basemul.o
	$(CC) -mavx2 -c $(UPSTREAM)/baseinv.s -o $(BUILD)/structure/official-baseinv.o
	$(CC) -mavx2 -c $(UPSTREAM)/invntt.s -o $(BUILD)/structure/official-invntt.o
	$(PYTHON) tools/audit_ntt_domain_lifecycle.py --ntt-object $(BUILD)/structure/official-ntt.o --basemul-object $(BUILD)/structure/official-basemul.o --baseinv-object $(BUILD)/structure/official-baseinv.o --invntt-object $(BUILD)/structure/official-invntt.o --upstream $(UPSTREAM) --output generated/ntt-domain-lifecycle-audit.json
	$(PYTHON) tools/generate_pipeline_layout.py --component-oracle generated/gt9x16-component-oracle.json --lifecycle-audit generated/ntt-domain-lifecycle-audit.json --output generated/gt9x16-pipeline-layout.json --cost-output generated/gt9x16-representation-cost-matrix.json --check
	$(PYTHON) tools/audit_pipeline_structure.py --candidate-elf $(BUILD)/structure/gt-pipeline --official-object $(BUILD)/structure/official-ntt.o --official-object $(BUILD)/structure/official-basemul.o --official-object $(BUILD)/structure/official-baseinv.o --official-object $(BUILD)/structure/official-invntt.o --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output generated/gt9x16-pipeline-structure-audit.json
	mkdir -p $(BUILD)/g1c
	$(CC) -mavx2 -I. -c $(G1C_LINKED_ASM) -o $(BUILD)/g1c/g1c-bmscale-inverse-d1.o
	$(PYTHON) tools/audit_g1c_bmscale_inverse_d1.py $(G1C_LINKED_AUDIT_ARGS)
	$(PYTHON) tools/audit_g1c_m3_full_inverse16.py $(G1C_M3_FULL_AUDIT_ARGS)
	$(CC) $(PAIRED_CFLAGS) -Isrc -Iref -Igenerated -c $(INVERSE_NTT9_REF) -o $(BUILD)/g1c/inverse-ntt9-reference.o
	$(PYTHON) tools/audit_inverse_ntt9_reference.py $(INVERSE_NTT9_AUDIT_ARGS) --output generated/g1c-inverse-ntt9-reference-audit.json
	$(CC) -mavx2 -I. -c $(INVERSE_NTT9_B0_ASM) -o $(BUILD)/g1c/inverse-ntt9-b0.o
	$(PYTHON) tools/audit_inverse_ntt9_b0.py $(INVERSE_NTT9_B0_AUDIT_ARGS)
	$(CC) -mavx2 -I. -c $(INVERSE_NTT9_B1_ASM) -o $(BUILD)/g1c/inverse-ntt9-b1.o
	$(PYTHON) tools/audit_inverse_ntt9_b1.py $(INVERSE_NTT9_B1_AUDIT_ARGS)
	$(PYTHON) tools/generate_inverse_tail_d0.py $(INVERSE_TAIL_D0_PROOF_ARGS) --check
	$(PYTHON) tools/generate_inverse_tail_d0.py $(INVERSE_TAIL_D0_M2_PROOF_ARGS) --check
	$(CC) -mavx2 -I. -c $(INVERSE_TAIL_D0_ASM) -o $(BUILD)/g1c/inverse-tail-d0.o
	$(PYTHON) tools/audit_inverse_tail_d0.py $(INVERSE_TAIL_D0_AUDIT_ARGS)
	$(CC) -mavx2 -Isrc -c $(G1C_M3C3_ASM) -o $(BUILD)/g1c/g1c-m3c3-reduction.o
	$(PYTHON) tools/audit_g1c_m3c3_reduction.py $(G1C_M3C3_AUDIT_ARGS)
	mkdir -p $(BUILD)/f0ma1
	$(CC) -mavx2 -I. -c $(F0_MA1_ASM) -o $(BUILD)/f0ma1/f0-ma1-asm0.o
	$(CC) $(CFLAGS_STRICT) -O3 -Igenerated -I. $(F0_MA1_ASM) tests/test_f0_ma1_asm0.c -o $(BUILD)/f0ma1/test-f0-ma1-asm0
	$(PYTHON) tools/audit_f0_ma1_asm0.py $(F0_MA1_AUDIT_ARGS)
	$(CC) -mavx2 -I. -c $(F0_MA1_ASM1) -o $(BUILD)/f0ma1/f0-ma1-asm1.o
	$(CC) $(CFLAGS_STRICT) -O3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA1_ASM1_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma1-asm1
	$(PYTHON) tools/audit_f0_ma1_asm1.py $(F0_MA1_ASM1_AUDIT_ARGS)
	$(CC) -mavx2 -I. -c $(F0_MA0_ADAPTER) -o $(BUILD)/f0ma1/f0-ma0-adapter.o
	$(PYTHON) tools/audit_f0_ma0_adapter.py $(F0_MA0_AUDIT_ARGS)
	$(PYTHON) tools/prove_f0_ma3_final_range.py $(F0_MA3_RANGE_ARGS) --check
	$(PYTHON) tools/generate_f0_ma3_asm.py $(F0_MA3_GENERATOR_ARGS) --check
	$(CC) -mavx2 -I. -c $(F0_MA3_ASM) -o $(BUILD)/f0ma1/f0-ma3.o
	$(CC) $(CFLAGS_STRICT) -O3 -DTEST_F0_MA3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -Isrc -I$(UPSTREAM) -I. $(F0_MA3_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma3
	$(PYTHON) tools/audit_f0_ma3.py $(F0_MA3_AUDIT_ARGS)
	$(PYTHON) tools/prove_f0_ma2_range.py $(F0_MA2_RANGE_ARGS) --check
	$(PYTHON) tools/generate_f0_ma2_asm.py $(F0_MA2_GENERATOR_ARGS) --check
	$(CC) -mavx2 -I. -c $(F0_MA2_ASM) -o $(BUILD)/f0ma1/f0-ma2.o
	$(CC) $(CFLAGS_STRICT) -O3 $(F0_MA1_ASM1_LINK_FLAGS) -Igenerated -I$(UPSTREAM) -I. $(F0_MA2_TEST_SOURCES) -o $(BUILD)/f0ma1/test-f0-ma2
	$(PYTHON) tools/audit_f0_ma2.py $(F0_MA2_AUDIT_ARGS)
	mkdir -p $(BUILD)/f0prod0
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_forward_for_ma2.c -o $(BUILD)/f0prod0/f0-forward-for-ma2.o
	$(PYTHON) tools/audit_f0_prod0.py $(F0_PROD0_AUDIT_ARGS)
	mkdir -p $(BUILD)/f0prod1
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_prod1_wrapper.c -o $(BUILD)/f0prod1/f0-prod1-p1h-wrapper.o
	$(CC) -mavx2 -I. -c $(F0_PROD1_ASM) -o $(BUILD)/f0prod1/f0-prod1-p1h.o
	$(PYTHON) tools/audit_f0_prod1_p1h.py $(F0_PROD1_AUDIT_ARGS)
	mkdir -p $(BUILD)/f0prod2
	$(CC) $(CFLAGS_STRICT) -O3 -I. -Isrc -Igenerated -c src/f0_prod2_ma2_wrapper.c -o $(BUILD)/f0prod2/f0-prod2-wrapper.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_ASM) -o $(BUILD)/f0prod2/f0-prod2-p2b.o
	$(CC) -mavx2 -I. -c $(F0_PROD2_PROJECTION_ASM) -o $(BUILD)/f0prod2/f0-generic-to-ma2-planes.o
	$(CC) -mavx2 -I. -c $(F0_MA2_ASM) -o $(BUILD)/f0prod2/f0-ma2.o
	$(PYTHON) tools/audit_f0_prod2_ma2_asm.py $(F0_PROD2_AUDIT_ARGS)
	$(PYTHON) tools/audit_f0_prod2_boundary.py $(F0_PROD2_BOUNDARY_AUDIT_ARGS)

bench-local:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) bench/bench_gt9x16_shear.c -o $(BUILD)/bench-gt9x16-shear
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-shear

bench-local-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 $(CPPFLAGS_LOCAL) $(SHEAR_SOURCES) bench/bench_gt9x16_shear.c -o $(BUILD)/bench-gt9x16-shear
	$(PYTHON) tools/run_shear_benchmark.py --binary $(BUILD)/bench-gt9x16-shear --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-shear-audit.json --output results/$(RESULT_TAG)/shear-diagnostic.json

bench-ntt16:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16.c -o $(BUILD)/bench-gt9x16-ntt16
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16

bench-ntt16-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16.c -o $(BUILD)/bench-gt9x16-ntt16
	$(PYTHON) tools/run_ntt16_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/ntt16-diagnostic.json

bench-c2:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16_c2.c -o $(BUILD)/bench-gt9x16-ntt16-c2
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16-c2

bench-c2-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) src/gt9x16_shear.c $(NTT16_ASM) bench/bench_gt9x16_ntt16_c2.c -o $(BUILD)/bench-gt9x16-ntt16-c2
	$(PYTHON) tools/run_c2_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16-c2 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/c2-diagnostic.json

bench-c3:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c3.c -o $(BUILD)/bench-gt9x16-ntt16-c3
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16-c3

bench-c3-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c3.c -o $(BUILD)/bench-gt9x16-ntt16-c3
	$(PYTHON) tools/run_c3_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16-c3 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/c3-diagnostic.json

bench-c4:
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c4.c -o $(BUILD)/bench-gt9x16-ntt16-c4
	taskset -c $(BENCH_CPU) $(BUILD)/bench-gt9x16-ntt16-c4

bench-c4-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(CFLAGS_STRICT) -O3 -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_gt9x16_ntt16_c4.c -o $(BUILD)/bench-gt9x16-ntt16-c4
	$(PYTHON) tools/run_c4_benchmark.py --binary $(BUILD)/bench-gt9x16-ntt16-c4 --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --output results/$(RESULT_TAG)/c4-diagnostic.json

bench-official-stages:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) bench/bench_official_stages_paired.c $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) -o $(BUILD)/bench-official-stages
	taskset -c $(BENCH_CPU) $(BUILD)/bench-official-stages

bench-official-stages-record:
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) bench/bench_official_stages_paired.c $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) -o $(BUILD)/bench-official-stages
	$(PYTHON) tools/run_official_stage_benchmark.py --binary $(BUILD)/bench-official-stages --cpu $(BENCH_CPU) --launches 9 --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --upstream upstream --output results/$(RESULT_TAG)/official-stage-paired.json

bench-transform-paired:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) bench/bench_full_forward_paired.c -o $(BUILD)/bench-full-forward-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-full-forward-paired

bench-transform-paired-record:
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) $(FULL_CPPFLAGS) $(FULL_SOURCES) $(OFFICIAL_FORWARD) bench/bench_full_forward_paired.c -o $(BUILD)/bench-full-forward-paired
	$(PYTHON) tools/run_transform_paired.py --binary $(BUILD)/bench-full-forward-paired --cpu $(BENCH_CPU) --launches 9 --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/transform-paired.json

bench-f-r3b:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_ntt9_paper_paired.c -o $(BUILD)/bench-ntt9-paper-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-ntt9-paper-paired

bench-f-r3b-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_ntt9_paper_paired.c -o $(BUILD)/bench-ntt9-paper-paired
	$(PYTHON) tools/run_ntt9_paper_benchmark.py --binary $(BUILD)/bench-ntt9-paper-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --range generated/gt9x16-ntt9-paper-range.json --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/ntt9-paper-paired.json

bench-f-r3c:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) bench/bench_paper_combined_paired.c -o $(BUILD)/bench-paper-combined-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-paper-combined-paired

bench-f-r3c-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) bench/bench_paper_combined_paired.c -o $(BUILD)/bench-paper-combined-paired
	$(PYTHON) tools/run_paper_combined_benchmark.py --binary $(BUILD)/bench-paper-combined-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --range generated/gt9x16-ntt9-paper-range.json --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/paper-combined-paired.json

bench-f-r3d:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) bench/bench_paper_combined_paired.c -o $(BUILD)/bench-paper-pipeline-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-paper-pipeline-paired

bench-f-r3d-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(FULL_CPPFLAGS) $(NTT16_ASM) $(OFFICIAL_PARTITIONS) $(OFFICIAL_FORWARD) bench/bench_paper_combined_paired.c -o $(BUILD)/bench-paper-pipeline-paired
	$(PYTHON) tools/run_paper_pipeline_benchmark.py --binary $(BUILD)/bench-paper-pipeline-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --range generated/gt9x16-ntt9-paper-range.json --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/paper-pipeline-paired.json

bench-g1b:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_g1b_f1_paired.c -o $(BUILD)/bench-g1b-f1-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-g1b-f1-paired

bench-g1b-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/bench_g1b_f1_paired.c -o $(BUILD)/bench-g1b-f1-paired
	$(PYTHON) tools/run_g1b_f1_benchmark.py --binary $(BUILD)/bench-g1b-f1-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/gt9x16-ntt16-audit.json --range generated/gt9x16-ntt9-paper-range.json --edge-oracle generated/g1-edge-oracles.json --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/g1b-f1-paired.json

bench-g1c-m2:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) bench/bench_g1c_m2_paired.c -o $(BUILD)/bench-g1c-m2-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-g1c-m2-paired

bench-g1c-m2-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) bench/bench_g1c_m2_paired.c -o $(BUILD)/bench-g1c-m2-paired
	$(PYTHON) tools/run_g1c_m2_benchmark.py --binary $(BUILD)/bench-g1c-m2-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/g1c-linked-bmscale-inverse-d1-audit.json --live-basis generated/g1c-m2-live-basis.json --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/g1c-m2-paired.json

bench-g1c-m3b-range:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/probe_g1c_m3b_correlated_range.c -o $(BUILD)/probe-g1c-m3b-range
	$(BUILD)/probe-g1c-m3b-range

bench-g1c-m3b-range-record: check
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/probe_g1c_m3b_correlated_range.c -o $(BUILD)/probe-g1c-m3b-range
	$(PYTHON) tools/run_g1c_m3b_range.py --binary $(BUILD)/probe-g1c-m3b-range --m3-oracle generated/g1c-m3-inverse16-oracle.json --source bench/probe_g1c_m3b_correlated_range.c --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/correlated-range.json

bench-g1c-m3c2-repair:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/probe_g1c_m3c2_repair.c -o $(BUILD)/probe-g1c-m3c2-repair
	$(BUILD)/probe-g1c-m3c2-repair

bench-g1c-m3c2-repair-record: check
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) bench/probe_g1c_m3c2_repair.c -o $(BUILD)/probe-g1c-m3c2-repair
	$(PYTHON) tools/run_g1c_m3c2_repair.py --binary $(BUILD)/probe-g1c-m3c2-repair --source bench/probe_g1c_m3c2_repair.c --common-header bench/g1c_m3_producer_common.h --m3-oracle generated/g1c-m3-inverse16-oracle.json --m3c0-oracle generated/g1c-m3c0-orientation-search.json --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/repair-observation.json

bench-g1c-m3c3-reduction:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -Isrc $(G1C_M3C3_ASM) bench/bench_g1c_m3c3_reduction_paired.c -o $(BUILD)/bench-g1c-m3c3-reduction-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-g1c-m3c3-reduction-paired

bench-g1c-m3c3-reduction-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -Isrc $(G1C_M3C3_ASM) bench/bench_g1c_m3c3_reduction_paired.c -o $(BUILD)/bench-g1c-m3c3-reduction-paired
	$(PYTHON) tools/run_g1c_m3c3_reduction_benchmark.py --binary $(BUILD)/bench-g1c-m3c3-reduction-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/g1c-m3c3-reduction-audit.json --proof generated/g1c-m3c2p-exact-proof.json --asm-source $(G1C_M3C3_ASM) --bench-source bench/bench_g1c_m3c3_reduction_paired.c --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/reduction-paired.json

bench-g1c-m3-full:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) bench/bench_g1c_m3_full_paired.c -o $(BUILD)/bench-g1c-m3-full-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-g1c-m3-full-paired

bench-g1c-m3-full-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) bench/bench_g1c_m3_full_paired.c -o $(BUILD)/bench-g1c-m3-full-paired
	$(PYTHON) tools/run_g1c_m3_full_benchmark.py --binary $(BUILD)/bench-g1c-m3-full-paired --cpu $(BENCH_CPU) --launches 9 --audit generated/g1c-m3-full-inverse16-audit.json --proof generated/g1c-m3-full-path-proof.json --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/full-paired.json

bench-inverse-tail:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(INVERSE_NTT9_REF) $(NTT16_ASM) $(G1C_LINKED_ASM) bench/bench_inverse_tail_paired.c -o $(BUILD)/bench-inverse-tail-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-inverse-tail-paired

bench-inverse-tail-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(INVERSE_NTT9_REF) $(NTT16_ASM) $(G1C_LINKED_ASM) bench/bench_inverse_tail_paired.c -o $(BUILD)/bench-inverse-tail-paired
	$(PYTHON) tools/run_inverse_tail_benchmark.py --binary $(BUILD)/bench-inverse-tail-paired --cpu $(BENCH_CPU) --launches 9 --map generated/g1c-inverse-tail-consumer-map.json --audit generated/g1c-inverse-ntt9-reference-audit.json --reference-source $(INVERSE_NTT9_REF) --bench-source bench/bench_inverse_tail_paired.c --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/paired.json

bench-inverse-ntt9-b0:
	mkdir -p $(BUILD)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) $(INVERSE_NTT9_B0_ASM) bench/bench_inverse_ntt9_b0_paired.c -o $(BUILD)/bench-inverse-ntt9-b0-paired
	taskset -c $(BENCH_CPU) $(BUILD)/bench-inverse-ntt9-b0-paired

bench-inverse-ntt9-b0-record: audit
	mkdir -p $(BUILD) results/$(RESULT_TAG)
	$(CC) $(PAIRED_CFLAGS) -I. $(CPPFLAGS_LOCAL) $(NTT16_ASM) $(G1C_LINKED_ASM) $(INVERSE_NTT9_B0_ASM) bench/bench_inverse_ntt9_b0_paired.c -o $(BUILD)/bench-inverse-ntt9-b0-paired
	$(PYTHON) tools/run_inverse_ntt9_b0_benchmark.py --binary $(BUILD)/bench-inverse-ntt9-b0-paired --cpu $(BENCH_CPU) --launches 9 --proof generated/g1c-inverse-ntt9-b0-range.json --audit generated/g1c-inverse-ntt9-b0-audit.json --source $(INVERSE_NTT9_B0_ASM) --bench-source bench/bench_inverse_ntt9_b0_paired.c --upstream upstream --compiler $(CC) --cflags "$(PAIRED_CFLAGS)" --output results/$(RESULT_TAG)/paired.json

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

supercop-itail-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-itail --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-itail-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-itail --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-itail-d0-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-itail-d0 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-itail-d0-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-itail-d0 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-itail-d0-m2-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-itail-d0-m2 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-itail-d0-m2-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-itail-d0-m2 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma1-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma1 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma1-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma1 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma1-ma0-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma1-ma0 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma1-ma0-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma1-ma0 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma3-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma3 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma3-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma3 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma2-chunk-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma2-chunk --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma2-chunk-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma2-chunk --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma2-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma2 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-ma2-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-ma2 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-prod1-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-prod1 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-prod1-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-prod1 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-prod2-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-prod2 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-prod2-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-prod2 --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-prod2-consumer-short:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-prod2-consumer --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SHORT) --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-f0-prod2-consumer-serious:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_benchmark.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --parameter $(PARAMETER) --implementation $(SUPERCOP_IMPLEMENTATION) --cpu $(BENCH_CPU) --mode derived-f0-prod2-consumer --fresh-launches $(SUPERCOP_FRESH_LAUNCHES_SERIOUS) --require-frequency-control --result-dir $(RESULTS)/$@ $(COMPILER_ARG)

supercop-gt9x16-prod3-price:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	test -n "$(SUPERCOP_COMPILER_WRAPPER)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_gt9x16_prod3_price.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --normal-implementation $${PROD3_NORMAL_IMPLEMENTATION:-avx2-gt9x16-prod3-price-normal} --reversed-implementation $${PROD3_REVERSED_IMPLEMENTATION:-avx2-gt9x16-prod3-price-reversed} --cpu $(BENCH_CPU) --compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER) --selection-launches 9 --output $(RESULTS)/$@

supercop-gt9x16-prod3-consumer:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	test -n "$(SUPERCOP_COMPILER_WRAPPER)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_gt9x16_prod3_consumer.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --normal-implementation $${PROD3_NORMAL_IMPLEMENTATION:-avx2-gt9x16-prod3-price-normal} --reversed-implementation $${PROD3_REVERSED_IMPLEMENTATION:-avx2-gt9x16-prod3-price-reversed} --cpu $(BENCH_CPU) --compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER) --output $(RESULTS)/$@

supercop-gt9x16-prod3-hash-fanout:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	test -n "$(SUPERCOP_COMPILER_WRAPPER)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_gt9x16_prod3_hash_fanout.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --normal-implementation $${PROD3_NORMAL_IMPLEMENTATION:-avx2-gt9x16-prod3-fanout-normal} --reversed-implementation $${PROD3_REVERSED_IMPLEMENTATION:-avx2-gt9x16-prod3-fanout-reversed} --cpu $(BENCH_CPU) --compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER) --output $(RESULTS)/$@

supercop-gt9x16-prod3-hash-h1-price:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	test -n "$(SUPERCOP_COMPILER_WRAPPER)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_gt9x16_prod3_hash_h1_price.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --normal-implementation $${PROD3_NORMAL_IMPLEMENTATION:-avx2-gt9x16-prod3-h1-price-normal} --reversed-implementation $${PROD3_REVERSED_IMPLEMENTATION:-avx2-gt9x16-prod3-h1-price-reversed} --cpu $(BENCH_CPU) --compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER) --output $(RESULTS)/$@

supercop-gt9x16-prod3-qorder-price:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	test -n "$(SUPERCOP_COMPILER_WRAPPER)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_gt9x16_prod3_qorder_price.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --normal-implementation $${PROD3_QORDER_NORMAL_IMPLEMENTATION:-avx2-gt9x16-prod3-qorder-price-normal} --reversed-implementation $${PROD3_QORDER_REVERSED_IMPLEMENTATION:-avx2-gt9x16-prod3-qorder-price-reversed} --cpu $(BENCH_CPU) --compiler-wrapper $(SUPERCOP_COMPILER_WRAPPER) --output $(RESULTS)/$@

gt9x16-prod3-h1-kat:
	test -n "$(SUPERCOP_CAMPAIGN_ROOT)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_gt9x16_prod3_h1_kat.py --campaign-root $(SUPERCOP_CAMPAIGN_ROOT) --implementation $${SUPERCOP_IMPLEMENTATION:-avx2-gt9x16-prod3-h1-exp001} --output $(RESULTS)/kat.json

supercop-paired-serious:
	test -n "$(OFFICIAL_MEASURE)"; test -n "$(CANDIDATE_MEASURE)"
	test -n "$(OFFICIAL_MEASURE_REVERSED)"; test -n "$(CANDIDATE_MEASURE_REVERSED)"
	$(PYTHON) $(REPO_ROOT)/scripts/run_supercop_paired.py --official $(OFFICIAL_MEASURE) --candidate $(CANDIDATE_MEASURE) --official-reversed $(OFFICIAL_MEASURE_REVERSED) --candidate-reversed $(CANDIDATE_MEASURE_REVERSED) --compiler-recipe "$${FIXED_COMPILER_RECIPE:-O3GC}" --cpu $(BENCH_CPU) --output $(RESULTS)/paired

supercop-promotion-report:
	$(PYTHON) $(REPO_ROOT)/scripts/supercop_promotion_report.py --paired $(PAIRED_RESULTS) --native-official $(NATIVE_OFFICIAL_RESULTS) --native-candidate $(NATIVE_CANDIDATE_RESULTS) --poly-official $(POLY_OFFICIAL_RESULTS) --poly-candidate $(POLY_CANDIDATE_RESULTS) --output $(RESULTS)/promotion.json
