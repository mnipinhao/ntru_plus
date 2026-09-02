PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
M5F := ../gt_forward_composition_barrett
M5N := ../gt_forward_six_bank_pass2_asm
M5O := ../gt_forward_full_poly_ntt_asm
M5R := ../gt_forward_full_register_pass2_dag
M5RC := ../gt_forward_one_mul_b3
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s
OFFICIAL := ../../../../../NTRU+864/asm/ntt.s

.PHONY: check proof prepare static check-pass2 check-full check-abi
check: proof static check-pass2 check-full check-abi
proof:
	$(PYTHON) prove_all_one_mul_b3.py
prepare:
	$(PYTHON) prepare.py
static: prepare
	$(PYTHON) audit_candidate.py
	$(PYTHON) generate_integration.py
$(BUILD):
	mkdir -p $@
$(BUILD)/gt864_forward_barrett_tables.h: $(M5F)/generate_tables.py | $(BUILD)
	$(PYTHON) $< $@
$(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/map-proof.json: $(M5O)/generate_official_map.py | $(BUILD)
	$(PYTHON) $< $(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/map-proof.json
$(BUILD)/pass2-test: $(M5RC)/test_pass2_modq.c gt864_forward_six_bank_all_one_mul_b3.S \
		$(M5F)/gt864_forward_compose.c $(BUILD)/gt864_forward_barrett_tables.h
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) -I$(M5F) \
		-Dgt864_forward_six_bank_pass2=gt864_forward_six_bank_pass2_all_one_mul_b3 \
		-o $@ $< $(M5F)/gt864_forward_compose.c gt864_forward_six_bank_all_one_mul_b3.S
$(BUILD)/full-test: $(M5O)/test_gt864_forward_poly_ntt.c $(BUILD)/gt864_fr0_to_official_map.h \
		gt864_forward_poly_ntt_all_one_mul_b3.S gt864_forward_six_bank_all_one_mul_b3.S \
		$(TOP) $(OFFICIAL)
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) \
		-Dgt864_forward_poly_ntt_experiment=gt864_forward_poly_ntt_all_one_mul_b3 \
		-o $@ $(M5O)/test_gt864_forward_poly_ntt.c gt864_forward_poly_ntt_all_one_mul_b3.S \
		gt864_forward_six_bank_all_one_mul_b3.S $(TOP) $(OFFICIAL)
$(BUILD)/abi-test: $(M5R)/test_abi.c $(M5R)/abi_probe.S \
		gt864_forward_poly_ntt_all_one_mul_b3.S gt864_forward_six_bank_all_one_mul_b3.S $(TOP)
	$(CC) $(CFLAGS) -march=armv8-a+simd \
		-Dgt864_forward_poly_ntt_full_register=gt864_forward_poly_ntt_all_one_mul_b3 \
		-o $@ $(M5R)/test_abi.c $(M5R)/abi_probe.S gt864_forward_poly_ntt_all_one_mul_b3.S \
		gt864_forward_six_bank_all_one_mul_b3.S $(TOP)
check-pass2: $(BUILD)/pass2-test
	$<
check-full: $(BUILD)/full-test
	$<
check-abi: $(BUILD)/abi-test
	$<
