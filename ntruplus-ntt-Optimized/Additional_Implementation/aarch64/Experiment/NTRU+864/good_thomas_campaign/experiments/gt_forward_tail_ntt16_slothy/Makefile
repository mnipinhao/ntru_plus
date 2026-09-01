PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output

.PHONY: all preflight check clean
all: check

$(BUILD):
	mkdir -p $@

preflight: | $(BUILD)
	$(PYTHON) prove_tail_ntt16.py > $(BUILD)/tail-ntt16-proof.json
	$(PYTHON) -m json.tool $(BUILD)/tail-ntt16-proof.json >/dev/null

check: preflight
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_tail_ntt16.n1.alloc.o $(RETURNED)/gt864_forward_tail_ntt16.n1.alloc.S
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_tail_ntt16.n1.opt.o $(RETURNED)/gt864_forward_tail_ntt16.n1.opt.S

clean:
	rm -f -r $(BUILD)
