# SPDX-License-Identifier: Apache-2.0

.PHONY: all clean bench-stock bench-gt bench-all bench-matrix

TARGET = bench
CC ?= gcc
LD := $(CC)
RM ?= rm -f
PYTHON ?= python3

VARIANT ?= gt
BENCH_MODE ?= ntt_mul_pipeline
USE_SHAKE_ASM ?= 0
NTESTS ?= 500
NITERATIONS ?= 300
NWARMUP ?= 50

NTRUPLUS = ntruplus

INVNTT_STAGE_MODES = invntt_rows invntt_row0 invntt_row1 invntt_row2 invntt_post \
	invntt_post_dft3_raw invntt_post_dft3_reduce invntt_post_untwist \
	invntt_post_finalmerge
ARITH_MODES = ntt invntt basemul basemul_add ntt_mul_pipeline ntt_basemul_add_pipeline $(INVNTT_STAGE_MODES)
KEM_MODES = kem_dec

IS_ARITH_MODE = $(filter $(BENCH_MODE),$(ARITH_MODES))
IS_KEM_MODE = $(filter $(BENCH_MODE),$(KEM_MODES))
IS_INVNTT_STAGE_MODE = $(filter $(BENCH_MODE),$(INVNTT_STAGE_MODES))

GT_INVNTT_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt.s
GT_INVNTT_STAGE_ASM ?= $(NTRUPLUS)/asm/inv_my_ntt_benchstages.s

ifneq ($(IS_INVNTT_STAGE_MODE),)
GT_INVNTT_SOURCE = $(GT_INVNTT_STAGE_ASM)
else
GT_INVNTT_SOURCE = $(GT_INVNTT_ASM)
endif
GT_BASE_OPT_ASM ?= $(NTRUPLUS)/asm/base_gt.opt.s
GT_NTT_ASM ?= $(NTRUPLUS)/asm/my_ntt.s
GT_NTT32_ASM ?= $(NTRUPLUS)/asm/slothy/my_32ntt.opt.s

ifeq ($(IS_ARITH_MODE)$(IS_KEM_MODE),)
$(error unknown BENCH_MODE=$(BENCH_MODE); use $(ARITH_MODES) or $(KEM_MODES))
endif

BENCH_SOURCES = \
	hal/hal.c \
	bench.c

KEM_COMMON_SOURCES = \
	$(NTRUPLUS)/randombytes.c \
	$(NTRUPLUS)/kem.c \
	$(NTRUPLUS)/symmetric.c \
	$(NTRUPLUS)/asm/add.s \
	$(NTRUPLUS)/asm/crepmod3.s \
	$(NTRUPLUS)/asm/pack.s \
	$(NTRUPLUS)/asm/cbd.s

STOCK_ARITH_SOURCES = \
	$(NTRUPLUS)/asm/base.s \
	$(NTRUPLUS)/asm/ntt.s

GT_ARITH_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(NTRUPLUS)/asm/base_gt.S \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

STOCK_OPT_ARITH_SOURCES = \
	$(NTRUPLUS)/asm/base.opt.s \
	$(NTRUPLUS)/asm/ntt.s

