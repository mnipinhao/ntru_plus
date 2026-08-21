ROOT := ../..
CC ?= gcc
OBJCOPY ?= objcopy
CFLAGS := -O3 -mavx2 -march=native -mtune=native -fomit-frame-pointer \
	-ffunction-sections -fdata-sections -Wall -Wextra -Wpedantic
LDFLAGS := -no-pie -Wl,--gc-sections
BUILD := build
GENERATED := generated
SUPERCOP_BENCH := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
CPU_INC := -I$(SUPERCOP_BENCH)/include/nontimecop/amd64
CPU_LIB := $(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

.PHONY: all check benchmark pmu clean

all: check

$(GENERATED)/pack_ltc.s $(GENERATED)/pack_factor_ltc.s $(GENERATED)/pack_decode_ltc.s $(GENERATED)/basemul_ltc.s: tools/generate_candidates.py $(ROOT)/pack.s $(ROOT)/basemul.s
	@mkdir -p $(GENERATED)
	python3 tools/generate_candidates.py --pack $(ROOT)/pack.s --basemul $(ROOT)/basemul.s --out-dir $(GENERATED)

$(BUILD)/pack_control.o: $(ROOT)/pack.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/basemul_control.o: $(ROOT)/basemul.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_candidate_raw.o: $(GENERATED)/pack_ltc.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/basemul_candidate_raw.o: $(GENERATED)/basemul_ltc.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_candidate.o: $(BUILD)/pack_candidate_raw.o
	$(OBJCOPY) --prefix-symbols=gt041_ $< $@

$(BUILD)/pack_factor_candidate_raw.o: $(GENERATED)/pack_factor_ltc.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_factor_candidate.o: $(BUILD)/pack_factor_candidate_raw.o
	$(OBJCOPY) --prefix-symbols=gt041_ $< $@

$(BUILD)/pack_decode_candidate_raw.o: $(GENERATED)/pack_decode_ltc.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_decode_candidate.o: $(BUILD)/pack_decode_candidate_raw.o
	$(OBJCOPY) --prefix-symbols=gt041d_ $< $@

$(BUILD)/basemul_candidate.o: $(BUILD)/basemul_candidate_raw.o
	$(OBJCOPY) --prefix-symbols=gt041_ $< $@

$(BUILD)/tables.o: src/tables_041.c
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<

$(BUILD)/bench_normal: bench/bench_041.c $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o $(BUILD)/basemul_control.o $(BUILD)/basemul_candidate.o $(BUILD)/tables.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_reversed: bench/bench_041.c $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o $(BUILD)/basemul_control.o $(BUILD)/basemul_candidate.o $(BUILD)/tables.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_041.c \
		$(BUILD)/pack_candidate.o $(BUILD)/pack_control.o \
		$(BUILD)/basemul_candidate.o $(BUILD)/basemul_control.o \
		$(BUILD)/tables.o $(CPU_LIB)

$(BUILD)/bench_factor_normal: bench/bench_041.c $(BUILD)/pack_control.o $(BUILD)/pack_factor_candidate.o $(BUILD)/basemul_control.o $(BUILD)/basemul_candidate.o $(BUILD)/tables.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_factor_reversed: bench/bench_041.c $(BUILD)/pack_control.o $(BUILD)/pack_factor_candidate.o $(BUILD)/basemul_control.o $(BUILD)/basemul_candidate.o $(BUILD)/tables.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_041.c \
		$(BUILD)/pack_factor_candidate.o $(BUILD)/pack_control.o \
		$(BUILD)/basemul_candidate.o $(BUILD)/basemul_control.o \
		$(BUILD)/tables.o $(CPU_LIB)

$(BUILD)/bench_decode_normal: bench/bench_decode_041.c $(BUILD)/pack_control.o $(BUILD)/pack_decode_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_decode_reversed: bench/bench_decode_041.c $(BUILD)/pack_control.o $(BUILD)/pack_decode_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_decode_041.c \
		$(BUILD)/pack_decode_candidate.o $(BUILD)/pack_control.o $(CPU_LIB)

$(BUILD)/pmu: bench/pmu_041.c $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o $(BUILD)/basemul_control.o $(BUILD)/basemul_candidate.o $(BUILD)/tables.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -o $@ $^

$(BUILD)/pmu_factor: bench/pmu_041.c $(BUILD)/pack_control.o $(BUILD)/pack_factor_candidate.o $(BUILD)/basemul_control.o $(BUILD)/basemul_candidate.o $(BUILD)/tables.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -o $@ $^

check: $(BUILD)/bench_normal $(BUILD)/bench_reversed $(BUILD)/bench_factor_normal $(BUILD)/bench_factor_reversed $(BUILD)/bench_decode_normal $(BUILD)/bench_decode_reversed
	./$(BUILD)/bench_normal >/dev/null
	./$(BUILD)/bench_reversed >/dev/null
	./$(BUILD)/bench_factor_normal >/dev/null
	./$(BUILD)/bench_factor_reversed >/dev/null
	./$(BUILD)/bench_decode_normal >/dev/null
	./$(BUILD)/bench_decode_reversed >/dev/null
	python3 tools/audit.py --root $(ROOT) --build $(BUILD) --output $(GENERATED)/load_map.json

benchmark: check
	python3 tools/run_benchmark.py --normal $(BUILD)/bench_normal --reversed $(BUILD)/bench_reversed --launches 16 --output $(GENERATED)/benchmark.json
	python3 tools/run_benchmark.py --normal $(BUILD)/bench_factor_normal --reversed $(BUILD)/bench_factor_reversed --launches 16 --output $(GENERATED)/benchmark_factor.json
	python3 tools/run_decode.py --normal $(BUILD)/bench_decode_normal --reversed $(BUILD)/bench_decode_reversed --launches 16 --output $(GENERATED)/benchmark_decode.json

pmu: $(BUILD)/pmu $(BUILD)/pmu_factor
	python3 tools/run_pmu.py --binary $(BUILD)/pmu --launches 8 --output $(GENERATED)/pmu.json
	python3 tools/run_pmu.py --binary $(BUILD)/pmu_factor --launches 8 --output $(GENERATED)/pmu_factor.json

clean:
	$(RM) -r $(BUILD) $(GENERATED)
