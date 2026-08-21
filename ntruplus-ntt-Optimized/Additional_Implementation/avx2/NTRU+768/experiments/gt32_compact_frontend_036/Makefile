CC ?= gcc
PYTHON ?= python3
CFLAGS := -O3 -march=native -mtune=native -fwrapv -Wall -Wextra
BASE := ../avx2_gt32_tile4_official_001
BUILD := build
GENERATED := generated

.PHONY: all generate check bench clean
all: check

generate:
	$(PYTHON) tools/generate_gate.py

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/normal: generate | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DGT32_FRONTEND_GATE_VARIANTS -I$(BASE)/src \
		-o $@ $(GENERATED)/tile4_compact_gate.S $(GENERATED)/bench_compact_frontend.c

$(BUILD)/reversed: generate | $(BUILD)
	$(CC) $(CFLAGS) -Werror -DGT32_FRONTEND_GATE_VARIANTS -DGT32_COMPACT_FIRST \
		-I$(BASE)/src -o $@ $(GENERATED)/tile4_compact_gate.S \
		$(GENERATED)/bench_compact_frontend.c

check: $(BUILD)/normal $(BUILD)/reversed
	$(BUILD)/normal 50 1 >/dev/null
	$(BUILD)/reversed 50 1 >/dev/null
	! objdump -drwC -Mintel --disassemble=gt32_tile4_frontend_wide_raw_compact_u3_asm \
		$(BUILD)/normal | rg -n '\[(?:r|e)?sp[+\-]'
	nm -S --size-sort $(BUILD)/normal | rg 'frontend_wide_raw_(asm|compact_u3_asm)'

bench: check
	$(PYTHON) tools/run_gate.py --normal $(BUILD)/normal --reversed $(BUILD)/reversed \
		--iterations 4000 --launches 8 --cpu 1 --output results/benchmark.json

clean:
	rm -rf $(BUILD) $(GENERATED) results
