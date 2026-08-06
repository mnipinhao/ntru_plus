CC ?= gcc
PYTHON ?= python3
CFLAGS ?= -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion
CFLAGS += -mavx2 -fno-strict-aliasing

BUILD := build
REFERENCE := ../../../../aarch64/NTRU+768/ntt.c
FROZEN := ../gt_ntt
OFFICIAL := ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
FROZEN_LAMBDA := ../avx2_gt16_quadratic_official_001/generated/quartic-lambda.c
GEN := generated/tile4_constants.inc generated/tile4_mapping.csv \
	generated/tile4_manifest.json generated/tile4_range_metadata.json \
	generated/tile4_frontend_constants.h generated/tile4_frontend_fixed.inc \
	generated/tile4_frontend_wide.inc generated/tile4_basemul_constants.h \
	generated/tile4_basemul_constants.inc generated/tile4_scale_contract.json \
	generated/tile4_private_inverse_constants.inc \
	generated/tile4_private_inverse_range.json \
	generated/tile4_raw_aos_inverse_range.json \
	generated/tile4_inverse_tail_constants.h \
	generated/tile4_inverse_tail_constants.inc \
	generated/tile4_inverse_tail_range.json \
	generated/tile4_serialized_mapping.h \
	generated/tile4_serialized_mapping.json \
	generated/tile4_frombytes_aos_stores.inc \
	generated/tile4_frombytes_direct_soa_plan.json \
	generated/tile4_wide_aos_range.json \
	generated/tile4_a2f_dag.json
SOURCES := src/tile4_ref.c src/tile4_frontend.c src/tile4_basemul.c \
	src/tile4_pack.c src/tile4_inverse_tail.c \
	src/tile4_frombytes_asm.S src/tile4_inverse_tail_asm.S src/tile4_asm.S \
	src/tile4_basemul_asm.S src/tile4_inverse_private_asm.S \
	tests/test_tile4.c

.PHONY: all generate check test sanitize audit bench-short bench-official-short \
	bench-official-cold bench-inverse-short bench-consumer-short \
	bench-basemul-short bench-promotion promotion-serious \
	promotion-serious-reversed promotion-pmu promotion-symbols \
	bench-mixed-frombytes-short bench-basemul-attribution \
	bench-forward-bm-redeposit bench-private-caller private-caller-serious \
	bench-s5-schedule clean

all: test

generate:
	$(PYTHON) tools/generate_tile4.py

check: generate $(BUILD)/test_tile4
	$(BUILD)/test_tile4

test: check

sanitize: generate $(BUILD)/test_tile4_sanitize
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_tile4_sanitize

audit: generate $(BUILD)/tile4_asm.o $(BUILD)/tile4_basemul_asm.o \
		$(BUILD)/tile4_basemul_attribution_asm.o \
		$(BUILD)/tile4_forward_bm_soa_attribution_asm.o \
		$(BUILD)/tile4_inverse_private_asm.o $(BUILD)/tile4_inverse_tail_asm.o \
		$(BUILD)/tile4_inverse_tail_isolated.o $(BUILD)/tile4_frombytes_asm.o
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
		rg 'gt32_tile4_basemul_(b2|b3_late|b4b_partial|k2|general_b2|scale_soa_private|scale_soa_aos_to_aos_private|raw_(soa|aos)_private|c3center(_late)?_aos_private)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_basemul_attribution_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_basemul_attribution_asm.o | \
		rg 'gt32_tile4_attr_(transpose_(one|two|three)|basemul_(raw|c3)_soa|basemul_i1_stage01_fused|inverse_i1_cross3|center_c3_soa)_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_forward_bm_soa_attribution_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_forward_bm_soa_attribution_asm.o | \
		rg 'gt32_tile4_attr_forward_all_bm_soa(_s5x4)?_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_inverse_private_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_inverse_private_asm.o | \
		rg 'gt32_tile4_inverse_soa_private(_parallel)?_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_inverse_tail_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_inverse_tail_asm.o | \
		rg 'gt32_tile4_inverse_tail_(asm_rminus1|t[1-8]_|t10_|champion_)'
	! objdump -drwC -Mintel $(BUILD)/tile4_inverse_tail_isolated.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_inverse_tail_isolated.o | \
		rg 'gt32_tile4_inverse_tail_t9_isolated_private_asm'
	! objdump -drwC -Mintel $(BUILD)/tile4_frombytes_asm.o | \
		rg -n '\[(?:r|e)?sp[+\-]'
	nm -g --defined-only $(BUILD)/tile4_frombytes_asm.o | \
		rg 'gt32_tile4_frombytes_(aos|bm_soa_aos_control)_asm'

bench-short: generate $(BUILD)/bench_forward_short
	$(BUILD)/bench_forward_short 2000

bench-official-short: generate $(BUILD)/bench_official_short
	$(BUILD)/bench_official_short 2000

