CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
M5D := ../gt_fr0_inverse_consumer
TABLES := $(BUILD_DIR)/gt864_fr0_inverse_tables.h
BARRETT_TABLES := $(BUILD_DIR)/gt864_fr0_inverse_barrett_tables.h
BARRETT_PROOF := $(BUILD_DIR)/barrett-proof.json
BARRETT_RANGE := $(BUILD_DIR)/barrett-range.json
BASELINE := $(BUILD_DIR)/bench_gt864_inverse_baseline
BENCH := $(BUILD_DIR)/bench_gt864_inverse
TEST := $(BUILD_DIR)/test_gt864_inverse_asm
AUDIT := $(BUILD_DIR)/audit.json

.PHONY: baseline benchmark check clean

baseline: $(BASELINE)
	./$(BASELINE)

check: $(TEST) $(AUDIT) $(BARRETT_PROOF) $(BARRETT_RANGE)
	./$(TEST)
	$(PYTHON) -m json.tool $(AUDIT) >/dev/null
	$(PYTHON) -m json.tool $(BARRETT_PROOF) >/dev/null
	$(PYTHON) -m json.tool $(BARRETT_RANGE) >/dev/null

benchmark: $(BENCH)
	./$(BENCH)

$(TABLES): $(M5D)/generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) $(M5D)/generate_tables.py --header $@ >/dev/null

$(BARRETT_TABLES): generate_barrett_tables.py $(M5D)/generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) generate_barrett_tables.py --header $@

$(BARRETT_PROOF): generate_barrett_tables.py $(M5D)/generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) generate_barrett_tables.py > $@

$(BARRETT_RANGE): prove_barrett_ranges.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_barrett_ranges.py > $@

$(BASELINE): bench_gt864_inverse.c $(M5D)/gt864_fr0_inverse.c \
             $(M5D)/gt864_fr0_inverse.h $(TABLES) $(BARRETT_TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(BUILD_DIR) -o $@ \
		bench_gt864_inverse.c $(M5D)/gt864_fr0_inverse.c

$(BENCH): bench_gt864_inverse.c gt864_fr0_inverse_asm_wrapper.c \
          gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
          gt864_fr0_inverse_asm.h $(M5D)/gt864_fr0_inverse.c \
          $(M5D)/gt864_fr0_inverse.h $(TABLES) $(BARRETT_TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DHAVE_ASM -I$(BUILD_DIR) -o $@ \
		bench_gt864_inverse.c gt864_fr0_inverse_asm_wrapper.c \
		gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
		$(M5D)/gt864_fr0_inverse.c

$(TEST): test_gt864_inverse_asm.c gt864_fr0_inverse_asm_wrapper.c \
         gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
         gt864_fr0_inverse_asm.h \
         $(M5D)/gt864_fr0_inverse.c $(M5D)/gt864_fr0_inverse.h $(TABLES) \
         $(BARRETT_TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(BUILD_DIR) -o $@ \
		test_gt864_inverse_asm.c gt864_fr0_inverse_asm_wrapper.c \
		gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
		$(M5D)/gt864_fr0_inverse.c

$(AUDIT): audit_kernel.py $(TEST)
	$(PYTHON) audit_kernel.py $(TEST) > $@

clean:
	$(RM) -r $(BUILD_DIR)
