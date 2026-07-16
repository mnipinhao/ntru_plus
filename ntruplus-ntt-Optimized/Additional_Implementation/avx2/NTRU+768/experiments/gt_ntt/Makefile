CC ?= clang
PYTHON ?= python3
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion
CFLAGS += -mavx2 -fno-strict-aliasing

REFERENCE = ../../../../aarch64/NTRU+768/ntt.c
SOURCES = gt_ntt_avx2.c gt_basemul_soa.c gt_invntt_soa.c gt_ntt_tables.c \
	test_gt_ntt.c $(REFERENCE)
HEADERS = gt_ntt_avx2.h gt_basemul_soa.h gt_basemul_soa_tables.inc \
	gt_invntt_soa.h gt_invntt_soa_tables.inc gt_ntt_tables.h
BUILD = build

ifeq ($(shell uname -s),Darwin)
ARCHFLAGS = -arch x86_64
RUNNER = arch -x86_64
else
SOURCES += gt_ntt_stage345_soa.s
CFLAGS += -DGT_HAVE_AVX2_ASM=1
endif

.PHONY: all test compile check check-tables sanitize asm clean

all: test

test: check-tables $(BUILD)/test_gt_ntt
	$(RUNNER) $(BUILD)/test_gt_ntt

compile: check-tables $(BUILD)/test_gt_ntt

check: check-tables
	$(CC) $(CFLAGS) $(ARCHFLAGS) -Werror -I. -fsyntax-only \
		gt_ntt_avx2.c gt_basemul_soa.c gt_invntt_soa.c gt_ntt_tables.c \
		test_gt_ntt.c

check-tables:
	$(PYTHON) generate_gt_soa_tables.py --check gt_basemul_soa_tables.inc
	$(PYTHON) generate_gt_invntt_tables.py --check gt_invntt_soa_tables.inc

sanitize: check-tables $(BUILD)/test_gt_ntt_sanitize
	$(RUNNER) $(BUILD)/test_gt_ntt_sanitize

$(BUILD)/test_gt_ntt: $(SOURCES) $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -o $@ $(SOURCES)

$(BUILD)/test_gt_ntt_sanitize: $(SOURCES) $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -I. -o $@ $(SOURCES)

asm: $(BUILD)/gt_ntt_avx2.s $(BUILD)/gt_basemul_soa.s \
	$(BUILD)/gt_invntt_soa.s

$(BUILD)/gt_ntt_avx2.s: gt_ntt_avx2.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_ntt_avx2.c

$(BUILD)/gt_basemul_soa.s: gt_basemul_soa.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_basemul_soa.c

$(BUILD)/gt_invntt_soa.s: gt_invntt_soa.c $(HEADERS)
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(ARCHFLAGS) -I. -S -o $@ gt_invntt_soa.c

clean:
	$(RM) -r $(BUILD)
	$(RM) -r __pycache__
