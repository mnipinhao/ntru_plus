PYTHON ?= python3
BUILD := build

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

check: | $(BUILD)
	$(PYTHON) prove_exact_dag.py > $(BUILD)/exact-dag-range.json
	$(PYTHON) -m json.tool $(BUILD)/exact-dag-range.json >/dev/null
	$(PYTHON) check_artifacts.py

clean:
	rm -f -r $(BUILD)
