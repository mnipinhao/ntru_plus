.PHONY: all check clean

all: check

check:
	python3 tools/audit.py
	python3 -m json.tool generated/transfer_matrix.json >/dev/null

clean:
	rm -f generated/transfer_matrix.json