GT_OPT_ARITH_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(GT_BASE_OPT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

STOCK_KEM_SOURCES = \
	$(NTRUPLUS)/poly.c \
	$(NTRUPLUS)/asm/base.s \
	$(NTRUPLUS)/asm/ntt.s

GT_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(NTRUPLUS)/gt_test/poly_gt_base_ref.c \
	$(NTRUPLUS)/asm/base_gt.S \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

STOCK_OPT_KEM_SOURCES = \
	$(NTRUPLUS)/poly.c \
	$(NTRUPLUS)/asm/base.opt.s \
	$(NTRUPLUS)/asm/ntt.s

GT_OPT_KEM_SOURCES = \
	$(NTRUPLUS)/ntt.c \
	$(NTRUPLUS)/gt_test/poly_gt_base_ref.c \
	$(GT_BASE_OPT_ASM) \
	$(GT_NTT_ASM) \
	$(GT_NTT32_ASM) \
	$(GT_INVNTT_SOURCE)

SOURCES = $(BENCH_SOURCES)
BENCH_ENABLE_KEM = 0
BENCH_ENABLE_INVNTT_STAGES = 0
SHAKE_CFLAGS =

ifneq ($(IS_INVNTT_STAGE_MODE),)
BENCH_ENABLE_INVNTT_STAGES = 1
ifneq ($(filter $(VARIANT),gt gt_opt),$(VARIANT))
$(error BENCH_MODE=$(BENCH_MODE) requires VARIANT=gt or VARIANT=gt_opt)
endif
endif

ifneq ($(IS_KEM_MODE),)
BENCH_ENABLE_KEM = 1
SOURCES += $(KEM_COMMON_SOURCES)
ifeq ($(USE_SHAKE_ASM),1)
SOURCES += $(NTRUPLUS)/CE/fips202.c $(NTRUPLUS)/CE/f1600.S
SHAKE_CFLAGS = -DSUPPORTS_SHAKE256_ASM
else
SOURCES += $(NTRUPLUS)/NO_CE/fips202.c
endif
endif

ifeq ($(VARIANT),stock)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(STOCK_KEM_SOURCES)
else
SOURCES += $(STOCK_ARITH_SOURCES)
endif
VARIANT_CFLAGS =
else ifeq ($(VARIANT),gt)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(GT_KEM_SOURCES)
else
SOURCES += $(GT_ARITH_SOURCES)
endif
VARIANT_CFLAGS = -DGT_BASE_REF_ONLY_BASEINV_ABI -DBENCH_VARIANT_GT=1
else ifeq ($(VARIANT),stock_opt)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(STOCK_OPT_KEM_SOURCES)
else
SOURCES += $(STOCK_OPT_ARITH_SOURCES)
endif
VARIANT_CFLAGS =
else ifeq ($(VARIANT),gt_opt)
ifneq ($(IS_KEM_MODE),)
SOURCES += $(GT_OPT_KEM_SOURCES)
else
SOURCES += $(GT_OPT_ARITH_SOURCES)
endif
VARIANT_CFLAGS = -DGT_BASE_REF_ONLY_BASEINV_ABI -DBENCH_VARIANT_GT=1
else
$(error unknown VARIANT=$(VARIANT); use stock, gt, stock_opt, or gt_opt)
endif

CFLAGS := \
	-Wall \
	-Wextra \
	-Werror=unused-result \
	-Wpedantic \
	-Wmissing-prototypes \
	-Wshadow \
	-Wpointer-arith \
	-Wredundant-decls \
	-Wno-long-long \
	-Wno-unknown-pragmas \
	-Wno-unused-command-line-argument \
	-Wno-unused-parameter \
	-Wno-unused-const-variable \
	-Wno-unused-function \
	-O3 \
	-fomit-frame-pointer \
	-std=c99 \
	-pedantic \
	-D_GNU_SOURCE \
	-DBENCH_MODE=\"$(BENCH_MODE)\" \
	-DBENCH_NAME=\"$(VARIANT)_$(BENCH_MODE)\" \
	-DBENCH_ENABLE_KEM=$(BENCH_ENABLE_KEM) \
	-DBENCH_ENABLE_INVNTT_STAGES=$(BENCH_ENABLE_INVNTT_STAGES) \
	-DNTESTS=$(NTESTS) \
	-DNITERATIONS=$(NITERATIONS) \
	-DNWARMUP=$(NWARMUP) \
	$(VARIANT_CFLAGS) \
	$(SHAKE_CFLAGS) \
	-Ihal \
	-I$(NTRUPLUS) \
	-I$(NTRUPLUS)/CE \
	-I$(NTRUPLUS)/NO_CE \
	-MMD \
	$(CFLAGS)

ifeq ($(CYCLES),PMU)
	CFLAGS += -DPMU_CYCLES
endif

ifeq ($(CYCLES),PERF)
	CFLAGS += -DPERF_CYCLES
endif

ifeq ($(CYCLES),MAC)
	CFLAGS += -DMAC_CYCLES
endif

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

bench-stock:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=stock BENCH_MODE=ntt_mul_pipeline
	sudo taskset -c 3 ./$(TARGET)

bench-gt:
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_mul_pipeline
	sudo taskset -c 3 ./$(TARGET)

bench-all:
	$(MAKE) bench-stock
	$(MAKE) bench-gt
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=stock BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)
	$(MAKE) clean
	$(MAKE) CYCLES=PERF VARIANT=gt BENCH_MODE=kem_dec
	sudo taskset -c 3 ./$(TARGET)

bench-matrix:
	$(PYTHON) scripts/run_pi5_matrix.py

clean:
	-$(RM) $(TARGET) *.d hal/*.d
