.PHONY: all check clean

all: check

check:
	python3 tools/generate_pair_maddwd_gate.py
	python3 -m json.tool generated/qbm_pair_maddwd_gate.json >/dev/null

clean:
