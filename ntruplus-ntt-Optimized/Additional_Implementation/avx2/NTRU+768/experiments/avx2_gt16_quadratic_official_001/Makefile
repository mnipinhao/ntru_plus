PYTHON ?= python3

.PHONY: all generate check clean

all: check

generate:
	$(PYTHON) tools/generate_quadratic.py

check:
	$(PYTHON) tools/generate_quadratic.py --check
	$(PYTHON) tests/test_quadratic_oracle.py

clean:
	$(RM) -r generated results
