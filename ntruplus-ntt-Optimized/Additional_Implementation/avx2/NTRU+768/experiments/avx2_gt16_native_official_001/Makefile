PYTHON ?= python3

.PHONY: all generate check clean

all: check

generate:
	$(PYTHON) tools/generate_gt16.py

check:
	$(PYTHON) tools/generate_gt16.py --check
	$(PYTHON) tests/test_scalar_gt16.py

clean:
	$(RM) -r generated results
