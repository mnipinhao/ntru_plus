PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s
M5F := ../gt_forward_composition_barrett
M5O := ../gt_forward_full_poly_ntt_asm
OFFICIAL := ../../../../../NTRU+864/asm/ntt.s

.PHONY: all static check-oracle check-full check-abi check clean
all: check

$(BUILD):
	mkdir -p $@

gt864_forward_one_bank_full_register.sym.S: generate_symbolic.py
	$(PYTHON) $<

gt864_forward_one_bank_full_register_pinned.sym.S: generate_pinned_symbolic.py gt864_forward_one_bank_full_register.sym.S
	$(PYTHON) $<

gt864_forward_six_bank_full_register.S: generate_six_bank.py \
		slothy-output/gt864_forward_one_bank_full_register_pinned.n1.opt.S \
		slothy-output/gt864_forward_one_bank_full_register_pinned.schedule.log
	$(PYTHON) $<

$(BUILD)/gt864_forward_barrett_tables.h: $(M5F)/generate_tables.py | $(BUILD)
	$(PYTHON) $< $@

$(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/map-proof.json: $(M5O)/generate_official_map.py | $(BUILD)
	$(PYTHON) $< $(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/map-proof.json

$(BUILD)/pass2-test: ../gt_forward_six_bank_pass2_asm/test_gt864_forward_six_bank.c \
		gt864_forward_six_bank_full_register.S $(M5F)/gt864_forward_compose.c $(BUILD)/gt864_forward_barrett_tables.h
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) -I$(M5F) \
		-Dgt864_forward_six_bank_pass2=gt864_forward_six_bank_pass2_full_register \
		-o $@ $< $(M5F)/gt864_forward_compose.c gt864_forward_six_bank_full_register.S

$(BUILD)/full-test: $(M5O)/test_gt864_forward_poly_ntt.c $(BUILD)/gt864_fr0_to_official_map.h \
		gt864_forward_poly_ntt_full_register.S gt864_forward_six_bank_full_register.S $(TOP) $(OFFICIAL)
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) \
		-Dgt864_forward_poly_ntt_experiment=gt864_forward_poly_ntt_full_register \
		-o $@ $(M5O)/test_gt864_forward_poly_ntt.c gt864_forward_poly_ntt_full_register.S \
		gt864_forward_six_bank_full_register.S $(TOP) $(OFFICIAL)

$(BUILD)/abi-test: test_abi.c abi_probe.S gt864_forward_poly_ntt_full_register.S \
		gt864_forward_six_bank_full_register.S $(TOP)
	$(CC) $(CFLAGS) -march=armv8-a+simd -o $@ test_abi.c abi_probe.S \
		gt864_forward_poly_ntt_full_register.S gt864_forward_six_bank_full_register.S $(TOP)

static: gt864_forward_one_bank_full_register_pinned.sym.S gt864_forward_six_bank_full_register.S | $(BUILD)
	$(PYTHON) audit_artifacts.py > $(BUILD)/artifact-audit.json
	$(PYTHON) -m json.tool $(BUILD)/artifact-audit.json >/dev/null

check-oracle: $(BUILD)/pass2-test
	$(BUILD)/pass2-test

check-full: $(BUILD)/full-test
	$(BUILD)/full-test

check-abi: $(BUILD)/abi-test
	$(BUILD)/abi-test

check: static check-oracle check-full check-abi

clean:
	rm -f -r $(BUILD)
