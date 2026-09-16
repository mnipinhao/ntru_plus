PYTHON ?= python3
CC ?= clang
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD := build
M5RD := ../gt_forward_level2_one_mul_b3
TOP := ../gt_2x9x16_ld3_top_split
M5C := ../gt_fr0_basemul_arithmetic
M5D := ../gt_fr0_inverse_consumer
M5E := ../gt_fr0_inverse_asm_realization
CHAIN := $(BUILD)/range-chain.json
FIXED := $(BUILD)/m5e-fixed-barrett.json
BASEMUL_TABLES := $(BUILD)/gt864_fr0_basemul_tables.h
INVERSE_TABLES := $(BUILD)/gt864_fr0_inverse_tables.h
BARRETT_TABLES := $(BUILD)/gt864_fr0_inverse_barrett_tables.h
FULL_TEST := $(BUILD)/test-full-chain
BOUND_TEST := $(BUILD)/test-m5e-bound-2205

.PHONY: check proof source-audit linked-check clean

check: proof source-audit linked-check

$(BUILD):
	mkdir -p $@

$(CHAIN): prove_range_chain.py | $(BUILD)
	$(PYTHON) $< > $@
	$(PYTHON) -m json.tool $@ >/dev/null

$(FIXED): $(M5E)/generate_barrett_tables.py | $(BUILD)
	$(PYTHON) $< > $@
	$(PYTHON) -m json.tool $@ >/dev/null

proof: $(CHAIN) $(FIXED)
	$(PYTHON) audit_results.py

source-audit:
	$(MAKE) -C $(M5RD) proof static
	$(MAKE) -C $(M5C) check
	$(MAKE) -C $(M5D) check
	$(MAKE) -C $(M5E) check

$(BASEMUL_TABLES): $(M5C)/generate_tables.py | $(BUILD)
	$(PYTHON) $< --header $@ >/dev/null

$(INVERSE_TABLES): $(M5D)/generate_tables.py | $(BUILD)
	$(PYTHON) $< --header $@ >/dev/null

$(BARRETT_TABLES): $(M5E)/generate_barrett_tables.py | $(BUILD)
	$(PYTHON) $< --header $@

$(FULL_TEST): test_full_chain.c $(BASEMUL_TABLES) $(INVERSE_TABLES) \
		$(BARRETT_TABLES) $(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S \
		$(TOP)/gt864_top_split.s $(M5C)/gt864_fr0_basemul.c \
		$(M5E)/gt864_fr0_inverse_asm_wrapper.c \
		$(M5E)/gt864_fr0_inverse9_block.s $(M5E)/gt864_inverse16_blocks.s
	$(CC) $(CFLAGS) -I$(BUILD) -I$(M5C) -I$(M5E) -o $@ \
		test_full_chain.c $(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S \
		$(TOP)/gt864_top_split.s $(M5C)/gt864_fr0_basemul.c \
		$(M5E)/gt864_fr0_inverse_asm_wrapper.c \
		$(M5E)/gt864_fr0_inverse9_block.s $(M5E)/gt864_inverse16_blocks.s

$(BOUND_TEST): $(M5E)/test_gt864_inverse_asm.c $(INVERSE_TABLES) \
		$(BARRETT_TABLES) $(M5E)/gt864_fr0_inverse_asm_wrapper.c \
		$(M5E)/gt864_fr0_inverse9_block.s $(M5E)/gt864_inverse16_blocks.s \
		$(M5D)/gt864_fr0_inverse.c
	$(CC) $(CFLAGS) -DINPUT_BOUND=2205 -I$(BUILD) -I$(M5E) -o $@ \
		$(M5E)/test_gt864_inverse_asm.c \
		$(M5E)/gt864_fr0_inverse_asm_wrapper.c \
		$(M5E)/gt864_fr0_inverse9_block.s $(M5E)/gt864_inverse16_blocks.s \
		$(M5D)/gt864_fr0_inverse.c

linked-check: $(FULL_TEST) $(BOUND_TEST)
	$(FULL_TEST)
	$(BOUND_TEST)

clean:
	$(RM) -r $(BUILD)
