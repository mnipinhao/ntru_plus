ROOT := ../..
E041 := ../gt32_load_to_compute_041
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
ROOT_C := $(ROOT)/consts.c $(ROOT)/fips202.c $(ROOT)/poly.c $(ROOT)/symmetric.c
ROOT_ASM := $(ROOT)/add.s $(ROOT)/cbd.s $(ROOT)/ntt.s $(ROOT)/ntt_m.s \
	$(ROOT)/KeccakP-1600-AVX2.s

.PHONY: all check benchmark clean
all: check

$(GENERATED)/pack_decode_ltc.s $(GENERATED)/basemul_ltc.s:
	@mkdir -p $(GENERATED)
	python3 $(E041)/tools/generate_candidates.py --pack $(ROOT)/pack.s \
		--basemul $(ROOT)/basemul.s --out-dir $(GENERATED)

DECODE_SECTIONS := --only-section=.text.ntruplus768_unpack_m_avx2 \
	--only-section=.rodata.gtclean.pack.q24_decode_mask_0123 \
	--only-section=.rodata.gtclean.pack.q24_decode_mask_1032 \
	--only-section=.rodata.gtclean.pack.q24_decode_mask_2310 \
	--only-section=.rodata.gtclean.pack.q24_decode_mask_3201 \
	--only-section=.rodata.gtclean.pack.q24_low12
DECODE_REMOVE := --remove-section=.text.ntruplus768_unpack_m_avx2 \
	--remove-section=.text.ntruplus768_unpack3_m_avx2 \
	--remove-section=.rodata.gtclean.pack.q24_decode_mask_0123 \
	--remove-section=.rodata.gtclean.pack.q24_decode_mask_1032 \
	--remove-section=.rodata.gtclean.pack.q24_decode_mask_2310 \
	--remove-section=.rodata.gtclean.pack.q24_decode_mask_3201

$(BUILD)/pack_full_control.o: $(ROOT)/pack.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/decode_control.o: $(BUILD)/pack_full_control.o
	$(OBJCOPY) $(DECODE_SECTIONS) $< $@

$(BUILD)/pack_shared.o: $(BUILD)/pack_full_control.o
	$(OBJCOPY) $(DECODE_REMOVE) $< $@

$(BUILD)/basemul_control.o: $(ROOT)/basemul.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pack_d_full_raw.o: $(GENERATED)/pack_decode_ltc.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/decode_d_raw.o: $(BUILD)/pack_d_full_raw.o
	$(OBJCOPY) $(DECODE_SECTIONS) $< $@

$(BUILD)/decode_d.o: $(BUILD)/decode_d_raw.o
	$(OBJCOPY) --prefix-symbols=gt042d_ $< $@

$(BUILD)/basemul_b_raw.o: $(GENERATED)/basemul_ltc.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/basemul_b.o: $(BUILD)/basemul_b_raw.o
	$(OBJCOPY) --prefix-symbols=gt042b_ $< $@

$(BUILD)/tables.o: src/tables_042.c
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<

$(BUILD)/encap_common.o: src/encap_042.c
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<

ENCAPS := $(BUILD)/encap_common.o
OBJECTS := $(BUILD)/decode_control.o $(BUILD)/decode_d.o $(BUILD)/pack_shared.o \
	$(BUILD)/basemul_control.o $(BUILD)/basemul_b.o $(BUILD)/tables.o

$(BUILD)/bench_normal: bench/bench_042.c $(ENCAPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ \
		bench/bench_042.c $(ENCAPS) $(OBJECTS) $(ROOT_C) $(ROOT_ASM) $(CPU_LIB)

$(BUILD)/bench_reversed: bench/bench_042.c $(ENCAPS) $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) $(CPU_INC) -o $@ \
		bench/bench_042.c $(BUILD)/encap_common.o \
		$(BUILD)/decode_d.o $(BUILD)/decode_control.o $(BUILD)/pack_shared.o \
		$(BUILD)/basemul_b.o $(BUILD)/basemul_control.o \
		$(BUILD)/tables.o $(ROOT_C) $(ROOT_ASM) $(CPU_LIB)

check: $(BUILD)/bench_normal $(BUILD)/bench_reversed
	./$(BUILD)/bench_normal >/dev/null
	./$(BUILD)/bench_reversed >/dev/null
	python3 tools/audit_geometry.py --control-pack $(BUILD)/decode_control.o \
		--candidate-pack $(BUILD)/decode_d_raw.o \
		--control-b3 $(BUILD)/basemul_control.o \
		--candidate-b3 $(BUILD)/basemul_b_raw.o \
		--normal $(BUILD)/bench_normal --reversed $(BUILD)/bench_reversed \
		--output $(GENERATED)/geometry.json

benchmark: check
	python3 tools/run_gate.py --normal $(BUILD)/bench_normal \
		--reversed $(BUILD)/bench_reversed --launches 48 \
		--output $(GENERATED)/benchmark.json

clean:
	$(RM) -r $(BUILD) $(GENERATED)
