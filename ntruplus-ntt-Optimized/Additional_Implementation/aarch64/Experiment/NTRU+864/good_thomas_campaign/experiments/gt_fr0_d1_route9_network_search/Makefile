PYTHON ?= python3

.PHONY: check audit clean
check: audit
audit:
	mkdir -p build
	$(PYTHON) -m py_compile prepare.py audit_results.py
	$(PYTHON) prepare.py > build/network-search.json
	$(PYTHON) audit_results.py > build/audit.json
	$(PYTHON) -m json.tool build/network-search.json >/dev/null
	$(PYTHON) -m json.tool build/audit.json >/dev/null
clean:
	rm -rf build __pycache__
