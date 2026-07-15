CC ?= gcc
NTRU_ROOT ?= ../Additional_Implementation/avx2/NTRU+768
GT_ROOT ?= $(NTRU_ROOT)/experiments/gt_ntt
AARCH64_REF ?= ../Additional_Implementation/aarch64/NTRU+768/ntt.c

BUILD_DIR := build
TARGET := $(BUILD_DIR)/avx2_bench

CPPFLAGS += -I$(NTRU_ROOT) -I$(GT_ROOT)
TARGET_FLAGS ?= -march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256
CFLAGS ?= -O3 -g
BENCH_CFLAGS := -Wall -Wextra -Wpedantic -Wshadow -Wconversion \
	-fomit-frame-pointer -fno-strict-aliasing
CPPFLAGS += -DBENCH_BUILD_FLAGS='"$(TARGET_FLAGS)"'

SOURCES := \
	bench.c \
	$(NTRU_ROOT)/consts.c \
	$(NTRU_ROOT)/asm/ntt.s \
	$(NTRU_ROOT)/asm/invntt.s \
	$(NTRU_ROOT)/asm/basemul.s \
	$(GT_ROOT)/gt_ntt_avx2.c \
	$(GT_ROOT)/gt_ntt_tables.c \
	$(AARCH64_REF)

.PHONY: all build validate scheme-test prototype-test run asm-audit clean

all: build

build: $(TARGET)

$(TARGET): $(SOURCES)
	mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(BENCH_CFLAGS) $(TARGET_FLAGS) -o $@ $(SOURCES)

scheme-test:
	$(MAKE) -C $(NTRU_ROOT) test
	$(NTRU_ROOT)/build/test

prototype-test:
	$(MAKE) -C $(GT_ROOT) test

validate: scheme-test prototype-test $(TARGET)
	$(TARGET) --validate

run: $(TARGET)
	./run_bench.sh

asm-audit: $(TARGET)
	@if objdump -d $(TARGET) | grep -Eq '\bzmm[0-9]+\b|\bk[0-7]\b'; then \
		echo "AVX-512 register found in AVX2 benchmark binary" >&2; exit 1; \
	else \
		echo "AVX2 binary audit: no zmm/opmask register found"; \
	fi

clean:
	$(RM) -r $(BUILD_DIR)
