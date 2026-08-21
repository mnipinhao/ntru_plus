ROOT := ../..
EXP034 := ../gt32_q24_canon_minuw_034
CC ?= gcc
CFLAGS := -O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-fomit-frame-pointer -ffunction-sections -fdata-sections \
	-Wall -Wextra -Wpedantic
LDFLAGS := -no-pie -Wl,--gc-sections
BUILD := build
GENERATED := generated
SUPERCOP_BENCH := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
CPU_INC := -I$(SUPERCOP_BENCH)/include/nontimecop/amd64
CPU_LIB := $(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

COMMON_OBJS := $(BUILD)/bench.o $(BUILD)/encap.o $(BUILD)/consts.o \
	$(BUILD)/fips202.o $(BUILD)/poly.o $(BUILD)/symmetric.o \
	$(BUILD)/keygen_tables.o $(BUILD)/add.o $(BUILD)/basemul.o \
	$(BUILD)/cbd.o $(BUILD)/ntt.o $(BUILD)/ntt_m.o $(BUILD)/keccak.o
ORDERS := current transform q24 arithmetic
comma := ,
BINARIES := $(foreach order,$(ORDERS),$(BUILD)/bench_$(order)_control \
	$(BUILD)/bench_$(order)_candidate)

.PHONY: all check benchmark pmu factorial recheck032 clean

all: check

$(GENERATED)/pack_minuw.s: $(EXP034)/tools/generate_candidate.py $(ROOT)/pack.s
	@mkdir -p $(GENERATED)
	python3 $< --input $(ROOT)/pack.s --output $@

$(BUILD):
	mkdir -p $@

$(BUILD)/bench.o: bench/bench_033b.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) $(CPU_INC) -c -o $@ $<

$(BUILD)/encap.o: src/encap_033b.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<

$(BUILD)/consts.o: $(ROOT)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<
$(BUILD)/fips202.o: $(ROOT)/fips202.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<
$(BUILD)/poly.o: $(ROOT)/poly.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<
$(BUILD)/symmetric.o: $(ROOT)/symmetric.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<
$(BUILD)/keygen_tables.o: ../gt32_encap_lifetime_031/src/keygen_tables.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(ROOT) -c -o $@ $<
$(BUILD)/add.o: $(ROOT)/add.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/basemul.o: $(ROOT)/basemul.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/cbd.o: $(ROOT)/cbd.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/ntt.o: $(ROOT)/ntt.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/ntt_m.o: $(ROOT)/ntt_m.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/keccak.o: $(ROOT)/KeccakP-1600-AVX2.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/pack_control.o: $(ROOT)/pack.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<
$(BUILD)/pack_candidate.o: $(GENERATED)/pack_minuw.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

define LINK_PAIR
$(BUILD)/bench_$(1)_control: $(COMMON_OBJS) $(BUILD)/pack_control.o
	$$(CC) $$(LDFLAGS) $(2) -o $$@ $$(COMMON_OBJS) $$(BUILD)/pack_control.o $$(CPU_LIB)
$(BUILD)/bench_$(1)_candidate: $(COMMON_OBJS) $(BUILD)/pack_candidate.o
	$$(CC) $$(LDFLAGS) $(2) -o $$@ $$(COMMON_OBJS) $$(BUILD)/pack_candidate.o $$(CPU_LIB)
endef

$(eval $(call LINK_PAIR,current,))
$(eval $(call LINK_PAIR,transform,-Wl$(comma)-T$(comma)link/order_transform.ld))
$(eval $(call LINK_PAIR,q24,-Wl$(comma)-T$(comma)link/order_q24.ld))
$(eval $(call LINK_PAIR,arithmetic,-Wl$(comma)-T$(comma)link/order_arithmetic.ld))

$(BUILD)/bench_transform_control $(BUILD)/bench_transform_candidate: link/order_transform.ld
$(BUILD)/bench_q24_control $(BUILD)/bench_q24_candidate: link/order_q24.ld
$(BUILD)/bench_arithmetic_control $(BUILD)/bench_arithmetic_candidate: link/order_arithmetic.ld

check: $(BINARIES)
	python3 $(EXP034)/tools/generate_candidate.py --input $(ROOT)/pack.s \
		--output $(GENERATED)/pack_minuw.s --check
	python3 tools/inventory.py --build $(BUILD) \
		--output $(GENERATED)/address_manifest.json --check
	python3 tools/check_outputs.py --build $(BUILD) \
		--output $(GENERATED)/correctness.json

