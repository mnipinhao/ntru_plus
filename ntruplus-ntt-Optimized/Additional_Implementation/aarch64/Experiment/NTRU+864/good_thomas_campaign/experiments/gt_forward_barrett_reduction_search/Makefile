PYTHON ?= python3
BUILD := build

.PHONY: all check clean
all: check

$(BUILD):
	mkdir -p $@

check: | $(BUILD)
	$(PYTHON) prove_constant_coverage.py > $(BUILD)/constant-coverage.json
	$(PYTHON) search_reductions.py > $(BUILD)/reduction-search.json
	$(PYTHON) -m json.tool $(BUILD)/constant-coverage.json >/dev/null
	$(PYTHON) -m json.tool $(BUILD)/reduction-search.json >/dev/null

clean:
	rm -f -r $(BUILD)
