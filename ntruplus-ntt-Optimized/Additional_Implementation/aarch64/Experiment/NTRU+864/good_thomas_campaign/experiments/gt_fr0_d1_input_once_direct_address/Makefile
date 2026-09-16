PYTHON ?= python3
CC ?= cc
CFLAGS := -O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes -march=armv8-a+simd -ffunction-sections -fdata-sections
BUILD := build
P3B6 := ../gt_fr0_d1_input_once_tobytes

.PHONY: all check clean
all: $(BUILD)/test
$(BUILD):
	mkdir -p $@
$(BUILD)/direct_address_tobytes.c: prepare.py | $(BUILD)
	$(PYTHON) prepare.py
$(BUILD)/candidate.o: $(BUILD)/direct_address_tobytes.c direct_address_tobytes.h
	$(CC) $(CFLAGS) -I. -c $< -o $@
$(BUILD)/control.o: $(P3B6)/build/input_once_tobytes.c $(P3B6)/input_once_tobytes.h | $(BUILD)
	$(CC) $(CFLAGS) -I$(P3B6) -c $< -o $@
$(BUILD)/test: harness.c $(BUILD)/control.o $(BUILD)/candidate.o
	$(CC) $(CFLAGS) -I. -o $@ $^
check: $(BUILD)/test
	./$(BUILD)/test
clean:
	rm -rf $(BUILD)
