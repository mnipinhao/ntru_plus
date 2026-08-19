.PHONY: all check clean

all: check

check:
	python3 tools/generate_degree_basis_gate.py
	python3 -m json.tool generated/degree_basis_commutation_gate.json >/dev/null

clean:
