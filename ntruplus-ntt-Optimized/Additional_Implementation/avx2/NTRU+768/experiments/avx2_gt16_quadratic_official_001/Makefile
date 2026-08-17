PYTHON ?= python3
CC ?= gcc
CFLAGS ?= -O3 -mavx2 -Wall -Wextra -Werror -std=c11
BUILD := build
SAN_BUILD := build-sanitize
INCLUDES := -Isrc -Igenerated
QBM_SRC := src/qbm_intrinsic.c
INVERSE_SRC := src/inverse_stage1_intrinsic.c
FUSED_QBM_INVERSE_ASM := src/qbm_inverse_fused_asm.S
INVERSE_NTT16_ASM := src/inverse_ntt16_asm.S
INVERSE_FULL_ASM := src/inverse_full_asm.S
QBM_ASM_CONSTANTS := src/qbm_asm_constants.c
FUSED_QBM_INVERSE_C := src/qbm_inverse_fused.c
INVERSE_SUPPORT := $(FUSED_QBM_INVERSE_ASM) $(INVERSE_NTT16_ASM) $(INVERSE_FULL_ASM) $(QBM_ASM_CONSTANTS)
FORWARD_SRC := src/forward_intrinsic.c
FORWARD_ASM := src/forward_ntt16_asm.S
LANE_NTT16_SRC := src/lane_ntt16_intrinsic.c
TRANSPOSE_SRC := src/transpose_intrinsic.c
QUARTIC_ASM := ../gt_ntt/gt_basemul_layout_asm.S
BASELINE_SRC := $(TRANSPOSE_SRC) generated/quartic-lambda.c $(QUARTIC_ASM)
FROZEN_INVERSE_SRC := ../gt_ntt/gt_invntt_soa.c ../gt_ntt/gt_invntt_fused_soa.S
FROZEN_FORWARD_SRC := ../gt_ntt/gt_ntt_tables.c \
	../gt_ntt/gt_ntt_frontend_stage12_soa.S ../gt_ntt/gt_ntt_stage345_soa.s
OFFICIAL_SNAPSHOT := ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
OFFICIAL_BM_INV_SRC := $(OFFICIAL_SNAPSHOT)/consts.c \
	$(OFFICIAL_SNAPSHOT)/asm/basemul.s $(OFFICIAL_SNAPSHOT)/asm/invntt.s

.PHONY: all generate check intrinsic-check lane-check ct8-check audit sanitize bench bench-forward bench-lane bench-ct8 bench-wide-qbm bench-fused-consumer clean

all: check

generate:
	$(PYTHON) tools/generate_quadratic.py

check:
	$(PYTHON) tools/generate_quadratic.py --check
	$(PYTHON) tests/test_quadratic_oracle.py
	$(MAKE) intrinsic-check
	$(MAKE) lane-check
	$(MAKE) ct8-check
	$(MAKE) audit

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_qbm_intrinsic: $(QBM_SRC) $(INVERSE_SRC) $(FUSED_QBM_INVERSE_ASM) $(FUSED_QBM_INVERSE_C) $(INVERSE_NTT16_ASM) $(INVERSE_FULL_ASM) $(QBM_ASM_CONSTANTS) $(BASELINE_SRC) tests/test_qbm_intrinsic.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(INVERSE_SRC) $(FUSED_QBM_INVERSE_ASM) $(FUSED_QBM_INVERSE_C) $(INVERSE_NTT16_ASM) $(INVERSE_FULL_ASM) $(QBM_ASM_CONSTANTS) $(BASELINE_SRC) tests/test_qbm_intrinsic.c -o $@

$(BUILD)/test_forward_intrinsic: $(QBM_SRC) $(INVERSE_SRC) $(INVERSE_SUPPORT) $(FORWARD_SRC) $(FORWARD_ASM) tests/test_forward_intrinsic.c generated/quadratic-constants.h generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(INVERSE_SRC) $(INVERSE_SUPPORT) $(FORWARD_SRC) $(FORWARD_ASM) tests/test_forward_intrinsic.c -o $@

$(BUILD)/bench_qbm_intrinsic: $(QBM_SRC) $(INVERSE_SRC) $(INVERSE_SUPPORT) $(BASELINE_SRC) $(FROZEN_INVERSE_SRC) bench/bench_qbm_intrinsic.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) -DGT_HAVE_AVX2_ASM=1 $(INCLUDES) -I../gt_ntt \
		$(QBM_SRC) $(INVERSE_SRC) $(INVERSE_SUPPORT) $(BASELINE_SRC) $(FROZEN_INVERSE_SRC) \
		bench/bench_qbm_intrinsic.c -o $@