benchmark: check
	python3 tools/run_orders.py --build $(BUILD) --launches 48 \
		--output $(GENERATED)/benchmark.json

pmu: check
	python3 tools/run_pmu.py --build $(BUILD) --launches 24 \
		--output $(GENERATED)/pmu.json

FACTORIAL := $(BUILD)/factorial
FACTORIAL_COMMON := $(FACTORIAL)/common
FACTORIAL_CFLAGS := $(CFLAGS) -I$(ROOT)
FACTORIAL_LD := -Wl$(comma)-T$(comma)link/order_transform_factorial.ld
FACTORIAL_COMMON_OBJS := $(FACTORIAL_COMMON)/bench.o \
	$(FACTORIAL_COMMON)/consts.o $(FACTORIAL_COMMON)/fips202.o \
	$(FACTORIAL_COMMON)/poly.o $(FACTORIAL_COMMON)/symmetric.o \
	$(FACTORIAL_COMMON)/keygen_tables.o $(FACTORIAL_COMMON)/add.o \
	$(FACTORIAL_COMMON)/cbd.o $(FACTORIAL_COMMON)/ntt.o \
	$(FACTORIAL_COMMON)/ntt_m.o $(FACTORIAL_COMMON)/keccak.o
FACTORIAL_LIB_OBJS := $(filter-out $(FACTORIAL_COMMON)/bench.o,$(FACTORIAL_COMMON_OBJS))

$(FACTORIAL_COMMON):
	mkdir -p $@

$(FACTORIAL_COMMON)/bench.o: bench/bench_factorial.c | $(FACTORIAL_COMMON)
	$(CC) $(FACTORIAL_CFLAGS) $(CPU_INC) -c -o $@ $<
