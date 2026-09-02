.PHONY: check

check:
	@for witness in solution-*.json; do python3 -m json.tool "$$witness" >/dev/null; done
	python3 verify_witnesses.py
