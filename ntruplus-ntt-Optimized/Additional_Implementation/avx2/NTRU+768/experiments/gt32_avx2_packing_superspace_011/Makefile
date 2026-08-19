.PHONY: all check clean

PYTHON ?= python3
OUT := generated/avx2_packing_superspace_gate.json

all: $(OUT)

$(OUT): tools/generate_packing_superspace_gate.py
	@mkdir -p generated
	$(PYTHON) $< --output $@

check: $(OUT)
	$(PYTHON) tools/generate_packing_superspace_gate.py --output /tmp/avx2_packing_superspace_gate.check.json
	diff -u $(OUT) /tmp/avx2_packing_superspace_gate.check.json

clean:
	rm -f $(OUT)
