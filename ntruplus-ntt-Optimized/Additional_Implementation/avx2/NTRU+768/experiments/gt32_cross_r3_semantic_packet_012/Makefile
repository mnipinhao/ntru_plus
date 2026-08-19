.PHONY: all check clean

PYTHON ?= python3
OUT := generated/cross_r3_semantic_packet_gate.json

all: $(OUT)

$(OUT): tools/generate_cross_r3_packet_gate.py
	@mkdir -p generated
	$(PYTHON) $< --output $@

check: $(OUT)
	$(PYTHON) tools/generate_cross_r3_packet_gate.py --output /tmp/cross_r3_semantic_packet_gate.check.json
	diff -u $(OUT) /tmp/cross_r3_semantic_packet_gate.check.json

clean:
	rm -f $(OUT)
