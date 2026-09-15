CC ?= gcc
NTRU_ROOT ?= ../Additional_Implementation/avx2/NTRU+768
GT_ROOT ?= $(NTRU_ROOT)/experiments/gt_ntt
AARCH64_REF ?= ../Additional_Implementation/aarch64/NTRU+768/ntt.c

BUILD_DIR := build
TARGET := $(BUILD_DIR)/avx2_bench
GT_GENERATED := \
	$(GT_ROOT)/gt_ntt_frontend_tables.inc \
	$(GT_ROOT)/gt_basemul_soa_tables.inc \
	$(GT_ROOT)/gt_invntt_soa_tables.inc
GT_ASM_INCLUDES := $(GT_ROOT)/gt_ntt_stage345_native_fused.inc \
	$(GT_ROOT)/gt_ntt_frontend_fixed_offsets.inc

CPPFLAGS += -I$(NTRU_ROOT) -I$(GT_ROOT)
CPPFLAGS += -DGT_HAVE_AVX2_ASM=1
BENCH_PRODUCTION_INPLACE ?= 0
ifeq ($(BENCH_PRODUCTION_INPLACE),1)
CPPFLAGS += -DBENCH_PRODUCTION_INPLACE=1
endif
TARGET_FLAGS ?= -march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256
BENCH_LDFLAGS ?=
CFLAGS ?= -O3 -g
BENCH_CFLAGS := -Wall -Wextra -Wpedantic -Wshadow -Wconversion \
	-fomit-frame-pointer -fno-strict-aliasing
CPPFLAGS += -DBENCH_BUILD_FLAGS='"$(TARGET_FLAGS) $(BENCH_LDFLAGS)"'

SOURCES := \
	bench.c \
	$(NTRU_ROOT)/consts.c \
	$(NTRU_ROOT)/asm/ntt.s \
	$(NTRU_ROOT)/asm/invntt.s \
	$(NTRU_ROOT)/asm/basemul.s \
	$(GT_ROOT)/gt_ntt_avx2.c \
	$(GT_ROOT)/gt_basemul_soa.c \
	$(GT_ROOT)/gt_basemul_layout_asm.S \
	$(GT_ROOT)/gt_invntt_soa.c \
	$(GT_ROOT)/gt_invntt_fused_soa.S \
	$(GT_ROOT)/gt_ntt_frontend_stage12_soa.S \
	$(GT_ROOT)/gt_ntt_stage345_soa.s \
	$(GT_ROOT)/gt_ntt_tables.c \
	$(AARCH64_REF)

.PHONY: all build validate scheme-test prototype-test run asm-audit clean

all: build

build: $(TARGET)

