PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
M5F := ../gt_forward_composition_barrett
M5N := ../gt_forward_six_bank_pass2_asm
M5O := ../gt_forward_full_poly_ntt_asm
M5R := ../gt_forward_full_register_pass2_dag
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s
OFFICIAL := ../../../../../NTRU+864/asm/ntt.s

.PHONY: check check-math prepare static check-pass2 check-full check-abi

check: check-math static check-pass2 check-full check-abi

check-math:
	$(PYTHON) search_fused_dag.py

prepare:
	$(PYTHON) prepare.py baseline
	$(PYTHON) prepare.py candidate

static: prepare
	$(PYTHON) audit_candidate.py
	$(PYTHON) generate_integration.py
	$(PYTHON) audit_emitted.py

$(BUILD):
	mkdir -p $@

$(BUILD)/gt864_forward_barrett_tables.h: $(M5F)/generate_tables.py | $(BUILD)
	$(PYTHON) $< $@

$(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/map-proof.json: $(M5O)/generate_official_map.py | $(BUILD)
	$(PYTHON) $< $(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/map-proof.json

$(BUILD)/pass2-test: $(M5N)/test_gt864_forward_six_bank.c \
		gt864_forward_six_bank_paired_twist_loads.S $(M5F)/gt864_forward_compose.c \
		$(BUILD)/gt864_forward_barrett_tables.h
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) -I$(M5F) \
		-Dgt864_forward_six_bank_pass2=gt864_forward_six_bank_pass2_paired_twist_loads \
		-o $@ $< $(M5F)/gt864_forward_compose.c gt864_forward_six_bank_paired_twist_loads.S

$(BUILD)/full-test: $(M5O)/test_gt864_forward_poly_ntt.c $(BUILD)/gt864_fr0_to_official_map.h \
		gt864_forward_poly_ntt_paired_twist_loads.S gt864_forward_six_bank_paired_twist_loads.S \
		$(TOP) $(OFFICIAL)
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) \
		-Dgt864_forward_poly_ntt_experiment=gt864_forward_poly_ntt_paired_twist_loads \
		-o $@ $(M5O)/test_gt864_forward_poly_ntt.c gt864_forward_poly_ntt_paired_twist_loads.S \
		gt864_forward_six_bank_paired_twist_loads.S $(TOP) $(OFFICIAL)

$(BUILD)/abi-test: $(M5R)/test_abi.c $(M5R)/abi_probe.S \
		gt864_forward_poly_ntt_paired_twist_loads.S gt864_forward_six_bank_paired_twist_loads.S $(TOP)
	$(CC) $(CFLAGS) -march=armv8-a+simd \
		-Dgt864_forward_poly_ntt_full_register=gt864_forward_poly_ntt_paired_twist_loads \
		-o $@ $(M5R)/test_abi.c $(M5R)/abi_probe.S gt864_forward_poly_ntt_paired_twist_loads.S \
		gt864_forward_six_bank_paired_twist_loads.S $(TOP)

check-pass2: $(BUILD)/pass2-test
	$<

check-full: $(BUILD)/full-test
	$<

check-abi: $(BUILD)/abi-test
	$<
