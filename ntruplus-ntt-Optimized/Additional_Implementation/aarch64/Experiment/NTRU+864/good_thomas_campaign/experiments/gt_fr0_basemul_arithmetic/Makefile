CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
TARGET := $(BUILD_DIR)/test_gt864_fr0_basemul
TABLES := $(BUILD_DIR)/gt864_fr0_basemul_tables.h
MAP := $(BUILD_DIR)/map.json
RANGE := $(BUILD_DIR)/range.json

.PHONY: check clean

check: $(TARGET) $(MAP) $(RANGE)
	./$(TARGET)
	$(PYTHON) -m json.tool $(MAP) >/dev/null
	$(PYTHON) -m json.tool $(RANGE) >/dev/null

$(TABLES): generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) generate_tables.py --header $@ >/dev/null

$(MAP): generate_tables.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) generate_tables.py > $@

$(RANGE): prove_ranges.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_ranges.py > $@

$(TARGET): test_gt864_fr0_basemul.c gt864_fr0_basemul.c \
           gt864_fr0_basemul.h $(TABLES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(BUILD_DIR) -o $@ \
		test_gt864_fr0_basemul.c gt864_fr0_basemul.c

clean:
	$(RM) -r $(BUILD_DIR)
