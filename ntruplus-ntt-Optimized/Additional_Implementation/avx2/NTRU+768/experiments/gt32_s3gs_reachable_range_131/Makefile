PYTHON ?= python3
CC ?= gcc
ROOT := ../..
PARENT := ../gt32_consumer_aware_forward_reduction_130
JSON := generated/reachable_range.json
HEADER := generated/witness.h
BUILD := build
CFLAGS := -O3 -mavx2 -march=native -ffunction-sections -fdata-sections -Wall -Wextra -Werror
LDFLAGS := -Wl,--gc-sections

.PHONY: all check clean

all: check

$(JSON) $(HEADER): tools/prove.py
	mkdir -p generated
	$(PYTHON) tools/prove.py --root $(ROOT) --json $(JSON) --header $(HEADER)

$(BUILD)/witness: tests/witness.c $(JSON) $(HEADER) $(PARENT)/generated/ntt130.s \
	$(ROOT)/ntt.s $(ROOT)/consts.c $(PARENT)/tests/tables.c
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Igenerated -o $@ tests/witness.c \
		$(PARENT)/generated/ntt130.s $(ROOT)/ntt.s $(ROOT)/consts.c $(PARENT)/tests/tables.c

check: $(JSON) $(HEADER) $(BUILD)/witness
	$(PYTHON) tools/prove.py --root $(ROOT) --json $(JSON) --header $(HEADER) --check
	$(BUILD)/witness

clean:
	rm -rf generated build