bench-official-cold: generate $(BUILD)/bench_official_short
	$(BUILD)/bench_official_short 2000 cold

bench-inverse-short: generate $(BUILD)/bench_inverse_short
	$(BUILD)/bench_inverse_short 2000

bench-consumer-short: generate $(BUILD)/bench_consumer_short
	$(BUILD)/bench_consumer_short 2000

bench-basemul-short: generate $(BUILD)/bench_basemul_short
	$(BUILD)/bench_basemul_short 2000

bench-mixed-frombytes-short: generate $(BUILD)/bench_mixed_frombytes
	$(PYTHON) tools/run_mixed_frombytes.py $(BUILD)/bench_mixed_frombytes \
		--iterations 2000 --output results/tile4-mixed-frombytes-short.json

bench-basemul-attribution: generate $(BUILD)/bench_basemul_attribution
	$(PYTHON) tools/run_basemul_attribution.py \
		$(BUILD)/bench_basemul_attribution --iterations 2000 \
		--output results/tile4-basemul-attribution-short.json

bench-forward-bm-redeposit: generate $(BUILD)/bench_forward_bm_redeposit
	$(PYTHON) tools/run_forward_bm_redeposit.py \
		$(BUILD)/bench_forward_bm_redeposit --iterations 2000 \
		--output results/tile4-forward-bm-redeposit-short.json

bench-s5-schedule: generate $(BUILD)/bench_s5_schedule
	$(PYTHON) tools/run_s5_schedule.py $(BUILD)/bench_s5_schedule \
		--iterations 2000 --output results/tile4-s5-schedule-short.json

bench-private-caller: generate $(BUILD)/bench_private_caller \
		$(BUILD)/bench_private_caller_reversed
	$(PYTHON) tools/run_private_caller.py \
		$(BUILD)/bench_private_caller --iterations 2000 \
		--corroboration-binary $(BUILD)/bench_private_caller_reversed \
		--output results/tile4-private-caller-short.json

private-caller-serious: generate $(BUILD)/bench_private_caller \
		$(BUILD)/bench_private_caller_reversed
	$(PYTHON) tools/run_private_caller.py \
		$(BUILD)/bench_private_caller --iterations 100000 --mode serious \
		--corroboration-binary $(BUILD)/bench_private_caller_reversed \
		--output results/tile4-private-caller-serious.json

bench-promotion: generate $(BUILD)/bench_promotion
	$(BUILD)/bench_promotion 100000 0

promotion-serious: generate $(BUILD)/bench_promotion
	$(PYTHON) tools/run_promotion.py $(BUILD)/bench_promotion \
		--iterations 100000 --launches 5 \
		--output results/tile4-promotion-serious.json

promotion-serious-reversed: generate $(BUILD)/bench_promotion_reversed
	$(PYTHON) tools/run_promotion.py $(BUILD)/bench_promotion_reversed \
		--iterations 100000 --launches 5 \
		--output results/tile4-promotion-serious-reversed.json

promotion-pmu: generate $(BUILD)/bench_promotion
	$(PYTHON) tools/run_promotion_pmu.py $(BUILD)/bench_promotion \
		--iterations 1000000 --repeats 3 \
		--output results/tile4-promotion-pmu.json

promotion-symbols: $(BUILD)/bench_promotion $(BUILD)/bench_promotion_reversed
	$(PYTHON) tools/report_promotion_symbols.py \
		$(BUILD)/bench_promotion $(BUILD)/bench_promotion_reversed \
		--output results/tile4-promotion-symbols.json

$(BUILD):
	mkdir -p $@

$(BUILD)/test_tile4: $(SOURCES) src/tile4.h $(GEN) \
		$(BUILD)/parent_ntt.o $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ $(SOURCES) $(BUILD)/parent_ntt.o \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/test_tile4_sanitize: $(SOURCES) src/tile4.h $(GEN) \
		$(BUILD)/parent_ntt_sanitize.o $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -O1 -fno-omit-frame-pointer \
		-fsanitize=address,undefined -Isrc -o $@ $(SOURCES) \
		$(BUILD)/parent_ntt_sanitize.o $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

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

$(BUILD)/tile4_basemul_attribution_asm.o: \
		src/tile4_basemul_attribution_asm.S \
		generated/tile4_basemul_constants.inc \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_basemul_attribution_asm.S

$(BUILD)/tile4_forward_bm_soa_attribution_asm.o: \
		src/tile4_forward_bm_soa_attribution_asm.S \
		generated/tile4_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_forward_bm_soa_attribution_asm.S

$(BUILD)/tile4_inverse_private_asm.o: src/tile4_inverse_private_asm.S \
		generated/tile4_private_inverse_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_inverse_private_asm.S

$(BUILD)/tile4_inverse_tail_asm.o: src/tile4_inverse_tail_asm.S \
		generated/tile4_inverse_tail_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_inverse_tail_asm.S

$(BUILD)/tile4_inverse_tail_isolated.o: src/tile4_inverse_tail_asm.S \
		generated/tile4_inverse_tail_constants.inc | $(BUILD)
	$(CC) $(CFLAGS) -DTILE4_ISOLATED=1 -c -o $@ src/tile4_inverse_tail_asm.S

$(BUILD)/tile4_frombytes_asm.o: src/tile4_frombytes_asm.S \
		generated/tile4_frombytes_aos_stores.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ src/tile4_frombytes_asm.S

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
		src/tile4_inverse_tail.c \
		src/tile4_inverse_tail_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S bench/bench_inverse_short.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -o $@ src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_inverse_tail.c \
		src/tile4_inverse_tail_asm.S src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S bench/bench_inverse_short.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_basemul_short: src/tile4_ref.c src/tile4_frontend.c \
		src/tile4_basemul.c src/tile4_asm.S src/tile4_inverse_private_asm.S \
		bench/bench_basemul_short.c $(GEN) \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN)/gt_basemul_soa.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Isrc -I$(FROZEN) -I$(OFFICIAL) -o $@ \
		src/tile4_ref.c src/tile4_frontend.c src/tile4_basemul.c \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_inverse_private_asm.S bench/bench_basemul_short.c \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN)/gt_basemul_soa.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/consts.c

$(BUILD)/bench_consumer_short: src/tile4_inverse_tail_asm.S src/tile4_asm.S \
		src/tile4_basemul_asm.S bench/bench_consumer_short.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN_LAMBDA) \
		$(FROZEN)/gt_invntt_soa.c \
		$(FROZEN)/gt_invntt_fused_soa.S $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -DGT_HAVE_AVX2_ASM=1 -Isrc -I$(FROZEN) -I$(OFFICIAL) \
		-o $@ src/tile4_inverse_tail_asm.S src/tile4_asm.S \
		src/tile4_basemul_asm.S bench/bench_consumer_short.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(FROZEN)/gt_basemul_layout_asm.S $(FROZEN_LAMBDA) \
		$(FROZEN)/gt_invntt_soa.c \
		$(FROZEN)/gt_invntt_fused_soa.S $(OFFICIAL)/asm/basemul.s \
		$(OFFICIAL)/asm/invntt.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_mixed_frombytes: src/tile4_pack.c src/tile4_asm.S \
		src/tile4_frombytes_asm.S src/tile4_basemul_asm.S \
		bench/bench_mixed_frombytes.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o $(OFFICIAL)/asm/pack.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ src/tile4_pack.c \
		src/tile4_frombytes_asm.S \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_mixed_frombytes.c $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/pack.s $(OFFICIAL)/consts.c

$(BUILD)/bench_promotion: src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_promotion.c $(GEN) $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -Werror \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S bench/bench_promotion.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_promotion_reversed: src/tile4_asm.S src/tile4_basemul_asm.S \
		bench/bench_promotion.c $(GEN) $(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -Werror \
		-Wl,--gc-sections -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/invntt.s \
		$(OFFICIAL)/asm/ntt.s $(OFFICIAL)/asm/crepmod3.s \
		$(OFFICIAL)/consts.c \
		bench/bench_promotion.c src/tile4_basemul_asm.S src/tile4_asm.S \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_basemul_attribution: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		bench/bench_basemul_attribution.c $(GEN) \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		bench/bench_basemul_attribution.c \
		$(OFFICIAL)/asm/basemul.s $(OFFICIAL)/asm/ntt.s \
		$(OFFICIAL)/consts.c

$(BUILD)/bench_forward_bm_redeposit: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_forward_bm_redeposit.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_forward_bm_redeposit.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_s5_schedule: src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_s5_schedule.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_s5_schedule.c \
		$(BUILD)/tile4_inverse_tail_isolated.o

$(BUILD)/bench_private_caller: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_private_caller.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		src/tile4_asm.S src/tile4_basemul_asm.S \
		src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_private_caller.c \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c

$(BUILD)/bench_private_caller_reversed: src/tile4_asm.S \
		src/tile4_basemul_asm.S src/tile4_basemul_attribution_asm.S \
		src/tile4_forward_bm_soa_attribution_asm.S \
		bench/bench_private_caller.c $(GEN) \
		$(BUILD)/tile4_inverse_tail_isolated.o \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -Werror -Isrc -I$(OFFICIAL) -o $@ \
		$(OFFICIAL)/asm/crepmod3.s $(OFFICIAL)/consts.c \
		bench/bench_private_caller.c \
		src/tile4_forward_bm_soa_attribution_asm.S \
		src/tile4_basemul_attribution_asm.S src/tile4_basemul_asm.S \
		src/tile4_asm.S $(BUILD)/tile4_inverse_tail_isolated.o

clean:
	$(RM) -r $(BUILD) __pycache__ tools/__pycache__
