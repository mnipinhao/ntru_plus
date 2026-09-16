CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD := build
M5D := ../gt_fr0_inverse_consumer
M5E := ../gt_fr0_inverse_asm_realization
TABLES := $(BUILD)/gt864_fr0_inverse_tables.h
BARRETT := $(BUILD)/gt864_fr0_inverse_barrett_tables.h

.PHONY: prepare check clean

prepare: $(BUILD)/gt864_inverse16_blocks_st1.s $(TABLES) $(BARRETT)

$(BUILD)/gt864_inverse16_blocks_st1.s: prepare.py $(M5E)/gt864_inverse16_blocks.s
	$(PYTHON) prepare.py

$(TABLES): $(M5D)/generate_tables.py
	@mkdir -p $(BUILD)
	$(PYTHON) $< --header $@ >/dev/null

$(BARRETT): $(M5E)/generate_barrett_tables.py $(M5D)/generate_tables.py
	@mkdir -p $(BUILD)
	$(PYTHON) $(M5E)/generate_barrett_tables.py --header $@

$(BUILD)/test-st1: test_st1.c gt864_inverse_st1_wrapper.c \
		$(BUILD)/gt864_inverse16_blocks_st1.s $(TABLES) $(BARRETT) \
		$(M5E)/gt864_fr0_inverse_asm_wrapper.c $(M5E)/gt864_fr0_inverse9_block.s \
		$(M5E)/gt864_inverse16_blocks.s $(M5D)/gt864_fr0_inverse.c
	$(CC) $(CFLAGS) -I$(BUILD) -I$(M5E) -I$(M5D) -o $@ \
		test_st1.c gt864_inverse_st1_wrapper.c \
		$(M5E)/gt864_fr0_inverse_asm_wrapper.c $(M5E)/gt864_fr0_inverse9_block.s \
		$(M5E)/gt864_inverse16_blocks.s $(BUILD)/gt864_inverse16_blocks_st1.s \
		$(M5D)/gt864_fr0_inverse.c

check: $(BUILD)/test-st1
	$(BUILD)/test-st1

clean:
	$(RM) -r $(BUILD)