$(FACTORIAL_COMMON)/consts.o: $(ROOT)/consts.c | $(FACTORIAL_COMMON)
	$(CC) $(FACTORIAL_CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/fips202.o: $(ROOT)/fips202.c | $(FACTORIAL_COMMON)
	$(CC) $(FACTORIAL_CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/poly.o: $(ROOT)/poly.c | $(FACTORIAL_COMMON)
	$(CC) $(FACTORIAL_CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/symmetric.o: $(ROOT)/symmetric.c | $(FACTORIAL_COMMON)
	$(CC) $(FACTORIAL_CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/keygen_tables.o: ../gt32_encap_lifetime_031/src/keygen_tables.c | $(FACTORIAL_COMMON)
	$(CC) $(FACTORIAL_CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/add.o: $(ROOT)/add.s | $(FACTORIAL_COMMON)
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/cbd.o: $(ROOT)/cbd.s | $(FACTORIAL_COMMON)
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/ntt.o: $(ROOT)/ntt.s | $(FACTORIAL_COMMON)
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/ntt_m.o: $(ROOT)/ntt_m.s | $(FACTORIAL_COMMON)
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL_COMMON)/keccak.o: $(ROOT)/KeccakP-1600-AVX2.s | $(FACTORIAL_COMMON)
	$(CC) $(CFLAGS) -c -o $@ $<

$(FACTORIAL)/a $(FACTORIAL)/b $(FACTORIAL)/c:
	mkdir -p $@
$(FACTORIAL)/a/encap.o: src/factorial_encap.c | $(FACTORIAL)/a
	$(CC) $(FACTORIAL_CFLAGS) -DFACTORIAL_A -c -o $@ $<
$(FACTORIAL)/b/encap.o: src/factorial_encap.c | $(FACTORIAL)/b
	$(CC) $(FACTORIAL_CFLAGS) -DFACTORIAL_B -c -o $@ $<
$(FACTORIAL)/c/encap.o: src/factorial_encap.c | $(FACTORIAL)/c
	$(CC) $(FACTORIAL_CFLAGS) -DFACTORIAL_C -c -o $@ $<
$(FACTORIAL_COMMON)/basemul.o: $(ROOT)/basemul.s | $(FACTORIAL_COMMON)
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL)/c/basemul.o: ../gt32_encap_b3_addm_032/generated/basemul_032.s | $(FACTORIAL)/c
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL)/a/pack.o: $(ROOT)/pack.s | $(FACTORIAL)/a
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL)/b/pack.o: $(GENERATED)/pack_minuw.s | $(FACTORIAL)/b
	$(CC) $(CFLAGS) -c -o $@ $<
$(FACTORIAL)/c/pack.o: $(GENERATED)/pack_minuw.s | $(FACTORIAL)/c
	$(CC) $(CFLAGS) -c -o $@ $<

$(FACTORIAL)/a/bench: $(FACTORIAL_COMMON_OBJS) $(FACTORIAL_COMMON)/basemul.o \
		$(FACTORIAL)/a/encap.o $(FACTORIAL)/a/pack.o link/order_transform_factorial.ld
	$(CC) $(LDFLAGS) $(FACTORIAL_LD) -o $@ $(FACTORIAL_COMMON_OBJS) \
		$(FACTORIAL)/a/encap.o $(FACTORIAL_COMMON)/basemul.o \
		$(FACTORIAL)/a/pack.o $(CPU_LIB)
$(FACTORIAL)/b/bench: $(FACTORIAL_COMMON_OBJS) $(FACTORIAL_COMMON)/basemul.o \
		$(FACTORIAL)/b/encap.o $(FACTORIAL)/b/pack.o link/order_transform_factorial.ld
	$(CC) $(LDFLAGS) $(FACTORIAL_LD) -o $@ $(FACTORIAL_COMMON_OBJS) \
		$(FACTORIAL)/b/encap.o $(FACTORIAL_COMMON)/basemul.o \
		$(FACTORIAL)/b/pack.o $(CPU_LIB)
$(FACTORIAL)/c/bench: $(FACTORIAL_COMMON_OBJS) $(FACTORIAL)/c/basemul.o \
		$(FACTORIAL)/c/encap.o $(FACTORIAL)/c/pack.o link/order_transform_factorial.ld
	$(CC) $(LDFLAGS) $(FACTORIAL_LD) -o $@ $(FACTORIAL_COMMON_OBJS) \
		$(FACTORIAL)/c/encap.o $(FACTORIAL)/c/basemul.o \
		$(FACTORIAL)/c/pack.o $(CPU_LIB)

factorial: $(FACTORIAL)/a/bench $(FACTORIAL)/b/bench $(FACTORIAL)/c/bench
	python3 tools/factorial_inventory.py --build $(BUILD) \
		--output $(GENERATED)/factorial_addresses.json
	python3 tools/run_factorial.py --build $(BUILD) --launches 48 \
		--output $(GENERATED)/factorial.json
	python3 tools/run_factorial_pmu.py --build $(BUILD) --launches 24 \
		--output $(GENERATED)/factorial_pmu.json

RECHECK032 := $(BUILD)/recheck032
$(RECHECK032):
	mkdir -p $@
$(RECHECK032)/bench.o: ../gt32_encap_b3_addm_032/bench/bench_032.c | $(RECHECK032)
	$(CC) $(CFLAGS) -I$(ROOT) -I../gt32_encap_b3_addm_032/src $(CPU_INC) -c -o $@ $<
$(RECHECK032)/encap.o: ../gt32_encap_b3_addm_032/src/encap_b3_addm_032.c | $(RECHECK032)
	$(CC) $(CFLAGS) -I$(ROOT) -I../gt32_encap_b3_addm_032/src -c -o $@ $<
$(RECHECK032)/basemul.o: ../gt32_encap_b3_addm_032/generated/basemul_032.s | $(RECHECK032)
	$(CC) $(CFLAGS) -c -o $@ $<
$(RECHECK032)/bench: $(FACTORIAL_LIB_OBJS) $(RECHECK032)/bench.o \
		$(RECHECK032)/encap.o $(RECHECK032)/basemul.o \
		$(FACTORIAL)/b/pack.o link/order_transform_032_recheck.ld
	$(CC) $(LDFLAGS) -Wl$(comma)-T$(comma)link/order_transform_032_recheck.ld \
		-o $@ $(RECHECK032)/bench.o $(FACTORIAL_LIB_OBJS) \
		$(RECHECK032)/encap.o $(RECHECK032)/basemul.o \
		$(FACTORIAL)/b/pack.o $(CPU_LIB)

recheck032: $(RECHECK032)/bench
	python3 ../gt32_encap_b3_addm_032/tools/run_benchmark.py \
		--binary $(RECHECK032)/bench --launches 32 \
		--output $(GENERATED)/factorial_032_same_elf.json

clean:
	$(RM) -r $(BUILD)
