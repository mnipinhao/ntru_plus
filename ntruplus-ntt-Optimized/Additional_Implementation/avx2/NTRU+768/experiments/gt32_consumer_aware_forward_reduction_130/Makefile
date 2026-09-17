PYTHON ?= python3
CC ?= gcc
ROOT := ../..
ARTIFACT := generated/consumer_range.json
ASM := generated/ntt130.s
BUILD := build
SUPER := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
CFLAGS := -O3 -mavx2 -march=native -ffunction-sections -fdata-sections -Wall -Wextra -Werror
LDFLAGS := -Wl,--gc-sections

.PHONY: all check clean

all: check

$(ARTIFACT): tools/gate.py \
	../gt32_mixed_ctgs_range_128/generated/search.json \
	../gt32_encap_b3_addm_032/generated/proof.json \
	$(ROOT)/basemul.s
	mkdir -p generated
	$(PYTHON) tools/gate.py --root $(ROOT) --output $@

$(ASM): tools/generate_asm.py ../gt32_mixed_ctgs_range_128/generated/search.json $(ROOT)/ntt_m.s
	mkdir -p generated
	$(PYTHON) tools/generate_asm.py --root $(ROOT) --output $@

$(BUILD)/test: tests/test.c tests/tables.c $(ASM) $(ROOT)/ntt.s $(ROOT)/basemul.s $(ROOT)/pack.s $(ROOT)/consts.c
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -o $@ tests/test.c $(ASM) \
		$(ROOT)/ntt.s $(ROOT)/basemul.s $(ROOT)/pack.s $(ROOT)/consts.c tests/tables.c

$(BUILD)/bench: bench/bench.c $(ASM)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -I$(SUPER)/include/nontimecop/amd64 \
		-o $@ bench/bench.c $(ASM) $(SUPER)/lib/nontimecop/amd64/libcpucycles.a

check: $(ARTIFACT) $(BUILD)/test
	$(PYTHON) tools/gate.py --root $(ROOT) --output $< --check
	$(PYTHON) tools/generate_asm.py --root $(ROOT) --output $(ASM) --check
	$(BUILD)/test
	@if objdump -d $(BUILD)/test | sed -n '/<gt32_130_candidate_normal>:/,/^$$/p' | grep -Eq '(%rsp|%rbp)'; then echo 'candidate stack reference found' >&2; exit 1; fi

benchmark: check $(BUILD)/bench
	$(PYTHON) tools/run_benchmark.py --binary $(BUILD)/bench --output generated/benchmark.json --launches 16

clean:
	rm -rf generated build
