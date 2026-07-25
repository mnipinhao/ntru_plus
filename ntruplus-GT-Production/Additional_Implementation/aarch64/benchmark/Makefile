CC ?= gcc
CFLAGS ?= -O3 -fomit-frame-pointer
CFLAGS += -std=c99 -Wall -Wextra -Wpedantic
CFLAGS += -ffunction-sections -fdata-sections
LDFLAGS += -Wl,--gc-sections

GT_ROOT ?= ../NTRU+768
KPQC_ROOT ?=
BUILD_DIR ?= build

NTESTS ?= 31
NITERATIONS ?= 2000
NWARMUP ?= 100

BENCH_COMMON := bench_kem.c deterministic_randombytes.c perf_counter.c

GT_SOURCES := \
	$(GT_ROOT)/kem.c \
	$(GT_ROOT)/symmetric.c \
	$(GT_ROOT)/NO_CE/fips202.c \
	$(GT_ROOT)/internal/keygen.c \
	$(GT_ROOT)/internal/keygen_lambda.c \
	$(GT_ROOT)/internal/basemul_lambda.c \
	$(GT_ROOT)/internal/decap_verify.c \
	$(GT_ROOT)/asm/ntt.S \
	$(GT_ROOT)/asm/invntt.S \
	$(GT_ROOT)/asm/base.S \
	$(GT_ROOT)/asm/pack.S \
	$(GT_ROOT)/asm/cbd.S \
	$(GT_ROOT)/asm/support.S \
	$(GT_ROOT)/asm/kem_api.S \
	$(GT_ROOT)/asm/internal/unpack.S \
	$(GT_ROOT)/asm/internal/keygen_baseinv_tree.S \
	$(GT_ROOT)/asm/internal/keygen_baseinv_finish.S \
	$(GT_ROOT)/asm/internal/keygen_pack.S \
	$(GT_ROOT)/asm/internal/fqinv.S \
	$(GT_ROOT)/asm/internal/encap_muladd.S \
	$(GT_ROOT)/asm/internal/decap_verify.S

KPQC_SOURCES := \
	$(KPQC_ROOT)/kem.c \
	$(KPQC_ROOT)/symmetric.c \
	$(KPQC_ROOT)/poly.c \
	$(KPQC_ROOT)/NO_CE/fips202.c \
	$(KPQC_ROOT)/asm/add.s \
	$(KPQC_ROOT)/asm/ntt.s \
	$(KPQC_ROOT)/asm/base.s \
	$(KPQC_ROOT)/asm/crepmod3.s \
	$(KPQC_ROOT)/asm/pack.s \
	$(KPQC_ROOT)/asm/cbd.s

MODES := keygen encap decap
GT_TARGETS := $(addprefix $(BUILD_DIR)/gt-,$(MODES))
KPQC_TARGETS := $(addprefix $(BUILD_DIR)/kpqc-,$(MODES))

.PHONY: all clean check-roots

all: check-roots $(GT_TARGETS) $(KPQC_TARGETS)

check-roots:
	@test -f "$(GT_ROOT)/api.h" || \
		(echo "invalid GT_ROOT=$(GT_ROOT)" >&2; exit 1)
	@test -n "$(KPQC_ROOT)" && test -f "$(KPQC_ROOT)/api.h" || \
		(echo "set KPQC_ROOT to KPQC-final NTRU+768" >&2; exit 1)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/gt-%: $(BENCH_COMMON) $(GT_SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(GT_ROOT) -I$(GT_ROOT)/internal \
		-DBENCH_MODE_STR=\"$*\" -DBENCH_VARIANT_STR=\"gt-optimized\" \
		-DNTESTS=$(NTESTS) -DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(BENCH_COMMON) $(GT_SOURCES) $(LDFLAGS) -o $@

$(BUILD_DIR)/kpqc-%: $(BENCH_COMMON) $(KPQC_SOURCES) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(KPQC_ROOT) \
		-DBENCH_MODE_STR=\"$*\" -DBENCH_VARIANT_STR=\"kpqc-final\" \
		-DNTESTS=$(NTESTS) -DNITERATIONS=$(NITERATIONS) \
		-DNWARMUP=$(NWARMUP) \
		$(BENCH_COMMON) $(KPQC_SOURCES) $(LDFLAGS) -o $@

clean:
	rm -rf $(BUILD_DIR)
