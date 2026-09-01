PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

check: | $(BUILD)
	$(PYTHON) prove_core.py > $(BUILD)/core-range.json
	$(PYTHON) -m json.tool $(BUILD)/core-range.json >/dev/null
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_ntt9_core.n1.alloc.o $(RETURNED)/gt864_forward_ntt9_core.n1.alloc.S
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_ntt9_core.n1.opt.o $(RETURNED)/gt864_forward_ntt9_core.n1.opt.S

clean:
	rm -f -r $(BUILD)
