ROOT := ../..
EXP031 := ../gt32_encap_lifetime_031
EXP032 := ../gt32_encap_b3_addm_032
EXP068 := ../gt32_encap_consumer_abi_068
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
COMMON := $(EXP068)/src/gate_068.c $(EXP031)/src/keygen_tables.c \
	$(ROOT_C) $(ROOT_ASM) $(EXP032)/generated/basemul_032.s \
	$(EXP068)/generated/candidate_068.s generated/candidate_069.s
INCLUDES := -I$(ROOT) -Isrc -I$(EXP068)/src

.PHONY: check benchmark clean

check: generated/candidate_069.s $(BUILD)/candidate_069.o \
	generated/shape_sweep.json $(BUILD)/test_069
	./$(BUILD)/test_069
	PYTHONPATH=$(EXP068)/tools python3 tools/generate_candidate.py \
		--basemul $(ROOT)/basemul.s --pack $(ROOT)/pack.s \
		--output generated/candidate_069.s --check
	python3 tools/audit_shapes.py --object $(BUILD)/candidate_069.o \
		--output generated/shape_sweep.json --check

generated/candidate_069.s: tools/generate_candidate.py \
	$(EXP068)/tools/generate_candidate.py $(EXP068)/tools/generate_mapping.py \
	$(ROOT)/basemul.s $(ROOT)/pack.s
	PYTHONPATH=$(EXP068)/tools python3 tools/generate_candidate.py \
		--basemul $(ROOT)/basemul.s --pack $(ROOT)/pack.s --output $@

$(BUILD)/candidate_069.o: generated/candidate_069.s
	@mkdir -p $(BUILD)
	$(CC) -c -mavx2 -o $@ $<

generated/shape_sweep.json: $(BUILD)/candidate_069.o tools/audit_shapes.py
	python3 tools/audit_shapes.py --object $(BUILD)/candidate_069.o --output $@

$(BUILD)/test_069: tests/test_069.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) $(INCLUDES) -o $@ tests/test_069.c $(COMMON)

$(BUILD)/bench_069: bench/bench_069.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) $(INCLUDES) \
		-I$(SUPERCOP_BENCH)/include/nontimecop/amd64 -o $@ \
		bench/bench_069.c $(COMMON) \
		$(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

$(BUILD)/pmu_069: bench/pmu_069.c $(COMMON)
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) $(INCLUDES) -o $@ bench/pmu_069.c $(COMMON)

benchmark: check $(BUILD)/bench_069 $(BUILD)/pmu_069
	python3 tools/run_benchmark.py --binary $(BUILD)/bench_069 \
		--launches 16 --output generated/benchmark.json
	python3 tools/run_pmu.py --binary $(BUILD)/pmu_069 --samples 5 \
		--output generated/pmu.json

clean:
	$(RM) -r $(BUILD)
