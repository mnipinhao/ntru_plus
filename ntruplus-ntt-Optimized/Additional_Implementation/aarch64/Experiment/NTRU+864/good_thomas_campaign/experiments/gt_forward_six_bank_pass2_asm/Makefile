PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic
BUILD := build
M5F := ../gt_forward_composition_barrett

.PHONY: all check check-oracle clean
all: check

$(BUILD):
	mkdir -p $@

gt864_forward_six_bank_pass2.S: generate_asm.py \
		../gt_forward_one_bank_slothy/slothy-output/gt864_forward_one_bank.n1.opt.S \
		../gt_forward_one_bank_slothy/slothy-output/gt864_forward_one_bank.schedule.log
	$(PYTHON) generate_asm.py

$(BUILD)/gt864_forward_barrett_tables.h: $(M5F)/generate_tables.py | $(BUILD)
	$(PYTHON) $(M5F)/generate_tables.py $@

$(BUILD)/gt864_forward_six_bank_pass2.o: gt864_forward_six_bank_pass2.S | $(BUILD)
	$(CC) -c -x assembler -march=armv8-a+simd -o $@ $<

$(BUILD)/test: test_gt864_forward_six_bank.c gt864_forward_six_bank_pass2.S \
		$(M5F)/gt864_forward_compose.c $(BUILD)/gt864_forward_barrett_tables.h
	$(CC) $(CFLAGS) -march=armv8-a+simd -I$(BUILD) -I$(M5F) \
		-o $@ test_gt864_forward_six_bank.c \
		$(M5F)/gt864_forward_compose.c gt864_forward_six_bank_pass2.S

check-oracle: $(BUILD)/test
	$(BUILD)/test

check: check-oracle $(BUILD)/gt864_forward_six_bank_pass2.o
	$(PYTHON) prove_six_bank.py > $(BUILD)/six-bank-proof.json
	$(PYTHON) -m json.tool $(BUILD)/six-bank-proof.json >/dev/null
	$(PYTHON) check_object.py > $(BUILD)/object-audit.json
	$(PYTHON) -m json.tool $(BUILD)/object-audit.json >/dev/null

clean:
	rm -f -r $(BUILD)
