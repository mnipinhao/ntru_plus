.PHONY: check clean

PYTHON ?= python3
OUT := generated/progressive_soa_gate.json

check: $(OUT)
	$(PYTHON) tools/generate_gate.py --check --output $(OUT)

$(OUT): tools/generate_gate.py
	@mkdir -p generated
	$(PYTHON) tools/generate_gate.py --output $(OUT)

clean:
	rm -f $(OUT)
