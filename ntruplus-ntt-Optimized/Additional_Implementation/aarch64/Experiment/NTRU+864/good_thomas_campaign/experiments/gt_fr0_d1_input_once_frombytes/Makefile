PYTHON ?= python3
CC ?= cc
CFLAGS := -O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes -march=armv8-a+simd -ffunction-sections -fdata-sections
BUILD := build

.PHONY: all prepare check disassemble clean
all: $(BUILD)/test
prepare: $(BUILD)/input_once_frombytes.c $(BUILD)/p3b11_tables.h
$(BUILD):
	mkdir -p $@
$(BUILD)/input_once_frombytes.c $(BUILD)/p3b11_tables.h: prepare.py | $(BUILD)
	$(PYTHON) prepare.py
$(BUILD)/input_once_frombytes.o: $(BUILD)/input_once_frombytes.c input_once_frombytes.h
	$(CC) $(CFLAGS) -I. -c $< -o $@
$(BUILD)/test: harness.c $(BUILD)/input_once_frombytes.o $(BUILD)/p3b11_tables.h
	$(CC) $(CFLAGS) -I. -I$(BUILD) harness.c $(BUILD)/input_once_frombytes.o -o $@
check: $(BUILD)/test
	./$(BUILD)/test
disassemble: $(BUILD)/input_once_frombytes.o
	objdump -dr $< > $(BUILD)/input_once_frombytes.dis
clean:
	rm -rf $(BUILD)
