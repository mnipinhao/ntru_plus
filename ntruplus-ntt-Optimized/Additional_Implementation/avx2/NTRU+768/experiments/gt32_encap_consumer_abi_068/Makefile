ROOT := ../..
EXP032 := ../gt32_encap_b3_addm_032
EXP031 := ../gt32_encap_lifetime_031
CC ?= gcc
CFLAGS := -O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-fomit-frame-pointer -ffunction-sections -fdata-sections \
	-Wall -Wextra -Wpedantic -Wshadow -Wmissing-prototypes
LDFLAGS := -Wl,--gc-sections
BUILD := build
SUPERCOP_BENCH := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209

ROOT_C := $(ROOT)/consts.c $(ROOT)/fips202.c $(ROOT)/poly.c $(ROOT)/symmetric.c
ROOT_ASM := $(ROOT)/add.s $(ROOT)/basemul.s $(ROOT)/cbd.s $(ROOT)/ntt.s \
	$(ROOT)/ntt_m.s $(ROOT)/pack.s $(ROOT)/KeccakP-1600-AVX2.s
COMMON := src/gate_068.c $(EXP031)/src/keygen_tables.c $(ROOT_C) $(ROOT_ASM) \
	$(EXP032)/generated/basemul_032.s generated/candidate_068.s

.PHONY: check benchmark clean

check: generated/mapping.json generated/mapping.csv generated/candidate_068.s \
	$(BUILD)/test_068 generated/static_audit.json
	./$(BUILD)/test_068
	python3 tools/generate_mapping.py --pack $(ROOT)/pack.s \
		--output generated/mapping.json --csv generated/mapping.csv --check
	PYTHONPATH=tools python3 tools/generate_candidate.py \
		--basemul $(ROOT)/basemul.s --pack $(ROOT)/pack.s \
		--output generated/candidate_068.s --check
	python3 tools/audit_binary.py --binary $(BUILD)/test_068 \
		--output generated/static_audit.json --check

generated/mapping.json generated/mapping.csv: tools/generate_mapping.py $(ROOT)/pack.s
	python3 tools/generate_mapping.py --pack $(ROOT)/pack.s \
		--output generated/mapping.json --csv generated/mapping.csv

generated/candidate_068.s: tools/generate_candidate.py tools/generate_mapping.py \
	$(ROOT)/basemul.s $(ROOT)/pack.s
	PYTHONPATH=tools python3 tools/generate_candidate.py \
		--basemul $(ROOT)/basemul.s --pack $(ROOT)/pack.s --output $@

$(BUILD)/test_068: tests/test_068.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ tests/test_068.c $(COMMON)

$(BUILD)/bench_068: bench/bench_068.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc \
		-I$(SUPERCOP_BENCH)/include/nontimecop/amd64 -o $@ \
		bench/bench_068.c $(COMMON) \
		$(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

$(BUILD)/pmu_068: bench/pmu_068.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ \
		bench/pmu_068.c $(COMMON)

generated/static_audit.json: $(BUILD)/test_068 tools/audit_binary.py
	python3 tools/audit_binary.py --binary $(BUILD)/test_068 --output $@

benchmark: check $(BUILD)/bench_068
	python3 tools/run_benchmark.py --binary $(BUILD)/bench_068 \
		--launches 16 --output generated/benchmark.json
	$(MAKE) $(BUILD)/pmu_068
	python3 tools/run_pmu.py --binary $(BUILD)/pmu_068 --samples 5 \
		--output generated/pmu.json

clean:
	$(RM) -r $(BUILD)
