PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

gt864_forward_two_ntt9_blocks.sym.S: generate_symbolic.py \
		../gt_forward_ntt16_ntt9_handoff_slothy/gt864_forward_ntt16_ntt9_handoff.sym.S \
		../gt_forward_ntt9_core_slothy/gt864_forward_ntt9_core.sym.S
	$(PYTHON) generate_symbolic.py

check: gt864_forward_two_ntt9_blocks.sym.S | $(BUILD)
	$(PYTHON) prove_two_blocks.py > $(BUILD)/two-block-proof.json
	$(PYTHON) -m json.tool $(BUILD)/two-block-proof.json >/dev/null
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_two_ntt9_blocks.n1.alloc.o $(RETURNED)/gt864_forward_two_ntt9_blocks.n1.alloc.S
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_two_ntt9_blocks.n1.opt.o $(RETURNED)/gt864_forward_two_ntt9_blocks.n1.opt.S

clean:
	rm -f -r $(BUILD)
