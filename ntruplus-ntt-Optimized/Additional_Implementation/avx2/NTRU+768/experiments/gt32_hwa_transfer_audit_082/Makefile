.PHONY: all check clean

all: check

check:
	python3 tools/generate_audit.py
	python3 -m json.tool generated/forward_callsite_graph.json >/dev/null
	python3 -m json.tool generated/transfer_audit.json >/dev/null

clean:
	rm -f generated/forward_callsite_graph.json generated/transfer_audit.json
