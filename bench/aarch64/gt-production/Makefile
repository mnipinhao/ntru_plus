CC ?= gcc
CFLAGS ?= -O3 -fomit-frame-pointer
CFLAGS += -std=c99 -Wall -Wextra -Wpedantic
CFLAGS += -ffunction-sections -fdata-sections
LDFLAGS += -Wl,--gc-sections

GT_ROOT ?= ../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768
GT_OVERLAY_ROOT ?=
GT_VARIANT_STR ?= gt-optimized
KPQC_ROOT ?=
BASELINE_ROOT ?= $(KPQC_ROOT)
BASELINE_VARIANT_STR ?= baseline
BASELINE_SUPERCOP_FLAT ?= 0
BUILD_DIR ?= build

NTESTS ?= 31
NITERATIONS ?= 2000
NWARMUP ?= 100
WAVE29_COLD_TARGET ?= build/wave29-cold-decap
WAVE29_MODE_SOURCE ?= $(abspath ../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/gt_production_icache_size/bench_full_kem_variants_pmu.c)
WAVE29_MODE_TARGET ?= build/wave29-modes-pmu

BENCH_COMMON := bench_kem.c deterministic_randombytes.c perf_counter.c

GT_KEM_SOURCE := $(GT_ROOT)/kem.c
GT_NTT_SOURCE := $(GT_ROOT)/asm/ntt.S
GT_PACK_SOURCE := $(GT_ROOT)/asm/pack.S
GT_DECAP_VERIFY_SOURCE := $(GT_ROOT)/internal/decap_verify.c
GT_EXTRA_SOURCES :=
GT_CPPFLAGS := -I$(GT_ROOT) -I$(GT_ROOT)/internal

ifneq ($(strip $(GT_OVERLAY_ROOT)),)
GT_KEM_SOURCE := $(GT_OVERLAY_ROOT)/kem.c
GT_DECAP_VERIFY_SOURCE := $(GT_OVERLAY_ROOT)/internal/decap_verify.c
GT_EXTRA_SOURCES := \
	$(GT_OVERLAY_ROOT)/asm/internal/checked_unpack.S \
	$(GT_OVERLAY_ROOT)/asm/internal/checked_qsoa.S
GT_CPPFLAGS := -I$(GT_OVERLAY_ROOT) -I$(GT_ROOT) -I$(GT_ROOT)/internal
endif

GT_SOURCES := \
	$(GT_KEM_SOURCE) \
	$(GT_ROOT)/symmetric.c \
	$(GT_ROOT)/NO_CE/fips202.c \
	$(GT_ROOT)/internal/keygen.c \
	$(GT_ROOT)/internal/keygen_lambda.c \
	$(GT_ROOT)/internal/basemul_lambda.c \
	$(GT_DECAP_VERIFY_SOURCE) \
	$(GT_NTT_SOURCE) \
	$(GT_ROOT)/asm/invntt.S \
	$(GT_ROOT)/asm/base.S \
	$(GT_PACK_SOURCE) \
	$(GT_ROOT)/asm/cbd.S \
	$(GT_ROOT)/asm/support.S \
	$(GT_ROOT)/asm/kem_api.S \
	$(GT_ROOT)/asm/internal/unpack.S \
	$(GT_ROOT)/asm/internal/keygen_baseinv_prepare.S \
	$(GT_ROOT)/asm/internal/keygen_baseinv_tree.S \
	$(GT_ROOT)/asm/internal/keygen_baseinv_finish.S \
	$(GT_ROOT)/asm/internal/keygen_pack.S \
	$(GT_ROOT)/asm/internal/fqinv.S \
	$(GT_ROOT)/asm/internal/encap_muladd.S \
	$(GT_ROOT)/asm/internal/decap_verify.S \
	$(GT_ROOT)/asm/internal/decap_packed64.S \
	$(GT_ROOT)/asm/internal/decap_official_add.S \
	$(GT_ROOT)/asm/internal/decap_official_base.S \
	$(GT_ROOT)/asm/internal/decap_official_ntt.S \
	$(GT_ROOT)/asm/internal/decap_official_pack.S \
	$(GT_ROOT)/asm/internal/decap_official_forward.S \
	$(GT_EXTRA_SOURCES)