$(BUILD)/bench_forward_intrinsic: $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(FROZEN_FORWARD_SRC) bench/bench_forward_intrinsic.c generated/quadratic-constants.h generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -DGT_HAVE_AVX2_ASM=1 $(INCLUDES) -I../gt_ntt \
		$(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(FROZEN_FORWARD_SRC) \
		bench/bench_forward_intrinsic.c -o $@

$(BUILD)/test_lane_ntt16: $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(LANE_NTT16_SRC) tests/test_lane_ntt16.c generated/quadratic-constants.h generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) \
		$(LANE_NTT16_SRC) tests/test_lane_ntt16.c -o $@

$(BUILD)/bench_lane_ntt16: $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(LANE_NTT16_SRC) bench/bench_lane_ntt16.c generated/quadratic-constants.h generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) \
		$(LANE_NTT16_SRC) bench/bench_lane_ntt16.c -o $@

$(BUILD)/test_ct8_schedule: $(FORWARD_ASM) tests/test_ct8_schedule.c generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(FORWARD_ASM) tests/test_ct8_schedule.c -o $@

$(BUILD)/bench_ct8_schedule: $(FORWARD_ASM) bench/bench_ct8_schedule.c generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(FORWARD_ASM) bench/bench_ct8_schedule.c -o $@

$(BUILD)/bench_wide_qbm: $(QBM_SRC) bench/bench_wide_qbm.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) bench/bench_wide_qbm.c -o $@

$(BUILD)/bench_fused_consumer: $(QBM_SRC) $(INVERSE_SRC) $(FUSED_QBM_INVERSE_ASM) $(INVERSE_NTT16_ASM) $(INVERSE_FULL_ASM) $(QBM_ASM_CONSTANTS) $(BASELINE_SRC) $(FROZEN_INVERSE_SRC) $(OFFICIAL_BM_INV_SRC) bench/bench_fused_consumer.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(INVERSE_SRC) $(FUSED_QBM_INVERSE_ASM) \
		$(INVERSE_NTT16_ASM) $(INVERSE_FULL_ASM) $(QBM_ASM_CONSTANTS) $(BASELINE_SRC) \
		$(FROZEN_INVERSE_SRC) $(OFFICIAL_BM_INV_SRC) bench/bench_fused_consumer.c -o $@

intrinsic-check: $(BUILD)/test_qbm_intrinsic $(BUILD)/test_forward_intrinsic
	$(BUILD)/test_qbm_intrinsic
	$(BUILD)/test_forward_intrinsic

lane-check: $(BUILD)/test_lane_ntt16
	$(BUILD)/test_lane_ntt16

ct8-check: $(BUILD)/test_ct8_schedule
	$(BUILD)/test_ct8_schedule

audit: $(BUILD)/bench_qbm_intrinsic $(BUILD)/bench_forward_intrinsic
	$(PYTHON) tools/audit_intrinsic.py --check

sanitize:
	mkdir -p $(SAN_BUILD)
	$(CC) -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(QBM_SRC) $(INVERSE_SRC) $(FUSED_QBM_INVERSE_ASM) $(FUSED_QBM_INVERSE_C) $(INVERSE_NTT16_ASM) $(INVERSE_FULL_ASM) $(QBM_ASM_CONSTANTS) $(BASELINE_SRC) tests/test_qbm_intrinsic.c \
		-o $(SAN_BUILD)/test_qbm_intrinsic
	ASAN_OPTIONS=detect_leaks=0 $(SAN_BUILD)/test_qbm_intrinsic
	$(CC) -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(QBM_SRC) $(INVERSE_SRC) $(INVERSE_SUPPORT) $(FORWARD_SRC) $(FORWARD_ASM) tests/test_forward_intrinsic.c \
		-o $(SAN_BUILD)/test_forward_intrinsic
	ASAN_OPTIONS=detect_leaks=0 $(SAN_BUILD)/test_forward_intrinsic
	$(CC) -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(LANE_NTT16_SRC) tests/test_lane_ntt16.c \
		-o $(SAN_BUILD)/test_lane_ntt16
	ASAN_OPTIONS=detect_leaks=0 $(SAN_BUILD)/test_lane_ntt16
	$(CC) -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(FORWARD_ASM) tests/test_ct8_schedule.c -o $(SAN_BUILD)/test_ct8_schedule
	ASAN_OPTIONS=detect_leaks=0 $(SAN_BUILD)/test_ct8_schedule

bench: $(BUILD)/bench_qbm_intrinsic
	$(BUILD)/bench_qbm_intrinsic

bench-forward: $(BUILD)/bench_forward_intrinsic
	$(BUILD)/bench_forward_intrinsic

bench-lane: $(BUILD)/bench_lane_ntt16
	$(BUILD)/bench_lane_ntt16

bench-ct8: $(BUILD)/bench_ct8_schedule
	$(BUILD)/bench_ct8_schedule

bench-wide-qbm: $(BUILD)/bench_wide_qbm
	$(BUILD)/bench_wide_qbm

bench-fused-consumer: $(BUILD)/bench_fused_consumer
	$(BUILD)/bench_fused_consumer

clean:
	$(RM) -r $(BUILD) $(SAN_BUILD)
