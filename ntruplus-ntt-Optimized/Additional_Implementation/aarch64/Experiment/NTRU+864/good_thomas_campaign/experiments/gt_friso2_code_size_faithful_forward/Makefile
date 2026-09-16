PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
CF0 := ../gt_friso2_forward_absorption
CF5A := ../gt_friso2_ntt16_producer_pair_link
M5RD := ../gt_forward_level2_one_mul_b3
M5U := ../gt_friso2_leaf_basis_abi
M5R := ../gt_forward_full_register_pass2_dag
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s
SKILL := /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts

.PHONY: check contracts generate static check-full check-abi clean
check: contracts static check-full check-abi
contracts:
	$(PYTHON) $(SKILL)/check-kernel-contract.py baseline-contract.yml --kind baseline
	$(PYTHON) $(SKILL)/check-kernel-contract.py kernel-contract.yml --kind kernel
	$(PYTHON) $(SKILL)/check-kernel-contract.py candidate-contract.yml --kind candidate
generate:
	$(PYTHON) generate_cf5b.py
$(BUILD):
	mkdir -p $@
static: generate | $(BUILD)
	$(PYTHON) audit_cf5b.py > $(BUILD)/audit.json
	$(PYTHON) -m json.tool $(BUILD)/audit.json >/dev/null
$(BUILD)/test: $(CF0)/test_forward_friso2.c gt864_forward_poly_ntt_cf5b.S \
		gt864_forward_six_bank_cf5b.S $(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S $(M5U)/gt864_friso2.c $(TOP) | $(BUILD)
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(M5U) \
		-Dgt864_forward_poly_ntt_friso2=gt864_forward_poly_ntt_cf5b -o $@ \
		$(CF0)/test_forward_friso2.c $(M5U)/gt864_friso2.c \
		gt864_forward_poly_ntt_cf5b.S gt864_forward_six_bank_cf5b.S \
		$(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S $(TOP)
$(BUILD)/abi-test: $(M5R)/test_abi.c $(M5R)/abi_probe.S \
		gt864_forward_poly_ntt_cf5b.S gt864_forward_six_bank_cf5b.S $(TOP) | $(BUILD)
	$(CC) $(CFLAGS) -march=armv8-a+simd \
		-Dgt864_forward_poly_ntt_full_register=gt864_forward_poly_ntt_cf5b \
		-o $@ $(M5R)/test_abi.c $(M5R)/abi_probe.S \
		gt864_forward_poly_ntt_cf5b.S gt864_forward_six_bank_cf5b.S $(TOP)
check-full: $(BUILD)/test
	$<
check-abi: $(BUILD)/abi-test
	$<
clean:
	rm -f -r $(BUILD)
