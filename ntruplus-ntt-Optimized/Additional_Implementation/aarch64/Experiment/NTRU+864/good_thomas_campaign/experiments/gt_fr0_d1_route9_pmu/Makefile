PYTHON?=python3
.PHONY: prepare run audit clean
prepare:
	mkdir -p build
	$(PYTHON) generate_tables.py
	$(PYTHON) -m py_compile generate_tables.py run_pi5.py
run: prepare
	$(PYTHON) run_pi5.py
audit:
	$(PYTHON) audit_results.py
clean:
	rm -rf build __pycache__
