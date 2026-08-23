CC ?= gcc
PYTHON ?= python3
ROOT := ../..
OFFICIAL := $(ROOT)/../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
GTBASE := ../avx2_gt32_tile4_official_001
E066 := ../gt32_late_soa_066
SUPER := /home/nuc/supercop-20260627
SUPERBENCH := $(SUPER)/bench/nucpromtlhcubinucai1ummsb209

CPPFLAGS := -DSUPERCOP -I$(ROOT) -Isrc -I$(OFFICIAL) -I$(SUPER)/include \
	-I$(SUPERBENCH)/include -I$(SUPERBENCH)/include/amd64 \
	-I$(SUPERBENCH)/include/nontimecop/amd64
CFLAGS := -O3 -g -mavx2 -mbmi2 -mpopcnt -maes -march=native \
	-mtune=native -fwrapv -fPIC -fPIE -fomit-frame-pointer \
	-ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wpedantic \
	-Wmissing-prototypes -Wredundant-decls -Wshadow -Wpointer-arith
LDFLAGS := -pie -Wl,--gc-sections
KAT_CFLAGS := $(filter-out -Werror -Wmissing-prototypes,$(CFLAGS)) \
	-Wno-unused-result -Wno-unused-parameter -Wno-sign-compare

ROOT_C_NAMES := baseinv consts encap fips202 keygen poly symmetric
ROOT_S_NAMES := add basemul batch_inverse cbd crepmod3 invntt ntt ntt_m \
	ntt_p pack KeccakP-1600-AVX2
ROOT_C_OBJS := $(addprefix build/root_,$(addsuffix .o,$(ROOT_C_NAMES)))
ROOT_S_OBJS := $(addprefix build/root_,$(addsuffix .o,$(ROOT_S_NAMES)))
ROOT_C_REVERSED := build/root_symmetric.o build/root_poly.o \
	build/root_keygen.o build/root_fips202.o build/root_encap.o \
	build/root_consts.o build/root_baseinv.o
ROOT_S_REVERSED := build/root_KeccakP-1600-AVX2.o build/root_pack.o \
	build/root_ntt_p.o build/root_ntt_m.o build/root_ntt.o \
	build/root_invntt.o build/root_crepmod3.o build/root_cbd.o \
	build/root_batch_inverse.o build/root_basemul.o build/root_add.o
EXP_OBJS := build/seam.o build/inverse_remainder.o
DUAL_OBJS := build/kem_dual.o build/decap_control.o build/decap_candidate.o
COMMON_OBJS := $(ROOT_C_OBJS) $(ROOT_S_OBJS) $(EXP_OBJS)
KAT_DIR := $(OFFICIAL)/kat
KAT_OBJS := build/kat_main.o build/kat_aes.o build/kat_rng.o

.PHONY: all test strict audit kat bench-primary pmu clean
all: build/test build/bench_normal build/bench_reversed

build:
	mkdir -p build results

build/root_%.o: $(ROOT)/%.c | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/root_%.o: $(ROOT)/%.s | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/decap_control.o: src/decap_control.c $(ROOT)/decap.c | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/decap_candidate.o: src/decap_candidate.c $(ROOT)/decap.c | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/kem_dual.o: src/kem_dual.c src/late067.h | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/support.o: src/supercop_support.c | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/bench_randombytes.o: bench/deterministic_randombytes.c | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/bench.o: bench/bench.c src/late067.h | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/test.o: tests/test.c src/late067.h | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/seam.o: $(E066)/src/seam.S \
	../gt32_late_soa_064/src/full_bridge.S \
	../gt32_late_soa_063/src/late_soa.S \
	$(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/inverse_remainder.o: $(GTBASE)/src/tile4_basemul_attribution_asm.S \
	$(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

build/test: build/test.o build/support.o build/bench_randombytes.o \
	$(DUAL_OBJS) $(COMMON_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

# Normal follows the production family order; Reversed deliberately reverses
# the production objects and the two Decap bodies while retaining one ELF.
build/bench_normal: build/bench.o build/support.o build/bench_randombytes.o \
	build/kem_dual.o build/decap_control.o build/decap_candidate.o \
	$(ROOT_C_OBJS) $(ROOT_S_OBJS) build/seam.o build/inverse_remainder.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/bench_reversed: build/bench.o build/support.o build/bench_randombytes.o \
	build/inverse_remainder.o build/seam.o $(ROOT_S_REVERSED) \
	$(ROOT_C_REVERSED) build/decap_candidate.o build/decap_control.o \
	build/kem_dual.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/kat_main.o: $(KAT_DIR)/PQCgenKAT_kem.c | build
	$(CC) $(CPPFLAGS) $(KAT_CFLAGS) -I$(KAT_DIR) -c $< -o $@

build/kat_aes.o: $(KAT_DIR)/aes.c | build
	$(CC) $(CPPFLAGS) $(KAT_CFLAGS) -I$(KAT_DIR) -c $< -o $@

build/kat_rng.o: $(KAT_DIR)/rng.c | build
	$(CC) $(CPPFLAGS) $(KAT_CFLAGS) -I$(KAT_DIR) -c $< -o $@

build/kat_control_dispatch.o: src/kat_control.c src/late067.h | build
	$(CC) $(CPPFLAGS) $(KAT_CFLAGS) -c $< -o $@

build/kat_candidate_dispatch.o: src/kat_candidate.c src/late067.h | build
	$(CC) $(CPPFLAGS) $(KAT_CFLAGS) -c $< -o $@

build/kat_control: build/kat_control_dispatch.o build/support.o \
	$(KAT_OBJS) $(DUAL_OBJS) $(COMMON_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

build/kat_candidate: build/kat_candidate_dispatch.o build/support.o \
	$(KAT_OBJS) $(DUAL_OBJS) $(COMMON_OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

test: build/test
	./build/test

strict: all
	$(PYTHON) -m py_compile tools/*.py

audit: build/bench_normal build/bench_reversed
	$(PYTHON) tools/audit.py

kat: build/kat_control build/kat_candidate
	$(PYTHON) tools/run_kat.py

bench-primary: build/bench_normal build/bench_reversed
	$(PYTHON) tools/run_primary.py

pmu: build/bench_normal build/bench_reversed
	$(PYTHON) tools/run_pmu.py

clean:
	rm -rf build results/*.json results/*.rsp
