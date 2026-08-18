PYTHON ?= python3
GENERATOR := tools/generate_terminal_gate.py
OUTPUT := generated/current_m_terminal_gate.json
TM_GENERATOR := ../gt32_persistent_twiddle_major_002/tools/generate_persistent_gate.py
NTT_M := ../../ntt_m.s

ARGS := --tm-generator $(TM_GENERATOR) --ntt-m $(NTT_M)

.PHONY: all generate check

all: check

generate:
	$(PYTHON) $(GENERATOR) $(ARGS) --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) $(ARGS) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
