ROOT := ../..
EXP031 := ../gt32_encap_lifetime_031
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
COMMON := src/encap_b3_addm_032.c $(EXP031)/src/encap_lifetime_031.c \
	$(EXP031)/src/keygen_tables.c $(ROOT_C) $(ROOT_ASM) \
	generated/basemul_032.s

.PHONY: check benchmark clean

check: generated/proof.json generated/range_contract.h \
		generated/static_audit.json $(BUILD)/test_032
	./$(BUILD)/test_032
	python3 tools/generate_basemul.py --source $(ROOT)/basemul.s \
		--output generated/basemul_032.s --check
	python3 tools/generate_proof.py --root $(ROOT) --check \
		--output generated/proof.json --header generated/range_contract.h
	python3 tools/audit_binary.py --binary $(BUILD)/test_032 --check \
		--output generated/static_audit.json

generated/basemul_032.s: tools/generate_basemul.py $(ROOT)/basemul.s
	@mkdir -p generated
	python3 tools/generate_basemul.py --source $(ROOT)/basemul.s --output $@

generated/proof.json: tools/generate_proof.py generated/basemul_032.s \
		$(ROOT)/basemul.s
	python3 tools/generate_proof.py --root $(ROOT) --output $@ \
		--header generated/range_contract.h

generated/range_contract.h: generated/proof.json
	@test -f $@

$(BUILD)/test_032: tests/test_032.c generated/range_contract.h $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -Igenerated -I$(EXP031)/src \
		-o $@ tests/test_032.c $(COMMON)

generated/static_audit.json: $(BUILD)/test_032 tools/audit_binary.py
	python3 tools/audit_binary.py --binary $(BUILD)/test_032 --output $@

$(BUILD)/bench_032: bench/bench_032.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -Igenerated -I$(EXP031)/src \
		-I$(SUPERCOP_BENCH)/include/nontimecop/amd64 -o $@ \
		bench/bench_032.c $(COMMON) \
		$(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

benchmark: check $(BUILD)/bench_032
	python3 tools/run_benchmark.py --binary $(BUILD)/bench_032 \
		--launches 32 --output generated/benchmark.json

clean:
	$(RM) -r $(BUILD)