ifeq ($(BASELINE_SUPERCOP_FLAT),1)
SUPERCOP_ROOT ?= $(abspath $(BASELINE_ROOT)/../../..)
BASELINE_CPPFLAGS := \
	-I$(CURDIR)/supercop_compat \
	-I$(BASELINE_ROOT) \
	-I$(SUPERCOP_ROOT)/include \
	-I$(SUPERCOP_ROOT)/cryptoint
BASELINE_SOURCES := \
	$(BASELINE_ROOT)/kem.c \
	$(BASELINE_ROOT)/symmetric.c \
	$(BASELINE_ROOT)/poly.c \
	$(BASELINE_ROOT)/fips202.c \
	$(BASELINE_ROOT)/add.s \
	$(BASELINE_ROOT)/ntt.s \
	$(BASELINE_ROOT)/base.s \
	$(BASELINE_ROOT)/crepmod3.s \
	$(BASELINE_ROOT)/pack.s \
	$(BASELINE_ROOT)/cbd.s
else
BASELINE_CPPFLAGS := -I$(BASELINE_ROOT)
BASELINE_SOURCES := \
	$(BASELINE_ROOT)/kem.c \
	$(BASELINE_ROOT)/symmetric.c \
	$(BASELINE_ROOT)/poly.c \
	$(BASELINE_ROOT)/NO_CE/fips202.c \
	$(BASELINE_ROOT)/asm/add.s \
	$(BASELINE_ROOT)/asm/ntt.s \
	$(BASELINE_ROOT)/asm/base.s \
	$(BASELINE_ROOT)/asm/crepmod3.s \
	$(BASELINE_ROOT)/asm/pack.s \
	$(BASELINE_ROOT)/asm/cbd.s
endif

MODES := keygen encap decap
GT_TARGETS := $(addprefix $(BUILD_DIR)/gt-,$(MODES))
BASELINE_TARGETS := $(addprefix $(BUILD_DIR)/baseline-,$(MODES))

.PHONY: all clean check-roots wave29-cold-decap wave29-modes-pmu

all: check-roots $(GT_TARGETS) $(BASELINE_TARGETS)

check-roots:
	@test -f "$(GT_ROOT)/api.h" || \
		(echo "invalid GT_ROOT=$(GT_ROOT)" >&2; exit 1)
	@test -n "$(BASELINE_ROOT)" && test -f "$(BASELINE_ROOT)/api.h" || \
		(echo "set BASELINE_ROOT to the baseline NTRU+768 root" >&2; exit 1)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/gt-%: $(BENCH_COMMON) $(GT_SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(GT_CPPFLAGS) \
		-DBENCH_MODE_STR=\"$*\" -DBENCH_VARIANT_STR=\"$(GT_VARIANT_STR)\" \
		-DNTESTS=$(NTESTS) -DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(BENCH_COMMON) $(GT_SOURCES) $(LDFLAGS) -o $@

$(BUILD_DIR)/baseline-%: $(BENCH_COMMON) $(BASELINE_SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(BASELINE_CPPFLAGS) \
		-DBENCH_MODE_STR=\"$*\" \
		-DBENCH_VARIANT_STR=\"$(BASELINE_VARIANT_STR)\" \
		-DNTESTS=$(NTESTS) -DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(BENCH_COMMON) $(BASELINE_SOURCES) $(LDFLAGS) -o $@

$(WAVE29_COLD_TARGET): bench_cold_decap.c deterministic_randombytes.c perf_counter.c \
	bench_icache_thrash.S $(GT_SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(GT_CPPFLAGS) \
		-DNTESTS=$(NTESTS) \
		bench_cold_decap.c deterministic_randombytes.c perf_counter.c \
		bench_icache_thrash.S $(GT_SOURCES) $(LDFLAGS) -o $@

wave29-cold-decap: $(WAVE29_COLD_TARGET)
	taskset -c 3 ./$(WAVE29_COLD_TARGET)

$(WAVE29_MODE_TARGET): $(WAVE29_MODE_SOURCE) deterministic_randombytes.c $(GT_SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(GT_CPPFLAGS) \
		-DNTESTS=$(NTESTS) -DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(WAVE29_MODE_SOURCE) deterministic_randombytes.c $(GT_SOURCES) \
		$(LDFLAGS) -o $@

wave29-modes-pmu: $(WAVE29_MODE_TARGET)
	taskset -c 3 ./$(WAVE29_MODE_TARGET) decap $(NITERATIONS) 3
	taskset -c 3 ./$(WAVE29_MODE_TARGET) mixed $(NITERATIONS) 3

clean:
	rm -rf $(BUILD_DIR)
