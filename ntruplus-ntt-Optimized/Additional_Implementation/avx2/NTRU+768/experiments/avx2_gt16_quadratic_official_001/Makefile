PYTHON ?= python3
CC ?= gcc
CFLAGS ?= -O3 -mavx2 -Wall -Wextra -Werror -std=c11
BUILD := build
SAN_BUILD := build-sanitize
INCLUDES := -Isrc -Igenerated
QBM_SRC := src/qbm_intrinsic.c
INVERSE_SRC := src/inverse_stage1_intrinsic.c
FORWARD_SRC := src/forward_intrinsic.c
FORWARD_ASM := src/forward_ntt16_asm.S
TRANSPOSE_SRC := src/transpose_intrinsic.c
QUARTIC_ASM := ../gt_ntt/gt_basemul_layout_asm.S
BASELINE_SRC := $(TRANSPOSE_SRC) generated/quartic-lambda.c $(QUARTIC_ASM)
FROZEN_INVERSE_SRC := ../gt_ntt/gt_invntt_soa.c ../gt_ntt/gt_invntt_fused_soa.S
FROZEN_FORWARD_SRC := ../gt_ntt/gt_ntt_tables.c \
	../gt_ntt/gt_ntt_frontend_stage12_soa.S ../gt_ntt/gt_ntt_stage345_soa.s

.PHONY: all generate check intrinsic-check audit sanitize bench bench-forward clean

all: check

generate:
	$(PYTHON) tools/generate_quadratic.py

check:
	$(PYTHON) tools/generate_quadratic.py --check
	$(PYTHON) tests/test_quadratic_oracle.py
	$(MAKE) intrinsic-check
	$(MAKE) audit

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_qbm_intrinsic: $(QBM_SRC) $(INVERSE_SRC) $(BASELINE_SRC) tests/test_qbm_intrinsic.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(INVERSE_SRC) $(BASELINE_SRC) tests/test_qbm_intrinsic.c -o $@

$(BUILD)/test_forward_intrinsic: $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) tests/test_forward_intrinsic.c generated/quadratic-constants.h generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) tests/test_forward_intrinsic.c -o $@

$(BUILD)/bench_qbm_intrinsic: $(QBM_SRC) $(INVERSE_SRC) $(BASELINE_SRC) $(FROZEN_INVERSE_SRC) bench/bench_qbm_intrinsic.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) -DGT_HAVE_AVX2_ASM=1 $(INCLUDES) -I../gt_ntt \
		$(QBM_SRC) $(INVERSE_SRC) $(BASELINE_SRC) $(FROZEN_INVERSE_SRC) \
		bench/bench_qbm_intrinsic.c -o $@

$(BUILD)/bench_forward_intrinsic: $(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(FROZEN_FORWARD_SRC) bench/bench_forward_intrinsic.c generated/quadratic-constants.h generated/forward-ntt16-constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -DGT_HAVE_AVX2_ASM=1 $(INCLUDES) -I../gt_ntt \
		$(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) $(FROZEN_FORWARD_SRC) \
		bench/bench_forward_intrinsic.c -o $@

intrinsic-check: $(BUILD)/test_qbm_intrinsic $(BUILD)/test_forward_intrinsic
	$(BUILD)/test_qbm_intrinsic
	$(BUILD)/test_forward_intrinsic

audit: $(BUILD)/bench_qbm_intrinsic $(BUILD)/bench_forward_intrinsic
	$(PYTHON) tools/audit_intrinsic.py --check

sanitize:
	mkdir -p $(SAN_BUILD)
	$(CC) -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(QBM_SRC) $(INVERSE_SRC) $(BASELINE_SRC) tests/test_qbm_intrinsic.c \
		-o $(SAN_BUILD)/test_qbm_intrinsic
	ASAN_OPTIONS=detect_leaks=0 $(SAN_BUILD)/test_qbm_intrinsic
	$(CC) -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(QBM_SRC) $(FORWARD_SRC) $(FORWARD_ASM) tests/test_forward_intrinsic.c \
		-o $(SAN_BUILD)/test_forward_intrinsic
	ASAN_OPTIONS=detect_leaks=0 $(SAN_BUILD)/test_forward_intrinsic

bench: $(BUILD)/bench_qbm_intrinsic
	$(BUILD)/bench_qbm_intrinsic

bench-forward: $(BUILD)/bench_forward_intrinsic
	$(BUILD)/bench_forward_intrinsic

clean:
	$(RM) -r $(BUILD) $(SAN_BUILD)
