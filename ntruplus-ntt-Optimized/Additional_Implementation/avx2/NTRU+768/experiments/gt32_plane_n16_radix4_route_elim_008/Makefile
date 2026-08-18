PYTHON ?= python3
OUTPUT := generated/plane_n16_radix4_gate.json

.PHONY: all generate check

all: check

generate:
	$(PYTHON) tools/generate_radix4_gate.py --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) tools/generate_radix4_gate.py --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
