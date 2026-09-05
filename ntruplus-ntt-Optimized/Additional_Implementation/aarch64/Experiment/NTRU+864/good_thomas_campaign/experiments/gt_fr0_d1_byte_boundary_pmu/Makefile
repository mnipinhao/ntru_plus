PYTHON?=python3
.PHONY: prepare run local audit
prepare:
	$(PYTHON) generate.py
run: prepare
	$(PYTHON) run.py
local:
	$(PYTHON) run.py --local
audit: local
	$(PYTHON) audit.py
