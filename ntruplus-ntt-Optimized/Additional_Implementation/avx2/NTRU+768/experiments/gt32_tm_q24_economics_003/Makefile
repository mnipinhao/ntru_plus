PYTHON ?= python3
GENERATOR := tools/generate_economics_gate.py
OUTPUT := generated/tm_q24_economics.json
TM_GENERATOR := ../gt32_persistent_twiddle_major_002/tools/generate_persistent_gate.py
TM_PROOF := ../gt32_persistent_twiddle_major_002/generated/persistent_tm_gate.json
MAPPING := ../avx2_gt32_tile4_official_001/generated/tile4_serialized_mapping.json

ARGS := --tm-generator $(TM_GENERATOR) --tm-proof $(TM_PROOF) \
	--serialized-mapping $(MAPPING)

.PHONY: all generate check

all: check

generate:
	$(PYTHON) $(GENERATOR) $(ARGS) --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) $(ARGS) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
