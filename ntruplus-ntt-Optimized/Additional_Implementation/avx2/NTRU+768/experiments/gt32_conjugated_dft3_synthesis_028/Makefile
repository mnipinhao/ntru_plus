.PHONY: all check
all: check
check: generated/conjugated_dft3_gate.json
	python3 -m json.tool $< >/dev/null
generated/conjugated_dft3_gate.json: tools/generate_gate.py ../avx2_gt16_quadratic_official_001/generated/quadratic-constants.h
	python3 tools/generate_gate.py
