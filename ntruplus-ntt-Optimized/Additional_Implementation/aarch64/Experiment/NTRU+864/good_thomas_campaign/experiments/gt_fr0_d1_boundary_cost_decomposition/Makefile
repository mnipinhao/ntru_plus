PYTHON ?= python3
.PHONY: check audit remote clean
check:
	$(PYTHON) -m py_compile run_pi5.py audit_results.py
audit: check
	$(PYTHON) audit_results.py > build/audit.json
	$(PYTHON) -m json.tool build/audit.json >/dev/null
remote: check
	$(PYTHON) run_pi5.py
clean:
	rm -rf build __pycache__
