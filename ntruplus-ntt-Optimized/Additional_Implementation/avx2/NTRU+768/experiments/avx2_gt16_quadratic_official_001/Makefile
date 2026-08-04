PYTHON ?= python3
CC ?= gcc
CFLAGS ?= -O3 -mavx2 -Wall -Wextra -Werror -std=c11
BUILD := build
INCLUDES := -Isrc -Igenerated
QBM_SRC := src/qbm_intrinsic.c
TRANSPOSE_SRC := src/transpose_intrinsic.c
QUARTIC_ASM := ../gt_ntt/gt_basemul_layout_asm.S
BASELINE_SRC := $(TRANSPOSE_SRC) generated/quartic-lambda.c $(QUARTIC_ASM)

.PHONY: all generate check intrinsic-check audit sanitize bench clean

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

$(BUILD)/test_qbm_intrinsic: $(QBM_SRC) $(BASELINE_SRC) tests/test_qbm_intrinsic.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(BASELINE_SRC) tests/test_qbm_intrinsic.c -o $@

$(BUILD)/bench_qbm_intrinsic: $(QBM_SRC) $(BASELINE_SRC) bench/bench_qbm_intrinsic.c generated/quadratic-constants.h | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(QBM_SRC) $(BASELINE_SRC) bench/bench_qbm_intrinsic.c -o $@

intrinsic-check: $(BUILD)/test_qbm_intrinsic
	$(BUILD)/test_qbm_intrinsic

audit: $(BUILD)/bench_qbm_intrinsic
	$(PYTHON) tools/audit_intrinsic.py --check

sanitize: CFLAGS := -O1 -g -mavx2 -Wall -Wextra -Werror -std=c11 -fsanitize=address,undefined -fno-omit-frame-pointer
sanitize: clean $(BUILD)/test_qbm_intrinsic
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_qbm_intrinsic

bench: $(BUILD)/bench_qbm_intrinsic
	$(BUILD)/bench_qbm_intrinsic

clean:
	$(RM) -r $(BUILD)
