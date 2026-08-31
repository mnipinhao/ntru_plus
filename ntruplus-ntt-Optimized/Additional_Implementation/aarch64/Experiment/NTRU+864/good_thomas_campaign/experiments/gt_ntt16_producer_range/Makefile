CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
TOP := ../gt_2x9x16_ld3_top_split
TARGET := $(BUILD_DIR)/test_gt864_ntt16
PROOF := $(BUILD_DIR)/range.json
CODEGEN := $(BUILD_DIR)/codegen.json

.PHONY: check inspect clean

check: $(TARGET) $(PROOF) $(CODEGEN)
	./$(TARGET)
	$(PYTHON) -m json.tool $(PROOF) >/dev/null
	$(PYTHON) -m json.tool $(CODEGEN) >/dev/null

$(TARGET): test_gt864_ntt16.c gt864_ntt16.c gt864_ntt16.h \
           gt864_ntt16_tables.h $(TOP)/gt864_top_split.s $(TOP)/gt864_top_split.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(TOP) -o $@ test_gt864_ntt16.c gt864_ntt16.c \
		$(TOP)/gt864_top_split.s

$(PROOF): prove_ranges.py gt864_ntt16_tables.h
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) prove_ranges.py > $@

$(CODEGEN): $(TARGET) gt864_ntt16.c audit_codegen.py
	$(PYTHON) audit_codegen.py $(TARGET) gt864_ntt16.c > $@

inspect: $(TARGET)
	otool -tvV $(TARGET) | sed -n '/_gt864_ntt16_p8_neon:/,/ret/p'

clean:
	$(RM) -r $(BUILD_DIR)
