PYTHON ?= python3
NTT := ../../ntt.s
GENERATOR := tools/generate_gate.py
OUTPUT := generated/twiddle_major_gate.json

.PHONY: all generate check

all: check

generate:
	$(PYTHON) $(GENERATOR) --ntt $(NTT) --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) --ntt $(NTT) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
