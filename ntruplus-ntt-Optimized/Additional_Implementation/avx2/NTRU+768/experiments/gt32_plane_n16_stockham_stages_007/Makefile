PYTHON ?= python3
GENERATOR := tools/generate_stockham_gate.py
OUTPUT := generated/plane_n16_stockham_gate.json
ASM := generated/plane_n16_probe.S
CONTROL_ASM := generated/progressive_control.S
PAIR_ASM := generated/pair_control.S
HEADER := generated/plane_n16_probe.h
BUILD := build
CFLAGS := -O3 -mavx2 -Wall -Wextra -Werror

.PHONY: all generate asm test bench report check clean

all: check

generate:
	$(PYTHON) $(GENERATOR) --output $(OUTPUT)

asm: generate
	$(PYTHON) tools/emit_stockham_asm.py --gate $(OUTPUT) --asm $(ASM) --header $(HEADER)
	$(PYTHON) tools/extract_progressive_control.py --output $(CONTROL_ASM)
	$(PYTHON) tools/extract_pair_control.py --output $(PAIR_ASM)

$(BUILD)/test_stockham: asm test_stockham.c
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I. test_stockham.c $(ASM) $(CONTROL_ASM) $(PAIR_ASM) -o $@

test: $(BUILD)/test_stockham
	$(BUILD)/test_stockham

$(BUILD)/bench_stockham: asm bench_stockham.c
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I. bench_stockham.c $(ASM) $(CONTROL_ASM) $(PAIR_ASM) -o $@

bench: $(BUILD)/bench_stockham
	$(BUILD)/bench_stockham 100000 1 both

report:
	$(PYTHON) tools/summarize_benchmark.py --gate $(OUTPUT) \
		--benchmark generated/plane_n16_stockham_benchmark.json \
		--output generated/plane_n16_stockham_decision.json

check: test
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp

clean:
	rm -rf $(BUILD)
