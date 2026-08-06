CC ?= gcc
PYTHON ?= python3
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion
CFLAGS += -mavx2 -fno-strict-aliasing

BUILD := build
REFERENCE := ../../../../aarch64/NTRU+768/ntt.c
FROZEN := ../gt_ntt
OFFICIAL := ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
GEN := generated/tile4_constants.inc generated/tile4_mapping.csv \
	generated/tile4_manifest.json generated/tile4_range_metadata.json \
	generated/tile4_frontend_constants.h generated/tile4_frontend_fixed.inc \
	generated/tile4_frontend_wide.inc generated/tile4_basemul_constants.h \
	generated/tile4_basemul_constants.inc generated/tile4_scale_contract.json
SOURCES := src/tile4_ref.c src/tile4_frontend.c src/tile4_basemul.c src/tile4_asm.S \
	src/tile4_basemul_asm.S \
	tests/test_tile4.c

.PHONY: all generate check test sanitize audit bench-short bench-official-short \
	bench-official-cold bench-inverse-short bench-basemul-short clean

all: test

generate:
	$(PYTHON) tools/generate_tile4.py

check: generate $(BUILD)/test_tile4
	$(BUILD)/test_tile4

test: check

sanitize: generate $(BUILD)/test_tile4_sanitize
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_tile4_sanitize

audit: generate $(BUILD)/tile4_asm.o $(BUILD)/tile4_basemul_asm.o
	objdump -drwC -Mintel $(BUILD)/tile4_asm.o > $(BUILD)/tile4_asm.dump
	! objdump -drwC -Mintel --disassemble=gt32_tile4_forward_tile_asm \
		$(BUILD)/tile4_asm.o | rg -n '\[(?:r|e)?sp[+\-]'
	! objdump -drwC -Mintel --disassemble=gt32_tile4_inverse_tile_asm \
		$(BUILD)/tile4_asm.o | rg -n '\[(?:r|e)?sp[+\-]'
	rg -n 'sub[[:space:]]+rsp,0x600|add[[:space:]]+rsp,0x600' \
		$(BUILD)/tile4_asm.dump
	nm -g --defined-only $(BUILD)/tile4_asm.o | \
		rg 'gt32_tile4_(frontend.*|forward.*|inverse.*)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_basemul_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_basemul_asm.o | \
		rg 'gt32_tile4_basemul_(b2|general_b2|scale_soa_private)_asm'

bench-short: generate $(BUILD)/bench_forward_short
	$(BUILD)/bench_forward_short 2000

bench-official-short: generate $(BUILD)/bench_official_short
	$(BUILD)/bench_official_short 2000

bench-official-cold: generate $(BUILD)/bench_official_short
	$(BUILD)/bench_official_short 2000 cold

bench-inverse-short: generate $(BUILD)/bench_inverse_short
	$(BUILD)/bench_inverse_short 2000

bench-basemul-short: generate $(BUILD)/bench_basemul_short
	$(BUILD)/bench_basemul_short 2000

$(BUILD):
	mkdir -p $@

$(BUILD)/test_tile4: $(SOURCES) src/tile4.h $(GEN) \
		$(BUILD)/parent_ntt.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(SOURCES) $(BUILD)/parent_ntt.o

$(BUILD)/test_tile4_sanitize: $(SOURCES) src/tile4.h $(GEN) \
		$(BUILD)/parent_ntt_sanitize.o | $(BUILD)
	$(CC) $(CFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -Isrc -o $@ $(SOURCES) \
		$(BUILD)/parent_ntt_sanitize.o

$(BUILD)/parent_ntt.o: $(REFERENCE) | $(BUILD)
	$(CC) $(CFLAGS) -Wno-conversion -Wno-sign-conversion -c -o $@ $<

$(BUILD)/parent_ntt_sanitize.o: $(REFERENCE) | $(BUILD)
	$(CC) $(CFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -Wno-conversion -Wno-sign-conversion \
		-c -o $@ $<

$(BUILD)/tile4_asm.o: src/tile4_asm.S generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_asm.S

$(BUILD)/tile4_basemul_asm.o: src/tile4_basemul_asm.S \
		generated/tile4_basemul_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_basemul_asm.S

$(BUILD)/bench_forward_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_asm.S bench/bench_forward_short.c $(GEN) \
		$(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_asm.S \
		bench/bench_forward_short.c $(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c

$(BUILD)/bench_official_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_asm.S bench/bench_official_short.c $(GEN) \
		$(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -I$(OFFICIAL) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_asm.S \
		bench/bench_official_short.c $(FROZEN)/gt_ntt_frontend_stage12_soa.S \
		$(FROZEN)/gt_ntt_stage345_soa.s $(FROZEN)/gt_ntt_tables.c \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/consts.c

$(BUILD)/bench_inverse_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_asm.S bench/bench_inverse_short.c $(GEN) | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -o $@ src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_asm.S bench/bench_inverse_short.c

$(BUILD)/bench_basemul_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_basemul.c src/tile4_asm.S bench/bench_basemul_short.c $(GEN) \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN)/gt_basemul_soa.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -I$(OFFICIAL) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_basemul.c \
		src/tile4_asm.S src/tile4_basemul_asm.S bench/bench_basemul_short.c \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN)/gt_basemul_soa.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/consts.c

clean:
	$(RM) -r $(BUILD) __pycache__ tools/__pycache__
