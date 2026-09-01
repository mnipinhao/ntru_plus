PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output

.PHONY: all preflight check clean
all: check

$(BUILD):
	mkdir -p $@

gt864_forward_one_bank.sym.S: generate_symbolic.py \
		../gt_forward_tail_ntt16_slothy/gt864_forward_tail_ntt16.sym.S \
		../gt_forward_two_ntt9_blocks_slothy/gt864_forward_two_ntt9_blocks.sym.S
	$(PYTHON) generate_symbolic.py

preflight: gt864_forward_one_bank.sym.S | $(BUILD)
	$(PYTHON) prove_one_bank.py > $(BUILD)/one-bank-proof.json
	$(PYTHON) -m json.tool $(BUILD)/one-bank-proof.json >/dev/null

check: preflight
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_one_bank.n1.alloc.o $(RETURNED)/gt864_forward_one_bank.n1.alloc.S
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_one_bank.n1.opt.o $(RETURNED)/gt864_forward_one_bank.n1.opt.S

clean:
	rm -f -r $(BUILD)
