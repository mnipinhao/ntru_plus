PYTHON ?= python3
CC ?= cc
CFLAGS := -O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes -march=armv8-a+simd -ffunction-sections -fdata-sections
BUILD := build

.PHONY: all prepare check disassemble clean

all: $(BUILD)/test

prepare: $(BUILD)/p3b5_tables.h

$(BUILD):
	mkdir -p $@

$(BUILD)/p3b5_tables.h: prepare.py | $(BUILD)
	$(PYTHON) prepare.py

$(BUILD)/fused_tobytes.o: fused_tobytes.c fused_tobytes.h $(BUILD)/p3b5_tables.h
	$(CC) $(CFLAGS) -I$(BUILD) -c $< -o $@

$(BUILD)/test: harness.c $(BUILD)/fused_tobytes.o
	$(CC) $(CFLAGS) -I$(BUILD) harness.c $(BUILD)/fused_tobytes.o -o $@

check: $(BUILD)/test
	./$(BUILD)/test

disassemble: $(BUILD)/fused_tobytes.o
	objdump -dr $(BUILD)/fused_tobytes.o > $(BUILD)/fused_tobytes.dis

clean:
	rm -rf $(BUILD)
