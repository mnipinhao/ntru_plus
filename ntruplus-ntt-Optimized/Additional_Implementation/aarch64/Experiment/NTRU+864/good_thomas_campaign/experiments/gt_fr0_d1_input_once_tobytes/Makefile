PYTHON ?= python3
CC ?= cc
CFLAGS := -O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes -march=armv8-a+simd -ffunction-sections -fdata-sections
BUILD := build

.PHONY: all prepare check check-next disassemble clean
all: $(BUILD)/test
prepare: $(BUILD)/input_once_tobytes.c $(BUILD)/p3b6_tables.h
$(BUILD):
	mkdir -p $@
$(BUILD)/input_once_tobytes.c $(BUILD)/p3b6_tables.h: prepare.py | $(BUILD)
	$(PYTHON) prepare.py
$(BUILD)/input_once_tobytes.o: $(BUILD)/input_once_tobytes.c input_once_tobytes.h
	$(CC) $(CFLAGS) -I. -c $< -o $@
$(BUILD)/test: harness.c $(BUILD)/input_once_tobytes.o $(BUILD)/p3b6_tables.h
	$(CC) $(CFLAGS) -I. -I$(BUILD) harness.c $(BUILD)/input_once_tobytes.o -o $@
check: $(BUILD)/test
	./$(BUILD)/test
check-next:
	$(PYTHON) check_next_optimizations.py
disassemble: $(BUILD)/input_once_tobytes.o
	objdump -dr $< > $(BUILD)/input_once_tobytes.dis
clean:
	rm -rf $(BUILD)
