PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output/gt864_forward_ntt9_level1.n1.opt.S

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

check: | $(BUILD)
	$(PYTHON) prove_level1.py > $(BUILD)/level1-range.json
	$(PYTHON) -m json.tool $(BUILD)/level1-range.json >/dev/null
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_ntt9_level1.n1.opt.o $(RETURNED)

clean:
	rm -f -r $(BUILD)
