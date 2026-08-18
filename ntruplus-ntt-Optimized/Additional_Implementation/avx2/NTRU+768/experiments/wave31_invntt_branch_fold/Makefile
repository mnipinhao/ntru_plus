CC ?= gcc
PYTHON ?= python3

CURRENT := $(abspath ../..)
GT := $(CURRENT)/experiments/gt_ntt
WAVE20 := $(abspath ../wave20_gt_contract_optimization)
WAVE21 := $(abspath ../wave21_gt_consumer_fusion)
WAVE24 := $(abspath ../wave24_best_gt)
WAVE25 := $(abspath ../wave25_gt_production_arithmetic)
WAVE19 := $(abspath ../wave19_gt_official_attribution)
REPO := $(abspath ../../../../../..)
OFFICIAL := $(REPO)/third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
BUILD := build
TARGET_FLAGS ?= -march=x86-64-v3 -mtune=generic -mprefer-vector-width=256
CPPFLAGS := -I$(OFFICIAL) -I$(GT) -I$(WAVE20)/src -I$(WAVE24)/src \
	-I$(WAVE21)/src -I$(WAVE25)/src -I$(WAVE20)/build/generated \
	-DGT_HAVE_AVX2_ASM=1 \
	-DGT_ENABLE_L3PAIR_RMINUS1_CANDIDATE=1 \
	-Dwave25_invntt_native_rminus1_official_direct_avx2=wave31_invntt_native_rminus1_branch_fold_exact_avx2
CFLAGS ?= -O3 -g
CFLAGS += -Wall -Wextra -Wpedantic -Wshadow -Wconversion \
	-fomit-frame-pointer -fno-strict-aliasing -fno-pie -MMD -MP

W20B := $(WAVE20)/build
OFFICIAL_OBJECTS := $(addprefix $(W20B)/official/, \
	ntt.o invntt.o basemul.o baseinv.o pack.o add.o consts.o poly.o)
GT_OBJECTS := $(filter-out $(W20B)/gt/gt_basemul_layout_asm.o, \
	$(addprefix $(W20B)/gt/, \
	gt_ntt_avx2.o gt_basemul_soa.o gt_native_pack.o gt_invntt_soa.o \
	gt_ntt_tables.o gt_ntt_frontend_stage12_soa.o gt_ntt_stage345_soa.o \
	gt_invntt_fused_soa.o gt_basemul_layout_asm.o gt_native_pack_asm.o)) \
	$(WAVE25)/build/gt_basemul_layout_candidate.o
OBJECTS := $(OFFICIAL_OBJECTS) $(GT_OBJECTS) \
	$(WAVE24)/build/wave24_invntt_official_dag.o \
	$(W20B)/sysv_abi_probe.o $(WAVE25)/build/wave25_l3pair_basemul.o \
	$(BUILD)/wave31_branch_fold.o $(BUILD)/harness.o
TARGET := $(BUILD)/wave31_same_binary
W20F := $(W20B)/full
W19G := $(WAVE19)/build/gt
FULL_OFFICIAL := $(addprefix $(W20F)/official/, \
	add.o baseinv.o basemul.o cbd.o crepmod3.o invntt.o ntt.o pack.o \
	consts.o kem.o poly.o symmetric.o fips202.o keccak.o)
FULL_SUPPORT := $(FULL_OFFICIAL) $(GT_OBJECTS) \
	$(W19G)/gt_baseinv_native.o $(W19G)/gt_baseinv_native_prepare_asm.o \
	$(WAVE24)/build/wave24_unpack_only.o \
	$(WAVE24)/build/wave24_three_child_only.o \
	$(WAVE24)/build/wave24_stream_only.o \
	$(WAVE24)/build/wave24_fused_sub_only.o \
	$(WAVE24)/build/wave24_lazy_pack_fused.o \
	$(WAVE24)/build/wave24_canonical_lazy_stream.o \
	$(WAVE24)/build/wave24_canonical_lazy_nocenter_stream.o \
	$(WAVE24)/build/wave24_invntt_official_dag.o \
	$(WAVE24)/build/wave24_baseinv_tail.o
FULL_OBJECTS := $(FULL_SUPPORT) \
	$(WAVE24)/build/full/best_kem.o \
	$(WAVE24)/build/full/invdag_kem.o \
	$(WAVE24)/build/full/lazy_kem.o \
	$(WAVE24)/build/full/lazy_invdag_kem.o \
	$(WAVE24)/build/full/lazy_asm_kem.o \
	$(WAVE24)/build/full/lazy_asm_invdag_kem.o \
	$(WAVE24)/build/full/lazy_asm_nc_kem.o \
	$(WAVE24)/build/full/lazy_asm_nc_invdag_kem.o \
	$(WAVE24)/build/full/keygen_current.o \
	$(WAVE24)/build/full/keygen_no_clear.o \
	$(WAVE24)/build/full/keygen_hardened.o \
	$(WAVE25)/build/wave25_l3pair_basemul.o \
	$(BUILD)/wave31_branch_fold.o $(BUILD)/full/algebraic_kem.o \
	$(BUILD)/full/fold_lazy_kem.o \
	$(BUILD)/full/fold_exact_kem.o $(BUILD)/full/harness.o
FULL_TARGET := $(BUILD)/wave31_full_kem_same_binary

.PHONY: all correctness linkage full-kem-correctness prerequisites clean
all: $(TARGET)

correctness: $(TARGET)
	$(TARGET) --validate

linkage: $(TARGET)
	! nm -u $(BUILD)/wave31_branch_fold.o | \
		grep -E 'native_to_official|wave24_private'
	test "$$(nm -g --defined-only $(BUILD)/wave31_branch_fold.o | \
		grep -c 'wave31_invntt_native_rminus1_')" -eq 3

