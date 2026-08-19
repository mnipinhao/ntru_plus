PYTHON ?= python3
GEN := generated/qword_semantic_packet_gate.json
SCRIPT := tools/generate_qword_semantic_packet_gate.py

.PHONY: all check clean

all: $(GEN)

$(GEN): $(SCRIPT)
	$(PYTHON) $(SCRIPT) --output $(GEN)

check: $(GEN)
	$(PYTHON) $(SCRIPT) --output /tmp/qword_semantic_packet_gate.check.json
	cmp $(GEN) /tmp/qword_semantic_packet_gate.check.json
	$(PYTHON) -m py_compile $(SCRIPT)

clean:
	rm -f /tmp/qword_semantic_packet_gate.check.json
