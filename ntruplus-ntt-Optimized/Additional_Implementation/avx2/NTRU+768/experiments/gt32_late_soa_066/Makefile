CC ?= gcc
PYTHON ?= python3
ROOT := ../..
OFFICIAL := $(ROOT)/../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
GTBASE := ../avx2_gt32_tile4_official_001

CFLAGS := -O3 -g -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-fomit-frame-pointer -ffunction-sections -fdata-sections \
	-Wall -Wextra -Werror -Wpedantic -Wmissing-prototypes -I$(ROOT) -Isrc \
	-I$(OFFICIAL)
LDFLAGS := -Wl,--gc-sections
KAT_CFLAGS := $(filter-out -Werror -Wmissing-prototypes,$(CFLAGS)) \
	-Wno-unused-result -Wno-unused-parameter -Wno-sign-compare

ROOT_C_NAMES := baseinv consts decap encap fips202 keygen poly symmetric
ROOT_S_NAMES := add basemul batch_inverse cbd crepmod3 invntt ntt ntt_m \
	ntt_p pack KeccakP-1600-AVX2
ROOT_C_OBJS := $(addprefix build/root_,$(addsuffix .o,$(ROOT_C_NAMES)))
ROOT_S_OBJS := $(addprefix build/root_,$(addsuffix .o,$(ROOT_S_NAMES)))
ROOT_CORE_OBJS := $(ROOT_C_OBJS) $(ROOT_S_OBJS)
ROOT_OBJS := $(ROOT_CORE_OBJS) build/randombytes.o
EXP_OBJS := build/decap_gate.o build/seam.o build/inverse_remainder.o
KAT_DIR := $(OFFICIAL)/kat
KAT_OBJS := build/kat_main.o build/kat_aes.o build/kat_rng.o

.PHONY: all test audit bench-primary bench-short pmu pmu-full kat clean
all: build/test build/bench_normal build/bench_reversed

build:
	mkdir -p build

build/root_%.o: $(ROOT)/%.c | build
	$(CC) $(CFLAGS) -c $< -o $@

build/root_%.o: $(ROOT)/%.s | build
	$(CC) $(CFLAGS) -c $< -o $@

build/randombytes.o: $(OFFICIAL)/randombytes.c | build
	$(CC) $(CFLAGS) -c $< -o $@

build/bench_randombytes.o: bench/deterministic_randombytes.c | build
	$(CC) $(CFLAGS) -c $< -o $@

build/decap_gate.o: src/decap_gate.c src/late066.h | build
	$(CC) $(CFLAGS) -c $< -o $@

build/seam.o: src/seam.S \
	../gt32_late_soa_064/src/full_bridge.S \
	../gt32_late_soa_063/src/late_soa.S \
	$(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/inverse_remainder.o: $(GTBASE)/src/tile4_basemul_attribution_asm.S \
	$(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/test.o: tests/test.c src/late066.h | build
	$(CC) $(CFLAGS) -c $< -o $@

build/bench.o: bench/bench.c src/late066.h | build
	$(CC) $(CFLAGS) -c $< -o $@

build/bench_primary.o: bench/bench_primary.c src/late066.h | build
	$(CC) $(CFLAGS) -c $< -o $@

build/root_kem.o: $(ROOT)/kem.c | build
	$(CC) $(CFLAGS) -c $< -o $@

build/kem_candidate.o: src/kem_candidate.c src/late066.h | build
	$(CC) $(CFLAGS) -c $< -o $@

build/kat_main.o: $(KAT_DIR)/PQCgenKAT_kem.c | build
	$(CC) $(KAT_CFLAGS) -I$(KAT_DIR) -c $< -o $@

build/kat_aes.o: $(KAT_DIR)/aes.c | build
	$(CC) $(KAT_CFLAGS) -I$(KAT_DIR) -c $< -o $@

build/kat_rng.o: $(KAT_DIR)/rng.c | build
	$(CC) $(KAT_CFLAGS) -I$(KAT_DIR) -c $< -o $@

build/test: build/test.o $(EXP_OBJS) $(ROOT_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/bench_normal: build/bench.o $(EXP_OBJS) $(ROOT_CORE_OBJS) \
	build/bench_randombytes.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/bench_reversed: $(ROOT_CORE_OBJS) build/inverse_remainder.o build/seam.o \
	build/decap_gate.o build/bench.o build/bench_randombytes.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/primary_normal: build/bench_primary.o $(EXP_OBJS) $(ROOT_CORE_OBJS) \
	build/bench_randombytes.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/primary_reversed: $(ROOT_CORE_OBJS) build/inverse_remainder.o build/seam.o \
	build/decap_gate.o build/bench_primary.o build/bench_randombytes.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/kat_control: build/root_kem.o $(KAT_OBJS) $(ROOT_C_OBJS) \
	$(ROOT_S_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/kat_candidate: build/kem_candidate.o $(KAT_OBJS) $(EXP_OBJS) \
	$(ROOT_C_OBJS) $(ROOT_S_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

test: build/test
	./build/test

audit: build/bench_normal build/bench_reversed
	$(PYTHON) tools/audit.py

bench-short: build/bench_normal build/bench_reversed
	$(PYTHON) tools/run_short.py

bench-primary: build/primary_normal build/primary_reversed
	$(PYTHON) tools/run_primary.py

pmu: build/bench_normal build/bench_reversed
	$(PYTHON) tools/run_pmu.py

pmu-full: build/bench_normal build/bench_reversed
	$(PYTHON) tools/run_full_pmu.py

kat: build/kat_control build/kat_candidate
	$(PYTHON) tools/run_kat.py

clean:
	rm -rf build results/*.json results/*.rsp
