.PHONY: all check clean

all: check

check:
	python3 tools/generate_cross_factor_packing_gate.py
	python3 -m json.tool generated/cross_factor_packing_gate.json >/dev/null

clean:
