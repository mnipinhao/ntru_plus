.PHONY: all check clean

all: check

check:
	python3 tools/generate_degree8_gate.py
	python3 -m json.tool generated/degree8_incomplete_ntt_gate.json >/dev/null

clean:
