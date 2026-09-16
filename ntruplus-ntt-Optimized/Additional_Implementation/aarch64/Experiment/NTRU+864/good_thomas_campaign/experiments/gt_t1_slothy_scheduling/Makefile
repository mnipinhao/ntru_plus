PYTHON ?= python3
SKILL := /Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring

.PHONY: prepare contracts static post-slothy candidate check clean

prepare:
	$(PYTHON) prepare_baseline.py
	$(PYTHON) generate_symbolic.py

contracts: prepare
	$(PYTHON) $(SKILL)/scripts/check-kernel-contract.py baseline-contract.yml --kind baseline
	$(PYTHON) $(SKILL)/scripts/check-kernel-contract.py kernel-contract.yml --kind kernel
	$(PYTHON) $(SKILL)/scripts/check-kernel-contract.py candidate-contract.yml --kind candidate

static: contracts
	$(PYTHON) static_audit.py
	# Known checker limitation: its LOAD rule defines only the first LDP output.
	# static_audit.py performs the strict two-destination LDP-aware def/use gate.
	$(PYTHON) $(SKILL)/scripts/check-symbolic-asm.py --candidate \
		--kernel-contract kernel-contract.yml --baseline-contract baseline-contract.yml \
		--mode existing_region_replacement --warnings-only gt864_t1_one_bank.sym.S
	$(PYTHON) $(SKILL)/scripts/check-physical-reg-leaks.py \
		--contract kernel-contract.yml gt864_t1_one_bank.sym.S
	$(PYTHON) $(SKILL)/scripts/compare-kernel-contract.py \
		baseline-contract.yml candidate-contract.yml

check: static post-slothy candidate

post-slothy:
	$(PYTHON) post_slothy_audit.py

candidate: post-slothy
	$(PYTHON) prepare_candidate.py

clean:
	$(RM) -r build
