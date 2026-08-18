OFFICIAL_ROOT ?= ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
OFFICIAL_CONSTS := $(OFFICIAL_ROOT)/consts.c
D4_ROOT := ../avx2_gt_d4_aos_official_api
CC ?= gcc
CFLAGS := -O3 -g -Wall -Wextra -Wpedantic -Wshadow -Wconversion -march=x86-64-v3 -mtune=native -mprefer-vector-width=256
BUILD := build
TERMINAL_JSON := $(D4_ROOT)/generated/f32x3_terminal/d4_aos_f32x3_terminal_tables.json
TERMINAL_INC := generated/official_f32x3_rminus1_terminal.inc
LANE_CT := generated/official_invntt_ct_lane_native.S

.PHONY: test test-lane-native prove-canonical-ct diagnose-lane-native bench bench-lane-native check-generated clean
check-generated: $(TERMINAL_INC) $(LANE_CT)
	python3 generate_rminus1_terminal.py --source $(TERMINAL_JSON) --check $(TERMINAL_INC)
	python3 generate_lane_native_ct.py --source $(OFFICIAL_ROOT)/asm/invntt.s --consts $(OFFICIAL_CONSTS) --check $(LANE_CT)

prove-canonical-ct:
	python3 prove_canonical_ct_boundary.py --consts $(OFFICIAL_CONSTS)

$(TERMINAL_INC): generate_rminus1_terminal.py $(TERMINAL_JSON)
	mkdir -p generated
	python3 generate_rminus1_terminal.py --source $(TERMINAL_JSON) --output $@

$(LANE_CT): generate_lane_native_ct.py derive_lane_native_ct.py $(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_CONSTS)
	mkdir -p generated
	python3 generate_lane_native_ct.py --source $(OFFICIAL_ROOT)/asm/invntt.s --consts $(OFFICIAL_CONSTS) --output $@

test: check-generated
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer \
		-DD4AOS_Y2_SYMBOL=official_f32x3_rminus1_invntt_ct_asm \
		-DD4AOS_TERMINAL_TABLE_INCLUDE='"../official_invntt_ct/$(TERMINAL_INC)"' \
		-I$(OFFICIAL_ROOT) -I$(D4_ROOT) -o $(BUILD)/test_official_invntt_ct \
		official_invntt_ct.c test_official_invntt_ct.c \
		$(D4_ROOT)/d4_aos_ref.c $(D4_ROOT)/d4_aos_f32x3_ref.c \
		$(D4_ROOT)/d4_aos_f32x3_invntt_avx2_asm.S \
		$(OFFICIAL_ROOT)/asm/ntt.s $(OFFICIAL_ROOT)/asm/basemul.s \
		$(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_official_invntt_ct

test-lane-native: check-generated
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer \
		-I$(OFFICIAL_ROOT) -o $(BUILD)/test_lane_native_ct \
		test_lane_native_ct.c $(LANE_CT) \
		$(OFFICIAL_ROOT)/asm/ntt.s $(OFFICIAL_ROOT)/asm/basemul.s \
		$(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c
	ASAN_OPTIONS=detect_leaks=0 $(BUILD)/test_lane_native_ct

diagnose-lane-native: check-generated
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL_ROOT) -o $(BUILD)/diagnose_lane_native_ct \
		diagnose_lane_native_ct.c $(LANE_CT) \
		$(OFFICIAL_ROOT)/asm/ntt.s $(OFFICIAL_ROOT)/asm/basemul.s \
		$(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c
	$(BUILD)/diagnose_lane_native_ct

bench: check-generated
	mkdir -p $(BUILD)
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 \
		-fomit-frame-pointer -fno-strict-aliasing \
		-DD4AOS_Y2_SYMBOL=official_f32x3_rminus1_invntt_ct_asm \
		-DD4AOS_TERMINAL_TABLE_INCLUDE='"../official_invntt_ct/$(TERMINAL_INC)"' \
		-I$(OFFICIAL_ROOT) -I$(D4_ROOT) -o $(BUILD)/bench_official_invntt_ct \
		official_invntt_ct.c bench_official_invntt_ct.c \
		$(D4_ROOT)/d4_aos_f32x3_invntt_avx2_asm.S \
		$(OFFICIAL_ROOT)/asm/ntt.s $(OFFICIAL_ROOT)/asm/basemul.s \
		$(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c
	$(BUILD)/bench_official_invntt_ct

bench-lane-native: check-generated
	mkdir -p $(BUILD)
	$(CC) -O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256 \
		-fomit-frame-pointer -fno-strict-aliasing \
		-I$(OFFICIAL_ROOT) -o $(BUILD)/bench_lane_native_ct \
		bench_lane_native_ct.c $(LANE_CT) \
		$(OFFICIAL_ROOT)/asm/ntt.s $(OFFICIAL_ROOT)/asm/basemul.s \
		$(OFFICIAL_ROOT)/asm/invntt.s $(OFFICIAL_ROOT)/consts.c
	$(BUILD)/bench_lane_native_ct

clean:
	rm -rf $(BUILD)
