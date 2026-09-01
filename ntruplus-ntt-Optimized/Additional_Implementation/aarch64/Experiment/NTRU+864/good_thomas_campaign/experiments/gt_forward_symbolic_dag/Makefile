PYTHON ?= python3
CC ?= cc
BUILD := build
RETURNED := slothy-output/gt864_forward_b3_two_product.n1.opt.S

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

check: | $(BUILD)
	$(PYTHON) prove_exact_dag.py > $(BUILD)/exact-dag-range.json
	$(PYTHON) -m json.tool $(BUILD)/exact-dag-range.json >/dev/null
	$(PYTHON) check_artifacts.py
	$(CC) -c -x assembler -march=armv8-a+simd -o $(BUILD)/gt864_forward_b3_two_product.n1.opt.o $(RETURNED)

clean:
	rm -f -r $(BUILD)
