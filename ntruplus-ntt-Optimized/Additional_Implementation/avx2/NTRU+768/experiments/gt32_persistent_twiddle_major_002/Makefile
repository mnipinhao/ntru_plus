PYTHON ?= python3
GENERATOR := tools/generate_persistent_gate.py
OUTPUT := generated/persistent_tm_gate.json
NTT_M := ../../ntt_m.s
BASEMUL := ../../basemul.s
PACK := ../../pack.s
INVNTT := ../../invntt.s
MAPPING := ../avx2_gt32_tile4_official_001/generated/tile4_serialized_mapping.json

ARGS := --ntt-m $(NTT_M) --basemul $(BASEMUL) --pack $(PACK) \
	--invntt $(INVNTT) --serialized-mapping $(MAPPING)

.PHONY: all generate check

all: check

generate:
	$(PYTHON) $(GENERATOR) $(ARGS) --output $(OUTPUT)

check: generate
	@tmp=$$(mktemp); \
	$(PYTHON) $(GENERATOR) $(ARGS) --output $$tmp; \
	cmp $(OUTPUT) $$tmp; \
	rm -f $$tmp
