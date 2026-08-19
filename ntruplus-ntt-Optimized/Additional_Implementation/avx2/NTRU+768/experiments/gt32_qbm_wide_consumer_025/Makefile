.PHONY: all check clean

all: check

check:
	python3 tools/generate_wide_consumer_gate.py
	python3 -m json.tool generated/wide_consumer_gate.json >/dev/null

clean:
