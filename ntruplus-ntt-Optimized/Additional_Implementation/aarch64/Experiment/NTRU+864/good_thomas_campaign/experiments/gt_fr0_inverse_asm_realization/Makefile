CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
M5D := ../gt_fr0_inverse_consumer
TABLES := $(BUILD_DIR)/gt864_fr0_inverse_tables.h
BASELINE := $(BUILD_DIR)/bench_gt864_inverse_baseline
BENCH := $(BUILD_DIR)/bench_gt864_inverse
TEST := $(BUILD_DIR)/test_gt864_inverse_asm
AUDIT := $(BUILD_DIR)/audit.json

.PHONY: baseline benchmark check clean

baseline: $(BASELINE)
	./$(BASELINE)

check: $(TEST) $(AUDIT)
	./$(TEST)
	$(PYTHON) -m json.tool $(AUDIT) >/dev/null

benchmark: $(BENCH)
	./$(BENCH)

$(TABLES): $(M5D)/generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) $(M5D)/generate_tables.py --header $@ >/dev/null

$(BASELINE): bench_gt864_inverse.c $(M5D)/gt864_fr0_inverse.c \
             $(M5D)/gt864_fr0_inverse.h $(TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(BUILD_DIR) -o $@ \
		bench_gt864_inverse.c $(M5D)/gt864_fr0_inverse.c

$(BENCH): bench_gt864_inverse.c gt864_fr0_inverse_asm_wrapper.c \
          gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
          gt864_fr0_inverse_asm.h $(M5D)/gt864_fr0_inverse.c \
          $(M5D)/gt864_fr0_inverse.h $(TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DHAVE_ASM -I$(BUILD_DIR) -o $@ \
		bench_gt864_inverse.c gt864_fr0_inverse_asm_wrapper.c \
		gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
		$(M5D)/gt864_fr0_inverse.c

$(TEST): test_gt864_inverse_asm.c gt864_fr0_inverse_asm_wrapper.c \
         gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
         gt864_fr0_inverse_asm.h \
         $(M5D)/gt864_fr0_inverse.c $(M5D)/gt864_fr0_inverse.h $(TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(BUILD_DIR) -o $@ \
		test_gt864_inverse_asm.c gt864_fr0_inverse_asm_wrapper.c \
		gt864_fr0_inverse9_block.s gt864_inverse16_blocks.s \
		$(M5D)/gt864_fr0_inverse.c

$(AUDIT): audit_kernel.py $(TEST)
	$(PYTHON) audit_kernel.py $(TEST) > $@

clean:
	$(RM) -r $(BUILD_DIR)
