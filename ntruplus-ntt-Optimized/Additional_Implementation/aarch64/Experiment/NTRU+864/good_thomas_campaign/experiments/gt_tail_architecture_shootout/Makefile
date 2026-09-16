PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
# The isolated pass-2 entry points are internal all-register kernels.  Keep the
# local C oracle out of v8-v15; the public full-Forward wrapper owns the AAPCS64
# d8-d15 save/restore boundary.
C_ORACLE_FLAGS := $(CFLAGS) -mgeneral-regs-only
BUILD := build
M5RD := ../gt_forward_level2_one_mul_b3
M5O := ../gt_forward_full_poly_ntt_asm
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s
OFFICIAL := ../../../../../NTRU+864/asm/ntt.s

.PHONY: prepare check benchmark clean

prepare: $(BUILD)/tail_variants.S $(BUILD)/pass2_t0.S $(BUILD)/pass2_t1.S $(BUILD)/pass2_t2.S \
	$(BUILD)/full_t0_wrapper.S $(BUILD)/full_t1_wrapper.S $(BUILD)/full_t2_wrapper.S

$(BUILD)/tail_variants.S: prepare.py
	$(PYTHON) prepare.py

$(BUILD)/pass2_t0.S $(BUILD)/pass2_t1.S $(BUILD)/pass2_t2.S $(BUILD)/full_t0_wrapper.S $(BUILD)/full_t1_wrapper.S \
		$(BUILD)/full_t2_wrapper.S: $(BUILD)/tail_variants.S
	@test -f $@

$(BUILD)/test_tail_variants.o: test_tail_variants.c | $(BUILD)/tail_variants.S
	$(CC) $(C_ORACLE_FLAGS) -c -o $@ $<

$(BUILD)/test-tail: $(BUILD)/test_tail_variants.o $(BUILD)/tail_variants.S
	$(CC) $(CFLAGS) -o $@ $^

$(BUILD)/gt864_fr0_to_official_map.h: $(M5O)/generate_official_map.py | $(BUILD)/tail_variants.S
	$(PYTHON) $< $@ $(BUILD)/map-proof.json

$(BUILD)/test_full_forward.o: test_full_forward.c $(BUILD)/gt864_fr0_to_official_map.h
	$(CC) $(C_ORACLE_FLAGS) -I$(BUILD) -c -o $@ $<

$(BUILD)/test-full: $(BUILD)/test_full_forward.o $(BUILD)/gt864_fr0_to_official_map.h \
		$(BUILD)/tail_variants.S $(BUILD)/pass2_t0.S $(BUILD)/pass2_t1.S $(BUILD)/pass2_t2.S \
		$(BUILD)/full_t1_wrapper.S $(BUILD)/full_t2_wrapper.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S $(TOP) $(OFFICIAL)
	$(CC) $(CFLAGS) -I$(BUILD) -o $@ $(BUILD)/test_full_forward.o \
		$(BUILD)/tail_variants.S $(BUILD)/pass2_t0.S $(BUILD)/pass2_t1.S $(BUILD)/pass2_t2.S \
		$(BUILD)/full_t1_wrapper.S $(BUILD)/full_t2_wrapper.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S $(TOP) $(OFFICIAL)

check: $(BUILD)/test-tail $(BUILD)/test-full
	$(BUILD)/test-tail
	$(BUILD)/test-full

$(BUILD)/bench-pmu: bench_pmu.c $(BUILD)/tail_variants.S
	$(CC) $(CFLAGS) -o $@ $^

benchmark: $(BUILD)/bench-pmu
	@echo "Run on Linux AArch64 with perf_event access: $< 012N"

clean:
	rm -f -r $(BUILD)
