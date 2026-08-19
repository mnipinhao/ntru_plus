ROOT := ../..
CC ?= gcc
CFLAGS := -O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-fomit-frame-pointer -ffunction-sections -fdata-sections \
	-Wall -Wextra -Wpedantic -Wshadow -Wmissing-prototypes
LDFLAGS := -Wl,--gc-sections
BUILD := build
SUPERCOP_BENCH := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209

ROOT_C := $(ROOT)/consts.c $(ROOT)/encap.c $(ROOT)/fips202.c \
	$(ROOT)/poly.c $(ROOT)/symmetric.c
ROOT_ASM := $(ROOT)/add.s $(ROOT)/basemul.s $(ROOT)/cbd.s \
	$(ROOT)/ntt.s $(ROOT)/ntt_m.s $(ROOT)/pack.s \
	$(ROOT)/KeccakP-1600-AVX2.s

.PHONY: check benchmark clean

check: generated/spec_gate.json generated/stack_audit.json $(BUILD)/test_031
	./$(BUILD)/test_031
	python3 tools/generate_spec_gate.py --check --output generated/spec_gate.json
	python3 tools/audit_stack.py --binary $(BUILD)/test_031 \
		--check --output generated/stack_audit.json

generated/spec_gate.json: tools/generate_spec_gate.py SPEC_INVARIANTS.md
	@mkdir -p generated
	python3 tools/generate_spec_gate.py --output $@

$(BUILD)/test_031: src/encap_lifetime_031.c src/keygen_tables.c tests/test_031.c \
		$(ROOT_C) $(ROOT_ASM)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ \
		tests/test_031.c src/encap_lifetime_031.c src/keygen_tables.c \
		$(ROOT_C) $(ROOT_ASM)

$(BUILD)/bench_031: src/encap_lifetime_031.c src/keygen_tables.c \
		bench/bench_031.c $(ROOT_C) $(ROOT_ASM)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc \
		-I$(SUPERCOP_BENCH)/include/nontimecop/amd64 -o $@ \
		bench/bench_031.c src/encap_lifetime_031.c src/keygen_tables.c \
		$(ROOT_C) $(ROOT_ASM) \
		$(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

benchmark: check $(BUILD)/bench_031
	python3 tools/run_benchmark.py --binary $(BUILD)/bench_031 \
		--launches 16 --output generated/benchmark.json

generated/stack_audit.json: $(BUILD)/test_031 tools/audit_stack.py
	python3 tools/audit_stack.py --binary $(BUILD)/test_031 --output $@

clean:
	$(RM) -r $(BUILD)
