PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
TOP := ../gt_2x9x16_ld3_top_split/gt864_top_split.s
M5N_DIR := ../gt_forward_six_bank_pass2_asm
M5N := $(M5N_DIR)/gt864_forward_six_bank_pass2.S
OFFICIAL := ../../../../../NTRU+864/asm/ntt.s

.PHONY: all check prerequisites clean
all: check

$(BUILD):
	mkdir -p $@

prerequisites:
	$(MAKE) -C $(M5N_DIR) gt864_forward_six_bank_pass2.S

$(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/abi-map-proof.json: generate_official_map.py | $(BUILD)
	$(PYTHON) $< $(BUILD)/gt864_fr0_to_official_map.h $(BUILD)/abi-map-proof.json

$(BUILD)/wrapper.o: gt864_forward_poly_ntt_experiment.S | $(BUILD)
	$(CC) -c -x assembler -march=armv8-a+simd -o $@ $<

$(BUILD)/top-split.o: $(TOP) | $(BUILD)
	$(CC) -c -x assembler -march=armv8-a+simd -o $@ $<

$(BUILD)/test: test_gt864_forward_poly_ntt.c gt864_forward_poly_ntt_experiment.S \
		$(TOP) $(M5N) $(OFFICIAL) $(BUILD)/gt864_fr0_to_official_map.h
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) -o $@ \
		test_gt864_forward_poly_ntt.c gt864_forward_poly_ntt_experiment.S \
		$(TOP) $(M5N) $(OFFICIAL)

check: prerequisites $(BUILD)/test $(BUILD)/wrapper.o $(BUILD)/top-split.o
	$(PYTHON) -m json.tool $(BUILD)/abi-map-proof.json >/dev/null
	$(BUILD)/test
	$(PYTHON) audit_composition.py > $(BUILD)/composition-audit.json
	$(PYTHON) -m json.tool $(BUILD)/composition-audit.json >/dev/null

clean:
	rm -f -r $(BUILD)
