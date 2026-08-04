PYTHON ?= python3

.PHONY: all generate check clean

all: check

generate:
	$(PYTHON) tools/generate_vertical_schedule.py

check:
	$(PYTHON) tools/generate_vertical_schedule.py --check
	$(PYTHON) tests/test_vertical_schedule.py

clean:
	$(RM) -r generated results
