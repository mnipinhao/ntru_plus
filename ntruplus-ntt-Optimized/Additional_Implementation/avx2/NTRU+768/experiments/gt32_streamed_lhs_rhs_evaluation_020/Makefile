.PHONY: all check clean

all: check

check:
	python3 tools/generate_streamed_contraction_gate.py
	python3 -m json.tool generated/streamed_contraction_gate.json >/dev/null

clean:
