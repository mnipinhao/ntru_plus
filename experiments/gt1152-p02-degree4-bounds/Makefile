PYTHON ?= python3
ITERATIONS ?= 2

.PHONY: check bounds empirical clean

check: bounds empirical

bounds:
	$(PYTHON) bounds.py

empirical: bounds
	$(PYTHON) instrument.py --iterations $(ITERATIONS)

clean:
	$(RM) bounds-report.json empirical-report.json
	$(RM) -r __pycache__
