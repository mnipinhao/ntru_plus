PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
M5RD := ../gt_forward_level2_one_mul_b3
M5U := ../gt_friso2_leaf_basis_abi
M5R := ../gt_forward_full_register_pass2_dag
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s

.PHONY: all check generate prove audit clean
all: check
generate:
	$(PYTHON) generate_candidate.py
prove: generate | $(BUILD)
	$(PYTHON) prove_absorption.py > $(BUILD)/proof.json
	$(PYTHON) -m json.tool $(BUILD)/proof.json >/dev/null
audit: generate | $(BUILD)
	$(PYTHON) audit_candidate.py > $(BUILD)/audit.json
	$(PYTHON) -m json.tool $(BUILD)/audit.json >/dev/null
$(BUILD):
	mkdir -p $@
$(BUILD)/test: test_forward_friso2.c gt864_forward_poly_ntt_friso2.S \
		gt864_forward_six_bank_friso2.S $(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S $(M5U)/gt864_friso2.c $(TOP) | $(BUILD)
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(M5U) -o $@ \
		test_forward_friso2.c $(M5U)/gt864_friso2.c \
		gt864_forward_poly_ntt_friso2.S gt864_forward_six_bank_friso2.S \
		$(M5RD)/gt864_forward_poly_ntt_all_one_mul_b3.S \
		$(M5RD)/gt864_forward_six_bank_all_one_mul_b3.S $(TOP)
$(BUILD)/abi-test: $(M5R)/test_abi.c $(M5R)/abi_probe.S \
		gt864_forward_poly_ntt_friso2.S gt864_forward_six_bank_friso2.S $(TOP) | $(BUILD)
	$(CC) $(CFLAGS) -march=armv8-a+simd \
		-Dgt864_forward_poly_ntt_full_register=gt864_forward_poly_ntt_friso2 \
		-o $@ $(M5R)/test_abi.c $(M5R)/abi_probe.S \
		gt864_forward_poly_ntt_friso2.S gt864_forward_six_bank_friso2.S $(TOP)
check: | $(BUILD)
check: prove audit $(BUILD)/test $(BUILD)/abi-test
	$(BUILD)/test
	$(BUILD)/abi-test
clean:
	rm -f -r $(BUILD)
