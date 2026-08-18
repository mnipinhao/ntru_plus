PYTHON ?= python3
GENERATOR := tools/generate_keygen_gate.py
OUTPUT := generated/p_tm_keygen_gate.json

.PHONY: all generate check

all: check

generate:
	$(PYTHON) $(GENERATOR) --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
