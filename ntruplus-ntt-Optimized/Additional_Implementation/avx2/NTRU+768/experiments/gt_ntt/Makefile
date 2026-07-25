CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion
CFLAGS += -mavx2 -fno-strict-aliasing

REFERENCE = ../../../../aarch64/NTRU+768/ntt.c
SOURCES = gt_ntt_avx2.c gt_basemul_soa.c gt_baseinv_native.c \
	gt_invntt_soa.c gt_ntt_tables.c test_gt_ntt.c $(REFERENCE)
HEADERS = gt_ntt_avx2.h gt_basemul_soa.h gt_baseinv_native.h \
	gt_forward_lazy_bounds.h gt_basemul_soa_tables.inc \
	baseinv-native-contract.yml forward-lazy-vector-bounds.yml \
	gt_native_pack.h gt_native_pack_tables.inc gt_keygen_native.h \
	gt_native_pack_asm_tables.inc \
	gt_invntt_soa.h gt_invntt_soa_tables.inc gt_ntt_tables.h \
	gt_ntt_frontend_tables.inc \
	gt_ntt_frontend_fixed_offsets.inc \
	gt_ntt_stage345_native_fused.inc \
	gt_invntt_ntt32_soa.s gt_invntt_dft3_soa.s \
	gt_invntt_postprocess_soa.s
BUILD = build
BENCH_BASEINV_SOURCES = gt_ntt_avx2.c gt_baseinv_native.c \
	gt_basemul_soa.c gt_ntt_tables.c bench_gt_baseinv.c

ifeq ($(shell uname -s),Darwin)
ARCHFLAGS = -arch x86_64
RUNNER = arch -x86_64
else
	SOURCES += gt_ntt_frontend_stage12_soa.S gt_ntt_stage345_soa.s \
		gt_invntt_fused_soa.S gt_basemul_layout_asm.S \
		gt_baseinv_native_prepare_asm.S
	CFLAGS += -DGT_HAVE_AVX2_ASM=1
	BENCH_BASEINV_SOURCES += gt_ntt_frontend_stage12_soa.S \
		gt_ntt_stage345_soa.s gt_baseinv_native_prepare_asm.S
endif

.PHONY: all test compile check check-tables sanitize asm bench-baseinv clean

all: test

test: check-tables $(BUILD)/test_gt_ntt
	$(RUNNER) $(BUILD)/test_gt_ntt

compile: check-tables $(BUILD)/test_gt_ntt

check: check-tables
	$(CC) $(CFLAGS) $(ARCHFLAGS) -Werror -I. -fsyntax-only \
		gt_ntt_avx2.c gt_basemul_soa.c gt_baseinv_native.c \
		gt_invntt_soa.c gt_ntt_tables.c test_gt_ntt.c
	$(CC) $(CFLAGS) $(ARCHFLAGS) -DGT_HAVE_AVX2_ASM=1 -Werror -I. \
		-fsyntax-only bench_gt_baseinv.c
	$(CC) $(CFLAGS) $(ARCHFLAGS) -DGT_HAVE_AVX2_ASM=1 -Werror \
		-I. -I../.. -fsyntax-only gt_native_pack.c gt_keygen_native.c

check-tables:
	$(PYTHON) generate_gt_frontend_tables.py --check gt_ntt_frontend_tables.inc
	$(PYTHON) generate_gt_frontend_tables.py --check-asm gt_ntt_frontend_fixed_offsets.inc
	$(PYTHON) generate_gt_soa_tables.py --check gt_basemul_soa_tables.inc
	$(PYTHON) generate_gt_invntt_tables.py --check gt_invntt_soa_tables.inc
	$(PYTHON) generate_gt_forward_lazy_bounds.py \
		--check-header gt_forward_lazy_bounds.h \
		--check-contract forward-lazy-vector-bounds.yml
	$(PYTHON) generate_gt_native_pack_tables.py \
		--check gt_native_pack_tables.inc
	$(PYTHON) generate_gt_native_pack_tables.py \
		--check-asm gt_native_pack_asm_tables.inc

sanitize: check-tables $(BUILD)/test_gt_ntt_sanitize
	$(RUNNER) $(BUILD)/test_gt_ntt_sanitize

bench-baseinv: check-tables $(BUILD)/bench_gt_baseinv

$(BUILD)/test_gt_ntt: $(SOURCES) $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -o $@ $(SOURCES)

$(BUILD)/test_gt_ntt_sanitize: $(SOURCES) $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -I. -o $@ $(SOURCES)

$(BUILD)/bench_gt_baseinv: $(BENCH_BASEINV_SOURCES) $(HEADERS) \
		bench_gt_baseinv.c
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -o $@ $(BENCH_BASEINV_SOURCES)

asm: $(BUILD)/gt_ntt_avx2.s $(BUILD)/gt_basemul_soa.s \
	$(BUILD)/gt_baseinv_native.s \
	$(BUILD)/gt_invntt_soa.s

$(BUILD)/gt_ntt_avx2.s: gt_ntt_avx2.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_ntt_avx2.c

$(BUILD)/gt_basemul_soa.s: gt_basemul_soa.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_basemul_soa.c

$(BUILD)/gt_baseinv_native.s: gt_baseinv_native.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_baseinv_native.c

$(BUILD)/gt_invntt_soa.s: gt_invntt_soa.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_invntt_soa.c

clean:
	$(RM) -r $(BUILD)
	$(RM) -r __pycache__