full-kem-correctness: $(FULL_TARGET)
	$(FULL_TARGET) --validate

prerequisites:
	$(MAKE) -C $(WAVE25) correctness candidate-linkage

$(BUILD) $(BUILD)/generated $(BUILD)/full:
	mkdir -p $@

$(BUILD)/generated/wave31_branch_fold.S: generate_branch_fold_asm.py \
		analyze_branch_fold.py $(GT)/gt_invntt_fused_soa.S \
		$(GT)/gt_invntt_ntt32_soa.s $(GT)/gt_invntt_dft3_soa.s \
		$(GT)/gt_invntt_postprocess_soa.s \
		$(WAVE20)/scripts/generate_native_three_child.py \
		| $(BUILD)/generated
	$(PYTHON) generate_branch_fold_asm.py \
		--source $(GT)/gt_invntt_fused_soa.S \
		--native-generator $(WAVE20)/scripts/generate_native_three_child.py \
		--analysis analyze_branch_fold.py --output $@

$(BUILD)/generated/harness.c: generate_harness.py \
		$(WAVE25)/src/wave25_harness.c | $(BUILD)/generated
	$(PYTHON) $< --source $(WAVE25)/src/wave25_harness.c --output $@

$(BUILD)/wave31_branch_fold.o: $(BUILD)/generated/wave31_branch_fold.S | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TARGET_FLAGS) -c $< -o $@

$(BUILD)/harness.o: $(BUILD)/generated/harness.c | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TARGET_FLAGS) -c $< -o $@

$(BUILD)/generated/fold_lazy_base.c: \
		$(WAVE24)/scripts/generate_best_kem.py \
		$(W20B)/generated/wave20_wire_kem.c | $(BUILD)/generated
	$(PYTHON) $< --source $(W20B)/generated/wave20_wire_kem.c \
		--prefix wave31_fold_lazy --forward lazy \
		--lazy-consumers asm-nocenter --invntt three-child --output $@

$(BUILD)/generated/algebraic_base.c: \
		$(WAVE24)/scripts/generate_best_kem.py \
		$(W20B)/generated/wave20_wire_kem.c | $(BUILD)/generated
	$(PYTHON) $< --source $(W20B)/generated/wave20_wire_kem.c \
		--prefix wave31_algebraic --forward lazy \
		--lazy-consumers asm-nocenter --invntt three-child --output $@

$(BUILD)/generated/fold_exact_base.c: \
		$(WAVE24)/scripts/generate_best_kem.py \
		$(W20B)/generated/wave20_wire_kem.c | $(BUILD)/generated
	$(PYTHON) $< --source $(W20B)/generated/wave20_wire_kem.c \
		--prefix wave31_fold_exact --forward lazy \
		--lazy-consumers asm-nocenter --invntt three-child --output $@

$(BUILD)/generated/fold_lazy_kem.c: generate_kem_variant.py \
		$(BUILD)/generated/fold_lazy_base.c | $(BUILD)/generated
	$(PYTHON) $< --source $(BUILD)/generated/fold_lazy_base.c \
		--endpoint wave31_invntt_native_rminus1_branch_fold_lazy_avx2 \
		--output $@

$(BUILD)/generated/algebraic_kem.c: generate_kem_variant.py \
		$(BUILD)/generated/algebraic_base.c | $(BUILD)/generated
	$(PYTHON) $< --source $(BUILD)/generated/algebraic_base.c \
		--endpoint wave31_invntt_native_rminus1_algebraic_avx2 \
		--output $@

$(BUILD)/generated/fold_exact_kem.c: generate_kem_variant.py \
		$(BUILD)/generated/fold_exact_base.c | $(BUILD)/generated
	$(PYTHON) $< --source $(BUILD)/generated/fold_exact_base.c \
		--endpoint wave31_invntt_native_rminus1_branch_fold_exact_avx2 \
		--output $@

$(BUILD)/full/fold_lazy_kem.o: $(BUILD)/generated/fold_lazy_kem.c | $(BUILD)/full
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TARGET_FLAGS) -c $< -o $@

$(BUILD)/full/algebraic_kem.o: $(BUILD)/generated/algebraic_kem.c | $(BUILD)/full
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TARGET_FLAGS) -c $< -o $@

$(BUILD)/full/fold_exact_kem.o: $(BUILD)/generated/fold_exact_kem.c | $(BUILD)/full
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TARGET_FLAGS) -c $< -o $@

$(BUILD)/generated/full_harness.c: generate_full_harness.py \
		$(WAVE24)/src/wave24_full_harness.c | $(BUILD)/generated
	$(PYTHON) $< --source $(WAVE24)/src/wave24_full_harness.c --output $@

$(BUILD)/full/harness.o: $(BUILD)/generated/full_harness.c | $(BUILD)/full
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TARGET_FLAGS) -c $< -o $@

$(TARGET): prerequisites $(OBJECTS) | $(BUILD)
	$(CC) $(TARGET_FLAGS) -no-pie -Wl,--build-id=sha1 \
		-Wl,-Map=$(BUILD)/wave31.map -o $@ $(OBJECTS)

$(FULL_TARGET): prerequisites $(FULL_OBJECTS) | $(BUILD)
	$(CC) $(TARGET_FLAGS) -no-pie -Wl,--build-id=sha1 \
		-Wl,-Map=$(BUILD)/wave31_full_kem.map -o $@ $(FULL_OBJECTS)

clean:
	$(RM) -r $(BUILD)

-include $(BUILD)/*.d
