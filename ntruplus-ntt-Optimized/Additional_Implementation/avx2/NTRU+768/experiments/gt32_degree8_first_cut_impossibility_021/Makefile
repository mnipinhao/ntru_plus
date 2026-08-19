.PHONY: all check clean

all: check

check:
	python3 tools/generate_first_cut_impossibility.py
	python3 -m json.tool generated/first_cut_impossibility.json >/dev/null

clean:
