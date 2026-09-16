PYTHON ?= python3
CC ?= cc
CFLAGS := -O3 -std=c11 -Wall -Wextra -Werror -Wmissing-prototypes -march=armv8-a+simd -ffunction-sections -fdata-sections
BUILD := build

.PHONY: all check analyze clean
all: $(BUILD)/test
$(BUILD):
	mkdir -p $@
$(BUILD)/pack8.c $(BUILD)/pack16.c: prepare.py | $(BUILD)
	$(PYTHON) prepare.py
$(BUILD)/%.o: $(BUILD)/%.c paired_pack16.h
	$(CC) $(CFLAGS) -I. -c $< -o $@
$(BUILD)/test: harness.c $(BUILD)/pack8.o $(BUILD)/pack16.o
	$(CC) $(CFLAGS) -I. -o $@ $^
check: $(BUILD)/test
	./$(BUILD)/test
analyze:
	$(PYTHON) analyze_integration.py
clean:
	rm -rf $(BUILD)
