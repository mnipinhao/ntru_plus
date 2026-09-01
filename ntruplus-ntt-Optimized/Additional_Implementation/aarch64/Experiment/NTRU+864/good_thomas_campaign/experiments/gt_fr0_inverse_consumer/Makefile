CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
TARGET := $(BUILD_DIR)/test_gt864_fr0_inverse
TABLES := $(BUILD_DIR)/gt864_fr0_inverse_tables.h
BASEMUL_TABLES := $(BUILD_DIR)/gt864_fr0_basemul_tables.h
MAP := $(BUILD_DIR)/map.json
RANGE := $(BUILD_DIR)/range.json
CODEGEN := $(BUILD_DIR)/codegen.json
TOP := ../gt_2x9x16_ld3_top_split
NTT16 := ../gt_ntt16_producer_range
BOUNDARY := ../gt_boundary_cost_campaign
BASEMUL := ../gt_fr0_basemul_arithmetic
REFERENCE := ../../../../../../../Reference_Implementation/NTRU+864

.PHONY: check clean

check: $(TARGET) $(MAP) $(RANGE) $(CODEGEN)
	./$(TARGET)
	$(PYTHON) -m json.tool $(MAP) >/dev/null
	$(PYTHON) -m json.tool $(RANGE) >/dev/null
	$(PYTHON) -m json.tool $(CODEGEN) >/dev/null

$(TABLES): generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) generate_tables.py --header $@ >/dev/null

$(BASEMUL_TABLES): $(BASEMUL)/generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) $(BASEMUL)/generate_tables.py --header $@ >/dev/null

$(MAP): generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) generate_tables.py > $@

$(RANGE): prove_ranges.py generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_ranges.py > $@

$(CODEGEN): audit_codegen.py $(TARGET)
	$(PYTHON) audit_codegen.py $(TARGET) > $@

$(TARGET): test_gt864_fr0_inverse.c gt864_fr0_inverse.c \
           gt864_fr0_inverse.h $(TABLES) $(BASEMUL_TABLES) \
           $(TOP)/gt864_top_split.s $(NTT16)/gt864_ntt16.c \
           $(BOUNDARY)/gt864_boundary.c $(BASEMUL)/gt864_fr0_basemul.c \
           $(REFERENCE)/ntt.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(BUILD_DIR) -I$(REFERENCE) -o $@ \
		test_gt864_fr0_inverse.c gt864_fr0_inverse.c \
		$(TOP)/gt864_top_split.s $(NTT16)/gt864_ntt16.c \
		$(BOUNDARY)/gt864_boundary.c $(BASEMUL)/gt864_fr0_basemul.c \
		$(REFERENCE)/ntt.c

clean:
	$(RM) -r $(BUILD_DIR)
