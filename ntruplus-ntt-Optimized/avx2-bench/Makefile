CC ?= gcc
NTRU_ROOT ?= ../Additional_Implementation/avx2/NTRU+768
GT_ROOT ?= $(NTRU_ROOT)/experiments/gt_ntt
AARCH64_REF ?= ../Additional_Implementation/aarch64/NTRU+768/ntt.c
KPQC_ROOT ?= ../../ntruplus-KpqC-Final/Additional_Implementation/avx2/NTRU+768

BUILD_DIR := build
TARGET := $(BUILD_DIR)/avx2_bench
GT_GENERATED := \
	$(GT_ROOT)/gt_basemul_soa_tables.inc \
	$(GT_ROOT)/gt_invntt_soa_tables.inc

CPPFLAGS += -I$(NTRU_ROOT) -I$(GT_ROOT)
CPPFLAGS += -DGT_HAVE_AVX2_ASM=1
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
	$(GT_ROOT)/gt_basemul_soa.c \
	$(GT_ROOT)/gt_invntt_soa.c \
	$(GT_ROOT)/gt_invntt_fused_soa.S \
	$(GT_ROOT)/gt_ntt_stage345_soa.s \
	$(GT_ROOT)/gt_ntt_tables.c \
	$(AARCH64_REF)

.PHONY: all build validate scheme-test prototype-test run asm-audit \
	kpqc-audit clean

all: build

build: $(TARGET)

$(TARGET): $(SOURCES) $(GT_GENERATED) \
	$(GT_ROOT)/gt_invntt_ntt32_soa.s \
	$(GT_ROOT)/gt_invntt_dft3_soa.s \
	$(GT_ROOT)/gt_invntt_postprocess_soa.s
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
	@if objdump -d --disassemble=gt_invntt_soa_ntt32_asm $(TARGET) | \
		grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
		echo "stack traffic or call found in inverse NTT32 ASM region" >&2; \
		exit 1; \
	else \
		echo "inverse NTT32 ASM audit: zero stack traffic and calls"; \
	fi
	@if objdump -d --disassemble=gt_invntt_soa_dft3_asm $(TARGET) | \
		grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
		echo "stack traffic or call found in inverse DFT3 ASM region" >&2; \
		exit 1; \
	else \
		echo "inverse DFT3 ASM audit: zero stack traffic and calls"; \
	fi
	@if objdump -d --disassemble=gt_invntt_soa_postprocess_asm $(TARGET) | \
		grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
		echo "stack traffic or call found in inverse postprocess ASM region" >&2; \
		exit 1; \
	else \
		echo "inverse postprocess ASM audit: zero stack traffic and calls"; \
	fi
	@if objdump -d --disassemble=gt_invntt_soa_avx2_fused_asm $(TARGET) | \
		grep -Eq '[[:space:]](push|pop|call)[[:space:]]'; then \
		echo "push, pop, or call found in fused inverse ASM entry" >&2; exit 1; \
	else \
		echo "fused inverse ASM audit: no push, pop, or internal call"; \
	fi
	@if objdump -d --disassemble=gt_invntt_soa_avx2_fused_asm $(TARGET) | \
		grep -Eq 'sub[[:space:]]+\$$0x600,%rsp'; then \
		echo "fused inverse ASM audit: exact 1536-byte stack scratch"; \
	else \
		echo "fused inverse ASM scratch allocation mismatch" >&2; exit 1; \
	fi
	@if test "$$(objdump -d --disassemble=gt_invntt_soa_avx2_fused_asm \
		$(TARGET) | grep -c vzeroupper)" -eq 1; then \
		echo "fused inverse ASM audit: one terminal vzeroupper"; \
	else \
		echo "fused inverse ASM vzeroupper count mismatch" >&2; exit 1; \
	fi

kpqc-audit:
	@for file in asm/ntt.s asm/invntt.s asm/basemul.s consts.c poly.c; do \
		cmp -s "$(NTRU_ROOT)/$$file" "$(KPQC_ROOT)/$$file" || { \
			echo "KPQC Final mismatch: $$file" >&2; exit 1; }; \
	done
	@echo "KPQC Final AVX2 arithmetic sources match the production baseline"

clean:
	$(RM) -r $(BUILD_DIR)
