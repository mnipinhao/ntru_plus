PYTHON ?= python3

.PHONY: check audit clean

check: audit

audit:
	mkdir -p build
	$(PYTHON) -m py_compile analyze_architecture.py audit_results.py
	$(PYTHON) analyze_architecture.py > build/architecture.json
	$(PYTHON) audit_results.py > build/audit.json
	$(PYTHON) -m json.tool build/architecture.json >/dev/null
	$(PYTHON) -m json.tool build/audit.json >/dev/null

clean:
	rm -rf build __pycache__
