PYTHON ?= python3
BUILD := build

.PHONY: static remote remote-d1 audit clean

static:
	mkdir -p $(BUILD)
	$(PYTHON) prove_static_feasibility.py > $(BUILD)/static-feasibility.json
	$(PYTHON) -m json.tool $(BUILD)/static-feasibility.json >/dev/null

remote:
	$(PYTHON) run_pi5.py

remote-d1:
	$(PYTHON) run_pi5_d1.py

audit: static
	$(PYTHON) audit_baseline.py > $(BUILD)/baseline-audit.json
	$(PYTHON) -m json.tool $(BUILD)/baseline-audit.json >/dev/null
	@if test -f $(BUILD)/pi5-b1-d1/summary.json; then \
		$(PYTHON) audit_d1.py > $(BUILD)/d1-audit.json; \
		$(PYTHON) -m json.tool $(BUILD)/d1-audit.json >/dev/null; \
	fi

clean:
	rm -rf $(BUILD)