$(TARGET): $(SOURCES) $(GT_GENERATED) $(GT_ASM_INCLUDES) \
	$(GT_ROOT)/gt_invntt_ntt32_soa.s \
	$(GT_ROOT)/gt_invntt_dft3_soa.s \
	$(GT_ROOT)/gt_invntt_postprocess_soa.s
	mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(BENCH_CFLAGS) $(TARGET_FLAGS) \
		$(BENCH_LDFLAGS) -o $@ $(SOURCES)

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
	@for symbol in gt_ntt_avx2_frontend_asm gt_ntt_avx2_stage12_asm \
		gt_ntt_avx2_stage12_identity_asm \
		gt_ntt_avx2_stage12_identity_row2q2_asm; do \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
			echo "stack traffic or call found in $$symbol" >&2; exit 1; \
		fi; \
	done
	@echo "forward frontend/stage12 ASM audit: zero stack traffic and calls"
	@for symbol in gt_ntt_avx2_frontend_stage12_asm \
		gt_ntt_avx2_frontend_stage12_identity_asm \
		gt_ntt_avx2_frontend_stage12_u2_asm \
		gt_ntt_avx2_frontend_stage12_u4_asm \
		gt_ntt_avx2_frontend_stage12_u2_identity_asm \
		gt_ntt_avx2_frontend_stage12_u4_identity_asm; do \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq '[[:space:]](push|pop|call)[[:space:]]'; then \
			echo "push, pop, or call found in $$symbol" >&2; exit 1; \
		fi; \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq 'sub[[:space:]]+\$$0x600,%rsp'; then \
			echo "$$symbol audit: exact 1536-byte semantic scratch"; \
		else \
			echo "$$symbol scratch allocation mismatch" >&2; exit 1; \
		fi; \
		if test "$$(objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -c vzeroupper)" -ne 1; then \
			echo "$$symbol vzeroupper count mismatch" >&2; exit 1; \
		fi; \
	done
	@echo "fused frontend/stage12 candidates: no calls and one terminal vzeroupper"
	@for symbol in \
		gt_ntt_avx2_forward_u2_identity_native_centered_fused_asm \
		gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm \
		gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm \
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm \
		gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm \
		gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm \
		gt_ntt_avx2_forward_u4_identity_native_centered_fused_asm; do \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq '[[:space:]](push|pop|call)[[:space:]]'; then \
			echo "push, pop, or call found in $$symbol" >&2; exit 1; \
		fi; \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq 'sub[[:space:]]+\$$0xc00,%rsp'; then \
			echo "$$symbol audit: exact 3072-byte semantic scratch"; \
		else \
			echo "$$symbol scratch allocation mismatch" >&2; exit 1; \
		fi; \
		expected_rsp_refs=8; \
		if test "$$symbol" = \
			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm; then \
			expected_rsp_refs=9; \
		fi; \
		if test "$$(objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -c '%rsp')" -ne $$expected_rsp_refs; then \
			echo "$$symbol unexpected rsp reference" >&2; exit 1; \
		fi; \
		if test "$$(objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Ec 'mov[[:space:]]+%r11,%rsp')" -ne 1; then \
			echo "$$symbol exact rsp restoration missing" >&2; exit 1; \
		fi; \
		if test "$$(objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -c vzeroupper)" -ne 1; then \
			echo "$$symbol vzeroupper count mismatch" >&2; exit 1; \
		fi; \
		previous_instruction="$$(objdump -d --disassemble=$$symbol \
			$(TARGET) | awk '/^[[:space:]]*[0-9a-f]+:/ \
			{ previous=last; last=$$0 } END { print previous }')"; \
		last_instruction="$$(objdump -d --disassemble=$$symbol \
			$(TARGET) | awk '/^[[:space:]]*[0-9a-f]+:/ \
			{ last=$$0 } END { print last }')"; \
		echo "$$previous_instruction" | grep -q vzeroupper || { \
			echo "$$symbol vzeroupper is not terminal" >&2; exit 1; }; \
		echo "$$last_instruction" | grep -Eq '[[:space:]]ret$$' || { \
			echo "$$symbol does not end in ret" >&2; exit 1; }; \
	done
	@echo "single-entry native forward candidates: no calls and one terminal vzeroupper"
	@for symbol in gt_ntt_avx2_frontend_stage12_direct_asm \
		gt_ntt_avx2_frontend_stage12_half_asm; do \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
			echo "stack traffic or call found in $$symbol" >&2; exit 1; \
		fi; \
		if test "$$(objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -c vzeroupper)" -ne 1; then \
			echo "vzeroupper count mismatch in $$symbol" >&2; exit 1; \
		fi; \
	done
	@echo "direct/half frontend-stage12 audit: zero stack traffic/calls and one vzeroupper"
	@for symbol in gt_ntt_avx2_stage345_soa_asm \
		gt_ntt_avx2_stage345_soa_interleaved_asm \
		gt_ntt_avx2_stage345_soa_remapped_asm \
		gt_ntt_avx2_stage345_soa_resident_asm \
		gt_ntt_avx2_stage345_soa_queued_store_asm \
		gt_ntt_avx2_stage345_soa_centered_asm \
		gt_ntt_avx2_stage345_soa_centered_queued_store_asm \
		gt_ntt_avx2_stage345_native_centered_asm; do \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
			echo "stack traffic or call found in $$symbol" >&2; exit 1; \
		fi; \
		if test "$$(objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -c vzeroupper)" -ne 1; then \
			echo "vzeroupper count mismatch in $$symbol" >&2; exit 1; \
		fi; \
	done
	@echo "stage345 candidates audit: zero stack traffic/calls and one vzeroupper"
	@for symbol in gt_basemul_soa_asm_avx2 gt_basemul_native_asm_avx2 \
		gt_basemul_soa_rminus1_asm_avx2 \
		gt_basemul_native_rminus1_asm_avx2 \
		gt_basemul_soa_rminus1_c0lazy_asm_avx2 \
		gt_basemul_native_rminus1_c0lazy_asm_avx2; do \
		if objdump -d --disassemble=$$symbol $(TARGET) | \
			grep -Eq '%rsp|[[:space:]](push|pop|call)[[:space:]]'; then \
			echo "stack traffic or call found in $$symbol" >&2; exit 1; \
		fi; \
	done
	@if test "$$(objdump -d --disassemble=gt_basemul_native_asm_avx2 \
		$(TARGET) | grep -c vzeroupper)" -eq 1; then \
		echo "GT basemul ASM audit: zero stack traffic/calls and one terminal vzeroupper"; \
	else \
		echo "GT basemul ASM vzeroupper count mismatch" >&2; exit 1; \
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

clean:
	$(RM) -r $(BUILD_DIR)
