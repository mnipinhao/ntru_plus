PYTHON ?= python3

.PHONY: check proof kat clean

check: proof kat

proof:
	$(PYTHON) proof.py

kat:
	$(PYTHON) test_kat.py

clean:
	$(RM) proof-report.json kat-report.json
	$(RM) -r __pycache__
