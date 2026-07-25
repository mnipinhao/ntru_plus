CC = gcc
PYTHON ?= python3
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -mavx2 -mbmi2 -mpopcnt -maes \
  -march=native -mtune=native -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -mavx2 -mbmi2 -mpopcnt -maes \
  -march=native -mtune=native -O3 -fomit-frame-pointer
RM = /bin/rm -f

SOURCES= asm/add.s asm/baseinv.s asm/basemul.s asm/cbd.s asm/crepmod3.s asm/invntt.s asm/ntt.s asm/pack.s consts.c kem.c poly.c symmetric.c fips202/fips202.c fips202/KeccakP-1600-AVX2.s
HEADERS= params.h api.h poly.h symmetric.h fips202/fips202.h fips202/KeccakP-1600-SnP.h

GT_ROOT = experiments/gt_ntt
GT_SOURCES = \
	$(GT_ROOT)/gt_keygen_native.c \
	$(GT_ROOT)/gt_native_pack.c \
	$(GT_ROOT)/gt_native_pack_asm.S \
	$(GT_ROOT)/gt_baseinv_native.c \
	$(GT_ROOT)/gt_basemul_soa.c \
	$(GT_ROOT)/gt_ntt_tables.c \
	$(GT_ROOT)/gt_ntt_frontend_stage12_soa.S \
	$(GT_ROOT)/gt_ntt_stage345_soa.s \
	$(GT_ROOT)/gt_baseinv_native_prepare_asm.S \
	$(GT_ROOT)/gt_basemul_layout_asm.S
GT_HEADERS = \
	$(GT_ROOT)/gt_keygen_native.h \
	$(GT_ROOT)/gt_native_pack.h \
	$(GT_ROOT)/gt_native_pack_tables.inc \
	$(GT_ROOT)/gt_native_pack_asm_tables.inc \
	$(GT_ROOT)/gt_baseinv_native.h \
	$(GT_ROOT)/gt_basemul_soa.h \
	$(GT_ROOT)/gt_basemul_soa_tables.inc \
	$(GT_ROOT)/gt_forward_lazy_bounds.h \
	$(GT_ROOT)/gt_ntt_avx2.h \
	$(GT_ROOT)/gt_ntt_tables.h \
	$(GT_ROOT)/gt_ntt_frontend_tables.inc \
	$(GT_ROOT)/gt_ntt_frontend_fixed_offsets.inc \
	$(GT_ROOT)/gt_ntt_stage345_native_fused.inc
GT_CPPFLAGS = -DGT_HAVE_AVX2_ASM=1 -I. -I$(GT_ROOT)

.PHONY: all PQCgenKAT_kem PQCgenKAT_kem_gt_keygen test \
	test-gt-keygen bench-gt-keygen check-gt-native-pack-tables clean

BUILD_DIR = build

all: \
	test \
	PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) kat/aes.h kat/rng.h $(SOURCES) kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(SOURCES)

PQCgenKAT_kem_gt_keygen: check-gt-native-pack-tables $(HEADERS) \
		$(GT_HEADERS) kat/aes.h kat/rng.h $(SOURCES) $(GT_SOURCES) \
		kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) $(GT_CPPFLAGS) \
		-DNTRUPLUS_EXTERNAL_KEYPAIR=1 \
		-DNTRUPLUS_GT_KEYPAIR_API=crypto_kem_keypair \
		-o $(BUILD_DIR)/PQCgenKAT_kem_gt_keygen \
		kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c \
		$(SOURCES) $(GT_SOURCES)

test: $(HEADERS) randombytes.h $(SOURCES) randombytes.c test/test.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test randombytes.c test/test.c $(SOURCES)

test-gt-keygen: check-gt-native-pack-tables $(BUILD_DIR)/bench_gt_keygen
	$(BUILD_DIR)/bench_gt_keygen validate

bench-gt-keygen: check-gt-native-pack-tables $(BUILD_DIR)/bench_gt_keygen

$(BUILD_DIR)/bench_gt_keygen: $(HEADERS) randombytes.h $(SOURCES) \
		$(GT_SOURCES) $(GT_HEADERS) test/bench_gt_keygen.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(GT_CPPFLAGS) \
		-DNTRUPLUS_BENCH_INTERNAL=1 \
		-o $@ test/bench_gt_keygen.c $(SOURCES) $(GT_SOURCES)

check-gt-native-pack-tables:
	$(PYTHON) $(GT_ROOT)/generate_gt_native_pack_tables.py \
		--consts consts.c \
		--check $(GT_ROOT)/gt_native_pack_tables.inc
	$(PYTHON) $(GT_ROOT)/generate_gt_native_pack_tables.py \
		--consts consts.c \
		--check-asm $(GT_ROOT)/gt_native_pack_asm_tables.inc

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) -r $(BUILD_DIR)
