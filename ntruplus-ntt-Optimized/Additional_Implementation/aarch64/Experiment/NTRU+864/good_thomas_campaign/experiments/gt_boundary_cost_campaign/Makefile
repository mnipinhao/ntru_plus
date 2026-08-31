CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd
BUILD_DIR ?= build
TEST := $(BUILD_DIR)/test_gt864_boundary
BENCH := $(BUILD_DIR)/bench_gt864_boundary
ASM := $(BUILD_DIR)/gt864_boundary.s
ROTATION := $(BUILD_DIR)/rotation_search.json
ABI := $(BUILD_DIR)/abi_metadata.json
CODEGEN := $(BUILD_DIR)/codegen.json
DIAGNOSTIC := $(BUILD_DIR)/diagnostic_results.json

.PHONY: all check bench campaign codegen metadata clean asm

all: $(TEST)

$(TEST): test_gt864_boundary.c gt864_boundary.c gt864_boundary.h gt864_boundary_tables.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -o $@ test_gt864_boundary.c gt864_boundary.c

check: $(TEST) $(ROTATION) $(ABI)
	./$(TEST)
	$(PYTHON) -m json.tool $(ROTATION) >/dev/null
	$(PYTHON) -m json.tool $(ABI) >/dev/null

$(ROTATION): search_rotations.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) search_rotations.py > $@

$(BENCH): bench_gt864_boundary.c gt864_boundary.c gt864_boundary.h gt864_boundary_tables.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -o $@ bench_gt864_boundary.c gt864_boundary.c

bench: check $(BENCH)
	./$(BENCH)

campaign: check codegen $(BENCH)
	$(PYTHON) run_campaign.py ./$(BENCH) > $(DIAGNOSTIC)
	$(PYTHON) -m json.tool $(DIAGNOSTIC) >/dev/null

asm: $(ASM)

codegen: $(BENCH) $(ASM)
	$(PYTHON) analyze_codegen.py $(ASM) $(BENCH) > $(CODEGEN)
	$(PYTHON) -m json.tool $(CODEGEN) >/dev/null

metadata: $(ROTATION) $(ABI)

$(ABI): emit_abi_metadata.py
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) emit_abi_metadata.py > $@

$(ASM): gt864_boundary.c gt864_boundary.h gt864_boundary_tables.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -S -o $@ gt864_boundary.c

clean:
	$(RM) -r $(BUILD_DIR)
