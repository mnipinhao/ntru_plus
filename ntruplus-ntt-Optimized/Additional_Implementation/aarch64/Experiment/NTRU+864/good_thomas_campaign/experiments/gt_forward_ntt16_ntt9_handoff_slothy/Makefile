PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

check: | $(BUILD)
	$(PYTHON) prove_handoff.py > $(BUILD)/handoff-proof.json
	$(PYTHON) -m json.tool $(BUILD)/handoff-proof.json >/dev/null
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_ntt16_ntt9_handoff.n1.alloc.o $(RETURNED)/gt864_forward_ntt16_ntt9_handoff.n1.alloc.S
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_ntt16_ntt9_handoff.n1.opt.o $(RETURNED)/gt864_forward_ntt16_ntt9_handoff.n1.opt.S

clean:
	rm -f -r $(BUILD)
