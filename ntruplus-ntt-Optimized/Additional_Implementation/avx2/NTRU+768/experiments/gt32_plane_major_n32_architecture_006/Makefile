PYTHON ?= python3
GENERATOR := tools/generate_architecture_gate.py
OUTPUT := generated/plane_major_n32_architecture_gate.json

.PHONY: all generate check

all: check

generate:
	$(PYTHON) $(GENERATOR) --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
