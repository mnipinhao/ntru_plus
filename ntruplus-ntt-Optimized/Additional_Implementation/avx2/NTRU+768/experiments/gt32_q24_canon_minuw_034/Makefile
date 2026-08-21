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
ROOT_C := $(ROOT)/consts.c $(ROOT)/fips202.c $(ROOT)/poly.c $(ROOT)/symmetric.c \
	../gt32_encap_lifetime_031/src/keygen_tables.c
ROOT_ASM_NO_PACK := $(ROOT)/add.s $(ROOT)/basemul.s $(ROOT)/cbd.s \
	$(ROOT)/ntt.s $(ROOT)/ntt_m.s $(ROOT)/KeccakP-1600-AVX2.s

.PHONY: all check benchmark pmu clean

all: check

$(GENERATED)/pack_minuw.s: tools/generate_candidate.py $(ROOT)/pack.s
	@mkdir -p $(GENERATED)
	python3 $< --input $(ROOT)/pack.s --output $@

$(BUILD)/pack_control.o: $(ROOT)/pack.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_candidate_raw.o: $(GENERATED)/pack_minuw.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_candidate.o: $(BUILD)/pack_candidate_raw.o
	$(OBJCOPY) --prefix-symbols=gt034_ $< $@

$(BUILD)/encap_control.o: src/encap_034.c
	$(CC) $(CFLAGS) -I$(ROOT) -DENCAP_NAME=gt034_encap_control \
		-DPACK_LAZY=ntruplus768_pack_m_lazy10788_avx2 \
		-DPACK_HIGH=ntruplus768_pack_m_highrange12699_avx2 -c -o $@ $<

$(BUILD)/encap_candidate.o: src/encap_034.c
	$(CC) $(CFLAGS) -I$(ROOT) -DENCAP_NAME=gt034_encap_candidate \
		-DPACK_LAZY=gt034_ntruplus768_pack_m_lazy10788_avx2 \
		-DPACK_HIGH=gt034_ntruplus768_pack_m_highrange12699_avx2 -c -o $@ $<

$(BUILD)/test_034: tests/test_034.c $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -o $@ tests/test_034.c \
		$(BUILD)/pack_control.o $(BUILD)/pack_candidate.o

$(BUILD)/bench_normal: bench/bench_034.c $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_034.c \
		$(BUILD)/pack_control.o $(BUILD)/pack_candidate.o $(CPU_LIB)

$(BUILD)/bench_reversed: bench/bench_034.c $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_034.c \
		$(BUILD)/pack_candidate.o $(BUILD)/pack_control.o $(CPU_LIB)

$(BUILD)/bench_fixed_control: bench/bench_fixed_034.c $(BUILD)/pack_control.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ $< \
		$(BUILD)/pack_control.o $(CPU_LIB)

$(BUILD)/bench_fixed_candidate: bench/bench_fixed_034.c $(BUILD)/pack_candidate_raw.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ $< \
		$(BUILD)/pack_candidate_raw.o $(CPU_LIB)

$(BUILD)/test_full_034: tests/test_full_034.c $(BUILD)/encap_control.o \
		$(BUILD)/encap_candidate.o $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -o $@ tests/test_full_034.c \
		$(BUILD)/encap_control.o $(BUILD)/encap_candidate.o \
		$(BUILD)/pack_control.o $(BUILD)/pack_candidate.o \
		$(ROOT_C) $(ROOT_ASM_NO_PACK)

$(BUILD)/bench_full_normal: bench/bench_full_034.c $(BUILD)/encap_control.o \
		$(BUILD)/encap_candidate.o $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_full_034.c \
		$(BUILD)/encap_control.o $(BUILD)/encap_candidate.o \
		$(BUILD)/pack_control.o $(BUILD)/pack_candidate.o \
		$(ROOT_C) $(ROOT_ASM_NO_PACK) $(CPU_LIB)

$(BUILD)/bench_full_reversed: bench/bench_full_034.c $(BUILD)/encap_control.o \
		$(BUILD)/encap_candidate.o $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ bench/bench_full_034.c \
		$(BUILD)/encap_candidate.o $(BUILD)/encap_control.o \
		$(BUILD)/pack_candidate.o $(BUILD)/pack_control.o \
		$(ROOT_C) $(ROOT_ASM_NO_PACK) $(CPU_LIB)

$(BUILD)/pmu_full_normal: bench/bench_full_034.c $(BUILD)/encap_control.o \
		$(BUILD)/encap_candidate.o $(BUILD)/pack_control.o $(BUILD)/pack_candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -DGT034_PMU_MODE -I$(ROOT) $(CPU_INC) -o $@ \
		bench/bench_full_034.c $(BUILD)/encap_control.o $(BUILD)/encap_candidate.o \
		$(BUILD)/pack_control.o $(BUILD)/pack_candidate.o \
		$(ROOT_C) $(ROOT_ASM_NO_PACK) $(CPU_LIB)

check: $(BUILD)/test_034 $(BUILD)/test_full_034 $(BUILD)/bench_normal \
		$(BUILD)/bench_reversed $(BUILD)/bench_fixed_control \
		$(BUILD)/bench_fixed_candidate $(BUILD)/bench_full_normal \
		$(BUILD)/bench_full_reversed
	python3 tools/generate_candidate.py --input $(ROOT)/pack.s \
		--output $(GENERATED)/pack_minuw.s --check
	./$(BUILD)/test_034
	./$(BUILD)/test_full_034
	python3 tools/audit_static.py --binary $(BUILD)/bench_normal \
		--output $(GENERATED)/static_normal.json --check
	python3 tools/audit_static.py --binary $(BUILD)/bench_reversed \
		--output $(GENERATED)/static_reversed.json --check
	python3 tools/audit_fixed_geometry.py --control $(BUILD)/bench_fixed_control \
		--candidate $(BUILD)/bench_fixed_candidate \
		--output $(GENERATED)/fixed_geometry.json --check

benchmark: check
	python3 tools/run_fixed_benchmark.py --control $(BUILD)/bench_fixed_control \
		--candidate $(BUILD)/bench_fixed_candidate --launches 48 \
		--output $(GENERATED)/benchmark_fixed_address.json
	python3 tools/run_benchmark.py --normal $(BUILD)/bench_normal \
		--reversed $(BUILD)/bench_reversed --launches 32 \
		--output $(GENERATED)/benchmark.json
	python3 tools/run_full_benchmark.py --normal $(BUILD)/bench_full_normal \
		--reversed $(BUILD)/bench_full_reversed --launches 32 \
		--output $(GENERATED)/benchmark_full.json

pmu: $(BUILD)/pmu_full_normal
	python3 tools/run_pmu.py --binary $< --launches 8 \
		--output $(GENERATED)/pmu_full.json

clean:
	$(RM) -r $(BUILD)
