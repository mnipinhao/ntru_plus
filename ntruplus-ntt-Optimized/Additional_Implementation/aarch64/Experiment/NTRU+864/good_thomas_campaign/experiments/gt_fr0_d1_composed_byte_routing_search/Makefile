PYTHON ?= python3

.PHONY: prepare audit clean
prepare:
	mkdir -p build
	$(PYTHON) -m py_compile analyze_composed.py audit_results.py
	$(PYTHON) analyze_composed.py > build/composed-routing.json

audit: prepare
	$(PYTHON) audit_results.py
	$(PYTHON) -m json.tool build/composed-routing.json >/dev/null
	$(PYTHON) -m json.tool build/audit.json >/dev/null

clean:
	rm -rf build __pycache__
