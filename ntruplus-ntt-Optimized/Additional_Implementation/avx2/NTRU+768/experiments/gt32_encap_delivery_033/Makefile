ROOT := ../..
EXP031 := ../gt32_encap_lifetime_031
CC ?= gcc
CFLAGS := -O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-fomit-frame-pointer -ffunction-sections -fdata-sections -fno-pie \
	-Wall -Wextra -Wpedantic -Wshadow -Wmissing-prototypes
LDFLAGS := -no-pie -Wl,--gc-sections -Wl,--sort-section=name
BUILD := build
OFFSETS := 0 32 64 96 128 160 192 224
BENCHES := $(addprefix $(BUILD)/bench_offset_,$(OFFSETS))
SUPERCOP_BENCH := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
.SECONDARY:

ROOT_C := $(ROOT)/consts.c $(ROOT)/encap.c $(ROOT)/fips202.c \
	$(ROOT)/poly.c $(ROOT)/symmetric.c
ROOT_ASM := $(ROOT)/add.s $(ROOT)/basemul.s $(ROOT)/cbd.s \
	$(ROOT)/ntt.s $(ROOT)/ntt_m.s $(ROOT)/pack.s \
	$(ROOT)/KeccakP-1600-AVX2.s
COMMON := bench/bench_033.c src/encap_delivery_033.c \
	$(EXP031)/src/encap_lifetime_031.c $(EXP031)/src/keygen_tables.c \
	$(ROOT_C) $(ROOT_ASM)

.PHONY: check benchmark pmu clean

generated/basemul_offset_%.s: tools/generate_caged_basemul.py $(ROOT)/basemul.s
	@mkdir -p generated
	python3 tools/generate_caged_basemul.py --source $(ROOT)/basemul.s \
		--offset $* --output $@

$(BUILD)/bench_offset_%: $(COMMON) generated/basemul_offset_%.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -I$(EXP031)/src \
		-I$(SUPERCOP_BENCH)/include/nontimecop/amd64 -o $@ $(COMMON) \
		generated/basemul_offset_$*.s \
		$(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

$(BUILD)/pmu_offset_%: $(COMMON) generated/basemul_offset_%.s
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -DGT033_PMU_MODE $(LDFLAGS) \
		-I$(ROOT) -Isrc -I$(EXP031)/src \
		-I$(SUPERCOP_BENCH)/include/nontimecop/amd64 -o $@ $(COMMON) \
		generated/basemul_offset_$*.s \
		$(SUPERCOP_BENCH)/lib/nontimecop/amd64/libcpucycles.a

generated/address_inventory.json: $(BENCHES) tools/inventory_addresses.py
	python3 tools/inventory_addresses.py --build $(BUILD) \
		--output $@ $(OFFSETS)

check: generated/address_inventory.json
	@for offset in $(OFFSETS); do \
		$(BUILD)/bench_offset_$$offset CHECK >/dev/null || exit 1; \
	done
	@for offset in $(OFFSETS); do \
		python3 tools/generate_caged_basemul.py --source $(ROOT)/basemul.s \
			--offset $$offset --output generated/basemul_offset_$$offset.s \
			--check || exit 1; \
	done

benchmark: check
	python3 tools/run_sweep.py --build $(BUILD) --launches 48 \
		--output generated/benchmark.json $(OFFSETS)

pmu: check $(BUILD)/pmu_offset_0 $(BUILD)/pmu_offset_128
	python3 tools/run_pmu.py --build $(BUILD) --launches 8 \
		--prefix pmu_offset_ --output generated/pmu.json 0 128

clean:
	$(RM) -r $(BUILD)
