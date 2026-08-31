CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
M4 := ../gt_boundary_cost_campaign
TARGET := $(BUILD_DIR)/test_gt864_fr0_asm
BENCH := $(BUILD_DIR)/bench_gt864_fr0
RANGE := $(BUILD_DIR)/range.json
AUDIT := $(BUILD_DIR)/audit.json
MAPS := $(BUILD_DIR)/maps.json
MAP_HEADER := $(BUILD_DIR)/gt864_fr0_maps.h

.PHONY: check bench clean

check: $(TARGET) $(RANGE) $(AUDIT) $(MAPS) $(MAP_HEADER)
	./$(TARGET)
	$(PYTHON) -m json.tool $(RANGE) >/dev/null
	$(PYTHON) -m json.tool $(AUDIT) >/dev/null
	$(PYTHON) -m json.tool $(MAPS) >/dev/null

$(TARGET): test_gt864_fr0_asm.c gt864_fr0_wrapper.c gt864_fr0_block.s gt864_fr0_asm.h \
           $(M4)/gt864_boundary.c $(M4)/gt864_boundary.h $(M4)/gt864_boundary_tables.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(M4) -o $@ test_gt864_fr0_asm.c \
		gt864_fr0_wrapper.c gt864_fr0_block.s $(M4)/gt864_boundary.c

$(RANGE): prove_ranges.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_ranges.py > $@

$(AUDIT): $(TARGET) gt864_fr0_block.s audit_kernel.py
	$(PYTHON) audit_kernel.py $(TARGET) gt864_fr0_block.s > $@

$(MAPS): prove_maps.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_maps.py > $@

$(MAP_HEADER): prove_maps.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_maps.py --header $@ >/dev/null

$(BENCH): bench_gt864_fr0.c gt864_fr0_wrapper.c gt864_fr0_block.s gt864_fr0_asm.h \
          $(M4)/gt864_boundary.c $(M4)/gt864_boundary.h $(M4)/gt864_boundary_tables.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(M4) -o $@ bench_gt864_fr0.c \
		gt864_fr0_wrapper.c gt864_fr0_block.s $(M4)/gt864_boundary.c

bench: check $(BENCH)
	./$(BENCH)

clean:
	$(RM) -r $(BUILD_DIR)
