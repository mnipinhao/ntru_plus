.PHONY: all check clean

all: check

check:
	python3 tools/generate_merge_basis_gate.py
	python3 -m json.tool generated/merge_basis_gate.json >/dev/null

clean:
